@echo off
REM ========================================
REM Instalar Probe como Servico do Windows
REM Inicia automaticamente com o sistema
REM ========================================

echo ========================================
echo   CORUJA MONITOR - INSTALAR SERVICO
echo ========================================
echo.

REM Verificar admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERRO: Execute como Administrador!
    echo Clique com botao direito e "Executar como administrador"
    pause
    exit /b 1
)

echo [OK] Privilegios de administrador verificados
echo.

REM Obter diretorio atual
set "PROBE_DIR=%~dp0"
set "PROBE_DIR=%PROBE_DIR:~0,-1%"

echo Diretorio da probe: %PROBE_DIR%
echo.

REM Verificar se Python esta instalado
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ERRO: Python nao encontrado!
    echo.
    echo Instale Python 3.8+ de: https://www.python.org/downloads/
    echo.
    echo IMPORTANTE: Marque "Add Python to PATH" durante instalacao
    pause
    exit /b 1
)

echo [OK] Python encontrado
python --version
echo.

REM Verificar se probe_core.py existe
if not exist "%PROBE_DIR%\probe_core.py" (
    echo ERRO: probe_core.py nao encontrado em %PROBE_DIR%
    echo.
    echo Certifique-se de executar este script da pasta probe/
    pause
    exit /b 1
)

echo [OK] probe_core.py encontrado
echo.

