from __future__ import annotations

import json
import math
import urllib.request
import zipfile
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import font_manager
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Circle

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "unep_plumes"
EXTERNAL = ROOT / "data" / "external"
FIG = ROOT / "docs" / "figures"
TABLE = ROOT / "docs" / "tables"
OUTPUTS = ROOT / "outputs"

PLUMES = RAW / "unep_methanedata_detected_plumes.geojson"
SOURCES = RAW / "unep_methanedata_detected_sources.geojson"
NE_ZIP = EXTERNAL / "ne_110m_admin_0_countries.zip"
NE_DIR = EXTERNAL / "ne_110m_admin_0_countries"
NE_URL = "https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip"

AGRO = "#83C327"
AGRO_DARK = "#12633E"
INK = "#182315"
SURFACE = "#F4F7F1"
GRID = "#C4D3BB"
ORANGE = "#E86A17"
BLUE = "#1677B8"
BROWN = "#B47A32"
MUTED = "#718176"
WARN = "#B7791F"

FONT_REG = Path.home() / "AppData/Local/Microsoft/Windows/Fonts/Montserrat-Regular.ttf"
FONT_BOLD = Path.home() / "AppData/Local/Microsoft/Windows/Fonts/Montserrat-Bold.ttf"
if FONT_REG.exists():
    font_manager.fontManager.addfont(str(FONT_REG))
if FONT_BOLD.exists():
    font_manager.fontManager.addfont(str(FONT_BOLD))

plt.rcParams.update({
    "font.family": "Montserrat" if FONT_REG.exists() else "DejaVu Sans",
    "axes.titlesize": 14,
    "axes.labelsize": 10,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "text.color": INK,
    "axes.labelcolor": INK,
    "axes.edgecolor": GRID,
    "xtick.color": INK,
    "ytick.color": INK,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
})


def ensure_dirs() -> None:
    for p in (EXTERNAL, FIG, TABLE):
        p.mkdir(parents=True, exist_ok=True)


def ensure_world() -> gpd.GeoDataFrame:
    NE_DIR.mkdir(parents=True, exist_ok=True)
    shp = next(NE_DIR.glob("*.shp"), None)
    if shp is None:
        if not NE_ZIP.exists():
            urllib.request.urlretrieve(NE_URL, NE_ZIP)
        with zipfile.ZipFile(NE_ZIP) as zf:
            zf.extractall(NE_DIR)
        shp = next(NE_DIR.glob("*.shp"))
    return gpd.read_file(shp).to_crs(4326)


