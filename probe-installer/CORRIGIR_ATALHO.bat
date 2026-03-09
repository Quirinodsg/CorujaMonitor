@echo off
REM ========================================
REM CORRIGIR ATALHO CONFIGURAR PROBE
REM ========================================

echo.
echo ========================================
echo   CORRIGIR ATALHO
echo ========================================
echo.

REM Verificar admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERRO] Execute como Administrador!
    pause
    exit /b 1
)

set "INSTALL_DIR=%ProgramFiles%\CorujaMonitor\Probe"

echo [1/3] Verificando instalacao...
if not exist "%INSTALL_DIR%\configurar_probe.bat" (
    echo [ERRO] Probe nao encontrada em: %INSTALL_DIR%
    echo Execute INSTALAR_TUDO.bat primeiro
    pause
    exit /b 1
)

echo [2/3] Removendo atalhos antigos...
del "%PUBLIC%\Desktop\Configurar Coruja Probe.lnk" >nul 2>&1
del "%USERPROFILE%\Desktop\Configurar Coruja Probe.lnk" >nul 2>&1
del "%ProgramData%\Microsoft\Windows\Start Menu\Programs\Configurar Coruja Probe.lnk" >nul 2>&1

echo [3/3] Criando atalhos corretos...

REM Atalho Desktop (usuário atual)
powershell -ExecutionPolicy Bypass -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Configurar Coruja Probe.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\configurar_probe.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = 'Configurar Coruja Monitor Probe'; $Shortcut.Save()"

REM Atalho Menu Iniciar
powershell -ExecutionPolicy Bypass -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%ProgramData%\Microsoft\Windows\Start Menu\Programs\Configurar Coruja Probe.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\configurar_probe.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = 'Configurar conexao com servidor'; $Shortcut.Save()"

echo.
echo ========================================
echo   ATALHOS CORRIGIDOS!
echo ========================================
echo.
echo Agora o atalho "Configurar Coruja Probe" deve funcionar!
echo.
pause
