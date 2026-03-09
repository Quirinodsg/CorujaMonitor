@echo off
setlocal enabledelayedexpansion
title Configurar Probe Coruja
color 0A

echo.
echo ========================================
echo   CONFIGURACAO DO PROBE
echo ========================================
echo.

cd /d "C:\Program Files\CorujaMonitor\Probe"

if not exist "C:\Program Files\CorujaMonitor\Probe" (
    color 0C
    echo [ERRO] Probe nao instalada!
    echo Execute primeiro o instalador.
    pause
    exit /b 1
)

echo Digite o IP do servidor:
set /p SERVER_IP="> "
if "%SERVER_IP%"=="" set "SERVER_IP=192.168.31.161"

echo.
echo Digite o TOKEN da probe:
set /p PROBE_TOKEN="> "

if "%PROBE_TOKEN%"=="" (
    echo.
    echo [ERRO] Token obrigatorio!
    pause
    exit /b 1
)

echo.
echo Criando configuracao...

(
echo # Configuracao Coruja Monitor Probe
echo server:
echo   host: "%SERVER_IP%"
echo   port: 8000
echo   protocol: "http"
echo token: "%PROBE_TOKEN%"
echo probe:
echo   name: "%COMPUTERNAME%"
echo   location: ""
echo collection_interval: 60
echo logging:
echo   level: "INFO"
echo   file: "logs/probe.log"
echo   max_size_mb: 10
echo   backup_count: 5
echo collectors:
echo   system: true
echo   ping: true
echo   snmp: true
echo   docker: false
echo   kubernetes: false
echo   wmi_remote: false
) > config.yaml

color 0A
echo.
echo ========================================
echo   CONFIGURACAO CONCLUIDA!
echo ========================================
echo.
echo Servidor: http://%SERVER_IP%:8000
echo Probe: %COMPUTERNAME%
echo Token: [configurado]
echo.
echo Arquivo criado: config.yaml
echo.
echo ========================================
echo   TESTAR PROBE
echo ========================================
echo.
echo Para testar, execute:
echo python probe_core.py
echo.
pause
