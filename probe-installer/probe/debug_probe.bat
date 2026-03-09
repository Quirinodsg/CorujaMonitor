@echo off
title Debug do Probe
color 0A

echo.
echo ========================================
echo   DEBUG DO PROBE
echo ========================================
echo.

echo [1] Configuracao atual:
if exist probe_config.json (
    type probe_config.json
) else (
    echo [ERRO] probe_config.json nao encontrado!
)
echo.
echo.

echo [2] Status do servico:
sc query CorujaProbe
echo.
echo.

echo [3] Log do probe (probe.log):
if exist probe.log (
    type probe.log
) else (
    echo [AVISO] probe.log nao existe - servico pode nao estar rodando corretamente
)
echo.
echo.

echo [4] Log do servico (probe_service.log):
if exist probe_service.log (
    type probe_service.log
) else (
    echo [AVISO] probe_service.log nao existe
)
echo.
echo.

echo [5] Testando conexao manual com a API:
python -c "import httpx; import json; config = json.load(open('probe_config.json')); print(f'Testando: {config[\"api_url\"]}/health'); r = httpx.get(f'{config[\"api_url\"]}/health', timeout=5, verify=False); print(f'Status: {r.status_code}'); print(f'Resposta: {r.text}')"
echo.
echo.

echo [6] Testando heartbeat manual:
python -c "import httpx; import json; config = json.load(open('probe_config.json')); print(f'Enviando heartbeat...'); r = httpx.post(f'{config[\"api_url\"]}/api/v1/probes/heartbeat', params={'probe_token': config['probe_token'], 'version': '1.0.0'}, timeout=10, verify=False); print(f'Status: {r.status_code}'); print(f'Resposta: {r.text}')"
echo.
echo.

pause
