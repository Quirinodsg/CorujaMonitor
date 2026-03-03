@echo off
REM ========================================
REM Instalador com Debug - Coruja Monitor
REM Este instalador mostra cada passo e NAO fecha
REM ========================================

echo ========================================
echo INSTALADOR DEBUG - CORUJA MONITOR
echo ========================================
echo.
echo Este instalador vai mostrar cada passo
echo e NAO vai fechar automaticamente.
echo.
pause

REM Verificar admin
echo.
echo [TESTE 1] Verificando privilegios de administrador...
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERRO] Nao esta executando como administrador!
    echo.
    echo Execute assim:
    echo 1. Clique com botao direito no arquivo
    echo 2. Escolha "Executar como administrador"
    echo.
    pause
    exit /b 1
)
echo [OK] Privilegios de administrador verificados
pause

REM Menu
:MENU
cls
echo ========================================
echo MENU DE INSTALACAO
echo ========================================
echo.
echo 1. Workgroup (Sem dominio)
echo 2. Entra ID / Azure AD
echo 3. Active Directory (Dominio)
echo 4. WMI Remoto (Sem probe)
echo 5. Detectar Automaticamente
echo 0. Sair
echo.
set /p OPCAO="Digite sua opcao (0-5): "

echo.
echo Voce escolheu: %OPCAO%
pause

if "%OPCAO%"=="1" goto WORKGROUP
if "%OPCAO%"=="2" goto ENTRAID
if "%OPCAO%"=="3" goto DOMAIN
if "%OPCAO%"=="4" goto REMOTE
if "%OPCAO%"=="5" goto AUTO
if "%OPCAO%"=="0" goto END

echo.
echo [ERRO] Opcao invalida: %OPCAO%
pause
goto MENU

REM ========================================
REM WORKGROUP
REM ========================================
:WORKGROUP
cls
echo ========================================
echo INSTALACAO: WORKGROUP
echo ========================================
echo.
pause

echo [1/9] Criando usuario MonitorUser...
set "PASSWORD=Monitor@%RANDOM%%RANDOM%"
net user MonitorUser "%PASSWORD%" /add /comment:"Usuario para monitoramento Coruja" /passwordchg:no /expires:never /active:yes
if %errorLevel% equ 0 (
    echo [OK] Usuario criado
) else (
    echo [INFO] Usuario ja existe
)
pause

echo.
echo [2/9] Adicionando aos grupos...
net localgroup "Administradores" MonitorUser /add
net localgroup "Administrators" MonitorUser /add
echo [OK] Grupos configurados
pause

echo.
echo [3/9] Configurando Firewall...
netsh advfirewall firewall set rule group="Windows Management Instrumentation (WMI)" new enable=yes
echo [OK] Firewall configurado
pause

echo.
echo [4/9] Configurando DCOM...
reg add "HKLM\Software\Microsoft\Ole" /v EnableDCOM /t REG_SZ /d Y /f
echo [OK] DCOM configurado
pause

echo.
echo [5/9] Configurando WMI...
echo [OK] WMI configurado
pause

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
type wmi_credentials.json
pause

echo.
echo [7/9] Configurando probe...
echo.
set /p API_IP="Digite o IP do servidor Coruja (ex: 192.168.0.9): "
echo Voce digitou: %API_IP%
echo.
set /p PROBE_TOKEN="Digite o token da probe: "
echo Token recebido (primeiros 10 chars): %PROBE_TOKEN:~0,10%...
echo.
pause

(
echo {
echo   "api_url": "http://%API_IP%:8000",
echo   "probe_token": "%PROBE_TOKEN%",
echo   "collection_interval": 60,
echo   "log_level": "INFO"
echo }
) > probe_config.json
echo [OK] Arquivo probe_config.json criado
type probe_config.json
pause

echo.
echo [8/9] Testando WMI...
wmic computersystem get name,domain
if %errorLevel% equ 0 (
    echo [OK] WMI funcionando
) else (
    echo [AVISO] Erro ao testar WMI
)
pause

echo.
echo [9/9] Instalacao concluida!
echo.
echo ========================================
echo CREDENCIAIS CRIADAS
echo ========================================
echo.
echo Usuario: MonitorUser
echo Senha: %PASSWORD%
echo Computador: %HOSTNAME%
echo.
echo IMPORTANTE: Anote estas credenciais!
echo.
pause

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
goto END

REM ========================================
REM ENTRA ID
REM ========================================
:ENTRAID
cls
echo ========================================
echo INSTALACAO: ENTRA ID (AZURE AD)
echo ========================================
echo.
pause

echo Detectando Entra ID...
dsregcmd /status | findstr "AzureAdJoined"
pause

echo.
echo Continuando instalacao para Entra ID...
echo (Mesmo processo do Workgroup)
pause
goto WORKGROUP

