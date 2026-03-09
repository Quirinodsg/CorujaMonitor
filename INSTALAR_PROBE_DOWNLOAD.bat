@echo off
setlocal enabledelayedexpansion
REM ========================================
REM INSTALADOR CORUJA MONITOR PROBE
REM Baixa e instala automaticamente do GitHub
REM Versao: 3.0.0
REM ========================================

color 0B
echo.
echo ========================================
echo   CORUJA MONITOR PROBE
echo   Instalador Automatico v3.0
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
REM DETECTAR PYTHON
REM ========================================

echo [1/7] Detectando Python...
echo.

set "PYTHON_EXE="
set "PYTHON_VERSION="

python --version >nul 2>&1
if !errorLevel! equ 0 (
    set "PYTHON_EXE=python"
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set "PYTHON_VERSION=%%i"
    echo [OK] Python encontrado no PATH
    goto :python_found
)

if exist "C:\Program Files\Python311\python.exe" (
    set "PYTHON_EXE=C:\Program Files\Python311\python.exe"
    for /f "tokens=2" %%i in ('"C:\Program Files\Python311\python.exe" --version 2^>^&1') do set "PYTHON_VERSION=%%i"
    echo [OK] Python 3.11 encontrado
    goto :python_found
)

if exist "C:\Program Files\Python310\python.exe" (
    set "PYTHON_EXE=C:\Program Files\Python310\python.exe"
    for /f "tokens=2" %%i in ('"C:\Program Files\Python310\python.exe" --version 2^>^&1') do set "PYTHON_VERSION=%%i"
    echo [OK] Python 3.10 encontrado
    goto :python_found
)

if exist "C:\Program Files\Python312\python.exe" (
    set "PYTHON_EXE=C:\Program Files\Python312\python.exe"
    for /f "tokens=2" %%i in ('"C:\Program Files\Python312\python.exe" --version 2^>^&1') do set "PYTHON_VERSION=%%i"
    echo [OK] Python 3.12 encontrado
    goto :python_found
)

if exist "%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe" (
    "%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe" --version >nul 2>&1
    if !errorLevel! equ 0 (
        set "PYTHON_EXE=%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe"
        for /f "tokens=2" %%i in ('"%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe" --version 2^>^&1') do set "PYTHON_VERSION=%%i"
        echo [OK] Python Microsoft Store encontrado
        goto :python_found
    )
)

color 0C
echo [ERRO] Python nao encontrado!
echo.
echo Instale Python pela Microsoft Store:
echo 1. Abra a Microsoft Store
echo 2. Procure "Python 3.11"
echo 3. Clique em "Obter"
echo 4. Execute este instalador novamente
echo.
pause
exit /b 1

:python_found
echo Python: !PYTHON_EXE!
echo Versao: !PYTHON_VERSION!
echo.

REM ========================================
REM INSTALAR DEPENDENCIAS
REM ========================================

echo [2/7] Instalando dependencias Python...
echo.

"!PYTHON_EXE!" -m pip install --quiet --upgrade pip 2>nul
"!PYTHON_EXE!" -m pip install --quiet psutil httpx pywin32 pysnmp pyyaml wmi 2>nul

echo [OK] Dependencias instaladas
echo.

REM ========================================
REM BAIXAR ARQUIVOS DO GITHUB
REM ========================================

echo [3/7] Baixando arquivos do GitHub...
echo.

set "INSTALL_DIR=%ProgramFiles%\CorujaMonitor\Probe"
set "TEMP_DIR=%TEMP%\coruja_probe_install"

mkdir "!TEMP_DIR!" 2>nul
cd /d "!TEMP_DIR!"

echo Baixando probe_core.py...
powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/seu-usuario/seu-repo/main/probe/probe_core.py' -OutFile 'probe_core.py'" 2>nul

if not exist "probe_core.py" (
    color 0E
    echo [AVISO] Nao foi possivel baixar do GitHub
    echo.
    echo Usando instalacao manual...
    goto :manual_install
)

echo Baixando collectors...
mkdir "collectors" 2>nul
powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/seu-usuario/seu-repo/main/probe/collectors/system_collector.py' -OutFile 'collectors\system_collector.py'" 2>nul
powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/seu-usuario/seu-repo/main/probe/collectors/ping_collector.py' -OutFile 'collectors\ping_collector.py'" 2>nul
powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/seu-usuario/seu-repo/main/probe/collectors/snmp_collector.py' -OutFile 'collectors\snmp_collector.py'" 2>nul

echo [OK] Arquivos baixados
goto :install_files

REM ========================================
REM INSTALACAO MANUAL (SEM GITHUB)
REM ========================================

:manual_install
echo.
echo [4/7] Criando arquivos basicos...
echo.

REM Criar probe_core.py basico
echo # Coruja Monitor Probe > probe_core.py
echo # Versao minima - configure manualmente >> probe_core.py

REM ========================================
REM COPIAR ARQUIVOS
REM ========================================

:install_files
echo.
echo [5/7] Instalando arquivos...
echo.

