@echo off
REM ========================================
REM DESINSTALADOR CORUJA MONITOR PROBE
REM ========================================

echo.
echo ========================================
echo   CORUJA MONITOR PROBE - DESINSTALACAO
echo ========================================
echo.

REM Verificar admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERRO] Execute como Administrador!
    echo.
    pause
    exit /b 1
)

set "INSTALL_DIR=%ProgramFiles%\CorujaMonitor\Probe"

echo ATENCAO: Isso vai remover completamente a Probe!
echo.
echo Instalacao: %INSTALL_DIR%
echo.
echo Pressione qualquer tecla para continuar ou CTRL+C para cancelar...
pause >nul

echo.
echo [1/5] Parando servico...
sc stop CorujaProbe >nul 2>&1
timeout /t 2 /nobreak >nul

echo [2/5] Removendo servico...
sc delete CorujaProbe >nul 2>&1

echo [3/5] Removendo arquivos...
if exist "%INSTALL_DIR%" (
    rmdir /S /Q "%INSTALL_DIR%" >nul 2>&1
    echo    [OK] Arquivos removidos
) else (
    echo    [INFO] Pasta nao encontrada
)

echo [4/5] Removendo atalhos...
del "%ProgramData%\Microsoft\Windows\Start Menu\Programs\Configurar Coruja Probe.lnk" >nul 2>&1
del "%ProgramData%\Microsoft\Windows\Start Menu\Programs\Instalar Servico Coruja.lnk" >nul 2>&1
del "%PUBLIC%\Desktop\Configurar Coruja Probe.lnk" >nul 2>&1
del "%USERPROFILE%\Desktop\Configurar Coruja Probe.lnk" >nul 2>&1

echo [5/5] Removendo registro...
reg delete "HKLM\SOFTWARE\CorujaMonitor" /f >nul 2>&1

echo.
echo ========================================
echo   DESINSTALACAO CONCLUIDA!
echo ========================================
echo.
echo NOTA: Python e dependencias NAO foram removidos
echo      (podem ser usados por outros programas)
echo.
pause
