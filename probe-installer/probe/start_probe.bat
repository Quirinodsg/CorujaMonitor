@echo off
echo ========================================
echo Iniciando Coruja Probe com Docker Support
echo ========================================
echo.

cd /d "%~dp0"

echo Verificando Python...
python --version
if errorlevel 1 (
    echo ERRO: Python nao encontrado!
    pause
    exit /b 1
)

echo.
echo Verificando Docker...
docker version >nul 2>&1
if errorlevel 1 (
    echo AVISO: Docker nao encontrado ou nao esta rodando!
    echo O coletor Docker nao funcionara.
    echo.
)

echo.
echo Iniciando probe...
python probe_core.py

pause
