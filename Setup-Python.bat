@echo off
REM ========================================
REM SETUP PYTHON 3.11 + DEPENDENCIAS
REM Coruja Monitor Probe v1.0.0
REM ========================================

echo.
echo ========================================
echo   SETUP PYTHON 3.11 + DEPENDENCIAS
echo   Coruja Monitor Probe
echo ========================================
echo.

REM Verificar admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    color 0C
    echo [ERRO] Execute como Administrador!
    echo.
    echo Clique direito neste arquivo e selecione:
    echo "Executar como Administrador"
    echo.
    pause
    exit /b 1
)

REM ========================================
REM VERIFICAR PYTHON
REM ========================================

echo [1/3] Verificando Python...
echo.

set "PYTHON_FOUND=0"

REM Tentar python no PATH
python --version >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Python ja instalado no PATH
    python --version
    set "PYTHON_FOUND=1"
    goto :install_deps
)

REM Tentar Python 3.11
if exist "C:\Program Files\Python311\python.exe" (
    echo [OK] Python 3.11 encontrado
    "C:\Program Files\Python311\python.exe" --version
    set "PYTHON_FOUND=1"
    goto :install_deps
)

REM Tentar Python 3.10
if exist "C:\Program Files\Python310\python.exe" (
    echo [OK] Python 3.10 encontrado
    "C:\Program Files\Python310\python.exe" --version
    set "PYTHON_FOUND=1"
    goto :install_deps
)

REM ========================================
REM BAIXAR PYTHON
REM ========================================

echo [INFO] Python nao encontrado - sera instalado
echo.
echo [2/3] Baixando Python 3.11.8...
echo.

if not exist "python-3.11.8-amd64.exe" (
    echo Baixando de python.org (25 MB)...
    echo Aguarde 1-3 minutos...
    echo.
    
    powershell -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; $ProgressPreference = 'SilentlyContinue'; Write-Host 'Baixando Python 3.11.8...'; try { Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe' -OutFile 'python-3.11.8-amd64.exe' -UseBasicParsing -TimeoutSec 300; Write-Host 'Download concluido!' -ForegroundColor Green } catch { Write-Host 'Erro no download: ' $_.Exception.Message -ForegroundColor Red }"
    
    if not exist "python-3.11.8-amd64.exe" (
        color 0C
        echo.
        echo ========================================
        echo [ERRO] Falha ao baixar Python!
        echo ========================================
        echo.
        echo SOLUCAO:
        echo 1. Baixe manualmente:
        echo    https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe
        echo.
        echo 2. Salve o arquivo nesta pasta:
        echo    %CD%
        echo.
        echo 3. Execute este instalador novamente
        echo.
        echo ========================================
        echo.
        pause
        exit /b 1
    )
)

REM ========================================
REM INSTALAR PYTHON
REM ========================================

echo.
echo [INFO] Instalando Python 3.11.8...
echo Aguarde 2-5 minutos...
echo NAO FECHE ESTA JANELA!
echo.

start /wait python-3.11.8-amd64.exe /quiet InstallAllUsers=1 PrependPath=1 Include_pip=1

echo Aguardando conclusao...
timeout /t 15 /nobreak >nul

"C:\Program Files\Python311\python.exe" --version >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Python instalado com sucesso!
    "C:\Program Files\Python311\python.exe" --version
) else (
    color 0E
    echo [AVISO] Python pode nao ter sido instalado corretamente
    echo Verifique manualmente
)

REM ========================================
REM INSTALAR DEPENDENCIAS
REM ========================================

:install_deps
echo.
echo [3/3] Instalando dependencias Python...
echo.

set "PYTHON_EXE=python"
if exist "C:\Program Files\Python311\python.exe" (
    set "PYTHON_EXE=C:\Program Files\Python311\python.exe"
)

"%PYTHON_EXE%" --version >nul 2>&1
if %errorLevel% neq 0 (
    color 0C
    echo [ERRO] Python nao encontrado!
    echo.
    pause
    exit /b 1
)

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

REM ========================================
REM VERIFICAR
REM ========================================

echo.
echo Verificando instalacao...
echo.

"%PYTHON_EXE%" -c "import psutil, httpx, win32api, pysnmp, yaml" >nul 2>&1
if %errorLevel% equ 0 (
    color 0A
    echo ========================================
    echo   INSTALACAO CONCLUIDA COM SUCESSO!
    echo ========================================
    echo.
    echo Python: 
    "%PYTHON_EXE%" --version
    echo.
    echo Dependencias instaladas:
    echo   - psutil
    echo   - httpx
    echo   - pywin32
    echo   - pysnmp
    echo   - pyyaml
    echo.
    echo ========================================
    echo   PROXIMO PASSO
    echo ========================================
    echo.
    echo Execute agora: Setup-Probe.bat
    echo.
) else (
    color 0E
    echo ========================================
    echo   AVISO: Algumas dependencias faltando
    echo ========================================
    echo.
    echo Testando individualmente:
    "%PYTHON_EXE%" -c "import psutil" >nul 2>&1 && echo   [OK] psutil || echo   [X] psutil
    "%PYTHON_EXE%" -c "import httpx" >nul 2>&1 && echo   [OK] httpx || echo   [X] httpx
    "%PYTHON_EXE%" -c "import win32api" >nul 2>&1 && echo   [OK] pywin32 || echo   [X] pywin32
    "%PYTHON_EXE%" -c "import pysnmp" >nul 2>&1 && echo   [OK] pysnmp || echo   [X] pysnmp
    "%PYTHON_EXE%" -c "import yaml" >nul 2>&1 && echo   [OK] pyyaml || echo   [X] pyyaml
    echo.
)

echo.
pause
