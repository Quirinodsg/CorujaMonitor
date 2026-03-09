@echo off
REM ========================================
REM INSTALAR PYTHON 3.11 AUTOMATICAMENTE
REM ========================================

echo.
echo ========================================
echo   INSTALAR PYTHON 3.11
echo ========================================
echo.

REM Verificar admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERRO] Execute como Administrador!
    pause
    exit /b 1
)

REM Verificar se Python já está instalado
python --version >nul 2>&1
if %errorLevel% equ 0 (
    echo [INFO] Python ja instalado:
    python --version
    echo.
    echo Deseja reinstalar? (S/N)
    set /p REINSTALL=
    if /i not "%REINSTALL%"=="S" (
        echo Instalacao cancelada
        pause
        exit /b 0
    )
)

echo [1/3] Baixando Python 3.11.8...
echo.

if not exist "python-3.11.8-amd64.exe" (
    echo Baixando de python.org...
    echo Aguarde, isso pode demorar alguns minutos...
    echo.
    
    powershell -ExecutionPolicy Bypass -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; $ProgressPreference = 'SilentlyContinue'; Write-Host 'Iniciando download...'; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe' -OutFile 'python-3.11.8-amd64.exe' -UseBasicParsing; Write-Host 'Download concluido!'}"
    
    if not exist "python-3.11.8-amd64.exe" (
        echo [ERRO] Falha ao baixar Python!
        echo.
        echo SOLUCAO:
        echo 1. Baixe manualmente: https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe
        echo 2. Coloque o arquivo nesta pasta
        echo 3. Execute este script novamente
        echo.
        pause
        exit /b 1
    )
) else (
    echo [OK] Instalador ja existe
)

echo.
echo [2/3] Instalando Python 3.11.8...
echo.
echo IMPORTANTE:
echo - Aguarde 2-5 minutos
echo - NAO FECHE ESTA JANELA
echo - A instalacao e silenciosa (sem janelas)
echo.
pause

REM Instalar com log detalhado
echo Instalando...
start /wait python-3.11.8-amd64.exe /quiet InstallAllUsers=1 PrependPath=1 Include_pip=1 /log python_install.log

echo.
echo Aguardando conclusao...
timeout /t 15 /nobreak >nul

echo.
echo [3/3] Verificando instalacao...
echo.

REM Atualizar PATH
set "PATH=%PATH%;C:\Program Files\Python311;C:\Program Files\Python311\Scripts"

REM Verificar instalacao
"C:\Program Files\Python311\python.exe" --version >nul 2>&1
if %errorLevel% equ 0 (
    echo ========================================
    echo   PYTHON INSTALADO COM SUCESSO!
    echo ========================================
    echo.
    "C:\Program Files\Python311\python.exe" --version
    echo.
    echo Instalado em: C:\Program Files\Python311
    echo.
    echo PROXIMO PASSO:
    echo Execute: INSTALAR_TUDO.bat
    echo.
) else (
    echo ========================================
    echo   ERRO NA INSTALACAO
    echo ========================================
    echo.
    echo Python nao foi instalado corretamente.
    echo.
    echo DIAGNOSTICO:
    echo 1. Verifique o log: python_install.log
    echo 2. Tente instalar manualmente
    echo 3. Baixe de: https://www.python.org/downloads/
    echo.
    echo DICA:
    echo Durante instalacao manual, marque:
    echo - "Add Python to PATH"
    echo - "Install for all users"
    echo.
)

pause
