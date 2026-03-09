@echo off
REM ========================================
REM Desinstalador Completo Coruja Probe
REM Remove tudo: tarefa, processo, arquivos
REM ========================================

title Desinstalar Coruja Probe

color 0C
echo.
echo ========================================
echo   DESINSTALADOR CORUJA PROBE
echo ========================================
echo.
echo ATENCAO: Este script vai remover:
echo.
echo   - Tarefa agendada "CorujaProbe"
echo   - Processo Python da probe
echo   - Arquivos de configuracao
echo   - Logs da probe
echo.
echo ========================================
echo.
set /p CONFIRM="Tem certeza que deseja DESINSTALAR? (S/N): "

if /i not "%CONFIRM%"=="S" (
    echo.
    echo Desinstalacao cancelada.
    echo.
    pause
    exit
)

REM ========================================
REM Verificar Admin
REM ========================================
cls
echo.
echo [1/6] Verificando privilegios...
net session >nul 2>&1
if %errorLevel% neq 0 (
    color 0C
    echo.
    echo [ERRO] Execute como Administrador!
    echo.
    echo Clique com botao direito e escolha:
    echo "Executar como administrador"
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
echo [2/6] Parando probe...
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
echo [3/6] Removendo tarefa agendada...
echo.

schtasks /query /tn "CorujaProbe" >nul 2>&1
if %errorLevel% equ 0 (
    echo Removendo tarefa "CorujaProbe"...
    schtasks /delete /tn "CorujaProbe" /f >nul 2>&1
    if %errorLevel% equ 0 (
        echo [OK] Tarefa agendada removida
    ) else (
        echo [AVISO] Erro ao remover tarefa
    )
) else (
    echo [INFO] Tarefa agendada nao encontrada
)
timeout /t 2 >nul

REM ========================================
REM Remover Arquivos de Configuracao
REM ========================================
cls
echo.
echo [4/6] Removendo arquivos de configuracao...
echo.

set FILES_REMOVED=0

if exist probe_config.json (
    del /f /q probe_config.json >nul 2>&1
    echo [OK] probe_config.json removido
    set FILES_REMOVED=1
)

if exist wmi_credentials.json (
    del /f /q wmi_credentials.json >nul 2>&1
    echo [OK] wmi_credentials.json removido
    set FILES_REMOVED=1
)

if exist probe.log (
    del /f /q probe.log >nul 2>&1
    echo [OK] probe.log removido
    set FILES_REMOVED=1
)

if %FILES_REMOVED% equ 0 (
    echo [INFO] Nenhum arquivo de configuracao encontrado
)

timeout /t 2 >nul

REM ========================================
REM Remover Logs
REM ========================================
cls
echo.
echo [5/6] Removendo logs...
echo.

if exist logs\ (
    echo Removendo pasta logs...
    rmdir /s /q logs >nul 2>&1
    echo [OK] Pasta logs removida
) else (
    echo [INFO] Pasta logs nao encontrada
)

timeout /t 2 >nul

REM ========================================
REM Verificacao Final
REM ========================================
cls
echo.
echo [6/6] Verificando remocao...
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

REM Verificar arquivos
if exist probe_config.json (
    echo [AVISO] probe_config.json ainda existe
    set CLEAN=0
) else (
    echo [OK] probe_config.json removido
)

if exist wmi_credentials.json (
    echo [AVISO] wmi_credentials.json ainda existe
    set CLEAN=0
) else (
    echo [OK] wmi_credentials.json removido
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
    echo   DESINSTALACAO CONCLUIDA COM SUCESSO!
    echo ========================================
    echo.
    echo A probe foi completamente removida:
    echo   - Tarefa agendada removida
    echo   - Processo parado
    echo   - Arquivos de configuracao removidos
    echo   - Logs removidos
    echo.
    echo ========================================
    echo   ARQUIVOS MANTIDOS
    echo ========================================
    echo.
    echo Os seguintes arquivos foram mantidos:
    echo   - probe_core.py (codigo da probe)
    echo   - collectors/ (coletores)
    echo   - requirements.txt (dependencias)
    echo   - Instaladores (.bat)
    echo.
    echo Para reinstalar, execute:
    echo   install_completo_com_servico.bat
    echo.
) else (
    color 0E
    echo.
    echo ========================================
    echo   DESINSTALACAO PARCIAL
    echo ========================================
    echo.
    echo Alguns itens nao foram removidos.
    echo Verifique os avisos acima.
    echo.
    echo Para remover manualmente:
    echo.
    echo 1. Remover tarefa:
    echo    schtasks /delete /tn "CorujaProbe" /f
    echo.
    echo 2. Parar processo:
    echo    taskkill /F /IM python.exe
    echo.
    echo 3. Remover arquivos:
    echo    del probe_config.json
    echo    del wmi_credentials.json
    echo    del probe.log
    echo.
)

echo ========================================
echo.
echo Pressione qualquer tecla para sair...
pause >nul
exit
