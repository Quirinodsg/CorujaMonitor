@echo off
REM ========================================
REM Instalador Universal - Coruja Monitor
REM Todas as opcoes em um unico instalador
REM ========================================

:MENU
cls
echo ========================================
echo   CORUJA MONITOR - INSTALADOR UNIVERSAL
echo ========================================
echo.
echo Escolha o tipo de instalacao:
echo.
echo 1. Workgroup (Sem dominio)
echo    - Maquinas em workgroup
echo    - Rede local simples
echo    - Usuario local
echo.
echo 2. Entra ID / Azure AD
echo    - Maquinas joined ao Entra ID
echo    - Microsoft 365 / Azure
echo    - Usuario local para WMI
echo.
echo 3. Active Directory (Dominio)
echo    - Dominio AD tradicional
echo    - On-premises
echo    - Usuario de dominio
echo.
echo 4. WMI Remoto (Sem probe)
echo    - Apenas configurar WMI remoto
echo    - Nao instala probe
echo    - Para monitoramento centralizado
echo.
echo 5. Detectar Automaticamente
echo    - Sistema detecta o tipo
echo    - Recomendado se nao souber
echo.
echo 0. Sair
echo.
echo ========================================
set /p OPCAO="Digite sua opcao (0-5): "

if "%OPCAO%"=="1" goto WORKGROUP
if "%OPCAO%"=="2" goto ENTRAID
if "%OPCAO%"=="3" goto DOMAIN
if "%OPCAO%"=="4" goto REMOTE
if "%OPCAO%"=="5" goto AUTO
if "%OPCAO%"=="0" goto END

echo.
echo Opcao invalida! Tente novamente.
timeout /t 2 >nul
goto MENU

REM ========================================
REM OPCAO 1: WORKGROUP
REM ========================================
:WORKGROUP
cls
echo ========================================
echo INSTALACAO: WORKGROUP (SEM DOMINIO)
echo ========================================
echo.
call :CHECK_ADMIN
call :INSTALL_BASE "WORKGROUP"
goto END

REM ========================================
REM OPCAO 2: ENTRA ID
REM ========================================
:ENTRAID
cls
echo ========================================
echo INSTALACAO: ENTRA ID (AZURE AD)
echo ========================================
echo.
call :CHECK_ADMIN
call :DETECT_ENTRAID
call :INSTALL_BASE "ENTRAID"
goto END

REM ========================================
REM OPCAO 3: ACTIVE DIRECTORY
REM ========================================
:DOMAIN
cls
echo ========================================
echo INSTALACAO: ACTIVE DIRECTORY
echo ========================================
echo.
call :CHECK_ADMIN
call :INSTALL_DOMAIN
goto END

REM ========================================
REM OPCAO 4: WMI REMOTO
REM ========================================
:REMOTE
cls
echo ========================================
echo INSTALACAO: WMI REMOTO (SEM PROBE)
echo ========================================
echo.
call :CHECK_ADMIN
call :INSTALL_REMOTE_ONLY
goto END

REM ========================================
REM OPCAO 5: AUTO DETECT
REM ========================================
:AUTO
cls
echo ========================================
echo DETECCAO AUTOMATICA
echo ========================================
echo.
call :CHECK_ADMIN
call :AUTO_DETECT
goto END

REM ========================================
REM FUNCAO: Verificar Admin
REM ========================================
:CHECK_ADMIN
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERRO: Execute como Administrador!
    echo Clique com botao direito e "Executar como administrador"
    pause
    exit /b 1
)
echo [OK] Privilegios de administrador verificados
echo.
exit /b 0

REM ========================================
REM FUNCAO: Detectar Entra ID
REM ========================================
:DETECT_ENTRAID
echo Detectando tipo de vinculo...
dsregcmd /status | findstr "AzureAdJoined" | findstr "YES" >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Maquina vinculada ao Entra ID (Azure AD)
) else (
    echo [AVISO] Maquina nao parece estar no Entra ID
    echo Continuando instalacao...
)
echo.
exit /b 0

REM ========================================
REM FUNCAO: Auto Detect
REM ========================================
:AUTO_DETECT
echo Analisando configuracao da maquina...
echo.

REM Verificar Entra ID
dsregcmd /status | findstr "AzureAdJoined" | findstr "YES" >nul 2>&1
if %errorLevel% equ 0 (
    echo [DETECTADO] Entra ID (Azure AD)
    echo.
    set /p CONFIRM="Confirma instalacao para Entra ID? (S/N): "
    if /i "%CONFIRM%"=="S" (
        call :INSTALL_BASE "ENTRAID"
        exit /b 0
    )
)

