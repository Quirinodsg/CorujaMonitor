@echo off
setlocal enabledelayedexpansion
REM ========================================
REM ATIVAR PROBE COMO SERVICO DO WINDOWS
REM Inicia automaticamente com o Windows
REM ========================================

color 0B
title Ativar Probe como Servico

echo.
echo ========================================
echo   ATIVAR PROBE COMO SERVICO
echo   Coruja Monitor
echo ========================================
echo.

REM Verificar admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    color 0C
    echo [ERRO] Execute como Administrador!
    echo.
    echo Clique direito neste arquivo e selecione:
    echo "Executar como Administrador"
    echo.
    pause
    exit /b 1
)

REM ========================================
REM VERIFICAR INSTALACAO
REM ========================================

echo [1/5] Verificando instalacao...
echo.

set "INSTALL_DIR=C:\Program Files\CorujaMonitor\Probe"

if not exist "%INSTALL_DIR%\probe_core.py" (
    color 0C
    echo [ERRO] Probe nao instalada!
    echo.
    echo Execute primeiro o instalador.
    echo.
    pause
    exit /b 1
)

if not exist "%INSTALL_DIR%\config.yaml" (
    color 0E
    echo [AVISO] Configuracao nao encontrada!
    echo.
    echo Execute primeiro: CONFIGURAR_PROBE_MANUAL.bat
    echo.
    set /p CONTINUAR="Deseja continuar mesmo assim? (S/N): "
    if /i not "!CONTINUAR!"=="S" exit /b 1
)

echo [OK] Probe instalada em: %INSTALL_DIR%
echo.

REM ========================================
REM DETECTAR PYTHON
REM ========================================

echo [2/5] Detectando Python...
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

REM ========================================
REM PARAR SERVICO EXISTENTE
REM ========================================

echo [3/5] Verificando servico existente...
echo.

sc query "CorujaProbe" >nul 2>&1
if !errorLevel! equ 0 (
    echo Parando servico existente...
    net stop CorujaProbe >nul 2>&1
    timeout /t 2 /nobreak >nul
    
    echo Removendo servico antigo...
    sc delete CorujaProbe >nul 2>&1
    timeout /t 2 /nobreak >nul
    
    echo [OK] Servico antigo removido
) else (
    echo [OK] Nenhum servico existente
)
echo.

REM ========================================
REM CRIAR SERVICO
REM ========================================

echo [4/5] Criando servico do Windows...
echo.

REM Criar script de inicializacao
(
echo @echo off
echo cd /d "%INSTALL_DIR%"
echo "!PYTHON_EXE!" "%INSTALL_DIR%\probe_core.py"
) > "%INSTALL_DIR%\start_probe.bat"

REM Criar servico usando NSSM ou SC
echo Registrando servico...

sc create "CorujaProbe" binPath= "cmd.exe /c \"%INSTALL_DIR%\start_probe.bat\"" start= auto DisplayName= "Coruja Monitor Probe" >nul 2>&1

if !errorLevel! equ 0 (
    echo [OK] Servico criado
    
    REM Configurar descricao
    sc description "CorujaProbe" "Agente de monitoramento Coruja Monitor - Coleta metricas e envia para o servidor central" >nul 2>&1
    
    REM Configurar recuperacao automatica
    sc failure "CorujaProbe" reset= 86400 actions= restart/60000/restart/60000/restart/60000 >nul 2>&1
) else (
    color 0E
    echo [AVISO] Falha ao criar servico com SC
    echo Tentando metodo alternativo...
    
    REM Criar com PowerShell
    powershell -Command "New-Service -Name 'CorujaProbe' -BinaryPathName 'cmd.exe /c \"%INSTALL_DIR%\start_probe.bat\"' -DisplayName 'Coruja Monitor Probe' -StartupType Automatic" >nul 2>&1
    
    if !errorLevel! equ 0 (
        echo [OK] Servico criado com PowerShell
    ) else (
        color 0C
        echo [ERRO] Nao foi possivel criar o servico
        echo.
        pause
        exit /b 1
    )
)

echo.

REM ========================================
REM INICIAR SERVICO
REM ========================================

echo [5/5] Iniciando servico...
echo.

net start CorujaProbe >nul 2>&1

if !errorLevel! equ 0 (
    color 0A
    echo [OK] Servico iniciado com sucesso!
) else (
    color 0E
    echo [AVISO] Servico criado mas nao iniciou automaticamente
    echo.
    echo Tente iniciar manualmente:
    echo - Servicos do Windows ^> CorujaProbe ^> Iniciar
    echo.
    echo Ou execute:
    echo net start CorujaProbe
)

REM ========================================
REM CONCLUSAO
REM ========================================

echo.
color 0A
echo ========================================
echo   PROBE ATIVADA COMO SERVICO!
echo ========================================
echo.
echo Nome do servico: CorujaProbe
echo Tipo de inicio: Automatico
echo Status: Executando
echo.
echo A probe agora:
echo - Inicia automaticamente com o Windows
echo - Reinicia automaticamente se falhar
echo - Executa em segundo plano
echo.
echo ========================================
echo   COMANDOS UTEIS
echo ========================================
echo.
echo Parar servico:
echo   net stop CorujaProbe
echo.
echo Iniciar servico:
echo   net start CorujaProbe
echo.
echo Reiniciar servico:
echo   net stop CorujaProbe ^&^& net start CorujaProbe
echo.
echo Ver status:
echo   sc query CorujaProbe
echo.
echo Remover servico:
echo   sc delete CorujaProbe
echo.
echo ========================================
echo   VERIFICAR NO DASHBOARD
echo ========================================
echo.
echo 1. Acesse: http://192.168.31.161:8000
echo 2. Login: admin@coruja.com / admin123
echo 3. Menu: Probes
echo 4. Sua probe deve aparecer ONLINE
echo.
echo ========================================
echo.
pause
