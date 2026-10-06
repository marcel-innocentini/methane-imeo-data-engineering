from __future__ import annotations

import hashlib
import json
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from shapely.geometry import Point

from qc import ALL_FLAGS, build_qc_flags, normalize

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
INPUT = RAW_DIR / "unep_plumes" / "unep_methanedata_detected_plumes.geojson"
ZIP_INPUT = RAW_DIR / "unep_methanedata_detected_plumes_geojson.zip"
PROCESSED = ROOT / "data" / "processed"
OUTPUTS = ROOT / "outputs"


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def ensure_dirs() -> None:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    OUTPUTS.mkdir(parents=True, exist_ok=True)


def build_point_geometry(df: pd.DataFrame):
    geoms = []
    for lon, lat in zip(df["lon"], df["lat"]):
        ok = (
            pd.notna(lon)
            and pd.notna(lat)
            and -180 <= float(lon) <= 180
            and -90 <= float(lat) <= 90
        )
        geoms.append(Point(float(lon), float(lat)) if ok else None)
    return geoms


def make_map(gdf: gpd.GeoDataFrame, path: Path) -> None:
    plot_df = gdf[
        gdf.geometry.notna()
        & gdf["ch4_fluxrate"].notna()
        & (gdf["ch4_fluxrate"] > 0)
    ].copy()
    if len(plot_df) > 15000:
        plot_df = plot_df.sample(15000, random_state=42)

    fig, ax = plt.subplots(figsize=(12, 6.5))
    values = np.log10(plot_df["ch4_fluxrate"].clip(lower=1))
    sc = ax.scatter(
        plot_df.geometry.x,
        plot_df.geometry.y,
        c=values,
        s=8,
        alpha=0.55,
        linewidths=0,
        cmap="viridis",
    )
    ax.set_xlim(-180, 180)
    ax.set_ylim(-60, 85)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.grid(True, linewidth=0.4, alpha=0.35)
    ax.set_title("UNEP IMEO MARS methane plume detections")
    ax.text(
        0.01,
        0.01,
        f"{len(gdf):,} records | point locations derived from published lat/lon",
        transform=ax.transAxes,
        fontsize=9,
    )
    cbar = fig.colorbar(sc, ax=ax, fraction=0.025, pad=0.02)
    cbar.set_label("log10(CH4 flux rate)")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def make_qa_figure(summary_df: pd.DataFrame, status_counts: dict[str, int], path: Path) -> None:
    flag_df = summary_df[summary_df["category"] == "flag"].sort_values("count")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(flag_df["metric"], flag_df["count"])
    ax.set_xlabel("Records flagged")
    ax.set_title("Reproducible QA/QC checks")
    status_text = " | ".join(f"{k}: {v:,}" for k, v in status_counts.items())
    ax.text(0.01, -0.16, status_text, transform=ax.transAxes, fontsize=10)
    ax.grid(axis="x", linewidth=0.4, alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    ensure_dirs()
    if not INPUT.exists():
        raise FileNotFoundError("Run: python src/download_data.py")

    original = gpd.read_file(INPUT)
    original = normalize(original)
    flags = build_qc_flags(original)
    for col in flags.columns:
        original[col] = flags[col]

    original["observed_at_utc"] = original["observed_at"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    original["has_original_footprint"] = ~original["missing_original_geometry"]

    point_gdf = gpd.GeoDataFrame(
        original.drop(columns=["geometry", "observed_at"], errors="ignore"),
        geometry=build_point_geometry(original),
        crs="EPSG:4326",
    )

    keep_cols = [
        "id_plume", "source_name", "satellite", "observed_at_utc", "lat", "lon",
        "ch4_fluxrate", "ch4_fluxrate_std", "wind_speed", "sector", "country",
        "actionable", "notified", "detection_institution", "quantification_institution",
        "has_original_footprint", "qa_status", "critical_flag_count", "flag_count",
    ] + ALL_FLAGS + ["geometry"]
    keep_cols = [c for c in keep_cols if c in point_gdf.columns]
    point_gdf = point_gdf[keep_cols]

    gpkg = PROCESSED / "mars_plumes_qc.gpkg"
    if gpkg.exists():
        gpkg.unlink()
    point_gdf.to_file(gpkg, layer="plumes_qc", driver="GPKG", engine="pyogrio")

    sample = point_gdf[
        point_gdf.geometry.notna() & point_gdf["qa_status"].ne("FAIL")
    ].sort_values("observed_at_utc", ascending=False).head(1000)
    sample.to_file(
        PROCESSED / "mars_plumes_sample.geojson",
        driver="GeoJSON",
        engine="pyogrio",
    )

    flags_export = pd.concat(
        [original[["id_plume"]].reset_index(drop=True), flags.reset_index(drop=True)],
        axis=1,
    )
    flags_export.to_csv(OUTPUTS / "qa_flags.csv", index=False)

    rows = [
        {"category": "dataset", "metric": "records_total", "count": int(len(original))},
    ]
    status_counts = flags["qa_status"].value_counts().reindex(["PASS", "WARN", "FAIL"], fill_value=0)
    for status, count in status_counts.items():
        rows.append({"category": "status", "metric": status, "count": int(count)})
    for flag in ALL_FLAGS:
        rows.append({"category": "flag", "metric": flag, "count": int(flags[flag].sum())})
    qa_summary = pd.DataFrame(rows)
    qa_summary["pct_of_records"] = (100 * qa_summary["count"] / len(original)).round(3)
    qa_summary.to_csv(OUTPUTS / "qa_summary.csv", index=False)

    flux = pd.to_numeric(original["ch4_fluxrate"], errors="coerce")
    observed = original["observed_at"].dropna()
    summary = {
        "dataset": "UNEP IMEO MARS detected plumes",
        "records_total": int(len(original)),
        "qa_status": {k: int(v) for k, v in status_counts.items()},
        "satellites": int(original["satellite"].nunique(dropna=True)),
        "countries": int(original["country"].nunique(dropna=True)),
        "date_min": observed.min().isoformat() if len(observed) else None,
        "date_max": observed.max().isoformat() if len(observed) else None,
        "flux_non_null": int(flux.notna().sum()),
        "flux_median": float(flux.median()) if flux.notna().any() else None,
        "top_satellites": {
            str(k): int(v) for k, v in original["satellite"].value_counts().head(10).items()
        },
        "top_sectors": {
            str(k): int(v) for k, v in original["sector"].value_counts().head(10).items()
        },
        "source_zip_sha256": file_sha256(ZIP_INPUT) if ZIP_INPUT.exists() else None,
        "crs": "EPSG:4326",
        "processed_artifact": str(gpkg.relative_to(ROOT)),
    }
    (OUTPUTS / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    make_map(point_gdf, OUTPUTS / "methane_plumes_global.png")
    make_qa_figure(
        qa_summary,
        {k: int(v) for k, v in status_counts.items()},
        OUTPUTS / "qa_overview.png",
    )

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
