@echo off
REM ========================================
REM Desinstalador COMPLETO Coruja Probe
REM Remove TUDO incluindo codigo fonte
REM ========================================

title Desinstalar TUDO - Coruja Probe

color 0C
echo.
echo ========================================
echo   DESINSTALADOR COMPLETO
echo   *** REMOVE TUDO ***
echo ========================================
echo.
echo ATENCAO: Este script vai remover TUDO:
echo.
echo   - Tarefa agendada "CorujaProbe"
echo   - Processo Python da probe
echo   - Arquivos de configuracao
echo   - Logs da probe
echo   - Codigo fonte (probe_core.py)
echo   - Coletores (collectors/)
echo   - Dependencias (requirements.txt)
echo   - TODA A PASTA PROBE
echo.
echo ========================================
echo   *** ISSO NAO PODE SER DESFEITO ***
echo ========================================
echo.
set /p CONFIRM1="Tem certeza ABSOLUTA? (S/N): "

if /i not "%CONFIRM1%"=="S" (
    echo.
    echo Desinstalacao cancelada.
    echo.
    pause
    exit
)

echo.
echo Digite "REMOVER TUDO" para confirmar:
set /p CONFIRM2="> "

if not "%CONFIRM2%"=="REMOVER TUDO" (
    echo.
    echo Confirmacao incorreta. Desinstalacao cancelada.
    echo.
    pause
    exit
)

REM ========================================
REM Verificar Admin
REM ========================================
cls
echo.
echo [1/7] Verificando privilegios...
net session >nul 2>&1
if %errorLevel% neq 0 (
    color 0C
    echo.
    echo [ERRO] Execute como Administrador!
    echo.
    pause
    exit
)
echo [OK] Privilegios verificados
timeout /t 2 >nul

REM ========================================
REM Parar Probe
REM ========================================
cls
echo.
echo [2/7] Parando probe...
echo.

tasklist | findstr python >nul 2>&1
if %errorLevel% equ 0 (
    echo Parando processos Python...
    taskkill /F /IM python.exe >nul 2>&1
    timeout /t 2 >nul
    echo [OK] Probe parada
) else (
    echo [INFO] Probe nao estava rodando
)
timeout /t 2 >nul

REM ========================================
REM Remover Tarefa Agendada
REM ========================================
cls
echo.
echo [3/7] Removendo tarefa agendada...
echo.

schtasks /query /tn "CorujaProbe" >nul 2>&1
if %errorLevel% equ 0 (
    echo Removendo tarefa "CorujaProbe"...
    schtasks /delete /tn "CorujaProbe" /f >nul 2>&1
    echo [OK] Tarefa agendada removida
) else (
    echo [INFO] Tarefa agendada nao encontrada
)
timeout /t 2 >nul

REM ========================================
REM Backup da Pasta (Opcional)
REM ========================================
cls
echo.
echo [4/7] Backup da pasta probe...
echo.
set /p BACKUP="Deseja fazer backup antes de remover? (S/N): "

if /i "%BACKUP%"=="S" (
    set BACKUP_NAME=probe_backup_%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%%time:~6,2%
    set BACKUP_NAME=%BACKUP_NAME: =0%
    echo.
    echo Criando backup: %BACKUP_NAME%.zip
    echo.
    echo [INFO] Backup manual necessario
    echo Copie a pasta probe para outro local antes de continuar
    echo.
    pause
) else (
    echo [INFO] Backup ignorado
)
timeout /t 2 >nul

REM ========================================
REM Listar Arquivos a Remover
REM ========================================
cls
echo.
echo [5/7] Listando arquivos a remover...
echo.

echo Arquivos de configuracao:
if exist probe_config.json echo   - probe_config.json
if exist wmi_credentials.json echo   - wmi_credentials.json
if exist probe.log echo   - probe.log

echo.
echo Codigo fonte:
if exist probe_core.py echo   - probe_core.py
if exist config.py echo   - config.py
if exist discovery_server.py echo   - discovery_server.py

