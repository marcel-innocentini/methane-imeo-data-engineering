from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image, KeepTogether, PageBreak, Paragraph, Preformatted, SimpleDocTemplate,
    Spacer, Table, TableStyle
)

ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "docs" / "report"
FIG_DIR = ROOT / "docs" / "figures"
DOI_FILE = ROOT / "metadata" / "doi.txt"
OUT = REPORT_DIR / "METHANE_IMEO_MARS_QAQC_REPORT_v1.0.0.pdf"

DOI = None
if DOI_FILE.exists():
    candidate = DOI_FILE.read_text(encoding="utf-8").strip()
    if candidate and candidate.upper() != "PENDING":
        DOI = candidate

FONT_DIR = Path.home() / "AppData/Local/Microsoft/Windows/Fonts"
REG = FONT_DIR / "Montserrat-Regular.ttf"
BOLD = FONT_DIR / "Montserrat-Bold.ttf"
if REG.exists() and BOLD.exists():
    pdfmetrics.registerFont(TTFont("Montserrat", str(REG)))
    pdfmetrics.registerFont(TTFont("Montserrat-Bold", str(BOLD)))
    FONT = "Montserrat"
    FONT_BOLD = "Montserrat-Bold"
else:
    FONT = "Helvetica"
    FONT_BOLD = "Helvetica-Bold"

AGRO = colors.HexColor("#83C327")
AGRO_DARK = colors.HexColor("#12633E")
INK = colors.HexColor("#182315")
SURFACE = colors.HexColor("#F4F7F1")
GRID = colors.HexColor("#C4D3BB")
ORANGE = colors.HexColor("#E86A17")
BLUE = colors.HexColor("#1677B8")
MUTED = colors.HexColor("#718176")
WARN = colors.HexColor("#B7791F")

PAGE_W, PAGE_H = A4
LEFT = 18 * mm
RIGHT = 18 * mm
TOP = 16 * mm
BOTTOM = 16 * mm
CONTENT_W = PAGE_W - LEFT - RIGHT

styles = getSampleStyleSheet()

title = ParagraphStyle(
    "Title", parent=styles["Title"], fontName=FONT_BOLD,
    fontSize=22, leading=25, textColor=INK, alignment=TA_LEFT,
    spaceAfter=8,
)
subtitle = ParagraphStyle(
    "Subtitle", parent=styles["BodyText"], fontName=FONT,
    fontSize=10.5, leading=14, textColor=MUTED, spaceAfter=7,
)
h1 = ParagraphStyle(
    "H1", parent=styles["Heading1"], fontName=FONT_BOLD,
    fontSize=15.5, leading=18, textColor=AGRO_DARK,
    spaceBefore=5, spaceAfter=6,
)
h2 = ParagraphStyle(
    "H2", parent=styles["Heading2"], fontName=FONT_BOLD,
    fontSize=11.5, leading=14, textColor=AGRO_DARK,
    spaceBefore=6, spaceAfter=3,
)
body = ParagraphStyle(
    "Body", parent=styles["BodyText"], fontName=FONT,
    fontSize=9.2, leading=13.2, textColor=INK,
    spaceAfter=6, alignment=TA_LEFT,
)
body_small = ParagraphStyle(
    "BodySmall", parent=body, fontSize=8.1, leading=10.8, spaceAfter=4,
)
caption = ParagraphStyle(
    "Caption", parent=body_small, fontSize=7.7, leading=9.5,
    textColor=MUTED, alignment=TA_CENTER, spaceBefore=2, spaceAfter=5,
)
metric_big = ParagraphStyle(
    "MetricBig", parent=body, fontName=FONT_BOLD, fontSize=17,
    leading=19, textColor=AGRO_DARK, alignment=TA_CENTER, spaceAfter=1,
)
metric_label = ParagraphStyle(
    "MetricLabel", parent=body_small, fontSize=7.3, leading=9,
    textColor=MUTED, alignment=TA_CENTER, spaceAfter=0,
)
table_body = ParagraphStyle(
    "TableBody", parent=body_small, fontSize=7.3, leading=9.2, spaceAfter=0,
)
table_head = ParagraphStyle(
    "TableHead", parent=table_body, fontName=FONT_BOLD, textColor=AGRO_DARK,
)
code = ParagraphStyle(
    "Code", parent=body_small, fontName="Courier", fontSize=7.4,
    leading=9.2, textColor=INK, leftIndent=5, rightIndent=5,
)


