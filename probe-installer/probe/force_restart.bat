@echo off
echo ========================================
echo Forcando Reinicio da Probe
echo ========================================
echo.

cd /d "%~dp0"

echo [1/4] Parando processos Python...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul

echo [2/4] Verificando configuracao...
type probe_config.json | findstr "api_url"

echo.
echo [3/4] Limpando cache...
del /Q __pycache__\*.* >nul 2>&1
del /Q collectors\__pycache__\*.* >nul 2>&1

echo.
echo [4/4] Iniciando probe atualizada...
echo.
start "Coruja Probe" python probe_core.py

echo.
echo ========================================
echo Probe reiniciada com sucesso!
echo ========================================
echo.
echo Aguarde 2 minutos e recarregue o frontend (F5)
echo.
pause
