@echo off
REM ========================================
REM INSTALADOR COMPLETO CORUJA MONITOR PROBE
REM Detecta Python automaticamente
REM Versao: 2.0.0
REM ========================================

color 0B
echo.
echo ========================================
echo   CORUJA MONITOR PROBE
echo   Instalador Completo v2.0
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
REM DETECTAR PYTHON AUTOMATICAMENTE
REM ========================================

echo [1/5] Detectando Python...
echo.

set "PYTHON_EXE="
set "PYTHON_VERSION="

REM Tentar 1: Python no PATH
python --version >nul 2>&1
if %errorLevel% equ 0 (
    set "PYTHON_EXE=python"
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set "PYTHON_VERSION=%%i"
    echo [OK] Python encontrado no PATH
    goto :python_found
)

REM Tentar 2: Python 3.11 (Program Files)
if exist "C:\Program Files\Python311\python.exe" (
    set "PYTHON_EXE=C:\Program Files\Python311\python.exe"
    for /f "tokens=2" %%i in ('"C:\Program Files\Python311\python.exe" --version 2^>^&1') do set "PYTHON_VERSION=%%i"
    echo [OK] Python 3.11 encontrado
    goto :python_found
)

REM Tentar 3: Python 3.10 (Program Files)
if exist "C:\Program Files\Python310\python.exe" (
    set "PYTHON_EXE=C:\Program Files\Python310\python.exe"
    for /f "tokens=2" %%i in ('"C:\Program Files\Python310\python.exe" --version 2^>^&1') do set "PYTHON_VERSION=%%i"
    echo [OK] Python 3.10 encontrado
    goto :python_found
)

REM Tentar 4: Python 3.12 (Program Files)
if exist "C:\Program Files\Python312\python.exe" (
    set "PYTHON_EXE=C:\Program Files\Python312\python.exe"
    for /f "tokens=2" %%i in ('"C:\Program Files\Python312\python.exe" --version 2^>^&1') do set "PYTHON_VERSION=%%i"
    echo [OK] Python 3.12 encontrado
    goto :python_found
)

REM Tentar 5: Microsoft Store Python
if exist "%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe" (
    "%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe" --version >nul 2>&1
    if %errorLevel% equ 0 (
        set "PYTHON_EXE=%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe"
        for /f "tokens=2" %%i in ('"%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe" --version 2^>^&1') do set "PYTHON_VERSION=%%i"
        echo [OK] Python Microsoft Store encontrado
        goto :python_found
    )
)

REM Python NAO encontrado
color 0C
echo ========================================
echo [ERRO] Python nao encontrado!
echo ========================================
echo.
echo SOLUCAO RAPIDA:
echo.
echo 1. Abra a Microsoft Store
echo 2. Procure por "Python 3.11"
echo 3. Clique em "Obter" ou "Instalar"
echo 4. Aguarde a instalacao (1-2 minutos)
echo 5. Execute este instalador novamente
echo.
echo OU
echo.
echo Baixe manualmente de:
echo https://www.python.org/downloads/
echo.
echo ========================================
echo.
pause
exit /b 1

:python_found
echo Python: %PYTHON_EXE%
echo Versao: %PYTHON_VERSION%
echo.

REM ========================================
REM INSTALAR DEPENDENCIAS
REM ========================================

echo [2/5] Instalando dependencias Python...
echo.
echo Aguarde 1-3 minutos...
echo NAO FECHE ESTA JANELA!
echo.

echo [1/7] Atualizando pip...
"%PYTHON_EXE%" -m pip install --quiet --upgrade pip 2>nul

echo [2/7] Instalando psutil...
"%PYTHON_EXE%" -m pip install --quiet psutil 2>nul

echo [3/7] Instalando httpx...
"%PYTHON_EXE%" -m pip install --quiet httpx 2>nul

echo [4/7] Instalando pywin32...
"%PYTHON_EXE%" -m pip install --quiet pywin32 2>nul

echo [5/7] Instalando pysnmp...
"%PYTHON_EXE%" -m pip install --quiet pysnmp 2>nul

echo [6/7] Instalando pyyaml...
"%PYTHON_EXE%" -m pip install --quiet pyyaml 2>nul

echo [7/7] Instalando wmi...
"%PYTHON_EXE%" -m pip install --quiet wmi 2>nul

echo.
echo Verificando instalacao...
"%PYTHON_EXE%" -c "import psutil, httpx, win32api, pysnmp, yaml" >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Todas as dependencias instaladas
) else (
    color 0E
    echo [AVISO] Algumas dependencias podem estar faltando
    echo Continuando instalacao...
)

REM ========================================
REM COPIAR ARQUIVOS
REM ========================================

echo.
echo [3/5] Instalando arquivos da Probe...
echo.

set "INSTALL_DIR=%ProgramFiles%\CorujaMonitor\Probe"

