@echo off
title Diagnostico do Probe
color 0A

echo.
echo ========================================
echo   DIAGNOSTICO DO PROBE
echo ========================================
echo.

echo [1] Status do servico:
sc query CorujaProbe
echo.

echo [2] Verificando configuracao:
if exist probe_config.json (
    echo [OK] Arquivo probe_config.json encontrado
    type probe_config.json
) else (
    echo [ERRO] Arquivo probe_config.json NAO encontrado!
    echo Execute: configurar_probe.bat
    pause
    exit /b 1
)
echo.

echo [3] Verificando logs do Windows Event Viewer:
echo Procurando erros do servico...
powershell -Command "Get-EventLog -LogName Application -Source 'Coruja Monitor Probe' -Newest 5 -ErrorAction SilentlyContinue | Format-List TimeGenerated, EntryType, Message"
echo.

echo [4] Tentando iniciar o servico:
net start CorujaProbe
echo.

echo [5] Status apos tentativa:
sc query CorujaProbe
echo.

echo [6] Verificando log do probe:
if exist probe.log (
    echo [OK] Log encontrado - Ultimas 30 linhas:
    powershell -Command "Get-Content probe.log -Tail 30"
) else (
    echo [AVISO] Arquivo probe.log nao encontrado
    echo O servico pode nao ter iniciado corretamente
)
echo.

echo [7] Testando conexao com API:
echo Testando: %API_URL%
python -c "import httpx; import json; config = json.load(open('probe_config.json')); print(f'API URL: {config[\"api_url\"]}'); r = httpx.get(f'{config[\"api_url\"]}/health', timeout=5); print(f'Status: {r.status_code}')"
echo.

echo ========================================
echo   SOLUCOES COMUNS
echo ========================================
echo.
echo Se o servico nao inicia:
echo 1. Verifique se probe_config.json existe
echo 2. Verifique se a API esta acessivel
echo 3. Execute manualmente: python probe_core.py
echo 4. Verifique logs do Windows Event Viewer
echo 5. Reinstale: uninstall_service.bat e setup_wizard.bat
echo.
pause
