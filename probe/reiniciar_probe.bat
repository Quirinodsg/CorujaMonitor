@echo off
echo ========================================
echo Reiniciando Coruja Probe
echo ========================================
echo.

cd /d "%~dp0"

echo Parando probe atual...
taskkill /F /FI "WINDOWTITLE eq probe*" /T >nul 2>&1
taskkill /F /FI "IMAGENAME eq python.exe" /FI "MEMUSAGE gt 50000" >nul 2>&1
timeout /t 2 /nobreak >nul

echo.
echo Verificando configuracao...
type probe_config.json | findstr "api_url"

echo.
echo Iniciando probe atualizada...
echo.
python probe_core.py

pause
