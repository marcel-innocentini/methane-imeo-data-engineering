CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS methane_plumes_demo (
    id_plume text PRIMARY KEY,
    source_name text,
    satellite text,
    observed_at timestamptz,
    lat double precision,
    lon double precision,
    ch4_fluxrate double precision,
    ch4_fluxrate_std double precision,
    sector text,
    country text,
    actionable text,
    notified boolean,
    qa_status text NOT NULL,
    qa_flag_count integer NOT NULL,
    source_dataset text NOT NULL DEFAULT 'UNEP IMEO MARS',
    geom geometry(Point, 4326)
);

CREATE INDEX IF NOT EXISTS methane_plumes_demo_geom_gix
    ON methane_plumes_demo USING GIST (geom);

CREATE INDEX IF NOT EXISTS methane_plumes_demo_observed_at_idx
    ON methane_plumes_demo (observed_at);

CREATE INDEX IF NOT EXISTS methane_plumes_demo_satellite_idx
    ON methane_plumes_demo (satellite);
