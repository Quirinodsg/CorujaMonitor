@echo off
REM ========================================
REM INSTALADOR CORUJA MONITOR PROBE v1.0.0
REM ========================================

echo.
echo ========================================
echo   CORUJA MONITOR PROBE - INSTALACAO
echo ========================================
echo.

REM Verificar admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERRO] Execute como Administrador!
    echo.
    echo Clique direito e selecione:
    echo "Executar como Administrador"
    echo.
    pause
    exit /b 1
)

echo [1/8] Criando diretorios...
set "INSTALL_DIR=%ProgramFiles%\CorujaMonitor\Probe"
mkdir "%INSTALL_DIR%" 2>nul
mkdir "%INSTALL_DIR%\collectors" 2>nul
mkdir "%INSTALL_DIR%\logs" 2>nul

echo [2/8] Copiando arquivos...
xcopy /E /I /Y /Q "probe\*.py" "%INSTALL_DIR%\" >nul 2>&1
xcopy /E /I /Y /Q "probe\*.bat" "%INSTALL_DIR%\" >nul 2>&1
xcopy /E /I /Y /Q "probe\*.txt" "%INSTALL_DIR%\" >nul 2>&1
xcopy /E /I /Y /Q "probe\collectors\*.py" "%INSTALL_DIR%\collectors\" >nul 2>&1

echo [3/8] Verificando Python...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo    [AVISO] Python nao encontrado!
    echo    Instale Python 3.8+ de: https://www.python.org/downloads/
    echo    Ou continue e instale depois
    pause
)

echo [4/8] Instalando dependencias...
python -m pip install --quiet psutil httpx pywin32 pysnmp pyyaml 2>nul

echo [5/8] Criando atalhos...
powershell -ExecutionPolicy Bypass -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%ProgramData%\Microsoft\Windows\Start Menu\Programs\Configurar Coruja Probe.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\configurar_probe.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Save()"

powershell -ExecutionPolicy Bypass -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Configurar Coruja Probe.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\configurar_probe.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Save()"

echo [6/8] Configurando firewall...
netsh advfirewall firewall set rule group="Windows Management Instrumentation (WMI)" new enable=yes >nul 2>&1

echo [7/8] Registrando instalacao...
reg add "HKLM\SOFTWARE\CorujaMonitor\Probe" /v InstallPath /t REG_SZ /d "%INSTALL_DIR%" /f >nul 2>&1
reg add "HKLM\SOFTWARE\CorujaMonitor\Probe" /v Version /t REG_SZ /d "1.0.0" /f >nul 2>&1

echo [8/8] Concluindo...

echo.
echo ========================================
echo   INSTALACAO CONCLUIDA!
echo ========================================
echo.
echo Instalado em: %INSTALL_DIR%
echo.
echo PROXIMOS PASSOS:
echo 1. Configure: "Configurar Coruja Probe" (Desktop)
echo 2. Digite IP do servidor: 192.168.31.161
echo 3. Digite o token da probe
echo 4. Instale como servico (opcional)
echo.
pause
