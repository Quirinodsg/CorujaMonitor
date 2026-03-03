@echo off
echo ========================================
echo Aplicando Token da Probe
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] Parando probe atual...
taskkill /F /FI "WINDOWTITLE eq Coruja Probe*" >nul 2>&1
timeout /t 2 /nobreak >nul

echo [2/3] Verificando configuracao com token...
type probe_config.json | findstr "probe_token"

echo.
echo [3/3] Iniciando probe com token...
echo.
start "Coruja Probe" python probe_core.py

echo.
echo ========================================
echo Probe reiniciada com token!
echo ========================================
echo.
echo Aguarde 1 minuto e verifique os logs
echo Deve mostrar: "Sent X metrics successfully"
echo.
pause
