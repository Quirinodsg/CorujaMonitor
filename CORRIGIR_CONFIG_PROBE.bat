@echo off
setlocal enabledelayedexpansion
title Corrigir Config Probe
color 0E

echo.
echo ========================================
echo   CORRIGIR CONFIG.YAML DA PROBE
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

cd /d "C:\Program Files\CorujaMonitor\Probe"

if not exist "probe_core.py" (
    color 0C
    echo [ERRO] Probe nao instalada!
    pause
    exit /b 1
)

echo DADOS ATUAIS:
echo.
echo IP do Servidor: 192.168.31.161
echo Token: qozrs7hP8ZcrzXc5odjHw60NVejB0RHIeTaFurorDE8
echo Nome da Probe: WIN-15GM8UTRS4K
echo.
echo ========================================
echo.
set /p CONFIRMA="Confirma estes dados? (S/N): "

if /i not "%CONFIRMA%"=="S" (
    echo.
    echo Operacao cancelada.
    pause
    exit /b 1
)

echo.
echo Criando config.yaml...

REM Criar backup
if exist "config.yaml" (
    copy /Y "config.yaml" "config.yaml.bak" >nul
    echo [OK] Backup criado: config.yaml.bak
)

REM Criar config.yaml correto
(
echo # Configuracao Coruja Monitor Probe
echo server:
echo   host: "192.168.31.161"
echo   port: 3000
echo   protocol: "http"
echo   token: "qozrs7hP8ZcrzXc5odjHw60NVejB0RHIeTaFurorDE8"
echo.
echo probe:
echo   name: "WIN-15GM8UTRS4K"
echo   location: ""
echo.
echo collection_interval: 60
echo.
echo logging:
echo   level: "INFO"
echo   file: "logs/probe.log"
echo   max_size_mb: 10
echo   backup_count: 5
echo.
echo collectors:
echo   system: true
echo   ping: true
echo   snmp: true
echo   docker: false
echo   kubernetes: false
echo   wmi_remote: false
) > config.yaml

echo [OK] config.yaml criado!
echo.

echo ========================================
echo   VERIFICANDO CONFIGURACAO
echo ========================================
echo.
type config.yaml
echo.
echo ========================================

color 0A
echo.
echo [OK] Configuracao corrigida!
echo.
echo ========================================
echo   PROXIMOS PASSOS
echo ========================================
echo.
echo 1. FECHE a janela da probe (se estiver rodando)
echo    Pressione Ctrl+C na janela preta
echo.
echo 2. EXECUTE novamente:
echo    EXECUTAR_PROBE_DIRETO.bat
echo.
echo 3. AGUARDE 60-90 segundos
echo.
echo 4. VERIFIQUE no dashboard se aparecem metricas
echo.
echo ========================================
echo.
pause
