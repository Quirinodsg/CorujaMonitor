@echo off
setlocal enabledelayedexpansion
title Executar Probe Coruja
color 0B

echo.
echo ========================================
echo   EXECUTAR PROBE CORUJA
echo   Modo Direto (sem servico)
echo ========================================
echo.

REM Verificar admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    color 0C
    echo [ERRO] Execute como Administrador!
    echo.
    pause
    exit /b 1
)

cd /d "C:\Program Files\CorujaMonitor\Probe"

if not exist "probe_core.py" (
    color 0C
    echo [ERRO] Probe nao instalada!
    pause
    exit /b 1
)

echo Detectando Python...
echo.

set "PYTHON_EXE="

python --version >nul 2>&1
if !errorLevel! equ 0 (
    set "PYTHON_EXE=python"
    goto :python_found
)

if exist "C:\Program Files\Python311\python.exe" (
    set "PYTHON_EXE=C:\Program Files\Python311\python.exe"
    goto :python_found
)

if exist "C:\Program Files\Python310\python.exe" (
    set "PYTHON_EXE=C:\Program Files\Python310\python.exe"
    goto :python_found
)

color 0C
echo [ERRO] Python nao encontrado!
pause
exit /b 1

:python_found
echo [OK] Python: !PYTHON_EXE!
"!PYTHON_EXE!" --version
echo.

color 0A
echo ========================================
echo   PROBE INICIANDO...
echo ========================================
echo.
echo A probe esta rodando!
echo.
echo Mantenha esta janela ABERTA
echo.
echo Para parar: Pressione Ctrl+C
echo.
echo Logs aparecerao abaixo:
echo ========================================
echo.

"!PYTHON_EXE!" probe_core.py

pause
