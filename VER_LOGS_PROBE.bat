@echo off
setlocal enabledelayedexpansion
title Logs da Probe em Tempo Real
color 0B

echo.
echo ========================================
echo   LOGS DA PROBE EM TEMPO REAL
echo ========================================
echo.

cd /d "C:\Program Files\CorujaMonitor\Probe"

if not exist "logs\probe.log" (
    color 0E
    echo [AVISO] Arquivo de log ainda nao existe
    echo.
    echo A probe precisa rodar por alguns segundos
    echo para criar o arquivo de log.
    echo.
    echo Execute: EXECUTAR_PROBE_DIRETO.bat
    echo.
    pause
    exit /b 1
)

echo Mostrando ultimas 50 linhas do log...
echo Pressione Ctrl+C para sair
echo.
echo ========================================
echo.

powershell -Command "Get-Content 'logs\probe.log' -Tail 50 -Wait"
