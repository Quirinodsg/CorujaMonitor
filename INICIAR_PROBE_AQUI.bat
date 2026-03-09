@echo off
chcp 65001 >nul
cls
echo ========================================
echo   INICIAR PROBE CORUJA
echo ========================================
echo.

echo Verificando localizacao...
echo.

REM Detectar onde estamos
if exist "probe\probe_core.py" (
    echo [OK] Encontrado na raiz do projeto
    cd probe
    goto :start_probe
)

if exist "probe_core.py" (
    echo [OK] Ja estamos na pasta probe
    goto :start_probe
)

if exist "..\probe\probe_core.py" (
    echo [OK] Encontrado na pasta pai
    cd ..\probe
    goto :start_probe
)

echo [ERRO] Nao encontrei probe_core.py!
echo.
echo Certifique-se de executar este script de:
echo - Raiz do projeto (onde esta a pasta probe)
echo - Dentro da pasta probe
echo.
pause
exit /b 1

:start_probe
echo.
echo Pasta atual: %CD%
echo.

echo Detectando Python...
where python >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
    echo [OK] Python encontrado: python
    python --version
) else (
    where py >nul 2>&1
    if %errorlevel% equ 0 (
        set PYTHON_CMD=py
        echo [OK] Python encontrado: py
        py --version
    ) else (
        echo [ERRO] Python nao encontrado!
        echo.
        echo Instale Python 3.8+ de: https://www.python.org/downloads/
        echo.
        pause
        exit /b 1
    )
)

echo.
echo Verificando config.yaml...
if not exist "config.yaml" (
    echo [ERRO] config.yaml nao encontrado!
    echo.
    echo Execute primeiro: configurar_probe.bat
    echo.
    pause
    exit /b 1
)
echo [OK] config.yaml encontrado
echo.

echo ========================================
echo   INICIANDO PROBE...
echo ========================================
echo.
echo A probe esta rodando
echo Mantenha esta janela ABERTA
echo Para parar: Pressione Ctrl+C
echo.
echo Logs aparecem abaixo:
echo ========================================
echo.

%PYTHON_CMD% probe_core.py

echo.
echo ========================================
echo   PROBE PARADA
echo ========================================
pause