echo Destino: %INSTALL_DIR%
echo.

mkdir "%INSTALL_DIR%" 2>nul
mkdir "%INSTALL_DIR%\collectors" 2>nul
mkdir "%INSTALL_DIR%\logs" 2>nul

if not exist "probe\probe_core.py" (
    color 0C
    echo [ERRO] Arquivos da probe nao encontrados!
    echo.
    echo Execute este instalador na pasta raiz do projeto
    echo onde existe a pasta "probe"
    echo.
    pause
    exit /b 1
)

echo Copiando arquivos Python...
xcopy /E /I /Y /Q "probe\*.py" "%INSTALL_DIR%\" >nul 2>&1
xcopy /E /I /Y /Q "probe\collectors\*.py" "%INSTALL_DIR%\collectors\" >nul 2>&1

echo Copiando scripts BAT...
xcopy /E /I /Y /Q "probe\*.bat" "%INSTALL_DIR%\" >nul 2>&1

echo Copiando configuracao...
copy /Y "probe\config.yaml" "%INSTALL_DIR%\" >nul 2>&1
copy /Y "probe\requirements.txt" "%INSTALL_DIR%\" >nul 2>&1

echo Copiando documentacao...
if exist "probe\*.txt" xcopy /E /I /Y /Q "probe\*.txt" "%INSTALL_DIR%\" >nul 2>&1
if exist "probe\*.md" xcopy /E /I /Y /Q "probe\*.md" "%INSTALL_DIR%\" >nul 2>&1

echo [OK] Arquivos instalados

REM ========================================
REM CONFIGURAR PYTHON PATH
REM ========================================

echo.
echo [4/5] Configurando Python...

REM Salvar caminho do Python no registro
reg add "HKLM\SOFTWARE\CorujaMonitor\Probe" /v PythonPath /t REG_SZ /d "%PYTHON_EXE%" /f >nul 2>&1

REM Criar script de inicializacao com Python correto
echo @echo off > "%INSTALL_DIR%\iniciar_probe.bat"
echo REM Gerado automaticamente pelo instalador >> "%INSTALL_DIR%\iniciar_probe.bat"
echo "%PYTHON_EXE%" "%INSTALL_DIR%\probe_core.py" >> "%INSTALL_DIR%\iniciar_probe.bat"

echo [OK] Python configurado

REM ========================================
REM FIREWALL E ATALHOS
REM ========================================

echo.
echo [5/5] Finalizando instalacao...

REM Firewall WMI
netsh advfirewall firewall set rule group="Windows Management Instrumentation (WMI)" new enable=yes >nul 2>&1

REM Atalho Desktop
powershell -ExecutionPolicy Bypass -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Configurar Coruja Probe.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\configurar_probe.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Save()" >nul 2>&1

REM Atalhos Menu Iniciar
powershell -ExecutionPolicy Bypass -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%ProgramData%\Microsoft\Windows\Start Menu\Programs\Configurar Coruja Probe.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\configurar_probe.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Save()" >nul 2>&1

powershell -ExecutionPolicy Bypass -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%ProgramData%\Microsoft\Windows\Start Menu\Programs\Instalar Servico Coruja.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\install_service.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Save()" >nul 2>&1

REM Registro
reg add "HKLM\SOFTWARE\CorujaMonitor\Probe" /v InstallPath /t REG_SZ /d "%INSTALL_DIR%" /f >nul 2>&1
reg add "HKLM\SOFTWARE\CorujaMonitor\Probe" /v Version /t REG_SZ /d "2.0.0" /f >nul 2>&1
reg add "HKLM\SOFTWARE\CorujaMonitor\Probe" /v InstallDate /t REG_SZ /d "%DATE% %TIME%" /f >nul 2>&1

echo [OK] Instalacao finalizada

REM ========================================
REM CONCLUSAO
REM ========================================

echo.
color 0A
echo ========================================
echo   INSTALACAO CONCLUIDA COM SUCESSO!
echo ========================================
echo.
echo Python: %PYTHON_VERSION%
echo Local: %PYTHON_EXE%
echo.
echo Probe instalada em:
echo %INSTALL_DIR%
echo.
echo ========================================
echo   PROXIMOS PASSOS
echo ========================================
echo.
echo 1. CONFIGURAR PROBE:
echo.
echo    No Desktop, clique duas vezes em:
echo    "Configurar Coruja Probe"
echo.
echo    Digite:
echo    - IP do servidor: 192.168.31.161
echo    - Token: (fornecido pelo admin)
echo.
echo 2. INSTALAR COMO SERVICO:
echo.
echo    Menu Iniciar ^> Procure:
echo    "Instalar Servico Coruja"
echo.
echo    Isso faz a probe iniciar automaticamente
echo.
echo ========================================
echo.
pause
