@echo off
REM ========================================
REM Testar Servico da Probe
REM ========================================

echo ========================================
echo   TESTE DO SERVICO CORUJA PROBE
echo ========================================
echo.

echo [1/6] Verificando privilegios...
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [AVISO] Nao esta executando como Administrador
    echo Alguns testes podem falhar
) else (
    echo [OK] Executando como Administrador
)
echo.

echo [2/6] Verificando Python...
python --version >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Python instalado
    python --version
) else (
    echo [ERRO] Python nao encontrado!
    echo Instale de: https://www.python.org/downloads/
)
echo.

echo [3/6] Verificando arquivos...
if exist "probe_core.py" (
    echo [OK] probe_core.py encontrado
) else (
    echo [ERRO] probe_core.py nao encontrado
)

if exist "probe_config.json" (
    echo [OK] probe_config.json encontrado
) else (
    echo [AVISO] probe_config.json nao encontrado
    echo Execute: install.bat
)

if exist "requirements.txt" (
    echo [OK] requirements.txt encontrado
) else (
    echo [ERRO] requirements.txt nao encontrado
)
echo.

echo [4/6] Verificando servicos instalados...
echo.

REM Task Scheduler
schtasks /query /tn "CorujaMonitorProbe" >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Task Scheduler: INSTALADO
    schtasks /query /tn "CorujaMonitorProbe" /fo list | findstr "Status:"
    set TASK_INSTALLED=1
) else (
    echo [INFO] Task Scheduler: NAO INSTALADO
    set TASK_INSTALLED=0
)

echo.

REM Servico Windows
nssm status CorujaProbe >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Servico Windows: INSTALADO
    nssm status CorujaProbe
    set SERVICE_INSTALLED=1
) else (
    echo [INFO] Servico Windows: NAO INSTALADO
    set SERVICE_INSTALLED=0
)

echo.

if %TASK_INSTALLED%==0 if %SERVICE_INSTALLED%==0 (
    echo [AVISO] Nenhum servico instalado!
    echo.
    echo Para instalar, execute:
    echo   install_service.bat
    echo.
)

echo [5/6] Verificando se probe esta rodando...
tasklist | findstr python.exe >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Processo Python encontrado
    echo.
    echo Processos Python rodando:
    wmic process where "name='python.exe'" get commandline,processid 2>nul
) else (
    echo [INFO] Nenhum processo Python rodando
)
echo.

echo [6/6] Verificando logs...
if exist "logs\probe.log" (
    echo [OK] Log encontrado
    echo.
    echo Ultimas 10 linhas do log:
    echo ----------------------------------------
    powershell Get-Content logs\probe.log -Tail 10 2>nul
    echo ----------------------------------------
) else (
    echo [INFO] Log nao encontrado
    echo Probe ainda nao foi executada
)
echo.

echo ========================================
echo RESUMO DO TESTE
echo ========================================
echo.

if %TASK_INSTALLED%==1 (
    echo ✅ Servico instalado: Task Scheduler
) else if %SERVICE_INSTALLED%==1 (
    echo ✅ Servico instalado: Windows Service
) else (
    echo ❌ Nenhum servico instalado
)

tasklist | findstr python.exe >nul 2>&1
if %errorLevel% equ 0 (
    echo ✅ Probe rodando
) else (
    echo ❌ Probe nao esta rodando
)

if exist "probe_config.json" (
    echo ✅ Configuracao OK
) else (
    echo ❌ Configuracao faltando
)

echo.
echo ========================================
echo ACOES RECOMENDADAS
echo ========================================
echo.

if %TASK_INSTALLED%==0 if %SERVICE_INSTALLED%==0 (
    echo 1. Instalar servico:
    echo    install_service.bat
    echo.
)

tasklist | findstr python.exe >nul 2>&1
if %errorLevel% neq 0 (
    if %TASK_INSTALLED%==1 (
        echo 2. Iniciar probe:
        echo    schtasks /run /tn "CorujaMonitorProbe"
        echo.
    ) else if %SERVICE_INSTALLED%==1 (
        echo 2. Iniciar probe:
        echo    nssm start CorujaProbe
        echo.
    ) else (
        echo 2. Iniciar probe manualmente:
        echo    python probe_core.py
        echo.
    )
)

if not exist "probe_config.json" (
    echo 3. Configurar probe:
    echo    install.bat
    echo.
)

echo ========================================
echo.
pause
exit /b 0