REM Verificar se probe_config.json existe
if not exist "%PROBE_DIR%\probe_config.json" (
    echo AVISO: probe_config.json nao encontrado!
    echo.
    echo Execute primeiro: install.bat
    echo Para configurar a probe antes de instalar o servico.
    echo.
    set /p CONTINUE="Deseja continuar mesmo assim? (S/N): "
    if /i not "%CONTINUE%"=="S" (
        echo.
        echo Instalacao cancelada.
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo ESCOLHA O METODO DE INSTALACAO
echo ========================================
echo.
echo 1. Task Scheduler (Recomendado)
echo    - Nativo do Windows
echo    - Mais simples
echo    - Inicia com o usuario logado
echo.
echo 2. Servico Windows (Avancado)
echo    - Requer NSSM
echo    - Inicia antes do login
echo    - Mais robusto
echo.
echo 0. Cancelar
echo.
set /p METODO="Escolha o metodo (1 ou 2): "

if "%METODO%"=="1" goto TASK_SCHEDULER
if "%METODO%"=="2" goto WINDOWS_SERVICE
if "%METODO%"=="0" goto END

echo Opcao invalida!
pause
exit /b 1

REM ========================================
REM METODO 1: TASK SCHEDULER
REM ========================================
:TASK_SCHEDULER
echo.
echo ========================================
echo INSTALANDO VIA TASK SCHEDULER
echo ========================================
echo.

REM Remover tarefa existente se houver
schtasks /delete /tn "CorujaMonitorProbe" /f >nul 2>&1

echo [1/3] Criando tarefa agendada...

REM Criar XML da tarefa
set "TASK_XML=%TEMP%\coruja_probe_task.xml"

(
echo ^<?xml version="1.0" encoding="UTF-16"?^>
echo ^<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task"^>
echo   ^<RegistrationInfo^>
echo     ^<Description^>Coruja Monitor Probe - Coleta metricas do sistema^</Description^>
echo     ^<URI^>\CorujaMonitorProbe^</URI^>
echo   ^</RegistrationInfo^>
echo   ^<Triggers^>
echo     ^<BootTrigger^>
echo       ^<Enabled^>true^</Enabled^>
echo       ^<Delay^>PT30S^</Delay^>
echo     ^</BootTrigger^>
echo     ^<LogonTrigger^>
echo       ^<Enabled^>true^</Enabled^>
echo       ^<Delay^>PT30S^</Delay^>
echo     ^</LogonTrigger^>
echo   ^</Triggers^>
echo   ^<Principals^>
echo     ^<Principal id="Author"^>
echo       ^<UserId^>S-1-5-18^</UserId^>
echo       ^<RunLevel^>HighestAvailable^</RunLevel^>
echo     ^</Principal^>
echo   ^</Principals^>
echo   ^<Settings^>
echo     ^<MultipleInstancesPolicy^>IgnoreNew^</MultipleInstancesPolicy^>
echo     ^<DisallowStartIfOnBatteries^>false^</DisallowStartIfOnBatteries^>
echo     ^<StopIfGoingOnBatteries^>false^</StopIfGoingOnBatteries^>
echo     ^<AllowHardTerminate^>false^</AllowHardTerminate^>
echo     ^<StartWhenAvailable^>true^</StartWhenAvailable^>
echo     ^<RunOnlyIfNetworkAvailable^>false^</RunOnlyIfNetworkAvailable^>
echo     ^<IdleSettings^>
echo       ^<StopOnIdleEnd^>false^</StopOnIdleEnd^>
echo       ^<RestartOnIdle^>false^</RestartOnIdle^>
echo     ^</IdleSettings^>
echo     ^<AllowStartOnDemand^>true^</AllowStartOnDemand^>
echo     ^<Enabled^>true^</Enabled^>
echo     ^<Hidden^>false^</Hidden^>
echo     ^<RunOnlyIfIdle^>false^</RunOnlyIfIdle^>
echo     ^<DisallowStartOnRemoteAppSession^>false^</DisallowStartOnRemoteAppSession^>
echo     ^<UseUnifiedSchedulingEngine^>true^</UseUnifiedSchedulingEngine^>
echo     ^<WakeToRun^>false^</WakeToRun^>
echo     ^<ExecutionTimeLimit^>PT0S^</ExecutionTimeLimit^>
echo     ^<Priority^>7^</Priority^>
echo     ^<RestartOnFailure^>
echo       ^<Interval^>PT1M^</Interval^>
echo       ^<Count^>3^</Count^>
echo     ^</RestartOnFailure^>
echo   ^</Settings^>
echo   ^<Actions Context="Author"^>
echo     ^<Exec^>
echo       ^<Command^>python^</Command^>
echo       ^<Arguments^>probe_core.py^</Arguments^>
echo       ^<WorkingDirectory^>%PROBE_DIR%^</WorkingDirectory^>
echo     ^</Exec^>
echo   ^</Actions^>
echo ^</Task^>
) > "%TASK_XML%"

echo [2/3] Registrando tarefa no sistema...
schtasks /create /tn "CorujaMonitorProbe" /xml "%TASK_XML%" /f

if %errorLevel% equ 0 (
    echo [OK] Tarefa criada com sucesso
) else (
    echo [ERRO] Falha ao criar tarefa
    del "%TASK_XML%" >nul 2>&1
    pause
    exit /b 1
)

del "%TASK_XML%" >nul 2>&1

echo [3/3] Iniciando probe...
schtasks /run /tn "CorujaMonitorProbe"

if %errorLevel% equ 0 (
    echo [OK] Probe iniciada
) else (
    echo [AVISO] Falha ao iniciar probe
)

echo.
echo ========================================
echo INSTALACAO CONCLUIDA!
echo ========================================
echo.
echo A probe foi instalada como tarefa agendada.
echo.
echo Ela iniciara automaticamente:
echo - Quando o computador ligar (30s apos boot)
echo - Quando um usuario fizer login (30s apos login)
echo.
echo COMANDOS UTEIS:
echo.
echo Ver status:
echo   schtasks /query /tn "CorujaMonitorProbe"
echo.
echo Iniciar manualmente:
echo   schtasks /run /tn "CorujaMonitorProbe"
echo.
echo Parar:
echo   taskkill /f /im python.exe /fi "WINDOWTITLE eq probe_core.py"
echo.
echo Desinstalar:
echo   schtasks /delete /tn "CorujaMonitorProbe" /f
echo.
echo Ver logs:
echo   type "%PROBE_DIR%\logs\probe.log"
echo.
pause
goto END

REM ========================================
REM METODO 2: WINDOWS SERVICE (NSSM)
REM ========================================
:WINDOWS_SERVICE
echo.
echo ========================================
echo INSTALANDO COMO SERVICO WINDOWS
echo ========================================
echo.

REM Verificar se NSSM esta instalado
where nssm >nul 2>&1
if %errorLevel% neq 0 (
    echo NSSM nao encontrado!
    echo.
    echo Baixando NSSM...
    echo.
    
    REM Criar pasta temp
    if not exist "%TEMP%\nssm" mkdir "%TEMP%\nssm"
    
    echo NOTA: NSSM precisa ser baixado manualmente.
    echo.
    echo 1. Baixe de: https://nssm.cc/download
    echo 2. Extraia nssm.exe para: C:\Windows\System32\
    echo 3. Execute este script novamente
    echo.
    pause
    exit /b 1
)

echo [OK] NSSM encontrado
echo.

REM Parar servico se existir
nssm stop CorujaProbe >nul 2>&1
nssm remove CorujaProbe confirm >nul 2>&1

echo [1/4] Instalando servico...
nssm install CorujaProbe python "%PROBE_DIR%\probe_core.py"

if %errorLevel% neq 0 (
    echo [ERRO] Falha ao instalar servico
    pause
    exit /b 1
)

echo [OK] Servico instalado
echo.

echo [2/4] Configurando servico...
nssm set CorujaProbe AppDirectory "%PROBE_DIR%"
nssm set CorujaProbe DisplayName "Coruja Monitor Probe"
nssm set CorujaProbe Description "Coleta metricas do sistema para Coruja Monitor"
nssm set CorujaProbe Start SERVICE_AUTO_START
nssm set CorujaProbe AppStdout "%PROBE_DIR%\logs\service_stdout.log"
nssm set CorujaProbe AppStderr "%PROBE_DIR%\logs\service_stderr.log"
nssm set CorujaProbe AppRotateFiles 1
nssm set CorujaProbe AppRotateOnline 1
nssm set CorujaProbe AppRotateSeconds 86400
nssm set CorujaProbe AppRotateBytes 1048576

echo [OK] Servico configurado
echo.

echo [3/4] Iniciando servico...
nssm start CorujaProbe

if %errorLevel% equ 0 (
    echo [OK] Servico iniciado
) else (
    echo [AVISO] Falha ao iniciar servico
)

echo.
echo [4/4] Verificando status...
nssm status CorujaProbe

echo.
echo ========================================
echo INSTALACAO CONCLUIDA!
echo ========================================
echo.
echo A probe foi instalada como servico Windows.
echo.
echo COMANDOS UTEIS:
echo.
echo Ver status:
echo   nssm status CorujaProbe
echo   sc query CorujaProbe
echo.
echo Iniciar:
echo   nssm start CorujaProbe
echo   net start CorujaProbe
echo.
echo Parar:
echo   nssm stop CorujaProbe
echo   net stop CorujaProbe
echo.
echo Reiniciar:
echo   nssm restart CorujaProbe
echo.
echo Desinstalar:
echo   nssm remove CorujaProbe confirm
echo.
echo Ver logs:
echo   type "%PROBE_DIR%\logs\service_stdout.log"
echo   type "%PROBE_DIR%\logs\service_stderr.log"
echo.
pause
goto END

REM ========================================
REM FIM
REM ========================================
:END
echo.
echo Instalacao finalizada!
echo.
exit /b 0