echo.
echo Pastas:
if exist collectors\ echo   - collectors/
if exist logs\ echo   - logs/
if exist __pycache__\ echo   - __pycache__/

echo.
timeout /t 3 >nul

REM ========================================
REM Remover Arquivos
REM ========================================
cls
echo.
echo [6/7] Removendo arquivos...
echo.

REM Configuracoes
if exist probe_config.json del /f /q probe_config.json >nul 2>&1
if exist wmi_credentials.json del /f /q wmi_credentials.json >nul 2>&1
if exist probe.log del /f /q probe.log >nul 2>&1
echo [OK] Configuracoes removidas

REM Codigo fonte
if exist probe_core.py del /f /q probe_core.py >nul 2>&1
if exist config.py del /f /q config.py >nul 2>&1
if exist discovery_server.py del /f /q discovery_server.py >nul 2>&1
if exist probe_service.py del /f /q probe_service.py >nul 2>&1
echo [OK] Codigo fonte removido

REM Pastas
if exist collectors\ rmdir /s /q collectors >nul 2>&1
if exist logs\ rmdir /s /q logs >nul 2>&1
if exist __pycache__\ rmdir /s /q __pycache__ >nul 2>&1
echo [OK] Pastas removidas

REM Dependencias
if exist requirements.txt del /f /q requirements.txt >nul 2>&1
echo [OK] Dependencias removidas

timeout /t 2 >nul

REM ========================================
REM Verificacao Final
REM ========================================
cls
echo.
echo [7/7] Verificando remocao...
echo.

set CLEAN=1

REM Verificar tarefa
schtasks /query /tn "CorujaProbe" >nul 2>&1
if %errorLevel% equ 0 (
    echo [AVISO] Tarefa agendada ainda existe
    set CLEAN=0
) else (
    echo [OK] Tarefa agendada removida
)

REM Verificar processo
tasklist | findstr python >nul 2>&1
if %errorLevel% equ 0 (
    echo [AVISO] Processo Python ainda rodando
    set CLEAN=0
) else (
    echo [OK] Processo parado
)

REM Verificar arquivos principais
if exist probe_core.py (
    echo [AVISO] probe_core.py ainda existe
    set CLEAN=0
) else (
    echo [OK] probe_core.py removido
)

if exist collectors\ (
    echo [AVISO] collectors/ ainda existe
    set CLEAN=0
) else (
    echo [OK] collectors/ removido
)

timeout /t 2 >nul

REM ========================================
REM Resultado Final
REM ========================================
cls

if %CLEAN% equ 1 (
    color 0A
    echo.
    echo ========================================
    echo   REMOCAO COMPLETA COM SUCESSO!
    echo ========================================
    echo.
    echo Tudo foi removido:
    echo   - Tarefa agendada
    echo   - Processo
    echo   - Configuracoes
    echo   - Codigo fonte
    echo   - Coletores
    echo   - Logs
    echo.
    echo ========================================
    echo   ARQUIVOS MANTIDOS
    echo ========================================
    echo.
    echo Apenas os instaladores foram mantidos:
    echo   - install_*.bat
    echo   - desinstalar_*.bat
    echo   - verificar_*.bat
    echo   - README.md
    echo   - INSTALACAO.md
    echo.
    echo Para reinstalar do zero:
    echo   1. Copie a pasta probe novamente
    echo   2. Execute: install_completo_com_servico.bat
    echo.
) else (
    color 0E
    echo.
    echo ========================================
    echo   REMOCAO PARCIAL
    echo ========================================
    echo.
    echo Alguns itens nao foram removidos.
    echo Verifique os avisos acima.
    echo.
    echo Para remover manualmente a pasta inteira:
    echo   1. Feche esta janela
    echo   2. Va para a pasta pai
    echo   3. Delete a pasta probe
    echo.
)

echo ========================================
echo.
echo Pressione qualquer tecla para sair...
pause >nul
exit