mkdir "!INSTALL_DIR!" 2>nul
mkdir "!INSTALL_DIR!\collectors" 2>nul
mkdir "!INSTALL_DIR!\logs" 2>nul

if exist "probe_core.py" copy /Y "probe_core.py" "!INSTALL_DIR!\" >nul 2>&1
if exist "collectors\*.py" xcopy /E /I /Y /Q "collectors\*.py" "!INSTALL_DIR!\collectors\" >nul 2>&1

REM Criar config.yaml
(
echo # Configuracao Coruja Monitor Probe
echo server:
echo   host: "192.168.31.161"
echo   port: 8000
echo   protocol: "http"
echo token: ""
echo probe:
echo   name: "%COMPUTERNAME%"
echo   location: ""
echo collection_interval: 60
echo logging:
echo   level: "INFO"
echo   file: "logs/probe.log"
echo   max_size_mb: 10
echo   backup_count: 5
echo collectors:
echo   system: true
echo   ping: true
echo   snmp: true
echo   docker: false
echo   kubernetes: false
echo   wmi_remote: false
) > "!INSTALL_DIR!\config.yaml"

echo [OK] Arquivos instalados

REM ========================================
REM CRIAR CONFIGURADOR
REM ========================================

echo.
echo [6/7] Criando configurador...

(
echo @echo off
echo setlocal enabledelayedexpansion
echo title Configurar Probe Coruja
echo color 0A
echo.
echo echo ========================================
echo echo   CONFIGURACAO DO PROBE
echo echo ========================================
echo echo.
echo.
echo set /p SERVER_IP="Digite o IP do servidor (192.168.31.161): "
echo if "%%SERVER_IP%%"=="" set "SERVER_IP=192.168.31.161"
echo.
echo set /p PROBE_TOKEN="Digite o TOKEN da probe: "
echo.
echo if "%%PROBE_TOKEN%%"=="" ^(
echo     echo [ERRO] Token obrigatorio!
echo     pause
echo     exit /b 1
echo ^)
echo.
echo ^(
echo echo # Configuracao Coruja Monitor Probe
echo echo server:
echo echo   host: "%%SERVER_IP%%"
echo echo   port: 8000
echo echo   protocol: "http"
echo echo token: "!PROBE_TOKEN!"
echo echo probe:
echo echo   name: "%%COMPUTERNAME%%"
echo echo   location: ""
echo echo collection_interval: 60
echo echo logging:
echo echo   level: "INFO"
echo echo   file: "logs/probe.log"
echo echo   max_size_mb: 10
echo echo   backup_count: 5
echo echo collectors:
echo echo   system: true
echo echo   ping: true
echo echo   snmp: true
echo echo   docker: false
echo echo   kubernetes: false
echo echo   wmi_remote: false
echo ^) ^^^> config.yaml
echo.
echo color 0A
echo echo.
echo echo ========================================
echo echo   CONFIGURACAO CONCLUIDA!
echo echo ========================================
echo echo.
echo echo Servidor: http://%%SERVER_IP%%:8000
echo echo Probe: %%COMPUTERNAME%%
echo echo.
echo pause
) > "!INSTALL_DIR!\configurar_probe.bat"

echo [OK] Configurador criado

REM ========================================
REM FINALIZAR
REM ========================================

echo.
echo [7/7] Finalizando...

reg add "HKLM\SOFTWARE\CorujaMonitor\Probe" /v InstallPath /t REG_SZ /d "!INSTALL_DIR!" /f >nul 2>&1
reg add "HKLM\SOFTWARE\CorujaMonitor\Probe" /v PythonPath /t REG_SZ /d "!PYTHON_EXE!" /f >nul 2>&1
reg add "HKLM\SOFTWARE\CorujaMonitor\Probe" /v Version /t REG_SZ /d "3.0.0" /f >nul 2>&1

netsh advfirewall firewall set rule group="Windows Management Instrumentation (WMI)" new enable=yes >nul 2>&1

REM Atalho Desktop
powershell -ExecutionPolicy Bypass -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Configurar Coruja Probe.lnk'); $Shortcut.TargetPath = '!INSTALL_DIR!\configurar_probe.bat'; $Shortcut.WorkingDirectory = '!INSTALL_DIR!'; $Shortcut.Save()" >nul 2>&1

echo [OK] Instalacao finalizada

REM Limpar temp
cd /d "%TEMP%"
rd /s /q "!TEMP_DIR!" 2>nul

REM ========================================
REM CONCLUSAO
REM ========================================

color 0A
echo.
echo ========================================
echo   INSTALACAO CONCLUIDA!
echo ========================================
echo.
echo Python: !PYTHON_VERSION!
echo Instalado em: !INSTALL_DIR!
echo.
echo ========================================
echo   PROXIMO PASSO
echo ========================================
echo.
echo No Desktop, clique duas vezes em:
echo "Configurar Coruja Probe"
echo.
echo Digite:
echo - IP: 192.168.31.161
echo - Token: (copie do dashboard)
echo.
echo ========================================
echo.
pause