def P(text: str, style=body) -> Paragraph:
    return Paragraph(text, style)


def img(name: str, width: float = CONTENT_W) -> Image:
    p = FIG_DIR / name
    im = Image(str(p))
    ratio = im.imageHeight / im.imageWidth
    im.drawWidth = width
    im.drawHeight = width * ratio
    return im


def data_table(rows, widths, font_size=7.2, header=True):
    t = Table(rows, colWidths=widths, hAlign="LEFT", repeatRows=1 if header else 0)
    style = [
        ("GRID", (0, 0), (-1, -1), 0.35, GRID),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ("FONTNAME", (0, 0), (-1, -1), FONT),
        ("FONTSIZE", (0, 0), (-1, -1), font_size),
        ("TEXTCOLOR", (0, 0), (-1, -1), INK),
    ]
    if header:
        style += [
            ("BACKGROUND", (0, 0), (-1, 0), SURFACE),
            ("FONTNAME", (0, 0), (-1, 0), FONT_BOLD),
            ("TEXTCOLOR", (0, 0), (-1, 0), AGRO_DARK),
        ]
    t.setStyle(TableStyle(style))
    return t


def callout(text: str, color=AGRO_DARK, bg=SURFACE):
    t = Table([[P(text, body_small)]], colWidths=[CONTENT_W])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("BOX", (0, 0), (-1, -1), 0.7, color),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def header_footer(canvas, doc):
    canvas.saveState()
    page = doc.page
    if page > 1:
        canvas.setStrokeColor(GRID)
        canvas.setLineWidth(0.5)
        canvas.line(LEFT, PAGE_H - 11 * mm, PAGE_W - RIGHT, PAGE_H - 11 * mm)
        canvas.setFont(FONT, 6.8)
        canvas.setFillColor(MUTED)
        canvas.drawString(LEFT, PAGE_H - 8.7 * mm, "METHANE - UNEP IMEO MARS QA/QC data engineering")
        canvas.drawRightString(PAGE_W - RIGHT, PAGE_H - 8.7 * mm, "Technical Report v1.0.0")
    canvas.setFont(FONT, 6.8)
    canvas.setFillColor(MUTED)
    canvas.drawString(LEFT, 8.5 * mm, "Marcel de Mello Innocentini | Agropixel | ORCID 0009-0006-2409-0946")
    canvas.drawRightString(PAGE_W - RIGHT, 8.5 * mm, f"Page {page}")
    canvas.restoreState()


story = []

# Cover
story.append(Spacer(1, 13 * mm))
story.append(P("A Reproducible QA/QC Pipeline for Public Satellite Methane Plume Data from UNEP IMEO MARS", title))
story.append(P("A compact geospatial data-engineering case study using the Eye on Methane public dataset", subtitle))
story.append(Spacer(1, 3 * mm))
story.append(P("<b>Marcel de Mello Innocentini</b><br/>Agropixel<br/>ORCID: https://orcid.org/0009-0006-2409-0946", body))
story.append(Spacer(1, 2 * mm))
cover_meta = [
    [P("Technical report", table_head), P("Version 1.0.0", table_body)],
    [P("Dataset snapshot", table_head), P("Retrieved 6 October 2026", table_body)],
    [P("Report / derived assets", table_head), P("CC BY-NC-SA 4.0", table_body)],
    [P("Pipeline source code", table_head), P("MIT License", table_body)],
]
if DOI:
    cover_meta.append([P("Zenodo DOI", table_head), P(f"https://doi.org/{DOI}", table_body)])
story.append(data_table(cover_meta, [48 * mm, 82 * mm], font_size=8, header=False))
story.append(Spacer(1, 7 * mm))
story.append(img("fig01_pipeline_architecture.png", width=174 * mm))
story.append(Spacer(1, 3 * mm))
story.append(callout(
    "<b>Independent technical demonstration.</b> This work uses already processed public UNEP IMEO MARS detections. "
    "It does not implement atmospheric methane retrieval, radiative transfer, plume-detection models, or an alternative to MARS."
))
story.append(PageBreak())

