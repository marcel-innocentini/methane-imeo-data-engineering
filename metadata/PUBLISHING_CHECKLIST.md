# Publication checklist

## Planned identifiers

- GitHub repository: `marcel-innocentini/methane-imeo-data-engineering`
- GitHub release: `v1.0.0`
- Zenodo object: **Publication -> Report**
- Zenodo report/derived-assets license: **CC BY-NC-SA 4.0**
- Source-code license: **MIT**

## A. Final local QA

- [x] Source archive provenance recorded.
- [x] Automated tests pass (2/2).
- [x] Core pipeline executed successfully.
- [x] GeoPackage read back successfully.
- [x] Publication figures generated.
- [x] 13-page report generated.
- [x] PDF rendered page-by-page and visually inspected.
- [x] Public README removes job-application framing.
- [x] Split licensing and UNEP attribution prepared.
- [ ] Reserve Zenodo DOI and insert it in the final PDF/CITATION/README.
- [ ] Re-run final report build after DOI insertion.
- [ ] Final `git status` review before first public push.

## B. GitHub publication

1. Create a **public** repository named:
   `methane-imeo-data-engineering`

2. Description:
   `Reproducible Python/GeoPandas QA/QC pipeline for public UNEP IMEO MARS satellite methane plume data, with GeoPackage/PostGIS outputs and an illustrated technical report.`

3. Suggested topics:
   `methane`, `remote-sensing`, `earth-observation`, `unep`, `imeo`, `mars`, `geopandas`, `postgis`, `qaqc`, `reproducible-research`, `environmental-data`

4. Push the prepared local repository to `main`.

5. Confirm that no raw UNEP archive, full raw GeoJSON, full GeoPackage, private application material, or render-QA folder is present on GitHub.

6. After the Zenodo report DOI is reserved, update:
   - `CITATION.cff` preferred-citation DOI;
   - README DOI badge/citation;
   - report citation page;
   - release notes.

7. Commit the DOI update.

8. Create tag and GitHub Release:
   `v1.0.0`

9. Use `RELEASE_NOTES_v1.0.0.md` as release notes.

## C. Zenodo report publication

Recommended sequence so the DOI is printed inside the PDF:

1. In Zenodo, create a **New upload**.
2. Resource type: **Publication -> Report**.
3. Enter metadata from `metadata/zenodo_report_metadata.json`.
4. Set file visibility to **Public**.
5. License: **CC BY-NC-SA 4.0**.
6. Click **Get a DOI now!** to reserve a DOI before publication.
7. Do **not** publish yet.
8. Run:
   `python src/prepare_release_doi.py <reserved-doi>`
9. Rebuild:
   `python src/build_publication_report.py`
10. Render/verify the final PDF again.
11. Upload only the final illustrated report PDF to the Zenodo report record.
12. Add the GitHub repository URL as related software.
13. Preview the Zenodo record.
14. Publish only after the GitHub repository is public and the final PDF matches the reserved DOI.

## D. After publication

- [ ] Confirm the Zenodo DOI badge in README.
- [ ] Confirm GitHub "Cite this repository" renders correctly from CITATION.cff.
- [ ] Confirm Zenodo creator, ORCID, affiliation, title, version, license, and GitHub relation.
- [ ] Confirm the PDF shown on Zenodo is exactly the final PDF in GitHub.
- [ ] Record DOI and GitHub URL for later application documentation.
