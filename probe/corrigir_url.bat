@echo off
title Coruja Monitor - Corrigir URL da Probe
color 0A

echo.
echo ========================================
echo   CORRIGIR URL DA PROBE
echo ========================================
echo.

REM Verificar privilegios de administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERRO] Execute como Administrador!
    pause
    exit /b 1
)

REM Mudar para o diretorio do script
cd /d "%~dp0"

echo [1] Parando servico...
net stop CorujaProbe >nul 2>&1
echo [OK] Servico parado
echo.

echo [2] Configuracao atual:
if exist probe_config.json (
    type probe_config.json
    echo.
) else (
    echo [ERRO] Arquivo probe_config.json nao encontrado!
    pause
    exit /b 1
)

echo.
echo ========================================
echo   NOVA CONFIGURACAO
echo ========================================
echo.
echo IMPORTANTE:
echo - Se Docker esta na MESMA maquina: use localhost:8000
echo - Se Docker esta em OUTRA maquina: use IP:8000 (ex: 192.168.0.37:8000)
echo.
echo Como o Docker esta rodando nesta maquina, vamos usar:
echo   http://localhost:8000
echo.

set /p PROBE_TOKEN="Cole o token do probe novamente: "

echo.
echo Criando nova configuracao...

(
echo {
echo   "api_url": "http://localhost:8000",
echo   "probe_token": "%PROBE_TOKEN%",
echo   "collection_interval": 60,
echo   "monitored_services": [],
echo   "ping_targets": [
echo     "8.8.8.8",
echo     "1.1.1.1"
echo   ]
echo }
) > probe_config.json

echo [OK] Configuracao atualizada
echo.

echo [3] Testando conexao com a API...
python -c "import httpx; r = httpx.get('http://localhost:8000/health', timeout=5); print('[OK] API respondendo!' if r.status_code == 200 else '[ERRO] API nao responde')" 2>nul
if %errorLevel% neq 0 (
    echo [ERRO] Nao foi possivel conectar a API
    echo.
    echo Verifique se a API esta rodando:
    echo   docker-compose up -d
    echo.
    echo Ou verifique os logs:
    echo   docker-compose logs api
    echo.
    pause
    exit /b 1
)
echo.

echo [4] Iniciando servico...
net start CorujaProbe
if %errorLevel% neq 0 (
    echo [ERRO] Falha ao iniciar servico
    echo.
    echo Tente manualmente:
    echo   python probe_core.py
    echo.
    pause
    exit /b 1
)

echo [OK] Servico iniciado
echo.

echo ========================================
echo   CORRECAO CONCLUIDA!
echo ========================================
echo.
echo Aguarde 1-2 minutos e verifique:
echo 1. Dashboard do Coruja (http://localhost:3000)
echo 2. Aba "Servidores" deve mostrar este computador
echo 3. Metricas devem comecar a aparecer
echo.
echo Para ver logs em tempo real:
echo   type probe.log
echo.

pause