# Executive summary
story.append(P("Executive summary", h1))
story.append(P(
    "Reliable methane monitoring requires more than retrieval algorithms. Public satellite-derived products also need "
    "traceable ingestion, schema normalization, data-quality controls, geospatial persistence, and reproducible outputs "
    "before they can support downstream analysis or operational workflows. This report presents a compact pipeline built "
    "around the public Methane Alert and Response System (MARS) plume and source data released by UNEP's International "
    "Methane Emissions Observatory (IMEO) through Eye on Methane."
))
metric_cells = [
    [P("30,116", metric_big), P("4,186", metric_big), P("99", metric_big), P("10", metric_big)],
    [P("plume observations", metric_label), P("detected sources", metric_label), P("countries", metric_label), P("sensor labels", metric_label)],
]
mt = Table(metric_cells, colWidths=[43.5 * mm] * 4)
mt.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, -1), SURFACE),
    ("BOX", (0, 0), (-1, -1), 0.6, GRID),
    ("INNERGRID", (0, 0), (-1, -1), 0.3, GRID),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("TOPPADDING", (0, 0), (-1, 0), 8),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
]))
story += [Spacer(1, 4), mt, Spacer(1, 7)]
story.append(P("What this demonstration proves", h2))
story.append(P(
    "The workflow captures source provenance, ingests GeoJSON, normalizes types, assigns deterministic QA/QC flags, "
    "creates a portable geospatial layer, prepares an indexed PostgreSQL/PostGIS loading path, runs automated tests, and "
    "exports machine-readable summaries and publication figures."
))
story.append(P("What it deliberately does not prove", h2))
story.append(P(
    "The project does not retrieve XCH4 from radiances, estimate methane enhancements, create plume masks, quantify "
    "emissions independently, train machine-learning models, or reproduce UNEP IMEO scientific retrieval methods."
))
story.append(P("Key QA/QC outcome", h2))
qa_rows = [
    [P("Status", table_head), P("Records", table_head), P("Share", table_head), P("Interpretation", table_head)],
    [P("PASS", table_body), P("27,871", table_body), P("92.545%", table_body), P("No defined checks triggered", table_body)],
    [P("WARN", table_body), P("2,245", table_body), P("7.455%", table_body), P("Only non-critical issues", table_body)],
    [P("FAIL", table_body), P("0", table_body), P("0.000%", table_body), P("No critical structural failures", table_body)],
]
story.append(data_table(qa_rows, [27 * mm, 27 * mm, 26 * mm, 94 * mm]))
story.append(Spacer(1, 5))
story.append(callout(
    "A PASS result here is a <b>downstream structural QA result</b>. It is not an independent scientific validation of the methane retrieval."
))
story.append(PageBreak())

# Context + provenance
story.append(P("1. MARS context and data provenance", h1))
story.append(P(
    "UNEP IMEO's Methane Alert and Response System is a public global satellite detection and notification system for "
    "very large methane emissions. UNEP describes MARS as integrating data from more than 30 satellite instruments with "
    "scientific expertise and analytical methods to support mitigation action. This report focuses on the downstream "
    "engineering layer once a validated public product is available."
))
story.append(P("Official public input", h2))
story.append(P(
    "The pipeline uses the Eye on Methane MARS GeoJSON export of detected plumes and sources. The data dictionary defines "
    "a plume as a single methane emission observation from one satellite overpass and a source as a ground location where "
    "one or more plumes have been detected over time."
))
prov_rows = [
    [P("Provenance item", table_head), P("Snapshot value", table_head)],
    [P("Download date", table_body), P("6 October 2026", table_body)],
    [P("Plume records", table_body), P("30,116", table_body)],
    [P("Source records", table_body), P("4,186", table_body)],
    [P("Observation window", table_body), P("2020-10-29 to 2026-09-05 UTC", table_body)],
    [P("Archive bytes", table_body), P("54,940,454", table_body)],
    [P("SHA-256", table_body), P("3755cc5206f6c60c770fe589d527a98f73779e16fe752f40dda6e120935ed03e", table_body)],
]
story.append(data_table(prov_rows, [48 * mm, 126 * mm]))
story.append(Spacer(1, 6))
story.append(P(
    "The official package also includes a data dictionary and the CC BY-NC-SA 4.0 license. The retrieval timestamp, "
    "source URL, archive size, file list and cryptographic hash are stored in <font name='Courier'>data/raw/provenance.json</font>."
))
story.append(callout(
    "<b>Snapshot sensitivity.</b> The MARS data dictionary states that Eye on Methane plumes detected by Sentinel-2, "
    "Landsat-8/9, EMIT, PRISMA and EnMAP were requantified after 20 February 2026. A cryptographic snapshot identifier is "
    "therefore essential for reproducibility.",
    color=BLUE, bg=colors.HexColor("#F2F8FC")
))
story.append(PageBreak())

