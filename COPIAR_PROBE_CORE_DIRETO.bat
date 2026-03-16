@echo off
echo ========================================
echo COPIAR PROBE_CORE.PY - VERSAO DIRETA
echo ========================================
echo.
echo IMPORTANTE: Execute este script no NOTEBOOK (DESKTOP-P9VGN04)
echo NAO execute na SRVSONDA001!
echo.

REM Verificar se estamos no diretorio correto
if not exist "probe\probe_core.py" (
    echo ERRO: Arquivo probe\probe_core.py nao encontrado!
    echo.
    echo Voce esta em: %CD%
    echo.
    echo Execute este script de: C:\Users\andre.quirino\Coruja Monitor
    echo.
    pause
    exit /b 1
)

echo Origem: %CD%\probe\probe_core.py
echo Destino: \\SRVSONDA001\C$\Program Files\CorujaMonitor\Probe\probe_core.py
echo.

REM Parar servico primeiro
echo Parando servico CorujaProbe...
sc \\SRVSONDA001 stop CorujaProbe
timeout /t 3 /nobreak

REM Copiar arquivo
echo.
echo Copiando arquivo...
copy /Y "probe\probe_core.py" "\\SRVSONDA001\C$\Program Files\CorujaMonitor\Probe\probe_core.py"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERRO ao copiar! Verifique:
    echo 1. Acesso de rede a SRVSONDA001
    echo 2. Permissoes de escrita
    echo 3. Caminho correto
    pause
    exit /b 1
)

echo OK - Arquivo copiado!
echo.

REM Iniciar servico
echo Iniciando servico CorujaProbe...
sc \\SRVSONDA001 start CorujaProbe

echo.
echo ========================================
echo SUCESSO!
echo ========================================
echo.
echo Aguarde 60 segundos e verifique os logs.
echo.

pause
