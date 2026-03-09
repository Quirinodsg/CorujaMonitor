@echo off
setlocal enabledelayedexpansion
title Adicionar Servidor Automaticamente
color 0B

echo.
echo ========================================
echo   ADICIONAR SERVIDOR AUTOMATICAMENTE
echo ========================================
echo.

REM Detectar Python
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

if exist "C:\Program Files\Python312\python.exe" (
    set "PYTHON_EXE=C:\Program Files\Python312\python.exe"
    goto :python_found
)

color 0C
echo [ERRO] Python nao encontrado!
echo.
pause
exit /b 1

:python_found
echo [OK] Python encontrado: !PYTHON_EXE!
echo.

echo Executando script...
echo.

"!PYTHON_EXE!" adicionar_servidor_automatico.py

echo.
pause
