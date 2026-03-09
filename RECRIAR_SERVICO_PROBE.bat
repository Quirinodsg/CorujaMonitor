@echo off
setlocal enabledelayedexpansion
title Recriar Servico Probe
color 0B

echo.
echo ========================================
echo   RECRIAR SERVICO PROBE
echo   Usando Task Scheduler
echo ========================================
echo.

REM Verificar admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    color 0C
    echo [ERRO] Execute como Administrador!
    pause
    exit /b 1
)

echo [1/4] Removendo servico antigo...
echo.

sc query CorujaProbe >nul 2>&1
if !errorLevel! equ 0 (
    net stop CorujaProbe >nul 2>&1
    timeout /t 2 /nobreak >nul
    sc delete CorujaProbe >nul 2>&1
    timeout /t 2 /nobreak >nul
    echo [OK] Servico antigo removido
) else (
    echo [OK] Nenhum servico existente
)

echo.
echo [2/4] Detectando Python...
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

color 0C
echo [ERRO] Python nao encontrado!
pause
exit /b 1

:python_found
echo [OK] Python: !PYTHON_EXE!
echo.

echo [3/4] Criando tarefa agendada...
echo.

REM Remover tarefa existente
schtasks /Delete /TN "CorujaProbe" /F >nul 2>&1

REM Criar nova tarefa que inicia com o Windows
schtasks /Create /TN "CorujaProbe" /TR "\"!PYTHON_EXE!\" \"C:\Program Files\CorujaMonitor\Probe\probe_core.py\"" /SC ONSTART /RU SYSTEM /RL HIGHEST /F >nul 2>&1

if !errorLevel! equ 0 (
    echo [OK] Tarefa criada com sucesso
) else (
    color 0C
    echo [ERRO] Falha ao criar tarefa
    pause
    exit /b 1
)

echo.
echo [4/4] Iniciando probe...
echo.

REM Iniciar a tarefa agora
schtasks /Run /TN "CorujaProbe" >nul 2>&1

timeout /t 3 /nobreak >nul

REM Verificar se esta rodando
tasklist /FI "IMAGENAME eq python.exe" 2>NUL | find /I /N "python.exe">NUL
if !errorLevel! equ 0 (
    color 0A
    echo [OK] Probe iniciada!
) else (
    color 0E
    echo [AVISO] Probe pode nao ter iniciado
)

echo.
color 0A
echo ========================================
echo   PROBE CONFIGURADA!
echo ========================================
echo.
echo Metodo: Task Scheduler (Tarefa Agendada)
echo Nome: CorujaProbe
echo Inicio: Automatico (com o Windows)
echo Usuario: SYSTEM
echo.
echo ========================================
echo   COMANDOS UTEIS
echo ========================================
echo.
echo Iniciar probe:
echo   schtasks /Run /TN "CorujaProbe"
echo.
echo Parar probe:
echo   taskkill /F /IM python.exe
echo.
echo Ver status:
echo   schtasks /Query /TN "CorujaProbe"
echo.
echo Remover tarefa:
echo   schtasks /Delete /TN "CorujaProbe" /F
echo.
echo Ver logs:
echo   C:\Program Files\CorujaMonitor\Probe\logs\probe.log
echo.
echo ========================================
echo.
pause
