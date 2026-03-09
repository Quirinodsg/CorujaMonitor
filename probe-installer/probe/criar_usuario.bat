@echo off
REM ========================================
REM Criar Usuario para Monitoramento
REM Execute DEPOIS do install_sem_usuario.bat
REM ========================================

title Criar Usuario MonitorUser

echo.
echo ========================================
echo   CRIAR USUARIO PARA MONITORAMENTO
echo ========================================
echo.
echo Este script cria o usuario MonitorUser
echo e atualiza o arquivo wmi_credentials.json
echo.
echo Pressione qualquer tecla para continuar...
pause >nul

REM ========================================
REM Verificar Admin
REM ========================================
cls
echo.
echo [1/5] Verificando privilegios...
net session >nul 2>&1
if %errorLevel% neq 0 (
    color 0C
    echo.
    echo [ERRO] Execute como Administrador!
    echo.
    echo Pressione qualquer tecla para sair...
    pause >nul
    exit
)
echo [OK] Privilegios verificados
timeout /t 2 >nul

REM ========================================
REM Criar Usuario
REM ========================================
cls
echo.
echo [2/5] Criando usuario MonitorUser...
set "PASSWORD=Monitor@%RANDOM%%RANDOM%"
net user MonitorUser "%PASSWORD%" /add /comment:"Usuario para monitoramento Coruja" /passwordchg:no /expires:never /active:yes >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Usuario criado com sucesso
) else (
    echo [INFO] Usuario ja existe
    echo.
    set /p PASSWORD="Digite a senha do usuario existente: "
)
wmic useraccount where "name='MonitorUser'" set PasswordExpires=FALSE >nul 2>&1
timeout /t 2 >nul

REM ========================================
REM Adicionar Grupos
REM ========================================
cls
echo.
echo [3/5] Adicionando aos grupos...
net localgroup "Administradores" MonitorUser /add >nul 2>&1
net localgroup "Administrators" MonitorUser /add >nul 2>&1
net localgroup "Usuarios de Gerenciamento Remoto" MonitorUser /add >nul 2>&1
net localgroup "Remote Management Users" MonitorUser /add >nul 2>&1
net localgroup "Usuarios do Monitor de Desempenho" MonitorUser /add >nul 2>&1
net localgroup "Performance Monitor Users" MonitorUser /add >nul 2>&1
net localgroup "Usuarios COM Distribuidos" MonitorUser /add >nul 2>&1
net localgroup "Distributed COM Users" MonitorUser /add >nul 2>&1
echo [OK] Grupos configurados
timeout /t 2 >nul

REM ========================================
REM Atualizar Credenciais
REM ========================================
cls
echo.
echo [4/5] Atualizando wmi_credentials.json...
for /f "tokens=*" %%a in ('hostname') do set HOSTNAME=%%a
(
echo {
echo   "%HOSTNAME%": {
echo     "username": "MonitorUser",
echo     "password": "%PASSWORD%",
echo     "domain": "%HOSTNAME%"
echo   }
echo }
) > wmi_credentials.json
echo [OK] Arquivo atualizado
timeout /t 2 >nul

REM ========================================
REM Testar
REM ========================================
cls
echo.
echo [5/5] Testando configuracao...
wmic computersystem get name,domain >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] WMI funcionando
) else (
    echo [AVISO] Erro ao testar WMI
)
timeout /t 2 >nul

REM ========================================
REM Concluido
REM ========================================
cls
color 0A
echo.
echo ========================================
echo   USUARIO CRIADO COM SUCESSO!
echo ========================================
echo.
echo Credenciais:
echo   Usuario: MonitorUser
echo   Senha: %PASSWORD%
echo   Computador: %HOSTNAME%
echo.
echo IMPORTANTE: Anote estas credenciais!
echo.
echo ========================================
echo   ARQUIVO ATUALIZADO
echo ========================================
echo.
echo wmi_credentials.json:
type wmi_credentials.json
echo.
echo ========================================
echo   PROXIMOS PASSOS
echo ========================================
echo.
echo 1. Instale Python (se ainda nao instalou):
echo    https://www.python.org/downloads/
echo.
echo 2. Instale dependencias:
echo    pip install -r requirements.txt
echo.
echo 3. Inicie a probe:
echo    python probe_core.py
echo.
echo 4. Verifique no dashboard (aguarde 2-3 minutos)
echo.
echo ========================================
echo.
echo Pressione qualquer tecla para sair...
pause >nul
exit
