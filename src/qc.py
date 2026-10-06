from __future__ import annotations

import pandas as pd
import geopandas as gpd

NUMERIC_COLUMNS = [
    "lat", "lon", "ch4_fluxrate", "ch4_fluxrate_std",
    "wind_u", "wind_v", "wind_speed", "total_emission", "total_emission_std",
]

CRITICAL_FLAGS = [
    "missing_id",
    "duplicate_id",
    "invalid_date",
    "missing_coordinates",
    "latitude_out_of_range",
    "longitude_out_of_range",
    "negative_flux",
]

ALL_FLAGS = CRITICAL_FLAGS + [
    "missing_flux",
    "missing_original_geometry",
    "invalid_original_geometry",
]


def normalize(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    out = gdf.copy()
    for col in NUMERIC_COLUMNS:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")
    for col in ["id_plume", "source_name", "satellite", "country", "sector"]:
        if col in out.columns:
            out[col] = out[col].astype("string").str.strip()
    out["observed_at"] = pd.to_datetime(out.get("tile_date"), errors="coerce", utc=True)
    return out


def build_qc_flags(gdf: gpd.GeoDataFrame) -> pd.DataFrame:
    flags = pd.DataFrame(index=gdf.index)
    flags["missing_id"] = gdf["id_plume"].isna() | gdf["id_plume"].eq("")
    flags["duplicate_id"] = gdf["id_plume"].duplicated(keep=False) & ~flags["missing_id"]
    flags["invalid_date"] = gdf["observed_at"].isna()
    flags["missing_coordinates"] = gdf["lat"].isna() | gdf["lon"].isna()
    flags["latitude_out_of_range"] = gdf["lat"].notna() & ~gdf["lat"].between(-90, 90)
    flags["longitude_out_of_range"] = gdf["lon"].notna() & ~gdf["lon"].between(-180, 180)
    flags["missing_flux"] = gdf["ch4_fluxrate"].isna()
    flags["negative_flux"] = gdf["ch4_fluxrate"].notna() & (gdf["ch4_fluxrate"] < 0)

    geom = gdf.geometry
    flags["missing_original_geometry"] = geom.isna() | geom.is_empty
    flags["invalid_original_geometry"] = (~flags["missing_original_geometry"]) & (~geom.is_valid)

    flags["critical_flag_count"] = flags[CRITICAL_FLAGS].sum(axis=1)
    flags["flag_count"] = flags[ALL_FLAGS].sum(axis=1)
    flags["qa_status"] = "PASS"
    flags.loc[(flags["critical_flag_count"] == 0) & (flags["flag_count"] > 0), "qa_status"] = "WARN"
    flags.loc[flags["critical_flag_count"] > 0, "qa_status"] = "FAIL"
    return flags
