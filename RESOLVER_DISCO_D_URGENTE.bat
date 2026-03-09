@echo off
chcp 65001 >nul
cls
echo ════════════════════════════════════════════════════════════════
echo   RESOLVER DISCO D - URGENTE
echo ════════════════════════════════════════════════════════════════
echo.
echo Este script vai:
echo   1. Parar a probe
echo   2. Copiar disk_collector.py atualizado (filtrar CD-ROM)
echo   3. Reiniciar a probe
echo.
echo IMPORTANTE: Execute na máquina de produção!
echo.
pause

echo.
echo ════════════════════════════════════════════════════════════════
echo   PASSO 1: Parar probe
echo ════════════════════════════════════════════════════════════════
echo.

cd "C:\Program Files\CorujaMonitor\Probe"

echo Procurando processo da probe...
tasklist /FI "IMAGENAME eq python.exe" | find /I "python.exe" >nul

if %errorLevel% equ 0 (
    echo Parando probe...
    taskkill /F /IM python.exe >nul 2>&1
    timeout /t 3 /nobreak >nul
    echo [OK] Probe parada
) else (
    echo [OK] Probe não estava rodando
)

echo.
echo ════════════════════════════════════════════════════════════════
echo   PASSO 2: Copiar disk_collector.py atualizado
echo ════════════════════════════════════════════════════════════════
echo.

set "ORIGEM=C:\Users\andre.quirino\Coruja\probe\collectors\disk_collector.py"
set "DESTINO=C:\Program Files\CorujaMonitor\Probe\collectors\disk_collector.py"

if not exist "%ORIGEM%" (
    echo [ERRO] Arquivo origem não encontrado: %ORIGEM%
    echo.
    echo Execute este script na máquina de desenvolvimento!
    pause
    exit /b 1
)

echo Copiando arquivo...
copy /Y "%ORIGEM%" "%DESTINO%"

if %errorLevel% equ 0 (
    echo [OK] Arquivo copiado com sucesso!
) else (
    echo [ERRO] Falha ao copiar arquivo
    pause
    exit /b 1
)

echo.
echo ════════════════════════════════════════════════════════════════
echo   PASSO 3: Reiniciar probe
echo ════════════════════════════════════════════════════════════════
echo.

echo Iniciando probe...
start "" "C:\Program Files\CorujaMonitor\Probe\INICIAR_PROBE.bat"

timeout /t 5 /nobreak >nul

echo.
echo ════════════════════════════════════════════════════════════════
echo   CONCLUÍDO!
echo ════════════════════════════════════════════════════════════════
echo.
echo ✓ Probe parada
echo ✓ disk_collector.py atualizado (CD-ROM filtrado)
echo ✓ Probe reiniciada
echo.
echo AGORA:
echo   1. Aguarde 60 segundos
echo   2. Recarregue dashboard (Ctrl+F5)
echo   3. DISCO D não deve aparecer mais
echo.
echo Se DISCO D ainda aparecer:
echo   - Aguarde mais 60 segundos (intervalo de coleta)
echo   - Verifique logs: type logs\probe.log
echo.
echo ════════════════════════════════════════════════════════════════
pause
