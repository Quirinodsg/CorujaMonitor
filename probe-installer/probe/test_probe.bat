@echo off
title Teste Manual do Probe
color 0A

echo.
echo ========================================
echo   TESTE MANUAL DO PROBE
echo ========================================
echo.

echo [1] Verificando Python...
python --version
if errorlevel 1 (
    echo [ERRO] Python nao encontrado!
    pause
    exit /b 1
)
echo.

echo [2] Verificando dependencias...
python -c "import psutil; import httpx; import win32service; print('[OK] Todas as dependencias instaladas')"
if errorlevel 1 (
    echo [ERRO] Dependencias faltando!
    echo Execute: pip install -r requirements.txt
    pause
    exit /b 1
)
echo.

echo [3] Verificando configuracao...
if not exist probe_config.json (
    echo [ERRO] Arquivo probe_config.json nao encontrado!
    echo Execute: configurar_probe.bat
    pause
    exit /b 1
)
echo [OK] Configuracao encontrada:
type probe_config.json
echo.

echo [4] Testando conexao com API...
python -c "import httpx; import json; config = json.load(open('probe_config.json')); r = httpx.get(f'{config[\"api_url\"]}/health', timeout=5, verify=False); print(f'[OK] API respondeu: {r.status_code}')"
if errorlevel 1 (
    echo [ERRO] Nao foi possivel conectar na API!
    echo Verifique se a URL esta correta e se a API esta rodando
    pause
    exit /b 1
)
echo.

echo [5] Executando probe manualmente...
echo Pressione Ctrl+C para parar
echo.
python probe_core.py
echo.

pause