# Data model
story.append(P("2. Data model and normalization", h1))
story.append(img("fig08_storage_model.png", width=174 * mm))
story.append(P("Figure 1. Data model and persistence path used by the demonstration.", caption))
story.append(P(
    "The raw plume export contains identifiers, satellite/instrument names, timestamps, WGS84 latitude and longitude, "
    "sector attributes, actionability/notification fields, methane flux-rate estimates and uncertainty fields, wind "
    "information, and optional original plume geometries."
))
schema_rows = [
    [P("Normalized field", table_head), P("Purpose", table_head), P("QA behavior", table_head)],
    [P("id_plume", table_body), P("Unique record key", table_body), P("Missing or duplicated -> FAIL", table_body)],
    [P("observed_at_utc", table_body), P("Canonical UTC timestamp", table_body), P("Invalid/missing -> FAIL", table_body)],
    [P("lat / lon", table_body), P("Published WGS84 location", table_body), P("Missing/out of range -> FAIL", table_body)],
    [P("geometry", table_body), P("Point EPSG:4326 from valid lat/lon", table_body), P("Built only from valid coordinates", table_body)],
    [P("ch4_fluxrate", table_body), P("Published kg/h estimate", table_body), P("Missing -> WARN; negative -> FAIL", table_body)],
    [P("has_original_footprint", table_body), P("Preserves upstream geometry availability", table_body), P("Missing footprint -> WARN", table_body)],
    [P("qa_status", table_body), P("PASS / WARN / FAIL", table_body), P("Derived from deterministic flags", table_body)],
]
story.append(data_table(schema_rows, [36 * mm, 68 * mm, 70 * mm]))
story.append(Spacer(1, 5))
story.append(P(
    "The normalized persistent geometry is a point derived from the published latitude/longitude fields. The workflow does "
    "not reconstruct missing plume polygons. Instead, original footprint availability is retained as an explicit QA field."
))
story.append(PageBreak())

# QA
story.append(P("3. Reproducible QA/QC", h1))
story.append(P(
    "The QA/QC layer is deterministic and record-level. Critical checks cover identity, time, coordinate validity and "
    "physically invalid negative flux values. Warning checks cover missing published flux values and missing/invalid "
    "upstream plume geometries."
))
story.append(img("fig07_qaqc_overview.png", width=174 * mm))
story.append(P("Figure 2. Record-level QA status and triggered validation flags.", caption))
flag_rows = [
    [P("Check", table_head), P("Count", table_head), P("Class", table_head)],
    [P("Missing CH4 flux rate", table_body), P("1,038", table_body), P("WARN", table_body)],
    [P("Missing original geometry", table_body), P("1,207", table_body), P("WARN", table_body)],
    [P("Missing/duplicate ID", table_body), P("0", table_body), P("FAIL", table_body)],
    [P("Invalid/missing date", table_body), P("0", table_body), P("FAIL", table_body)],
    [P("Missing/out-of-range coordinates", table_body), P("0", table_body), P("FAIL", table_body)],
    [P("Negative flux rate", table_body), P("0", table_body), P("FAIL", table_body)],
    [P("Invalid original geometry", table_body), P("0", table_body), P("WARN", table_body)],
]
story.append(data_table(flag_rows, [102 * mm, 32 * mm, 40 * mm]))
story.append(Spacer(1, 5))
story.append(P(
    "A missing original footprint is treated as a warning rather than a failure when valid latitude/longitude coordinates "
    "remain available for downstream location-level ingestion."
))
story.append(PageBreak())

