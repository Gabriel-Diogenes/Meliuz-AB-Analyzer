#Requires -Version 5.1
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

Write-Host ""
Write-Host "  Méliuz Growth A/B Analyzer" -ForegroundColor DarkYellow
Write-Host "  Iniciando backend + frontend..." -ForegroundColor Gray
Write-Host ""

function Test-Command($name) {
    return [bool](Get-Command $name -ErrorAction SilentlyContinue)
}

$pythonCmd = $null
if (Test-Command python) { $pythonCmd = "python" }
elseif (Test-Command py) {
    try {
        & py -3 -c "import sys" 2>$null | Out-Null
        if ($LASTEXITCODE -eq 0) { $pythonCmd = "py -3" }
    } catch { }
    if (-not $pythonCmd) { $pythonCmd = "py" }
}
if (-not $pythonCmd) { throw "Python nao encontrado. Instale Python 3.11+." }
if (-not (Test-Command node)) { throw "Node.js nao encontrado. Instale Node.js 18+." }

$venvPython = Join-Path $Root "backend\.venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Host "[SETUP] Criando ambiente Python..." -ForegroundColor Cyan
    Invoke-Expression "$pythonCmd -m venv `"$(Join-Path $Root 'backend\.venv')`""
    & (Join-Path $Root "backend\.venv\Scripts\pip.exe") install -r (Join-Path $Root "backend\requirements.txt") -q
}

if (-not (Test-Path (Join-Path $Root "frontend\node_modules\.bin\vite.cmd"))) {
    Write-Host "[SETUP] Instalando dependencias do frontend..." -ForegroundColor Cyan
    Push-Location (Join-Path $Root "frontend")
    npm install
    if ($LASTEXITCODE -ne 0) { throw "Falha ao instalar dependencias do frontend." }
    Pop-Location
}

$envFile = Join-Path $Root "backend\.env"
$envExample = Join-Path $Root "backend\.env.example"
if (-not (Test-Path $envFile) -and (Test-Path $envExample)) {
    Copy-Item $envExample $envFile
}

Write-Host "[OK] Iniciando backend (porta 8000)..." -ForegroundColor Green
Start-Process powershell -ArgumentList @(
    "-NoExit", "-Command",
    "Set-Location '$Root\backend'; .\.venv\Scripts\uvicorn app.principal:aplicacao --reload --port 8000"
) -WindowStyle Normal

$healthOk = $false
for ($i = 0; $i -lt 20; $i++) {
    Start-Sleep -Seconds 1
    try {
        $resp = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/health" -TimeoutSec 2
        if ($resp.status -eq "ok") { $healthOk = $true; break }
    } catch { }
}

if (-not $healthOk) {
    Write-Host "[AVISO] Backend ainda inicializando..." -ForegroundColor Yellow
}

Write-Host "[OK] Iniciando frontend (porta 5173)..." -ForegroundColor Green
Start-Process powershell -ArgumentList @(
    "-NoExit", "-Command",
    "Set-Location '$Root\frontend'; npm run dev"
) -WindowStyle Normal

Start-Sleep -Seconds 5
Start-Process "http://localhost:5173"

Write-Host ""
Write-Host "  Aplicacao iniciada!" -ForegroundColor Green
Write-Host "  Interface: http://localhost:5173"
Write-Host "  API:       http://localhost:8000"
Write-Host ""
Write-Host "  Para encerrar: execute Parar.bat ou feche as janelas abertas."
Write-Host ""
