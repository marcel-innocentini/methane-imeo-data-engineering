from __future__ import annotations

import argparse
import os
from pathlib import Path

import geopandas as gpd
import psycopg

ROOT = Path(__file__).resolve().parents[1]
GPKG = ROOT / "data" / "processed" / "mars_plumes_qc.gpkg"
SCHEMA = ROOT / "sql" / "postgis_schema.sql"

UPSERT = """
INSERT INTO methane_plumes_demo (
    id_plume, source_name, satellite, observed_at, lat, lon,
    ch4_fluxrate, ch4_fluxrate_std, sector, country, actionable,
    notified, qa_status, qa_flag_count, geom
)
VALUES (
    %s, %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s,
    %s, %s, %s,
    CASE WHEN %s IS NULL OR %s IS NULL THEN NULL
         ELSE ST_SetSRID(ST_MakePoint(%s, %s), 4326) END
)
ON CONFLICT (id_plume) DO UPDATE SET
    source_name = EXCLUDED.source_name,
    satellite = EXCLUDED.satellite,
    observed_at = EXCLUDED.observed_at,
    lat = EXCLUDED.lat,
    lon = EXCLUDED.lon,
    ch4_fluxrate = EXCLUDED.ch4_fluxrate,
    ch4_fluxrate_std = EXCLUDED.ch4_fluxrate_std,
    sector = EXCLUDED.sector,
    country = EXCLUDED.country,
    actionable = EXCLUDED.actionable,
    notified = EXCLUDED.notified,
    qa_status = EXCLUDED.qa_status,
    qa_flag_count = EXCLUDED.qa_flag_count,
    geom = EXCLUDED.geom;
"""


def clean(value):
    try:
        if value != value:
            return None
    except Exception:
        pass
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--database-url",
        default=os.getenv("DATABASE_URL"),
        help="Example: postgresql://postgres:postgres@localhost:5432/methane",
    )
    args = parser.parse_args()
    if not args.database_url:
        raise SystemExit("Set DATABASE_URL or pass --database-url")

    gdf = gpd.read_file(GPKG, layer="plumes_qc")
    rows = []
    for row in gdf.itertuples(index=False):
        lon = clean(row.lon)
        lat = clean(row.lat)
        rows.append(
            (
                clean(row.id_plume), clean(row.source_name), clean(row.satellite),
                clean(row.observed_at_utc), lat, lon,
                clean(row.ch4_fluxrate), clean(row.ch4_fluxrate_std),
                clean(row.sector), clean(row.country), clean(row.actionable),
                clean(row.notified), clean(row.qa_status), int(row.flag_count),
                lon, lat, lon, lat,
            )
        )

    with psycopg.connect(args.database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(SCHEMA.read_text(encoding="utf-8"))
            cur.executemany(UPSERT, rows)
        conn.commit()
    print(f"Loaded/upserted {len(rows):,} records into methane_plumes_demo")


if __name__ == "__main__":
    main()
