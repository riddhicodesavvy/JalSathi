$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
if (-not (Test-Path '.venv/Scripts/python.exe')) {
    $runtimePython = Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
    if (Test-Path $runtimePython) { & $runtimePython -m venv .venv }
    else { python -m venv .venv }
    if ($LASTEXITCODE -ne 0) { throw 'Python 3.12 or newer is required. Install Python and retry.' }
}
& ./.venv/Scripts/python.exe -m pip install -r backend/requirements.lock.txt
if ($LASTEXITCODE -ne 0) { throw 'Python dependency installation failed.' }
Push-Location frontend
try { npm ci; if ($LASTEXITCODE -ne 0) { throw 'Frontend dependency installation failed.' } }
finally { Pop-Location }
& ./.venv/Scripts/python.exe -m ml.train
if ($LASTEXITCODE -ne 0) { throw 'Model training failed.' }
& ./.venv/Scripts/python.exe -m ml.extensions
& ./.venv/Scripts/python.exe -m scripts.verify_artifacts
