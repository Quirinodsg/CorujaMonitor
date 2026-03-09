@echo off
setlocal enabledelayedexpansion
title Instalacao Automatizada - Probe Coruja Monitor
color 0A

REM ========================================
REM INSTALACAO AUTOMATIZADA DO PROBE
REM Baseado em CheckMK e PRTG
REM ========================================

echo.
echo ========================================
echo   INSTALACAO AUTOMATIZADA - PROBE
echo   Coruja Monitor - Agentless Monitoring
echo ========================================
echo.

REM Verificar privilegios de administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERRO] Este script precisa ser executado como Administrador!
    echo.
    echo Clique com botao direito e selecione "Executar como Administrador"
    echo.
    pause
    exit /b 1
)

echo [OK] Executando com privilegios de administrador
echo.

REM ========================================
REM ETAPA 1: Configuracao do Servidor
REM ========================================
echo ========================================
echo ETAPA 1/8: Configuracao do Servidor
echo ========================================
echo.

echo O servidor Coruja esta:
echo.
echo 1. Nesta mesma maquina (localhost)
echo 2. Em outra maquina na rede
echo.
set /p LOCATION="Digite 1 ou 2: "

if "%LOCATION%"=="1" (
    set API_URL=http://localhost:8000
    echo.
    echo [OK] Usando: http://localhost:8000
) else (
    echo.
    echo Digite o IP da maquina onde o Coruja esta instalado:
    echo (exemplo: 192.168.1.100)
    echo.
    set /p SERVER_IP="IP do servidor: "
    set API_URL=http://!SERVER_IP!:8000
    echo.
    echo [OK] Usando: http://!SERVER_IP!:8000
)

echo.
echo Cole o TOKEN do probe:
echo (copie do dashboard: Probes -^> Novo Probe)
echo.
set /p PROBE_TOKEN="Token: "

echo.
echo [OK] Configuracao do servidor concluida
timeout /t 2 >nul

REM ========================================
REM ETAPA 2: Criar Usuario de Monitoramento
REM ========================================
echo.
echo ========================================
echo ETAPA 2/8: Criar Usuario de Monitoramento
echo ========================================
echo.

set MONITOR_USER=MonitorUser
set MONITOR_PASS=M0n1t0r@%RANDOM%%RANDOM%

echo Criando usuario: %MONITOR_USER%
net user %MONITOR_USER% %MONITOR_PASS% /add /comment:"Usuario para monitoramento agentless" >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Usuario criado com sucesso
) else (
    echo [AVISO] Usuario ja existe ou erro ao criar
)

echo.
echo Adicionando aos grupos necessarios...
net localgroup "Performance Monitor Users" %MONITOR_USER% /add >nul 2>&1
net localgroup "Distributed COM Users" %MONITOR_USER% /add >nul 2>&1
net localgroup "Administrators" %MONITOR_USER% /add >nul 2>&1
echo [OK] Usuario adicionado aos grupos

echo.
echo IMPORTANTE: Anote estas credenciais!
echo Usuario: %MONITOR_USER%
echo Senha: %MONITOR_PASS%
echo.
echo Pressione qualquer tecla para continuar...
pause >nul

REM ========================================
REM ETAPA 3: Configurar Firewall
REM ========================================
echo.
echo ========================================
echo ETAPA 3/8: Configurar Firewall
echo ========================================
echo.

echo Habilitando regras WMI no firewall...
netsh advfirewall firewall set rule group="Windows Management Instrumentation (WMI)" new enable=yes >nul 2>&1
echo [OK] Regras WMI habilitadas

echo.
echo Criando regra para SNMP (porta 161)...
netsh advfirewall firewall add rule name="SNMP Monitoring" dir=in action=allow protocol=UDP localport=161 >nul 2>&1
echo [OK] Regra SNMP criada

timeout /t 2 >nul

REM ========================================
REM ETAPA 4: Configurar DCOM
REM ========================================
echo.
echo ========================================
echo ETAPA 4/8: Configurar DCOM
echo ========================================
echo.

echo Configurando permissoes DCOM...
reg add "HKLM\SOFTWARE\Microsoft\Ole" /v EnableDCOM /t REG_SZ /d Y /f >nul 2>&1
echo [OK] DCOM habilitado

timeout /t 2 >nul

REM ========================================
REM ETAPA 5: Criar Arquivo de Configuracao
REM ========================================
echo.
echo ========================================
echo ETAPA 5/8: Criar Arquivo de Configuracao
echo ========================================
echo.

echo Criando probe_config.json...
(
echo {
echo   "api_url": "%API_URL%",
echo   "probe_token": "%PROBE_TOKEN%",
echo   "collection_interval": 60,
echo   "monitored_services": [
echo     "W3SVC",
echo     "MSSQLSERVER",
echo     "MSSQL$SQLEXPRESS"
echo   ],
echo   "udm_targets": [
echo     "8.8.8.8"
echo   ]
echo }
) > probe_config.json