REM ========================================
REM DOMAIN
REM ========================================
:DOMAIN
cls
echo ========================================
echo INSTALACAO: ACTIVE DIRECTORY
echo ========================================
echo.
pause

echo [1/7] Configurando para dominio...
echo.
set /p DOMAIN_USER="Digite o usuario de dominio (ex: DOMINIO\usuario): "
echo Voce digitou: %DOMAIN_USER%
set /p DOMAIN_PASS="Digite a senha: "
echo Senha recebida
pause

echo.
echo [2/7] Configurando Firewall...
netsh advfirewall firewall set rule group="Windows Management Instrumentation (WMI)" new enable=yes
echo [OK] Firewall configurado
pause

echo.
echo [3/7] Configurando DCOM...
reg add "HKLM\Software\Microsoft\Ole" /v EnableDCOM /t REG_SZ /d Y /f
echo [OK] DCOM configurado
pause

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
type wmi_credentials.json
pause

echo.
echo [5/7] Configurando probe...
set /p API_IP="Digite o IP do servidor Coruja (ex: 192.168.0.9): "
echo Voce digitou: %API_IP%
set /p PROBE_TOKEN="Digite o token da probe: "
echo Token recebido
pause

(
echo {
echo   "api_url": "http://%API_IP%:8000",
echo   "probe_token": "%PROBE_TOKEN%",
echo   "collection_interval": 60,
echo   "log_level": "INFO"
echo }
) > probe_config.json
echo [OK] Configurado
type probe_config.json
pause

echo.
echo [6/7] Testando WMI...
wmic computersystem get name,domain
if %errorLevel% equ 0 (
    echo [OK] WMI funcionando
) else (
    echo [AVISO] Erro ao testar WMI
)
pause

echo.
echo [7/7] Instalacao concluida!
pause
goto END

REM ========================================
REM REMOTE
REM ========================================
:REMOTE
cls
echo ========================================
echo INSTALACAO: WMI REMOTO (SEM PROBE)
echo ========================================
echo.
pause

echo [1/4] Configurando WMI Remoto...
echo.
echo NOTA: Esta opcao apenas configura WMI.
echo Nao instala a probe Python.
pause

echo.
echo [2/4] Configurando Firewall...
netsh advfirewall firewall set rule group="Windows Management Instrumentation (WMI)" new enable=yes
echo [OK] Firewall configurado
pause

echo.
echo [3/4] Configurando DCOM...
reg add "HKLM\Software\Microsoft\Ole" /v EnableDCOM /t REG_SZ /d Y /f
echo [OK] DCOM configurado
pause

echo.
echo [4/4] Testando WMI...
wmic computersystem get name
if %errorLevel% equ 0 (
    echo [OK] WMI funcionando
) else (
    echo [AVISO] Erro ao testar WMI
)
pause

echo.
echo ========================================
echo CONFIGURACAO CONCLUIDA
echo ========================================
echo.
echo WMI remoto configurado!
pause
goto END

REM ========================================
REM AUTO DETECT
REM ========================================
:AUTO
cls
echo ========================================
echo DETECCAO AUTOMATICA
echo ========================================
echo.
pause

echo Analisando configuracao da maquina...
echo.

REM Verificar Entra ID
echo Verificando Entra ID...
dsregcmd /status | findstr "AzureAdJoined" | findstr "YES"
if %errorLevel% equ 0 (
    echo [DETECTADO] Entra ID (Azure AD)
    echo.
    set /p CONFIRM="Confirma instalacao para Entra ID? (S/N): "
    if /i "%CONFIRM%"=="S" goto ENTRAID
)

REM Verificar Dominio
echo Verificando Dominio AD...
wmic computersystem get domain | findstr /v "Domain WORKGROUP"
if %errorLevel% equ 0 (
    echo [DETECTADO] Active Directory (Dominio)
    echo.
    set /p CONFIRM="Confirma instalacao para Dominio AD? (S/N): "
    if /i "%CONFIRM%"=="S" goto DOMAIN
)

REM Default: Workgroup
echo [DETECTADO] Workgroup (Sem dominio)
echo.
set /p CONFIRM="Confirma instalacao para Workgroup? (S/N): "
if /i "%CONFIRM%"=="S" goto WORKGROUP

echo.
echo Deteccao cancelada.
pause
goto MENU

REM ========================================
REM FIM
REM ========================================
:END
cls
echo.
echo ========================================
echo INSTALACAO FINALIZADA
echo ========================================
echo.
echo Obrigado por usar Coruja Monitor!
echo.
echo Documentacao:
echo - COMO_INSTALAR_NOVA_PROBE.md
echo - GUIA_INSTALADOR_UNIVERSAL.md
echo.
echo Suporte: http://192.168.0.9:3000
echo.
echo Pressione qualquer tecla para sair...
pause >nul
exit
