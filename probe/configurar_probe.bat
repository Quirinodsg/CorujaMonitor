@echo off
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
    
    REM Testar conectividade
    echo.
    echo Testando conectividade...
    curl -s http://!SERVER_IP!:8000/health >nul 2>&1
    if !errorLevel! neq 0 (
        echo [AVISO] Nao foi possivel conectar ao servidor
        echo Verifique:
        echo - O IP esta correto?
        echo - O firewall esta bloqueando?
        echo - O servidor esta rodando?
        echo.
        set /p CONTINUE="Deseja continuar mesmo assim? (S/N): "
        if /i not "!CONTINUE!"=="S" exit /b 1
    ) else (
        echo [OK] Servidor acessivel!
    )
)

echo.
echo Agora cole o TOKEN do probe:
echo (copie do dashboard: Probes -> Novo Probe)
echo.
set /p PROBE_TOKEN="Token: "

echo.
echo Criando arquivo de configuracao...
echo.

(
echo {
echo   "api_url": "%API_URL%",
echo   "probe_token": "%PROBE_TOKEN%",
echo   "collection_interval": 60,
echo   "monitored_services": [
echo     "W3SVC",
echo     "MSSQLSERVER"
echo   ],
echo   "udm_targets": [
echo     "8.8.8.8"
echo   ]
echo }
) > probe_config.json

echo [OK] Configuracao salva em: probe_config.json
echo.
echo Proximos passos:
echo 1. Instale as dependencias: pip install -r requirements.txt
echo 2. Teste o probe: python probe_core.py
echo 3. Instale como servico: python probe_service.py install
echo 4. Inicie o servico: python probe_service.py start
echo.
pause
