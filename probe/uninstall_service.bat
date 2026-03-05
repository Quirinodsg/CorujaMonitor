@echo off
REM ========================================
REM Desinstalar Servico da Probe
REM ========================================

echo ========================================
echo   DESINSTALAR SERVICO CORUJA PROBE
echo ========================================
echo.

REM Verificar admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERRO: Execute como Administrador!
    pause
    exit /b 1
)

echo [OK] Privilegios de administrador verificados
echo.

echo Verificando servicos instalados...
echo.

REM Verificar Task Scheduler
schtasks /query /tn "CorujaMonitorProbe" >nul 2>&1
if %errorLevel% equ 0 (
    echo [ENCONTRADO] Tarefa agendada: CorujaMonitorProbe
    set TASK_EXISTS=1
) else (
    set TASK_EXISTS=0
)

REM Verificar NSSM Service
nssm status CorujaProbe >nul 2>&1
if %errorLevel% equ 0 (
    echo [ENCONTRADO] Servico Windows: CorujaProbe
    set SERVICE_EXISTS=1
) else (
    set SERVICE_EXISTS=0
)

if %TASK_EXISTS%==0 if %SERVICE_EXISTS%==0 (
    echo.
    echo Nenhum servico da probe encontrado!
    echo.
    pause
    exit /b 0
)

echo.
set /p CONFIRM="Deseja desinstalar? (S/N): "
if /i not "%CONFIRM%"=="S" (
    echo.
    echo Operacao cancelada.
    pause
    exit /b 0
)

echo.

REM Desinstalar Task Scheduler
if %TASK_EXISTS%==1 (
    echo [1/2] Removendo tarefa agendada...
    schtasks /delete /tn "CorujaMonitorProbe" /f
    if %errorLevel% equ 0 (
        echo [OK] Tarefa removida
    ) else (
        echo [ERRO] Falha ao remover tarefa
    )
    echo.
)

REM Desinstalar NSSM Service
if %SERVICE_EXISTS%==1 (
    echo [2/2] Removendo servico Windows...
    nssm stop CorujaProbe >nul 2>&1
    nssm remove CorujaProbe confirm
    if %errorLevel% equ 0 (
        echo [OK] Servico removido
    ) else (
        echo [ERRO] Falha ao remover servico
    )
    echo.
)

echo ========================================
echo DESINSTALACAO CONCLUIDA
echo ========================================
echo.
echo A probe foi removida do inicio automatico.
echo.
echo Para iniciar manualmente:
echo   python probe_core.py
echo.
pause
exit /b 0