def save(fig, filename: str, dpi: int = 220) -> None:
    fig.savefig(FIG / filename, dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def fig_pipeline() -> None:
    labels = [
        ("Official UNEP\nMARS GeoJSON", "public input"),
        ("Python\ningestion", "provenance + schema"),
        ("QA/QC\nnormalization", "flags + validation"),
        ("Geospatial\nstorage", "GeoPackage / PostGIS"),
        ("Reproducible\noutputs", "CSV / JSON / maps"),
    ]
    fig, ax = plt.subplots(figsize=(12.5, 3.5))
    ax.set_xlim(0, 12.5)
    ax.set_ylim(0, 3.5)
    ax.axis("off")

    xs = [0.4, 2.9, 5.4, 7.9, 10.4]
    for i, ((title, sub), x) in enumerate(zip(labels, xs)):
        box = FancyBboxPatch(
            (x, 1.15), 1.7, 1.2,
            boxstyle="round,pad=0.03,rounding_size=0.09",
            linewidth=1.4, edgecolor=AGRO_DARK,
            facecolor=SURFACE if i not in (2, 4) else "#EEF5E9",
        )
        ax.add_patch(box)
        ax.text(x + 0.85, 1.82, title, ha="center", va="center",
                fontsize=10.2, fontweight="bold", color=AGRO_DARK)
        ax.text(x + 0.85, 1.35, sub, ha="center", va="center",
                fontsize=7.8, color=MUTED)
        if i < len(xs) - 1:
            arrow = FancyArrowPatch(
                (x + 1.72, 1.75), (xs[i + 1] - 0.08, 1.75),
                arrowstyle="-|>", mutation_scale=15,
                linewidth=1.5, color=AGRO,
            )
            ax.add_patch(arrow)

    ax.text(0.4, 2.9, "METHANE publication pipeline", fontsize=15,
            fontweight="bold", color=INK)
    ax.text(0.4, 0.55,
            "Scope boundary: uses already processed methane detections; no atmospheric retrieval or plume-detection model is implemented.",
            fontsize=8.7, color=MUTED)
    save(fig, "fig01_pipeline_architecture.png")


def fig_global_map(plumes: gpd.GeoDataFrame, world: gpd.GeoDataFrame) -> None:
    p = plumes.copy()
    p["flux"] = pd.to_numeric(p["ch4_fluxrate"], errors="coerce")
    p = p[p["lat"].notna() & p["lon"].notna() & p["flux"].gt(0)]
    fig, ax = plt.subplots(figsize=(13, 6.8))
    world.plot(ax=ax, color=SURFACE, edgecolor=GRID, linewidth=0.45)
    vals = np.log10(p["flux"].clip(lower=1))
    sc = ax.scatter(
        p["lon"], p["lat"], c=vals, s=6, alpha=0.48,
        cmap="viridis", linewidths=0, rasterized=True,
    )
    ax.set_xlim(-180, 180)
    ax.set_ylim(-60, 85)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title("UNEP IMEO MARS methane plume observations in the downloaded snapshot",
                 loc="left", fontweight="bold", color=INK)
    ax.grid(True, linewidth=0.35, alpha=0.35, color=GRID)
    cbar = fig.colorbar(sc, ax=ax, fraction=0.025, pad=0.015)
    cbar.set_label("log10(CH4 flux rate, kg/h)")
    ax.text(
        0.01, 0.015,
        f"{len(plumes):,} plume records | snapshot downloaded 2026-10-06 | points use published lat/lon",
        transform=ax.transAxes, fontsize=8, color=MUTED,
        bbox=dict(facecolor="white", edgecolor="none", alpha=0.8, pad=2),
    )
    save(fig, "fig02_global_plumes_map.png")


def fig_satellites(plumes: gpd.GeoDataFrame) -> pd.DataFrame:
    counts = plumes["satellite"].fillna("Unknown").value_counts().rename_axis("satellite").reset_index(name="count")
    counts["pct"] = 100 * counts["count"] / len(plumes)
    plot = counts.sort_values("count")
    fig, ax = plt.subplots(figsize=(10.8, 6.2))
    bars = ax.barh(plot["satellite"], plot["count"], color=AGRO_DARK)
    ax.set_title("Observation mix by satellite / instrument", loc="left", fontweight="bold")
    ax.set_xlabel("Plume records")
    ax.grid(axis="x", color=GRID, linewidth=0.4, alpha=0.5)
    maxv = plot["count"].max()
    for bar, pct in zip(bars, plot["pct"]):
        pct_label = "<0.1%" if pct < 0.1 else f"{pct:.1f}%"
        ax.text(bar.get_width() + maxv * 0.012, bar.get_y() + bar.get_height()/2,
                pct_label, va="center", fontsize=8, color=MUTED)
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, "fig03_satellite_mix.png")
    counts.to_csv(TABLE / "satellite_summary.csv", index=False)
    return counts


def normalize_source_sector(series: pd.Series) -> pd.Series:
    s = series.fillna("Unknown").astype(str)
    return s.where(~s.str.contains("Coal", case=False, na=False), "Coal")


