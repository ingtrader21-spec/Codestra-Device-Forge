$ErrorActionPreference='Stop'
$Repo=Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $Repo
$Python=Join-Path $Repo '.venv\Scripts\python.exe'
if(-not (Test-Path $Python)){ throw "Device Forge venv missing: $Python" }
& $Python -m uvicorn app.main:app --host 127.0.0.1 --port 8090
