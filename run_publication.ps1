$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "[1/5] Download / provenance"
python src\download_data.py

Write-Host "[2/5] Tests"
python -m pytest -q

Write-Host "[3/5] Core pipeline"
python src\run_pipeline.py

Write-Host "[4/5] Publication figures and tables"
python src\publication_assets.py

Write-Host "[5/5] Illustrated technical report"
python src\build_publication_report.py

Write-Host "Publication package rebuilt successfully."
