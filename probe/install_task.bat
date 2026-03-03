@echo off
title Instalar Probe como Tarefa Agendada
color 0A

:: Check admin rights
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERRO] Execute como Administrador!
    pause
    exit /b 1
)

echo.
echo ========================================
echo   INSTALAR PROBE COMO TAREFA AGENDADA
echo ========================================
echo.
echo Esta e uma alternativa ao servico Windows
echo que funciona de forma mais confiavel.
echo.

echo [1] Parando servico antigo (se existir)...
net stop CorujaProbe 2>nul
sc delete CorujaProbe 2>nul

echo [2] Removendo tarefa antiga (se existir)...
schtasks /delete /tn "CorujaProbe" /f 2>nul

echo [3] Obtendo caminho do Python...
for /f "delims=" %%i in ('where python') do set PYTHON_PATH=%%i
echo Python: %PYTHON_PATH%

echo [4] Obtendo diretorio atual...
set PROBE_DIR=%~dp0
echo Diretorio: %PROBE_DIR%

echo [5] Criando tarefa agendada...
schtasks /create /tn "CorujaProbe" /tr "\"%PYTHON_PATH%\" \"%PROBE_DIR%probe_core.py\"" /sc onstart /ru SYSTEM /rl HIGHEST /f

if errorlevel 1 (
    echo [ERRO] Falha ao criar tarefa!
    pause
    exit /b 1
)

echo [OK] Tarefa criada com sucesso!
echo.

echo [6] Iniciando tarefa...
schtasks /run /tn "CorujaProbe"

echo.
echo [7] Aguardando 5 segundos...
timeout /t 5 /nobreak

echo.
echo [8] Verificando se esta rodando...
tasklist | findstr python

echo.
echo [9] Verificando logs...
if exist probe.log (
    echo === Ultimas linhas do probe.log ===
    powershell -Command "Get-Content probe.log -Tail 10"
) else (
    echo [AVISO] probe.log ainda nao foi criado
)

echo.
echo ========================================
echo   CONCLUIDO
echo ========================================
echo.
echo O probe agora roda como tarefa agendada
echo e inicia automaticamente com o Windows.
echo.
echo Para parar: schtasks /end /tn "CorujaProbe"
echo Para remover: schtasks /delete /tn "CorujaProbe" /f
echo.
echo Aguarde 1 minuto e verifique no frontend
echo se o probe ficou VERDE.
echo.
pause
