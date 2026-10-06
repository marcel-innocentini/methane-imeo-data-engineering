from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOI_FILE = ROOT / "metadata" / "doi.txt"
CITATION = ROOT / "CITATION.cff"
README = ROOT / "README.md"
RELEASE = ROOT / "RELEASE_NOTES_v1.0.0.md"
REPORT_MD = ROOT / "docs" / "report" / "METHANE_IMEO_MARS_QAQC_REPORT.md"

DOI_RE = re.compile(r"^10\.\d{4,9}/zenodo\.\d+$", re.IGNORECASE)


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"Expected placeholder not found in {path}: {old!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def update_citation(doi: str) -> None:
    text = CITATION.read_text(encoding="utf-8")
    placeholder = '  # doi: "TO_BE_ADDED_AFTER_ZENODO_DOI_RESERVATION"'
    current = re.search(r'^  doi: "10\.\d{4,9}/zenodo\.\d+"$', text, flags=re.MULTILINE)
    if current:
        text = text[:current.start()] + f'  doi: "{doi}"' + text[current.end():]
    elif placeholder in text:
        text = text.replace(placeholder, f'  doi: "{doi}"', 1)
    else:
        raise RuntimeError("DOI placeholder not found in CITATION.cff")
    CITATION.write_text(text, encoding="utf-8")


def update_readme(doi: str) -> None:
    text = README.read_text(encoding="utf-8")
    badge = f"[![DOI](https://zenodo.org/badge/DOI/{doi}.svg)](https://doi.org/{doi})"
    if "<!-- ZENODO_DOI_BADGE -->" in text:
        text = text.replace("<!-- ZENODO_DOI_BADGE -->", badge, 1)
    else:
        text = re.sub(
            r"\[!\[DOI\]\(https://zenodo\.org/badge/DOI/10\.\d{4,9}/zenodo\.\d+\.svg\)\]\(https://doi\.org/10\.\d{4,9}/zenodo\.\d+\)",
            badge,
            text,
            count=1,
        )
    old = "Its DOI will be added after the Zenodo draft DOI is reserved."
    new = f"Zenodo report DOI: https://doi.org/{doi}"
    if old in text:
        text = text.replace(old, new, 1)
    else:
        text = re.sub(r"Zenodo report DOI: https://doi\.org/10\.\d{4,9}/zenodo\.\d+", new, text, count=1)
    README.write_text(text, encoding="utf-8")


def update_release(doi: str) -> None:
    text = RELEASE.read_text(encoding="utf-8")
    text = re.sub(
        r"Zenodo DOI: (?:TO_BE_ADDED_AFTER_RESERVATION|10\.\d{4,9}/zenodo\.\d+)",
        f"Zenodo DOI: {doi}",
        text,
        count=1,
    )
    RELEASE.write_text(text, encoding="utf-8")


def update_report_markdown(doi: str) -> None:
    text = REPORT_MD.read_text(encoding="utf-8")
    old_heading = "**Suggested citation before DOI assignment**"
    if old_heading in text:
        text = text.replace(old_heading, "**Suggested citation**", 1)
    citation_old = "Innocentini, M. de M. (2026). *A Reproducible QA/QC Pipeline for Public Satellite Methane Plume Data from UNEP IMEO MARS* (Version 1.0.0). Agropixel. Technical report."
    citation_new = f"Innocentini, M. de M. (2026). *A Reproducible QA/QC Pipeline for Public Satellite Methane Plume Data from UNEP IMEO MARS* (Version 1.0.0). Zenodo. https://doi.org/{doi}"
    if citation_old in text:
        text = text.replace(citation_old, citation_new, 1)
    elif "Zenodo. https://doi.org/" in text:
        text = re.sub(
            r"Innocentini, M\. de M\. \(2026\)\. \*A Reproducible QA/QC Pipeline for Public Satellite Methane Plume Data from UNEP IMEO MARS\* \(Version 1\.0\.0\)\. Zenodo\. https://doi\.org/10\.\d{4,9}/zenodo\.\d+",
            citation_new,
            text,
            count=1,
        )
    REPORT_MD.write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Insert a reserved Zenodo DOI into all publication metadata.")
    parser.add_argument("doi", help="Example: 10.5281/zenodo.12345678")
    args = parser.parse_args()

    doi = args.doi.strip()
    if not DOI_RE.match(doi):
        raise SystemExit("Expected a Zenodo DOI such as 10.5281/zenodo.12345678")

    DOI_FILE.write_text(doi + "\n", encoding="utf-8")
    update_citation(doi)
    update_readme(doi)
    update_release(doi)
    update_report_markdown(doi)

    print(f"DOI inserted: {doi}")
    print("Next: python src/build_publication_report.py")


if __name__ == "__main__":
    main()
