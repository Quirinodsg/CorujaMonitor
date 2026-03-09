@echo off
REM ========================================
REM INSTALAR DEPENDENCIAS PYTHON
REM Coruja Monitor Probe v1.0.0
REM ========================================

echo.
echo ========================================
echo   INSTALANDO DEPENDENCIAS PYTHON
echo ========================================
echo.

REM Localizar Python
set "PYTHON_EXE=python"

REM Tentar Python no PATH
python --version >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Python encontrado no PATH
    goto :install
)

REM Tentar Python 3.11
if exist "C:\Program Files\Python311\python.exe" (
    set "PYTHON_EXE=C:\Program Files\Python311\python.exe"
    echo [OK] Python 3.11 encontrado
    goto :install
)

REM Tentar Python 3.10
if exist "C:\Program Files\Python310\python.exe" (
    set "PYTHON_EXE=C:\Program Files\Python310\python.exe"
    echo [OK] Python 3.10 encontrado
    goto :install
)

echo [ERRO] Python nao encontrado!
echo.
echo Instale Python primeiro usando SetupDependencias.msi
echo.
exit /b 1

:install
echo.
echo Python: %PYTHON_EXE%
"%PYTHON_EXE%" --version
echo.

echo [1/6] Atualizando pip...
"%PYTHON_EXE%" -m pip install --quiet --upgrade pip

echo [2/6] Instalando psutil...
"%PYTHON_EXE%" -m pip install --quiet psutil

echo [3/6] Instalando httpx...
"%PYTHON_EXE%" -m pip install --quiet httpx

echo [4/6] Instalando pywin32...
"%PYTHON_EXE%" -m pip install --quiet pywin32

echo [5/6] Instalando pysnmp...
"%PYTHON_EXE%" -m pip install --quiet pysnmp

echo [6/6] Instalando pyyaml...
"%PYTHON_EXE%" -m pip install --quiet pyyaml

echo.
echo ========================================
echo   DEPENDENCIAS INSTALADAS COM SUCESSO!
echo ========================================
echo.

exit /b 0