# Sensor mix
story.append(P("4. Multi-sensor snapshot composition", h1))
story.append(img("fig03_satellite_mix.png", width=168 * mm))
story.append(P("Figure 3. Distribution of plume observations by satellite/instrument label in the downloaded snapshot.", caption))
story.append(P(
    "EMIT accounts for 31.6% of plume records, followed by Sentinel-5P/TROPOMI (21.7%), Sentinel-2 (20.7%), Landsat "
    "(12.3%), EnMAP (7.6%) and PRISMA (4.0%). The remaining records include VIIRS, Sentinel-3, Planet Tanager and GOES."
))
story.append(callout(
    "<b>Do not read this as a sensor ranking.</b> Record counts depend on spatial resolution, detection limits, revisit, "
    "tasking, cloud/surface conditions, validation and data availability. They describe this MARS snapshot, not relative "
    "instrument quality."
))
story.append(P("TROPOMI context", h2))
story.append(P(
    "The Sentinel-5P/TROPOMI Level-2 methane product provides column-averaged methane information with broad spatial "
    "coverage. UNEP IMEO technical documentation describes TROPOMI hotspot information as one input used to direct "
    "targeting and monitoring with higher-spatial-resolution satellites. This report does not reproduce that hotspot or "
    "retrieval methodology; it only handles the published downstream MARS records."
))
story.append(PageBreak())

# Sector + timeline
story.append(P("5. Sector and temporal composition", h1))
story.append(img("fig04_sector_mix.png", width=174 * mm))
story.append(P("Figure 4. Sector composition of plume observations and distinct detected sources.", caption))
story.append(P(
    "Oil and gas dominates both plume observations and detected sources in this snapshot. Coal and waste are the next "
    "largest groups. This is consistent with MARS' historical focus and should not be interpreted as a sector-neutral "
    "global methane inventory."
))
story.append(Spacer(1, 4))
story.append(img("fig05_detection_timeline.png", width=167 * mm))
story.append(P("Figure 5. Plume records by observation year. The 2026 count is partial through 5 September.", caption))
story.append(P(
    "The strong increase in records from 2023 onward reflects the evolving observing system, program operations, sensor "
    "availability, targeting, validation and public-data coverage. It is not a controlled time series of global methane emissions."
))
story.append(PageBreak())

# Flux
story.append(P("6. Published flux-rate fields", h1))
story.append(P(
    "The public MARS plume export contains methane flux-rate estimates in kg/h for most records. After numeric validation, "
    "29,058 records have a positive flux-rate value. These values are summarized exactly as published; the pipeline does "
    "not perform cross-sensor recalibration or uncertainty harmonization."
))
flux_metrics = [
    [P("Statistic", table_head), P("Published positive flux rate", table_head)],
    [P("Valid positive records", table_body), P("29,058", table_body)],
    [P("25th percentile", table_body), P("1,393 kg/h", table_body)],
    [P("Median", table_body), P("3,027 kg/h", table_body)],
    [P("75th percentile", table_body), P("11,000 kg/h", table_body)],
    [P("95th percentile", table_body), P("73,000 kg/h", table_body)],
]
story.append(data_table(flux_metrics, [70 * mm, 104 * mm]))
story.append(Spacer(1, 5))
story.append(img("fig06_flux_distribution.png", width=169 * mm))
story.append(P("Figure 6. Distribution of positive published methane flux-rate estimates on a log10 x-axis.", caption))
story.append(callout(
    "Flux-rate comparisons across sensors require scientific context beyond this demonstration because instruments and "
    "quantification pathways differ. The figure is a data-field summary, not a cross-sensor performance analysis.",
    color=ORANGE, bg=colors.HexColor("#FFF7F1")
))
story.append(PageBreak())

# Map
story.append(P("7. Spatial distribution", h1))
story.append(img("fig02_global_plumes_map.png", width=174 * mm))
story.append(P(
    "Figure 7. Global distribution of published plume locations. Positive flux-rate records are colored by log10(CH4 flux rate). "
    "Natural Earth boundaries are shown only for geographic context.",
    caption
))
story.append(P(
    "The snapshot spans 99 countries. The map represents where MARS has detected and published plume observations, not a "
    "complete global map of methane emissions. Coverage depends on instrument capability, observation opportunities, cloud "
    "and surface conditions, targeting, retrieval sensitivity, validation and program priorities."
))
story.append(P(
    "The MARS data dictionary notes that Sentinel-5P source coordinates are approximate and automatically generated based "
    "on plume-mask and wind-direction information. The normalized point layer therefore preserves upstream coordinates "
    "without claiming greater spatial precision than the source product."
))
story.append(PageBreak())

