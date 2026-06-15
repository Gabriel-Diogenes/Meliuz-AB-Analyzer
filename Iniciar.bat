@echo off
setlocal EnableExtensions
title Meliuz AB Analyzer - Iniciando
cd /d "%~dp0"

echo.
echo  ============================================
echo    Meliuz Growth A/B Analyzer
echo    Iniciando backend + frontend...
echo  ============================================
echo.

set "PYCMD="
where python >nul 2>&1 && set "PYCMD=python"
if not defined PYCMD where py >nul 2>&1 && set "PYCMD=py -3.11"
if not defined PYCMD (
    echo [ERRO] Python nao encontrado. Instale Python 3.11+ e tente novamente.
    pause
    exit /b 1
)

where node >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Node.js nao encontrado. Instale Node.js 18+ e tente novamente.
    pause
    exit /b 1
)

if not exist "backend\.venv\Scripts\python.exe" (
    echo [SETUP] Criando ambiente Python...
    %PYCMD% -m venv backend\.venv
    call backend\.venv\Scripts\pip install -r backend\requirements.txt -q
)

if not exist "frontend\node_modules" (
    echo [SETUP] Instalando dependencias do frontend...
    pushd frontend
    call npm install
    popd
)

if not exist "backend\.env" (
    if exist "backend\.env.example" copy "backend\.env.example" "backend\.env" >nul
)

echo [OK] Iniciando backend na porta 8000...
start "Meliuz Backend" cmd /k "cd /d "%~dp0backend" && .venv\Scripts\uvicorn app.principal:aplicacao --reload --port 8000"

echo [OK] Aguardando backend ficar pronto...
timeout /t 4 /nobreak >nul

echo [OK] Iniciando frontend na porta 5173...
start "Meliuz Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo [OK] Aguardando frontend ficar pronto...
timeout /t 5 /nobreak >nul

echo [OK] Abrindo navegador em http://localhost:5173
start "" "http://localhost:5173"

echo.
echo  Aplicacao iniciada com sucesso!
echo  - Interface:  http://localhost:5173
echo  - API:        http://localhost:8000
echo.
echo  Para encerrar, feche as janelas Backend e Frontend
echo  ou execute Parar.bat
echo.
pause
