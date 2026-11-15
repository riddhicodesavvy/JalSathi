$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
Set-Location $projectRoot
$projectPython = Join-Path $projectRoot '.venv/Scripts/python.exe'
if (-not (Test-Path $projectPython)) { throw 'Run scripts/setup.ps1 first.' }
if (-not (Test-Path 'ml/artifacts/registry.json')) { throw 'Train models first: .venv/Scripts/python.exe -m ml.train' }
$apiProcess = Start-Process -FilePath $projectPython -ArgumentList @('-m','uvicorn','backend.app.main:app','--host','127.0.0.1','--port','8000') -WorkingDirectory $projectRoot -WindowStyle Hidden -PassThru
Write-Host 'JalSathi: http://127.0.0.1:5173  | API docs: http://127.0.0.1:8000/docs'
Push-Location frontend
try { npm run dev }
finally {
    Pop-Location
    if (-not $apiProcess.HasExited) { Stop-Process -Id $apiProcess.Id }
}