# Reproducibility
story.append(P("8. Reproducibility and operational path", h1))
story.append(P(
    "The pipeline is designed to be rerun from the official data source rather than relying on a hand-curated local copy. "
    "The current repository includes download automation, provenance hashing, QA logic, tests, publication assets, a "
    "portable GeoPackage output, Docker packaging and a PostGIS loading path."
))
story.append(P("Rebuild sequence", h2))
cmd = """python src\\download_data.py
python -m pytest -q
python src\\run_pipeline.py
python src\\publication_assets.py
python src\\build_publication_report.py"""
story.append(Preformatted(cmd, code))
story.append(P("Executed evidence", h2))
evidence_rows = [
    [P("Component", table_head), P("Observed result", table_head)],
    [P("Automated tests", table_body), P("2/2 passed", table_body)],
    [P("Normalized GeoPackage", table_body), P("30,116 records, EPSG:4326", table_body)],
    [P("Inspection sample", table_body), P("1,000 GeoJSON records", table_body)],
    [P("Machine summaries", table_body), P("CSV + JSON", table_body)],
    [P("PostGIS", table_body), P("Schema + GIST/time/satellite indexes + UPSERT loader", table_body)],
    [P("Containerization", table_body), P("Dockerfile included", table_body)],
]
story.append(data_table(evidence_rows, [50 * mm, 124 * mm]))
story.append(Spacer(1, 5))
story.append(P(
    "GeoPackage is the default executed artifact so the demonstration can be reproduced without provisioning a database "
    "server. The PostGIS path remains explicit for migration to an operational service-backed environment."
))
story.append(PageBreak())

# Limitations and licensing
story.append(P("9. Limitations, licensing and responsible interpretation", h1))
limitations = [
    ("No atmospheric retrieval", "The project starts from already processed MARS detections."),
    ("Snapshot dependence", "Results are tied to the 6 October 2026 archive and SHA-256 hash."),
    ("No completeness claim", "Public MARS observations are not a complete census of methane emissions."),
    ("No sensor ranking", "Observation counts reflect dataset composition and observing strategy."),
    ("No trend inference", "Annual counts are not a controlled global methane-emission time series."),
    ("No cross-sensor harmonization", "Published flux rates are not recalibrated across retrieval approaches."),
    ("Point normalization", "Missing plume polygons are not reconstructed; published lat/lon are used."),
]
lim_rows = [[P("Limitation", table_head), P("Interpretation", table_head)]]
for a, b in limitations:
    lim_rows.append([P(a, table_body), P(b, table_body)])
story.append(data_table(lim_rows, [53 * mm, 121 * mm]))
story.append(Spacer(1, 6))
story.append(P("Licensing and attribution", h2))
story.append(P(
    "The UNEP Eye on Methane MARS dataset is shared under Creative Commons Attribution-NonCommercial-ShareAlike 4.0 "
    "International (CC BY-NC-SA 4.0). Derived figures, tables, the lightweight sample and this report are distributed "
    "under the same license. The independently authored pipeline source code is distributed under the MIT License."
))
story.append(callout(
    "<b>Attribution statement.</b> Contains data derived from UNEP International Methane Emissions Observatory (IMEO), "
    "Eye on Methane / Methane Alert and Response System (MARS), downloaded 6 October 2026. Data were normalized, "
    "quality-flagged, aggregated and visualized for this independent technical demonstration. Original MARS data are "
    "licensed CC BY-NC-SA 4.0. This work is not produced by or endorsed by UNEP or IMEO."
))
story.append(P(
    "Natural Earth vector boundaries used for cartographic context are public-domain data. The intended publication model "
    "is a GitHub software repository plus a separately citable Zenodo technical report with its own DOI."
))
story.append(PageBreak())

