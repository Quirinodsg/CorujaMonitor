@echo off
chcp 65001 >nul
cls
echo ========================================
echo   INICIAR PROBE CORUJA - MODO DIRETO
echo ========================================
echo.

cd /d "%~dp0probe"

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
        echo [ERRO] Python não encontrado!
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
echo A probe está rodando
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