REM Verificar Dominio AD
wmic computersystem get domain | findstr /v "Domain WORKGROUP" >nul 2>&1
if %errorLevel% equ 0 (
    echo [DETECTADO] Active Directory (Dominio)
    echo.
    set /p CONFIRM="Confirma instalacao para Dominio AD? (S/N): "
    if /i "%CONFIRM%"=="S" (
        call :INSTALL_DOMAIN
        exit /b 0
    )
)

REM Default: Workgroup
echo [DETECTADO] Workgroup (Sem dominio)
echo.
set /p CONFIRM="Confirma instalacao para Workgroup? (S/N): "
if /i "%CONFIRM%"=="S" (
    call :INSTALL_BASE "WORKGROUP"
    exit /b 0
)

echo.
echo Deteccao cancelada. Voltando ao menu...
timeout /t 2 >nul
goto MENU

REM ========================================
REM FUNCAO: Instalacao Base (Workgroup/Entra ID)
REM ========================================
:INSTALL_BASE
set INSTALL_TYPE=%~1

echo [1/9] Criando usuario local MonitorUser...
set "PASSWORD=Monitor@%RANDOM%%RANDOM%"
net user MonitorUser "%PASSWORD%" /add /comment:"Usuario para monitoramento Coruja" /passwordchg:no /expires:never /active:yes >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Usuario MonitorUser criado
) else (
    echo [INFO] Usuario MonitorUser ja existe
)
wmic useraccount where "name='MonitorUser'" set PasswordExpires=FALSE >nul 2>&1
echo.

echo [2/9] Adicionando usuario aos grupos...
net localgroup "Administradores" MonitorUser /add >nul 2>&1
net localgroup "Administrators" MonitorUser /add >nul 2>&1
net localgroup "Usuarios de Gerenciamento Remoto" MonitorUser /add >nul 2>&1
net localgroup "Remote Management Users" MonitorUser /add >nul 2>&1
net localgroup "Usuarios do Monitor de Desempenho" MonitorUser /add >nul 2>&1
net localgroup "Performance Monitor Users" MonitorUser /add >nul 2>&1
net localgroup "Usuarios COM Distribuidos" MonitorUser /add >nul 2>&1
net localgroup "Distributed COM Users" MonitorUser /add >nul 2>&1
echo [OK] Usuario adicionado aos grupos
echo.

echo [3/9] Configurando Firewall para WMI...
netsh advfirewall firewall set rule group="Instrumentacao de Gerenciamento do Windows (WMI)" new enable=yes >nul 2>&1
netsh advfirewall firewall set rule group="Windows Management Instrumentation (WMI)" new enable=yes >nul 2>&1
netsh advfirewall firewall add rule name="WMI-In-TCP" dir=in action=allow protocol=TCP localport=135 >nul 2>&1
netsh advfirewall firewall add rule name="WMI-In-TCP-Dynamic" dir=in action=allow protocol=TCP localport=1024-65535 program="%%systemroot%%\system32\svchost.exe" service=winmgmt >nul 2>&1
echo [OK] Firewall configurado
echo.

echo [4/9] Configurando DCOM...
reg add "HKLM\Software\Microsoft\Ole" /v EnableDCOM /t REG_SZ /d Y /f >nul 2>&1
reg add "HKLM\Software\Microsoft\Ole" /v LegacyAuthenticationLevel /t REG_DWORD /d 2 /f >nul 2>&1
reg add "HKLM\Software\Microsoft\Ole" /v LegacyImpersonationLevel /t REG_DWORD /d 3 /f >nul 2>&1
echo [OK] DCOM configurado
echo.

echo [5/9] Configurando seguranca WMI...
powershell -Command "$namespace = Get-WmiObject -Namespace 'root' -Class '__SystemSecurity'; $null = $namespace.PsBase.InvokeMethod('SetSecurityDescriptor', $null)" >nul 2>&1
echo [OK] Seguranca WMI configurada
echo.

echo [6/9] Criando arquivo de credenciais...
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
echo [OK] Arquivo wmi_credentials.json criado
echo.

echo [7/9] Configurando probe...
echo.
set /p API_IP="Digite o IP do servidor Coruja (ex: 192.168.0.9): "
echo.
set /p PROBE_TOKEN="Digite o token da probe: "
echo.

(
echo {
echo   "api_url": "http://%API_IP%:8000",
echo   "probe_token": "%PROBE_TOKEN%",
echo   "collection_interval": 60,
echo   "log_level": "INFO"
echo }
) > probe_config.json
echo [OK] Arquivo probe_config.json criado
echo.

echo [8/9] Testando WMI local...
wmic computersystem get name,domain,manufacturer,model >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] WMI funcionando corretamente
) else (
    echo [AVISO] Erro ao testar WMI
)
echo.

