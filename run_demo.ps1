$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
python src/download_data.py
python -m pytest -q
python src/run_pipeline.py
Write-Host "METHANE demo complete. See outputs\ and data\processed\."
