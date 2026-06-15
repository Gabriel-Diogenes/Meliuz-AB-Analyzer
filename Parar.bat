@echo off
setlocal EnableExtensions
title Meliuz AB Analyzer - Encerrando
cd /d "%~dp0"

echo.
echo  Encerrando servicos nas portas 8000 e 5173...
echo.

for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do (
    echo [OK] Encerrando backend PID %%a
    taskkill /PID %%a /F >nul 2>&1
)

for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5173" ^| findstr "LISTENING"') do (
    echo [OK] Encerrando frontend PID %%a
    taskkill /PID %%a /F >nul 2>&1
)

echo.
echo  Servicos encerrados.
echo.
pause
