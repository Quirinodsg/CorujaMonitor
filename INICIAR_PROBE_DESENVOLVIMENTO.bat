@echo off
chcp 65001 >nul
cls
echo ========================================
echo   INICIAR PROBE - DESENVOLVIMENTO
echo ========================================
echo.

REM Ir para a pasta do código-fonte
cd /d "C:\Users\andre.quirino\Coruja Monitor\probe"

echo Pasta atual: %CD%
echo.

echo Verificando arquivos...
if not exist "probe_core.py" (
    echo [ERRO] probe_core.py nao encontrado!
    echo.
    echo Verifique se esta na pasta correta:
    echo C:\Users\andre.quirino\Coruja Monitor\probe
    echo.
    pause
    exit /b 1
)

if not exist "config.yaml" (
    echo [ERRO] config.yaml nao encontrado!
    echo.
    echo Execute primeiro: configurar_probe.bat
    echo.
    pause
    exit /b 1
)

echo [OK] Arquivos encontrados
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