def fig_sectors(plumes: gpd.GeoDataFrame, sources: gpd.GeoDataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    pc = plumes["sector"].fillna("Unknown").replace({"unknown": "Unknown"}).value_counts().rename_axis("sector").reset_index(name="plume_count")
    sc = normalize_source_sector(sources["sector"]).value_counts().rename_axis("sector").reset_index(name="source_count")
    order = ["Oil and Gas", "Coal", "Waste", "Other", "Steel", "Unknown"]
    pc["sector"] = pd.Categorical(pc["sector"], categories=order, ordered=True)
    sc["sector"] = pd.Categorical(sc["sector"], categories=order, ordered=True)
    pc = pc.sort_values("sector").dropna(subset=["sector"])
    sc = sc.sort_values("sector").dropna(subset=["sector"])

    fig, axes = plt.subplots(1, 2, figsize=(12, 5.4))
    axes[0].bar(pc["sector"].astype(str), pc["plume_count"], color=AGRO_DARK)
    axes[0].set_title("Plume observations", loc="left", fontweight="bold")
    axes[0].set_ylabel("Records")
    axes[1].bar(sc["sector"].astype(str), sc["source_count"], color=AGRO)
    axes[1].set_title("Distinct detected sources", loc="left", fontweight="bold")
    axes[1].set_ylabel("Sources")
    for ax in axes:
        ax.tick_params(axis="x", rotation=30)
        ax.grid(axis="y", color=GRID, linewidth=0.4, alpha=0.5)
        ax.spines[["top", "right"]].set_visible(False)
    fig.suptitle("Sector composition of the MARS snapshot", x=0.08, ha="left",
                 fontsize=14, fontweight="bold", color=INK)
    fig.tight_layout()
    save(fig, "fig04_sector_mix.png")
    pc.to_csv(TABLE / "plume_sector_summary.csv", index=False)
    sc.to_csv(TABLE / "source_sector_summary.csv", index=False)
    return pc, sc


def fig_timeline(plumes: gpd.GeoDataFrame) -> pd.DataFrame:
    dt = pd.to_datetime(plumes["tile_date"], errors="coerce", utc=True)
    years = dt.dt.year.value_counts().sort_index().rename_axis("year").reset_index(name="count")
    fig, ax = plt.subplots(figsize=(10.5, 4.8))
    bars = ax.bar(years["year"].astype(str), years["count"], color=AGRO_DARK)
    ax.set_title("Plume records by observation year", loc="left", fontweight="bold")
    ax.set_ylabel("Records")
    ax.grid(axis="y", color=GRID, linewidth=0.4, alpha=0.5)
    ax.spines[["top", "right"]].set_visible(False)
    for bar in bars:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(years["count"])*0.018,
                f"{int(bar.get_height()):,}", ha="center", va="bottom", fontsize=8)
    ax.text(0.99, 0.86, "2026 is partial through 5 Sep 2026",
            transform=ax.transAxes, ha="right", va="top", fontsize=8, color=MUTED)
    save(fig, "fig05_detection_timeline.png")
    years.to_csv(TABLE / "annual_detection_summary.csv", index=False)
    return years


def fig_flux(plumes: gpd.GeoDataFrame) -> dict:
    flux = pd.to_numeric(plumes["ch4_fluxrate"], errors="coerce")
    valid = flux[flux.gt(0)].dropna()
    logv = np.log10(valid)
    q = valid.quantile([0.25, 0.5, 0.75, 0.95]).to_dict()

    fig, ax = plt.subplots(figsize=(10.5, 5.0))
    ax.hist(logv, bins=55, color=AGRO_DARK, alpha=0.9)
    ax.axvline(math.log10(q[0.5]), color=ORANGE, linewidth=1.8, label=f"Median = {q[0.5]:,.0f} kg/h")
    ax.set_title("Distribution of published methane flux-rate estimates", loc="left", fontweight="bold")
    ax.set_xlabel("log10(CH4 flux rate, kg/h)")
    ax.set_ylabel("Plume records")
    ax.grid(axis="y", color=GRID, linewidth=0.4, alpha=0.5)
    ax.legend(frameon=False, loc="upper left")
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, "fig06_flux_distribution.png")
    return {
        "non_null_positive": int(len(valid)),
        "q25": float(q[0.25]),
        "median": float(q[0.5]),
        "q75": float(q[0.75]),
        "q95": float(q[0.95]),
    }


def fig_qaqc() -> pd.DataFrame:
    qa = pd.read_csv(OUTPUTS / "qa_summary.csv")
    status = qa[qa["category"].eq("status")].copy()
    flags = qa[qa["category"].eq("flag")].copy()
    flags["label"] = flags["metric"].str.replace("_", " ", regex=False)
    plot_flags = flags.sort_values("count")

    fig, axes = plt.subplots(1, 2, figsize=(12, 5.2), gridspec_kw={"width_ratios": [0.9, 1.6]})
    colors_status = [AGRO_DARK, WARN, "#D9480F"]
    axes[0].bar(status["metric"], status["count"], color=colors_status)
    axes[0].set_title("Record status", loc="left", fontweight="bold")
    axes[0].set_ylabel("Records")
    axes[0].grid(axis="y", color=GRID, linewidth=0.4, alpha=0.5)
    for x, y in zip(status["metric"], status["count"]):
        axes[0].text(x, y + 350, f"{int(y):,}", ha="center", fontsize=8)

    axes[1].barh(plot_flags["label"], plot_flags["count"], color=AGRO)
    axes[1].set_title("Triggered QA flags", loc="left", fontweight="bold")
    axes[1].set_xlabel("Records flagged")
    axes[1].grid(axis="x", color=GRID, linewidth=0.4, alpha=0.5)
    for ax in axes:
        ax.spines[["top", "right"]].set_visible(False)
    fig.suptitle("Reproducible QA/QC outcome", x=0.08, ha="left",
                 fontsize=14, fontweight="bold", color=INK)
    fig.tight_layout()
    save(fig, "fig07_qaqc_overview.png")
    qa.to_csv(TABLE / "qa_summary.csv", index=False)
    return qa


