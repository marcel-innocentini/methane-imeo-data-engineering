# METHANE - UNEP IMEO MARS Data Engineering

A reproducible Python/GeoPandas QA/QC pipeline for public satellite methane plume data from the **UNEP International Methane Emissions Observatory (IMEO) Methane Alert and Response System (MARS)**.

> **Independent technical demonstration.** This repository uses already processed public MARS detections. It does not implement atmospheric methane retrieval, radiative transfer, plume-detection models, or an alternative to MARS.

## Technical report

**A Reproducible QA/QC Pipeline for Public Satellite Methane Plume Data from UNEP IMEO MARS**  
Marcel de Mello Innocentini - Agropixel - ORCID 0009-0006-2409-0946

[Read the illustrated technical report](docs/report/METHANE_IMEO_MARS_QAQC_REPORT_v1.0.0.pdf)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23196446.svg)](https://doi.org/10.5281/zenodo.23196446)

![Pipeline architecture](docs/figures/fig01_pipeline_architecture.png)

## Snapshot used in version 1.0.0

The reproducible example was validated against the official Eye on Methane GeoJSON archive downloaded on **6 October 2026**.

| Metric | Value |
|---|---:|
| Plume observations | 30,116 |
| Detected sources | 4,186 |
| Countries | 99 |
| Satellite/instrument labels | 10 |
| Observation period | 2020-10-29 to 2026-09-05 |
| QA PASS | 27,871 (92.545%) |
| QA WARN | 2,245 (7.455%) |
| QA FAIL | 0 |
| Source archive SHA-256 | `3755cc5206f6c60c770fe589d527a98f73779e16fe752f40dda6e120935ed03e` |

![Global MARS plume snapshot](docs/figures/fig02_global_plumes_map.png)

## Workflow

```text
Official UNEP MARS GeoJSON
          |
          v
download + provenance hash
          |
          v
schema normalization
          |
          v
deterministic record-level QA/QC
          |
          +--> GeoPackage (executed local artifact)
          |
          +--> PostgreSQL/PostGIS loading path
          |
          +--> CSV / JSON machine summaries
          |
          +--> publication figures + report
```

The project intentionally starts from **published MARS products**. Scientific methane detection and quantification remain upstream of this demonstration.

## QA/QC checks

Critical checks include missing/duplicate plume IDs, invalid timestamps, missing or out-of-range coordinates, and negative methane flux values. Warning-level checks include missing methane flux values and missing/invalid original plume geometry.

Each record receives `PASS`, `WARN`, or `FAIL` plus machine-readable flags.

![QA/QC overview](docs/figures/fig07_qaqc_overview.png)

## Reproduce locally

Python 3.11+ recommended.

```powershell
git clone https://github.com/marcel-innocentini/methane-imeo-data-engineering.git
cd methane-imeo-data-engineering

python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

python src\download_data.py
python -m pytest -q
python src\run_pipeline.py
python src\publication_assets.py
python src\build_publication_report.py
```

On Windows, the complete sequence is also available as:

```powershell
.\run_publication.ps1
```

## PostgreSQL/PostGIS

The local executed artifact is a GeoPackage so the demo can run without a database service. An operational loading path is included in `sql/postgis_schema.sql` and `src/load_postgis.py`.

The schema uses `geometry(Point,4326)`, a primary key on `id_plume`, GIST spatial indexing, timestamp/satellite indexes, and idempotent UPSERT behavior.

## Repository structure

```text
METHANE/
|-- docs/
|   |-- figures/
|   |-- report/
|   |-- tables/
|-- metadata/
|-- data/
|   |-- processed/
|   |-- raw/
|-- outputs/
|-- sql/
|-- src/
|-- tests/
|-- CITATION.cff
|-- CHANGELOG.md
|-- LICENSE.md
|-- NOTICE.md
|-- RELEASE_NOTES_v1.0.0.md
|-- Dockerfile
|-- requirements.txt
|-- run_publication.ps1
|-- README.md
```

## Official upstream sources

- UNEP IMEO: https://www.unep.org/topics/energy/methane/international-methane-emissions-observatory
- UNEP MARS: https://www.unep.org/topics/energy/methane/methane-alert-and-response-system-mars
- Eye on Methane data: https://methanedata.unep.org/download-dataset
- MARS plume/source data dictionary: https://methanedata.unep.org/dict-mars-plumes
- UNEP IMEO satellite methodology: https://wedocs.unep.org/handle/20.500.11822/46241
- TROPOMI methane product: https://www.tropomi.eu/data-products/methane
- CAMS Methane Hotspot Explorer: https://apps.atmosphere.copernicus.eu/methane-explorer/

## Licensing

This repository is intentionally **multi-licensed**.

| Material | License |
|---|---|
| Independently authored source code in `src/`, `tests/`, `sql/`, and build/configuration scripts | MIT |
| Technical report, derived figures/tables, and derived sample data | CC BY-NC-SA 4.0 |
| Original UNEP IMEO MARS data | CC BY-NC-SA 4.0, under UNEP terms |
| Natural Earth map boundaries | Public domain |

See [LICENSE.md](LICENSE.md) and [NOTICE.md](NOTICE.md).

### Required attribution for derived MARS material

> Contains data derived from UNEP International Methane Emissions Observatory (IMEO), Eye on Methane / Methane Alert and Response System (MARS), downloaded 6 October 2026. Data were normalized, quality-flagged, aggregated and visualized for this independent technical demonstration. Original MARS data are licensed CC BY-NC-SA 4.0. This work is not produced by or endorsed by UNEP or IMEO.

## Citation

GitHub citation metadata are provided in [CITATION.cff](CITATION.cff). The preferred citation is the illustrated Zenodo technical report. Zenodo report DOI: https://doi.org/10.5281/zenodo.23196446

## Publication status

**Prepared for publication; not yet published.**

Intended repository:

`https://github.com/marcel-innocentini/methane-imeo-data-engineering`

See [metadata/PUBLISHING_CHECKLIST.md](metadata/PUBLISHING_CHECKLIST.md) for the final release sequence.
