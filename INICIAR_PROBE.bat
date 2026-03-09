@echo off
title Iniciar Probe Coruja
color 0B

echo.
echo ========================================
echo   INICIAR PROBE CORUJA
echo ========================================
echo.

REM Verificar admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    color 0C
    echo [ERRO] Execute como Administrador!
    echo.
    pause
    exit /b 1
)

echo Iniciando servico CorujaProbe...
echo.

net start CorujaProbe

if %errorLevel% equ 0 (
    color 0A
    echo.
    echo ========================================
    echo   PROBE INICIADA COM SUCESSO!
    echo ========================================
    echo.
    echo Status: Executando
    echo.
    echo Aguarde 60 segundos para a primeira coleta
    echo.
    echo Verificar no dashboard:
    echo http://192.168.31.161:8000
    echo Menu: Probes
    echo.
    echo Ver logs em tempo real:
    echo powershell -Command "Get-Content 'C:\Program Files\CorujaMonitor\Probe\logs\probe.log' -Wait"
    echo.
) else (
    color 0C
    echo.
    echo ========================================
    echo   ERRO AO INICIAR PROBE
    echo ========================================
    echo.
    echo Possíveis causas:
    echo - Python não encontrado
    echo - Dependências faltando
    echo - Erro no config.yaml
    echo.
    echo Execute: DIAGNOSTICAR_PROBE.bat
    echo.
)

echo ========================================
echo.
pause