# Conclusions
story.append(P("10. Conclusions", h1))
story.append(P(
    "A compact downstream workflow is sufficient to demonstrate capabilities that matter for operational environmental "
    "Earth-observation systems: provenance, schema discipline, geospatial normalization, deterministic validation, explicit "
    "quality flags, reproducible summaries, spatial persistence and transparent limitations."
))
story.append(P(
    "The main contribution is not a new methane retrieval algorithm. It is a defensible data-engineering layer around a "
    "real public methane EO product. The workflow receives an official MARS snapshot, validates its structure, preserves "
    "source provenance, creates a portable spatial representation, exposes a PostGIS loading path, and produces "
    "machine-readable and illustrated outputs without overstating the scientific scope."
))
story.append(P(
    "This boundary is deliberate: it demonstrates how established remote-sensing and geospatial engineering practices can "
    "be transferred to methane data while preserving the distinction between <b>data engineering</b> and "
    "<b>atmospheric retrieval science</b>."
))
story.append(Spacer(1, 8))
story.append(img("fig01_pipeline_architecture.png", width=166 * mm))
story.append(PageBreak())

# References
story.append(P("References", h1))
refs = [
    "United Nations Environment Programme (UNEP). Methane Alert and Response System (MARS). https://www.unep.org/topics/energy/methane/methane-alert-and-response-system-mars",
    "United Nations Environment Programme (UNEP). UNEP IMEO Technical Documentation for Methane Satellite Detection and Quantification. September 2024. https://wedocs.unep.org/handle/20.500.11822/46241",
    "UNEP IMEO. Eye on Methane - Download data set. https://methanedata.unep.org/download-dataset",
    "UNEP IMEO. Data dictionary: MARS methane plumes and sources. https://methanedata.unep.org/dict-mars-plumes",
    "TROPOMI. Methane (L2__CH4___) product documentation. https://www.tropomi.eu/data-products/methane",
    "Copernicus Atmosphere Monitoring Service. Methane Hotspot Explorer. https://apps.atmosphere.copernicus.eu/methane-explorer/",
    "European Space Agency. Copernicus Sentinel-5P TROPOMI Level 2 Methane products, Version 02. DOI: 10.5270/S5P-3lcdqiv",
    "Creative Commons. Attribution-NonCommercial-ShareAlike 4.0 International. https://creativecommons.org/licenses/by-nc-sa/4.0/",
    "Natural Earth. Natural Earth vector map data. https://www.naturalearthdata.com/",
]
for i, ref in enumerate(refs, 1):
    story.append(P(f"<b>{i}.</b> {ref}", body_small))
story.append(Spacer(1, 8))
if DOI:
    story.append(P("Suggested citation", h2))
    story.append(callout(
        "Innocentini, M. de M. (2026). <i>A Reproducible QA/QC Pipeline for Public Satellite Methane Plume Data from UNEP IMEO MARS</i> "
        f"(Version 1.0.0). Zenodo. https://doi.org/{DOI}"
    ))
else:
    story.append(P("Suggested citation before DOI assignment", h2))
    story.append(callout(
        "Innocentini, M. de M. (2026). <i>A Reproducible QA/QC Pipeline for Public Satellite Methane Plume Data from UNEP IMEO MARS</i> "
        "(Version 1.0.0). Agropixel. Technical report."
    ))
story.append(Spacer(1, 6))
doi_line = f"<b>Zenodo DOI:</b> https://doi.org/{DOI}<br/>" if DOI else ""
story.append(P(
    doi_line
    + "<b>Code repository:</b> https://github.com/marcel-innocentini/methane-imeo-data-engineering<br/>"
    + "<b>Report license:</b> CC BY-NC-SA 4.0<br/>"
    + "<b>Code license:</b> MIT",
    body_small,
))

doc = SimpleDocTemplate(
    str(OUT),
    pagesize=A4,
    leftMargin=LEFT,
    rightMargin=RIGHT,
    topMargin=15 * mm,
    bottomMargin=15 * mm,
    title="A Reproducible QA/QC Pipeline for Public Satellite Methane Plume Data from UNEP IMEO MARS",
    author="Marcel de Mello Innocentini",
    subject="UNEP IMEO MARS methane satellite data engineering, QA/QC and reproducibility",
    keywords="methane, UNEP, IMEO, MARS, satellite remote sensing, QA/QC, PostGIS, GeoPandas",
)
doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
print(OUT)
