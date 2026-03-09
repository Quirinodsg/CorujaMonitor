@echo off
setlocal enabledelayedexpansion
title Diagnostico Probe Coruja
color 0B

echo.
echo ========================================
echo   DIAGNOSTICO PROBE CORUJA
echo ========================================
echo.

cd /d "C:\Program Files\CorujaMonitor\Probe"

if not exist "C:\Program Files\CorujaMonitor\Probe" (
    color 0C
    echo [ERRO] Probe nao instalada!
    pause
    exit /b 1
)

echo [1/6] Verificando arquivos...
echo.

if exist "probe_core.py" (
    echo [OK] probe_core.py encontrado
) else (
    echo [X] probe_core.py NAO encontrado
)

if exist "config.yaml" (
    echo [OK] config.yaml encontrado
) else (
    echo [X] config.yaml NAO encontrado
)

if exist "collectors\" (
    echo [OK] Pasta collectors encontrada
) else (
    echo [X] Pasta collectors NAO encontrada
)

echo.
echo [2/6] Verificando servico...
echo.

sc query CorujaProbe >nul 2>&1
if !errorLevel! equ 0 (
    echo [OK] Servico CorujaProbe existe
    sc query CorujaProbe | findstr "STATE"
) else (
    echo [X] Servico CorujaProbe NAO existe
)

echo.
echo [3/6] Verificando Python...
echo.

python --version >nul 2>&1
if !errorLevel! equ 0 (
    echo [OK] Python encontrado:
    python --version
) else (
    echo [X] Python NAO encontrado no PATH
)

echo.
echo [4/6] Verificando dependencias...
echo.

python -c "import psutil" >nul 2>&1
if !errorLevel! equ 0 (echo [OK] psutil) else (echo [X] psutil)

python -c "import httpx" >nul 2>&1
if !errorLevel! equ 0 (echo [OK] httpx) else (echo [X] httpx)

python -c "import win32api" >nul 2>&1
if !errorLevel! equ 0 (echo [OK] pywin32) else (echo [X] pywin32)

python -c "import yaml" >nul 2>&1
if !errorLevel! equ 0 (echo [OK] pyyaml) else (echo [X] pyyaml)

echo.
echo [5/6] Verificando configuracao...
echo.

if exist "config.yaml" (
    echo Conteudo do config.yaml:
    echo ----------------------------------------
    type config.yaml
    echo ----------------------------------------
) else (
    echo [X] Arquivo config.yaml nao existe!
)

echo.
echo [6/6] Verificando logs...
echo.

if exist "logs\probe.log" (
    echo Ultimas 20 linhas do log:
    echo ----------------------------------------
    powershell -Command "Get-Content 'logs\probe.log' -Tail 20"
    echo ----------------------------------------
) else (
    echo [X] Arquivo de log nao existe ainda
)

echo.
echo ========================================
echo   TESTE DE CONECTIVIDADE
echo ========================================
echo.

echo Testando conexao com servidor...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://192.168.31.161:8000/health' -TimeoutSec 5 -UseBasicParsing; Write-Host '[OK] Servidor acessivel' -ForegroundColor Green } catch { Write-Host '[X] Servidor NAO acessivel' -ForegroundColor Red }"

echo.
echo ========================================
echo   RESUMO
echo ========================================
echo.
echo Probe instalada em:
echo C:\Program Files\CorujaMonitor\Probe
echo.
echo Para ver logs em tempo real:
echo Get-Content "C:\Program Files\CorujaMonitor\Probe\logs\probe.log" -Wait
echo.
echo Para reiniciar servico:
echo net stop CorujaProbe ^&^& net start CorujaProbe
echo.
echo ========================================
echo.
pause
