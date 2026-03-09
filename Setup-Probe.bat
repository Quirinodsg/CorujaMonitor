@echo off
REM ========================================
REM SETUP CORUJA MONITOR PROBE
REM Instala arquivos da Probe
REM Versao: 1.0.0
REM ========================================

echo.
echo ========================================
echo   SETUP CORUJA MONITOR PROBE
echo   Instalador de Arquivos
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

echo [1/6] Verificando Python...
echo.

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

color 0C
echo [ERRO] Python nao encontrado!
echo.
echo Execute primeiro: Setup-Python.bat
echo.
pause
exit /b 1

:check_deps
echo [OK] Python encontrado:
"%PYTHON_EXE%" --version
echo.

REM ========================================
REM VERIFICAR DEPENDENCIAS
REM ========================================

echo [2/6] Verificando dependencias...
echo.

"%PYTHON_EXE%" -c "import psutil, httpx, win32api, pysnmp, yaml" >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Todas as dependencias instaladas
) else (
    color 0E
    echo [AVISO] Algumas dependencias faltando
    echo.
    echo Execute primeiro: Setup-Python.bat
    echo.
    pause
    exit /b 1
)

REM ========================================
REM COPIAR ARQUIVOS
REM ========================================

echo.
echo [3/6] Copiando arquivos da Probe...
echo.

set "INSTALL_DIR=%ProgramFiles%\CorujaMonitor\Probe"

echo Destino: %INSTALL_DIR%
echo.

mkdir "%INSTALL_DIR%" 2>nul
mkdir "%INSTALL_DIR%\collectors" 2>nul
mkdir "%INSTALL_DIR%\logs" 2>nul

echo Copiando arquivos Python...
xcopy /E /I /Y /Q "probe\*.py" "%INSTALL_DIR%\" >nul 2>&1
xcopy /E /I /Y /Q "probe\collectors\*.py" "%INSTALL_DIR%\collectors\" >nul 2>&1

echo Copiando scripts BAT...
xcopy /E /I /Y /Q "probe\*.bat" "%INSTALL_DIR%\" >nul 2>&1

echo Copiando documentacao...
xcopy /E /I /Y /Q "probe\*.txt" "%INSTALL_DIR%\" >nul 2>&1
xcopy /E /I /Y /Q "probe\*.md" "%INSTALL_DIR%\" >nul 2>&1
copy /Y "probe\requirements.txt" "%INSTALL_DIR%\" >nul 2>&1
copy /Y "probe\config.yaml" "%INSTALL_DIR%\" >nul 2>&1

echo [OK] Arquivos copiados

REM ========================================
REM FIREWALL
REM ========================================

echo.
echo [4/6] Configurando firewall (WMI)...

netsh advfirewall firewall set rule group="Windows Management Instrumentation (WMI)" new enable=yes >nul 2>&1
echo [OK] Firewall configurado

REM ========================================
REM ATALHOS
REM ========================================

echo.
echo [5/6] Criando atalhos...

REM Desktop
powershell -ExecutionPolicy Bypass -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Configurar Coruja Probe.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\configurar_probe.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Save()" >nul 2>&1

REM Menu Iniciar
powershell -ExecutionPolicy Bypass -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%ProgramData%\Microsoft\Windows\Start Menu\Programs\Configurar Coruja Probe.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\configurar_probe.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Save()" >nul 2>&1

powershell -ExecutionPolicy Bypass -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%ProgramData%\Microsoft\Windows\Start Menu\Programs\Instalar Servico Coruja.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\install_service.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Save()" >nul 2>&1

powershell -ExecutionPolicy Bypass -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%ProgramData%\Microsoft\Windows\Start Menu\Programs\Diagnostico Coruja Probe.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\diagnostico_probe.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Save()" >nul 2>&1

echo [OK] Atalhos criados

REM ========================================
REM REGISTRO
REM ========================================

echo.
echo [6/6] Registrando instalacao...

reg add "HKLM\SOFTWARE\CorujaMonitor\Probe" /v InstallPath /t REG_SZ /d "%INSTALL_DIR%" /f >nul 2>&1
reg add "HKLM\SOFTWARE\CorujaMonitor\Probe" /v Version /t REG_SZ /d "1.0.0" /f >nul 2>&1
reg add "HKLM\SOFTWARE\CorujaMonitor\Probe" /v InstallDate /t REG_SZ /d "%DATE% %TIME%" /f >nul 2>&1

echo [OK] Instalacao registrada

REM ========================================
REM CONCLUSAO
REM ========================================

echo.
color 0A
echo ========================================
echo   INSTALACAO CONCLUIDA COM SUCESSO!
echo ========================================
echo.
echo Instalado em: %INSTALL_DIR%
echo.
echo Atalhos criados:
echo   - Desktop: Configurar Coruja Probe
echo   - Menu Iniciar: Configurar Coruja Probe
echo   - Menu Iniciar: Instalar Servico Coruja
echo   - Menu Iniciar: Diagnostico Coruja Probe
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
echo    - Token da probe: (fornecido pelo admin)
echo.
echo 2. INSTALAR COMO SERVICO (Opcional):
echo.
echo    Menu Iniciar ^> Procure por:
echo    "Instalar Servico Coruja"
echo.
echo    Isso faz a probe iniciar automaticamente
echo    com o Windows
echo.
echo 3. VERIFICAR LOGS (se necessario):
echo.
echo    Pasta: %INSTALL_DIR%\logs
echo.
echo ========================================
echo.
pause