def fig_storage_model() -> None:
    fig, ax = plt.subplots(figsize=(12.3, 4.7))
    ax.set_xlim(0, 12.3)
    ax.set_ylim(0, 4.7)
    ax.axis("off")

    groups = [
        (0.4, 1.0, 2.2, 2.6, "Raw UNEP export",
         ["GeoJSON plume polygon", "published lat/lon", "sensor + time", "flux + uncertainty"], BLUE),
        (3.4, 1.0, 2.4, 2.6, "Normalized record",
         ["id_plume (PK)", "observed_at UTC", "Point EPSG:4326", "QA flags + status"], AGRO),
        (6.8, 1.0, 2.2, 2.6, "Local artifact",
         ["GeoPackage", "portable", "30,116 records", "no service required"], AGRO_DARK),
        (9.8, 1.0, 2.0, 2.6, "Operational path",
         ["PostGIS", "GIST index", "time index", "idempotent UPSERT"], ORANGE),
    ]
    for x, y, w, h, title, items, color in groups:
        box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.04,rounding_size=0.08",
                             linewidth=1.4, edgecolor=color, facecolor="white")
        ax.add_patch(box)
        ax.text(x + 0.15, y + h - 0.42, title, fontsize=10.2, fontweight="bold", color=color)
        for i, item in enumerate(items):
            ax.text(x + 0.18, y + h - 0.88 - i*0.42, f"• {item}", fontsize=8.2, color=INK)
    for a, b in [(2.6, 3.3), (5.8, 6.7), (9.0, 9.7)]:
        ax.add_patch(FancyArrowPatch((a, 2.3), (b, 2.3), arrowstyle="-|>",
                                     mutation_scale=14, color=MUTED, linewidth=1.4))
    ax.text(0.4, 4.15, "Data model and persistence path", fontsize=15, fontweight="bold")
    ax.text(0.4, 0.45, "The local GeoPackage is executed by default; PostGIS remains an explicit, production-oriented loading path.",
            fontsize=8.5, color=MUTED)
    save(fig, "fig08_storage_model.png")


def build_metrics(plumes: gpd.GeoDataFrame, sources: gpd.GeoDataFrame, flux_stats: dict) -> dict:
    observed = pd.to_datetime(plumes["tile_date"], errors="coerce", utc=True)
    metrics = {
        "snapshot_date": "2026-10-06",
        "plume_records": int(len(plumes)),
        "source_records": int(len(sources)),
        "countries": int(plumes["country"].nunique(dropna=True)),
        "satellites": int(plumes["satellite"].nunique(dropna=True)),
        "observation_start": observed.min().isoformat(),
        "observation_end": observed.max().isoformat(),
        "actionable_counts": {str(k): int(v) for k, v in plumes["actionable"].fillna("Missing").value_counts().items()},
        "notified_counts": {str(k): int(v) for k, v in plumes["notified"].fillna("Missing").value_counts().items()},
        "flux": flux_stats,
    }
    (TABLE / "publication_metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    pd.DataFrame([{
        "plume_records": metrics["plume_records"],
        "source_records": metrics["source_records"],
        "countries": metrics["countries"],
        "satellites": metrics["satellites"],
        "observation_start": metrics["observation_start"],
        "observation_end": metrics["observation_end"],
        "flux_median_kg_h": flux_stats["median"],
    }]).to_csv(TABLE / "dataset_summary.csv", index=False)
    return metrics


def main() -> None:
    ensure_dirs()
    if not PLUMES.exists() or not SOURCES.exists():
        raise FileNotFoundError("Run python src/download_data.py first")

    plumes = gpd.read_file(PLUMES)
    sources = gpd.read_file(SOURCES)
    world = ensure_world()

    fig_pipeline()
    fig_global_map(plumes, world)
    fig_satellites(plumes)
    fig_sectors(plumes, sources)
    fig_timeline(plumes)
    flux_stats = fig_flux(plumes)
    fig_qaqc()
    fig_storage_model()
    metrics = build_metrics(plumes, sources, flux_stats)

    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