echo [9/9] Instalacao concluida!
echo.
echo ========================================
echo CREDENCIAIS CRIADAS
echo ========================================
echo.
echo Tipo: %INSTALL_TYPE%
echo Usuario: MonitorUser
echo Senha: %PASSWORD%
echo Computador: %HOSTNAME%
echo.
echo IMPORTANTE: Guarde estas credenciais!
echo.
echo ========================================
echo PROXIMOS PASSOS
echo ========================================
echo.
echo 1. Instale Python 3.8+
echo    https://www.python.org/downloads/
echo.
echo 2. Instale dependencias:
echo    pip install -r requirements.txt
echo.
echo 3. Inicie a probe:
echo    python probe_core.py
echo.
pause
exit /b 0

REM ========================================
REM FUNCAO: Instalacao Dominio
REM ========================================
:INSTALL_DOMAIN
echo [1/7] Configurando para Active Directory...
echo.
set /p DOMAIN_USER="Digite o usuario de dominio (ex: DOMINIO\usuario): "
set /p DOMAIN_PASS="Digite a senha: "
echo.

echo [2/7] Configurando Firewall...
netsh advfirewall firewall set rule group="Windows Management Instrumentation (WMI)" new enable=yes >nul 2>&1
echo [OK] Firewall configurado
echo.

echo [3/7] Configurando DCOM...
reg add "HKLM\Software\Microsoft\Ole" /v EnableDCOM /t REG_SZ /d Y /f >nul 2>&1
echo [OK] DCOM configurado
echo.

echo [4/7] Criando arquivo de credenciais...
for /f "tokens=*" %%a in ('hostname') do set HOSTNAME=%%a
for /f "tokens=1 delims=\" %%a in ("%DOMAIN_USER%") do set DOMAIN_NAME=%%a
for /f "tokens=2 delims=\" %%a in ("%DOMAIN_USER%") do set USER_NAME=%%a
(
echo {
echo   "%HOSTNAME%": {
echo     "username": "%USER_NAME%",
echo     "password": "%DOMAIN_PASS%",
echo     "domain": "%DOMAIN_NAME%"
echo   }
echo }
) > wmi_credentials.json
echo [OK] Arquivo criado
echo.

echo [5/7] Configurando probe...
set /p API_IP="Digite o IP do servidor Coruja (ex: 192.168.0.9): "
echo.
set /p PROBE_TOKEN="Digite o token da probe: "
echo.
(
echo {
echo   "api_url": "http://%API_IP%:8000",
echo   "probe_token": "%PROBE_TOKEN%",
echo   "collection_interval": 60,
echo   "log_level": "INFO"
echo }
) > probe_config.json
echo [OK] Configurado
echo.

echo [6/7] Testando WMI...
wmic computersystem get name,domain >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] WMI funcionando
) else (
    echo [AVISO] Erro ao testar WMI
)
echo.

echo [7/7] Instalacao concluida!
echo.
echo ========================================
echo PROXIMOS PASSOS
echo ========================================
echo.
echo 1. Instale Python 3.8+
echo 2. pip install -r requirements.txt
echo 3. python probe_core.py
echo.
pause
exit /b 0

REM ========================================
REM FUNCAO: WMI Remoto Apenas
REM ========================================
:INSTALL_REMOTE_ONLY
echo [1/4] Configurando WMI Remoto...
echo.
echo NOTA: Esta opcao apenas configura WMI remoto.
echo Nao instala a probe Python.
echo.
pause

echo [2/4] Configurando Firewall...
netsh advfirewall firewall set rule group="Windows Management Instrumentation (WMI)" new enable=yes >nul 2>&1
netsh advfirewall firewall add rule name="WMI-In-TCP" dir=in action=allow protocol=TCP localport=135 >nul 2>&1
echo [OK] Firewall configurado
echo.

echo [3/4] Configurando DCOM...
reg add "HKLM\Software\Microsoft\Ole" /v EnableDCOM /t REG_SZ /d Y /f >nul 2>&1
echo [OK] DCOM configurado
echo.

echo [4/4] Testando WMI...
wmic computersystem get name >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] WMI funcionando
) else (
    echo [AVISO] Erro ao testar WMI
)
echo.

echo ========================================
echo CONFIGURACAO CONCLUIDA
echo ========================================
echo.
echo WMI remoto configurado com sucesso!
echo.
echo Configure as credenciais na probe que vai
echo monitorar esta maquina remotamente.
echo.
pause
exit /b 0

REM ========================================
REM FIM
REM ========================================
:END
cls
echo.
echo ========================================
echo Obrigado por usar Coruja Monitor!
echo ========================================
echo.
echo Documentacao completa em:
echo - GUIA_RAPIDO_INSTALACAO.md
echo - PASSO_A_PASSO_NOVA_EMPRESA.md
echo.
echo Suporte: http://192.168.0.9:3000
echo.
pause
exit
