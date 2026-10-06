# Release notes - v1.0.0

## METHANE - public UNEP IMEO MARS data-engineering demonstration

This first public release provides a compact, reproducible downstream QA/QC pipeline for public satellite methane plume data from UNEP IMEO's Methane Alert and Response System (MARS).

### Highlights

- official MARS GeoJSON download with provenance and SHA-256 capture;
- 30,116 plume observations and 4,186 detected sources in the validated 2026-10-06 snapshot;
- deterministic schema, ID, date, coordinate, flux and geometry checks;
- 27,871 PASS, 2,245 WARN and 0 FAIL records under the defined structural rules;
- portable GeoPackage output and PostgreSQL/PostGIS loading path;
- automated tests and Docker packaging;
- machine-readable CSV/JSON summaries;
- publication-quality analytical figures;
- 13-page illustrated technical report.

### Scientific scope

The project intentionally starts from already processed MARS detections. It does not implement atmospheric methane retrieval, radiative transfer, plume-detection models, or an alternative quantification method.

### Main publication

**A Reproducible QA/QC Pipeline for Public Satellite Methane Plume Data from UNEP IMEO MARS**  
Marcel de Mello Innocentini, Agropixel, 2026.

Zenodo DOI: 10.5281/zenodo.23196446

### Licensing

- source code: MIT;
- technical report, derived figures/tables, and sample data: CC BY-NC-SA 4.0;
- original UNEP IMEO MARS data: CC BY-NC-SA 4.0 under UNEP terms.
