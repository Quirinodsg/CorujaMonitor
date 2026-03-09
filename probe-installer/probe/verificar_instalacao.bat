@echo off
REM ========================================
REM Verificar Instalacao Completa
REM Verifica se probe foi instalada corretamente
REM ========================================

title Verificar Instalacao Coruja Probe
color 0B

echo.
echo ========================================
echo   VERIFICACAO DE INSTALACAO
echo   Coruja Monitor Probe
echo ========================================
echo.

REM ========================================
REM 1. Verificar Arquivos
REM ========================================
echo [1/6] Verificando arquivos de configuracao...
echo.

set ARQUIVOS_OK=1

if exist probe_config.json (
    echo [OK] probe_config.json encontrado
) else (
    echo [ERRO] probe_config.json NAO encontrado
    set ARQUIVOS_OK=0
)

if exist wmi_credentials.json (
    echo [OK] wmi_credentials.json encontrado
) else (
    echo [ERRO] wmi_credentials.json NAO encontrado
    set ARQUIVOS_OK=0
)

if exist probe_core.py (
    echo [OK] probe_core.py encontrado
) else (
    echo [ERRO] probe_core.py NAO encontrado
    set ARQUIVOS_OK=0
)

if exist requirements.txt (
    echo [OK] requirements.txt encontrado
) else (
    echo [ERRO] requirements.txt NAO encontrado
    set ARQUIVOS_OK=0
)

echo.
timeout /t 2 >nul

REM ========================================
REM 2. Verificar Python
REM ========================================
cls
echo.
echo [2/6] Verificando Python...
echo.

python --version >nul 2>&1
if %errorLevel% equ 0 (
    for /f "tokens=*" %%v in ('python --version') do echo [OK] %%v instalado
) else (
    echo [ERRO] Python NAO encontrado
    echo Instale Python 3.8+ de: https://www.python.org/downloads/
    set ARQUIVOS_OK=0
)

echo.
timeout /t 2 >nul

REM ========================================
REM 3. Verificar Dependencias
REM ========================================
cls
echo.
echo [3/6] Verificando dependencias Python...
echo.

pip show psutil >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] psutil instalado
) else (
    echo [AVISO] psutil NAO instalado
)

pip show httpx >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] httpx instalado
) else (
    echo [AVISO] httpx NAO instalado
)

pip show pywin32 >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] pywin32 instalado
) else (
    echo [AVISO] pywin32 NAO instalado
)

echo.
timeout /t 2 >nul

REM ========================================
REM 4. Verificar Tarefa Agendada
REM ========================================
cls
echo.
echo [4/6] Verificando tarefa agendada...
echo.

schtasks /query /tn "CorujaProbe" >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Tarefa "CorujaProbe" encontrada
    echo.
    echo Detalhes da tarefa:
    schtasks /query /tn "CorujaProbe" /fo LIST | findstr /C:"Status" /C:"Proxima"
) else (
    echo [AVISO] Tarefa "CorujaProbe" NAO encontrada
    echo A probe nao vai iniciar automaticamente com o Windows
)

echo.
timeout /t 2 >nul

REM ========================================
REM 5. Verificar Probe Rodando
REM ========================================
cls
echo.
echo [5/6] Verificando se probe esta rodando...
echo.

tasklist | findstr python >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Python esta rodando
    echo.
    echo Processos Python ativos:
    tasklist | findstr python
) else (
    echo [AVISO] Python NAO esta rodando
    echo A probe pode nao estar ativa
)

echo.
timeout /t 2 >nul

REM ========================================
REM 6. Verificar Log
REM ========================================
cls
echo.
echo [6/6] Verificando log da probe...
echo.

if exist probe.log (
    echo [OK] probe.log encontrado
    echo.
    echo === Ultimas 20 linhas do log ===
    echo.
    powershell -Command "Get-Content probe.log -Tail 20"
) else (
    echo [AVISO] probe.log NAO encontrado
    echo A probe pode nao ter sido iniciada ainda
)

echo.
timeout /t 3 >nul

REM ========================================
REM Resumo Final
REM ========================================
cls
color 0A
echo.
echo ========================================
echo   RESUMO DA VERIFICACAO
echo ========================================
echo.

if %ARQUIVOS_OK% equ 1 (
    echo [OK] Arquivos de configuracao: OK
) else (
    echo [ERRO] Arquivos de configuracao: FALTANDO
)

python --version >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Python: INSTALADO
) else (
    echo [ERRO] Python: NAO INSTALADO
)

schtasks /query /tn "CorujaProbe" >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Tarefa agendada: CRIADA
) else (
    echo [AVISO] Tarefa agendada: NAO CRIADA
)

tasklist | findstr python >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Probe: RODANDO
) else (
    echo [AVISO] Probe: NAO RODANDO
)

echo.
echo ========================================
echo   PROXIMOS PASSOS
echo ========================================
echo.

if %ARQUIVOS_OK% equ 0 (
    echo 1. Execute o instalador novamente:
    echo    install_completo_com_servico.bat
    echo.
)

tasklist | findstr python >nul 2>&1
if %errorLevel% neq 0 (
    echo 2. Inicie a probe manualmente:
    echo    start_probe.bat
    echo.
)

echo 3. Acesse o dashboard:
echo    http://192.168.0.9:3000
echo.
echo 4. Va em "Servidores" para ver os sensores
echo.
echo ========================================
echo.
echo Pressione qualquer tecla para sair...
pause >nul
exit
