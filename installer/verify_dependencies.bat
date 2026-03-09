@echo off
REM ========================================
REM VERIFICAR DEPENDENCIAS
REM Coruja Monitor Probe v1.0.0
REM ========================================

echo.
echo ========================================
echo   VERIFICACAO DE DEPENDENCIAS
echo ========================================
echo.

REM Localizar Python
set "PYTHON_EXE=python"
set "PYTHON_FOUND=0"

python --version >nul 2>&1
if %errorLevel% equ 0 (
    set "PYTHON_FOUND=1"
    goto :check_deps
)

if exist "C:\Program Files\Python311\python.exe" (
    set "PYTHON_EXE=C:\Program Files\Python311\python.exe"
    set "PYTHON_FOUND=1"
    goto :check_deps
)

if exist "C:\Program Files\Python310\python.exe" (
    set "PYTHON_EXE=C:\Program Files\Python310\python.exe"
    set "PYTHON_FOUND=1"
    goto :check_deps
)

:check_deps
echo [1/3] Verificando Python...
if %PYTHON_FOUND% equ 1 (
    echo [OK] Python instalado:
    "%PYTHON_EXE%" --version
) else (
    echo [ERRO] Python nao encontrado
    echo.
    echo Instale usando SetupDependencias.msi
    echo.
    pause
    exit /b 1
)

echo.
echo [2/3] Verificando dependencias...
"%PYTHON_EXE%" -c "import psutil, httpx, win32api, pysnmp, yaml" >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Todas as dependencias instaladas
) else (
    echo [AVISO] Algumas dependencias faltando
    echo.
    echo Testando individualmente:
    "%PYTHON_EXE%" -c "import psutil" >nul 2>&1 && echo   [OK] psutil || echo   [X] psutil
    "%PYTHON_EXE%" -c "import httpx" >nul 2>&1 && echo   [OK] httpx || echo   [X] httpx
    "%PYTHON_EXE%" -c "import win32api" >nul 2>&1 && echo   [OK] pywin32 || echo   [X] pywin32
    "%PYTHON_EXE%" -c "import pysnmp" >nul 2>&1 && echo   [OK] pysnmp || echo   [X] pysnmp
    "%PYTHON_EXE%" -c "import yaml" >nul 2>&1 && echo   [OK] pyyaml || echo   [X] pyyaml
)

echo.
echo [3/3] Verificando Probe...
if exist "C:\Program Files\CorujaMonitor\Probe\probe_core.py" (
    echo [OK] Probe instalada em:
    echo     C:\Program Files\CorujaMonitor\Probe
) else (
    echo [AVISO] Probe nao encontrada
    echo.
    echo Instale usando SetupProbe.msi
)

echo.
echo ========================================
echo   VERIFICACAO CONCLUIDA
echo ========================================
echo.
pause
