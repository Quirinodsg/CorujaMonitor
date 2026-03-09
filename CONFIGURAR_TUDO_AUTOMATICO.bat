@echo off
setlocal enabledelayedexpansion
title Configurar Probe Automaticamente
color 0E

echo.
echo ========================================
echo   CONFIGURAR PROBE AUTOMATICAMENTE
echo   Tudo em um script!
echo ========================================
echo.

REM Verificar admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    color 0C
    echo [ERRO] Execute como Administrador!
    echo.
    echo Clique com botao DIREITO e escolha:
    echo "Executar como administrador"
    echo.
    pause
    exit /b 1
)

echo [1/4] Verificando Python...
echo.

set "PYTHON_EXE="

python --version >nul 2>&1
if !errorLevel! equ 0 (
    set "PYTHON_EXE=python"
    goto :python_found
)

if exist "C:\Program Files\Python311\python.exe" (
    set "PYTHON_EXE=C:\Program Files\Python311\python.exe"
    goto :python_found
)

if exist "C:\Program Files\Python310\python.exe" (
    set "PYTHON_EXE=C:\Program Files\Python310\python.exe"
    goto :python_found
)

if exist "C:\Program Files\Python312\python.exe" (
    set "PYTHON_EXE=C:\Program Files\Python312\python.exe"
    goto :python_found
)

color 0C
echo [ERRO] Python nao encontrado!
pause
exit /b 1

:python_found
echo [OK] Python: !PYTHON_EXE!
"!PYTHON_EXE!" --version
echo.

echo [2/4] Corrigindo config.yaml da probe...
echo.

cd /d "C:\Program Files\CorujaMonitor\Probe"

if not exist "probe_core.py" (
    color 0C
    echo [ERRO] Probe nao instalada!
    echo Execute primeiro: INSTALAR_PROBE_V2.bat
    pause
    exit /b 1
)

REM Criar backup
if exist "config.yaml" (
    copy /Y "config.yaml" "config.yaml.bak" >nul
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

echo [3/4] Adicionando servidor no dashboard...
echo.

cd /d "%~dp0"
"!PYTHON_EXE!" adicionar_servidor_automatico.py

if !errorLevel! neq 0 (
    echo.
    echo [AVISO] Erro ao adicionar servidor automaticamente
    echo Pode ser que o servidor ja exista
    echo.
)

echo.
echo [4/4] Iniciando probe...
echo.

color 0A
echo ========================================
echo   CONFIGURACAO CONCLUIDA!
echo ========================================
echo.
echo A probe vai iniciar agora.
echo.
echo Mantenha a janela ABERTA para ver os logs.
echo.
echo Aguarde 60-90 segundos e acesse:
echo http://192.168.31.161:3000
echo.
echo Menu: Servidores ^> WIN-15GM8UTRS4K
echo.
echo ========================================
echo.
pause

cd /d "C:\Program Files\CorujaMonitor\Probe"
"!PYTHON_EXE!" probe_core.py

pause
