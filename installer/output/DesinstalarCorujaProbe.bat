@echo off
REM Desinstalador Coruja Monitor Probe

echo.
echo ========================================
echo   DESINSTALAR CORUJA MONITOR PROBE
echo ========================================
echo.

net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERRO] Execute como Administrador!
    pause
    exit /b 1
)

echo Parando servico...
sc stop CorujaProbe >nul 2>&1
sc delete CorujaProbe >nul 2>&1

echo Removendo arquivos...
rmdir /s /q "%ProgramFiles%\CorujaMonitor" 2>nul

echo Removendo atalhos...
del "%ProgramData%\Microsoft\Windows\Start Menu\Programs\Configurar Coruja Probe.lnk" >nul 2>&1
del "%USERPROFILE%\Desktop\Configurar Coruja Probe.lnk" >nul 2>&1

echo Removendo registro...
reg delete "HKLM\SOFTWARE\CorujaMonitor" /f >nul 2>&1

echo.
echo Desinstalacao concluida!
pause
