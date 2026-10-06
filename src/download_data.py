from __future__ import annotations

import argparse
import hashlib
import json
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

SOURCE_URL = "https://unepazeconomyadlsstorage.blob.core.windows.net/public/unep_methanedata_detected_plumes_geojson.zip"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    raw = root / "data" / "raw"
    extract_dir = raw / "unep_plumes"
    raw.mkdir(parents=True, exist_ok=True)
    extract_dir.mkdir(parents=True, exist_ok=True)
    zip_path = raw / "unep_methanedata_detected_plumes_geojson.zip"

    if args.force or not zip_path.exists():
        tmp = zip_path.with_suffix(zip_path.suffix + ".part")
        urllib.request.urlretrieve(SOURCE_URL, tmp)
        tmp.replace(zip_path)

    with zipfile.ZipFile(zip_path) as zf:
        zf.testzip()
        zf.extractall(extract_dir)

    provenance = {
        "source": "UNEP IMEO Eye on Methane - MARS detected plumes and sources",
        "source_url": SOURCE_URL,
        "retrieved_utc": datetime.now(timezone.utc).isoformat(),
        "sha256": sha256(zip_path),
        "archive_bytes": zip_path.stat().st_size,
        "license": "CC BY-NC-SA 4.0 (see extracted LICENSE-CC-BY-NC-SA.txt)",
        "files": sorted(p.name for p in extract_dir.iterdir()),
    }
    (raw / "provenance.json").write_text(json.dumps(provenance, indent=2), encoding="utf-8")
    print(json.dumps(provenance, indent=2))


if __name__ == "__main__":
    main()
