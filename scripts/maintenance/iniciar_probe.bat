@echo off
echo ========================================
echo Iniciando Probe Coruja Monitor
echo ========================================
echo.

cd "C:\Users\user\OneDrive - EmpresaXPTO Ltda\Desktop\Coruja Monitor\probe"

echo Verificando configuracao...
if not exist probe_config.json (
    echo ERRO: probe_config.json nao encontrado!
    echo Execute configurar_probe.bat primeiro
    pause
    exit /b 1
)

echo.
echo Configuracao encontrada:
type probe_config.json
echo.
echo.

echo Iniciando coleta de metricas...
echo Pressione Ctrl+C para parar
echo.

python probe_core.py

pause
