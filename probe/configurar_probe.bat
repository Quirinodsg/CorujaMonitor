@echo off
setlocal enabledelayedexpansion
title Configurar Probe Coruja
color 0A

echo.
echo ========================================
echo   CONFIGURACAO DO PROBE
echo ========================================
echo.

echo Este script vai ajudar a configurar o probe.
echo.

REM Perguntar onde esta o servidor
echo O servidor Coruja esta:
echo.
echo 1. Nesta mesma maquina (localhost)
echo 2. Em outra maquina na rede
echo.
set /p LOCATION="Digite 1 ou 2: "

if "%LOCATION%"=="1" (
    set "API_URL=http://localhost:8000"
    set "SERVER_IP=localhost"
    echo.
    echo [OK] Usando: http://localhost:8000
) else (
    echo.
    echo Digite o IP da maquina onde o Coruja esta instalado:
    echo (exemplo: 192.168.1.100)
    echo.
    set /p SERVER_IP="IP do servidor: "
    set "API_URL=http://!SERVER_IP!:8000"
    echo.
    echo [OK] Usando: http://!SERVER_IP!:8000
    
    REM Testar conectividade
    echo.
    echo Testando conectividade...
    powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://!SERVER_IP!:8000/health' -TimeoutSec 5 -UseBasicParsing; exit 0 } catch { exit 1 }" >nul 2>&1
    if !errorLevel! neq 0 (
        echo [AVISO] Nao foi possivel conectar ao servidor
        echo.
        echo Verifique:
        echo - O IP esta correto?
        echo - O firewall esta bloqueando?
        echo - O servidor esta rodando?
        echo.
        set /p CONTINUE="Deseja continuar mesmo assim? (S/N): "
        if /i not "!CONTINUE!"=="S" (
            echo.
            echo Configuracao cancelada.
            echo.
            pause
            exit /b 1
        )
    ) else (
        echo [OK] Servidor acessivel!
    )
)

echo.
echo Agora cole o TOKEN do probe:
echo (copie do dashboard: Probes ^> Novo Probe)
echo.
set /p PROBE_TOKEN="Token: "

if "!PROBE_TOKEN!"=="" (
    echo.
    echo [ERRO] Token nao pode estar vazio!
    echo.
    pause
    exit /b 1
)

echo.
echo Criando arquivo de configuracao...
echo.

REM Atualizar config.yaml
(
echo # ========================================
echo # CONFIGURACAO CORUJA MONITOR PROBE
echo # ========================================
echo.
echo # Servidor Coruja Monitor
echo server:
echo   host: "!SERVER_IP!"
echo   port: 8000
echo   protocol: "http"
echo.  
echo # Token de autenticacao
echo token: "!PROBE_TOKEN!"
echo.
echo # Identificacao da Probe
echo probe:
echo   name: "%COMPUTERNAME%"
echo   location: ""
echo.  
echo # Intervalo de coleta (segundos^)
echo collection_interval: 60
echo.
echo # Logs
echo logging:
echo   level: "INFO"
echo   file: "logs/probe.log"
echo   max_size_mb: 10
echo   backup_count: 5
echo.
echo # Coletores habilitados
echo collectors:
echo   system: true
echo   ping: true
echo   snmp: true
echo   docker: false
echo   kubernetes: false
echo   wmi_remote: false
) > config.yaml

echo [OK] Configuracao salva em: config.yaml
echo.
echo ========================================
echo   CONFIGURACAO CONCLUIDA!
echo ========================================
echo.
echo Servidor: !API_URL!
echo Nome da Probe: %COMPUTERNAME%
echo Token: [configurado]
echo.
echo ========================================
echo   PROXIMOS PASSOS
echo ========================================
echo.
echo 1. TESTAR A PROBE:
echo    python probe_core.py
echo.
echo 2. INSTALAR COMO SERVICO:
echo    Menu Iniciar ^> "Instalar Servico Coruja"
echo.
echo 3. VERIFICAR NO DASHBOARD:
echo    !API_URL!
echo    Menu: Probes
echo.
echo ========================================
echo.
pause
