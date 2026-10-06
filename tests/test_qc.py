from pathlib import Path
import sys

import geopandas as gpd
from shapely.geometry import Point

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from qc import normalize, build_qc_flags


def sample_gdf():
    return gpd.GeoDataFrame(
        {
            "id_plume": ["a", "a", "c"],
            "tile_date": ["2026-01-01T00:00:00", "bad", "2026-01-03T00:00:00"],
            "lat": [10.0, 95.0, 5.0],
            "lon": [20.0, 20.0, 30.0],
            "ch4_fluxrate": [100.0, -1.0, None],
        },
        geometry=[Point(20, 10), Point(20, 95), None],
        crs="EPSG:4326",
    )


def test_duplicate_and_invalid_flags():
    gdf = normalize(sample_gdf())
    flags = build_qc_flags(gdf)
    assert flags["duplicate_id"].tolist() == [True, True, False]
    assert bool(flags.loc[1, "invalid_date"])
    assert bool(flags.loc[1, "latitude_out_of_range"])
    assert bool(flags.loc[1, "negative_flux"])


def test_warning_for_noncritical_missing_values():
    gdf = normalize(sample_gdf())
    flags = build_qc_flags(gdf)
    assert flags.loc[2, "qa_status"] == "WARN"
    assert bool(flags.loc[2, "missing_flux"])
    assert bool(flags.loc[2, "missing_original_geometry"])
