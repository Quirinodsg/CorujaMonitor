@echo off
REM ========================================
REM Instalador com Elevacao Automatica
REM ========================================

REM Verificar se ja esta como admin
net session >nul 2>&1
if %errorLevel% equ 0 goto ADMIN_OK

REM Se nao for admin, pedir elevacao
echo ========================================
echo ELEVACAO DE PRIVILEGIOS NECESSARIA
echo ========================================
echo.
echo Este instalador precisa de privilegios de administrador.
echo Uma janela UAC vai aparecer - clique em SIM.
echo.
pause

REM Executar como admin
powershell -Command "Start-Process '%~f0' -Verb RunAs"
exit

:ADMIN_OK
REM Agora sim, executar o instalador
cd /d "%~dp0"
call install.bat