echo [OK] Arquivo de configuracao criado
timeout /t 2 >nul

REM ========================================
REM ETAPA 6: Criar Arquivo de Credenciais WMI
REM ========================================
echo.
echo ========================================
echo ETAPA 6/8: Criar Template de Credenciais
echo ========================================
echo.

echo Criando wmi_credentials.json (template)...
(
echo {
echo   "credentials": [
echo     {
echo       "name": "Local Machine",
echo       "hostname": "localhost",
echo       "username": "%MONITOR_USER%",
echo       "password": "%MONITOR_PASS%",
echo       "domain": "",
echo       "enabled": true
echo     }
echo   ]
echo }
) > wmi_credentials.json

echo [OK] Template de credenciais criado
echo.
echo Para monitorar outras maquinas, edite wmi_credentials.json
timeout /t 2 >nul

REM ========================================
REM ETAPA 7: Instalar Dependencias Python
REM ========================================
echo.
echo ========================================
echo ETAPA 7/8: Instalar Dependencias Python
echo ========================================
echo.

echo Verificando Python...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [AVISO] Python nao encontrado!
    echo.
    echo Instale Python 3.8+ de: https://www.python.org/downloads/
    echo Marque a opcao "Add Python to PATH" durante instalacao
    echo.
    echo Apos instalar Python, execute novamente este script
    pause
    exit /b 1
)

echo [OK] Python encontrado
echo.
echo Instalando dependencias...
pip install -r requirements.txt
if %errorLevel% equ 0 (
    echo [OK] Dependencias instaladas
) else (
    echo [AVISO] Erro ao instalar dependencias
    echo Execute manualmente: pip install -r requirements.txt
)

timeout /t 2 >nul

REM ========================================
REM ETAPA 8: Criar Tarefa Agendada
REM ========================================
echo.
echo ========================================
echo ETAPA 8/8: Criar Tarefa Agendada
echo ========================================
echo.

echo Criando tarefa agendada para iniciar probe automaticamente...

set SCRIPT_DIR=%~dp0
set PYTHON_PATH=python
set PROBE_SCRIPT=%SCRIPT_DIR%probe_core.py

schtasks /create /tn "Coruja Probe Monitor" /tr "%PYTHON_PATH% %PROBE_SCRIPT%" /sc onstart /ru SYSTEM /rl HIGHEST /f >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Tarefa agendada criada
    echo.
    echo A probe iniciara automaticamente no boot do sistema
) else (
    echo [AVISO] Erro ao criar tarefa agendada
    echo Execute manualmente: python probe_core.py
)

timeout /t 2 >nul

REM ========================================
REM ETAPA 9: Testar Conexao WMI
REM ========================================
echo.
echo ========================================
echo TESTE: Verificar WMI Local
echo ========================================
echo.

echo Testando acesso WMI...
wmic computersystem get name >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] WMI funcionando corretamente
) else (
    echo [AVISO] Erro ao acessar WMI
)

timeout /t 2 >nul

REM ========================================
REM ETAPA 10: Iniciar Probe
REM ========================================
echo.
echo ========================================
echo INICIAR PROBE
echo ========================================
echo.

echo Deseja iniciar o probe agora?
echo.
echo 1. Sim, iniciar agora
echo 2. Nao, iniciar manualmente depois
echo.
set /p START_NOW="Digite 1 ou 2: "

if "%START_NOW%"=="1" (
    echo.
    echo Iniciando probe...
    start "Coruja Probe" python probe_core.py
    echo [OK] Probe iniciado em nova janela
    echo.
    echo Verifique no dashboard se o probe aparece como conectado
) else (
    echo.
    echo [OK] Para iniciar manualmente, execute: python probe_core.py
)

REM ========================================
REM RESUMO FINAL
REM ========================================
echo.
echo ========================================
echo   INSTALACAO CONCLUIDA!
echo ========================================
echo.
echo Resumo da instalacao:
echo.
echo [V] Usuario de monitoramento criado
echo     Usuario: %MONITOR_USER%
echo     Senha: %MONITOR_PASS%
echo.
echo [V] Firewall configurado (WMI + SNMP)
echo [V] DCOM habilitado
echo [V] Arquivo de configuracao criado
echo [V] Template de credenciais criado
echo [V] Tarefa agendada configurada
echo.
echo Proximos passos:
echo.
echo 1. Verifique no dashboard se probe aparece conectado
echo 2. Para monitorar outras maquinas:
echo    - Edite wmi_credentials.json
echo    - Adicione credenciais das maquinas remotas
echo    - Configure firewall nas maquinas remotas
echo.
echo 3. Para monitorar dispositivos SNMP:
echo    - Crie snmp_devices.json
echo    - Configure community strings ou credenciais v3
echo.
echo Documentacao completa:
echo - GUIA_MONITORAMENTO_AGENTLESS_COMPLETO.md
echo - probe/INSTALACAO.md
echo.
echo ========================================
echo.
pause
