@echo off
chcp 65001 >nul
cls
echo ════════════════════════════════════════════════════════════════
echo   REINICIAR PROBE - APLICAR FILTRO CD-ROM
echo ════════════════════════════════════════════════════════════════
echo.
echo Este script vai:
echo   1. Parar a probe
echo   2. Reiniciar a probe
echo.
echo IMPORTANTE: Você já deve ter copiado disk_collector.py manualmente!
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
echo   PASSO 2: Reiniciar probe
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
echo ✓ Probe reiniciada com filtro de CD-ROM
echo.
echo AGORA:
echo   1. Aguarde 60 segundos
echo   2. Recarregue dashboard (Ctrl+F5)
echo   3. DISCO D não deve aparecer mais
echo.
echo Se DISCO D ainda aparecer:
echo   - Aguarde mais 60 segundos (intervalo de coleta)
echo   - Verifique se disk_collector.py foi copiado corretamente
echo   - Verifique logs: type logs\probe.log
echo.
echo ════════════════════════════════════════════════════════════════
pause
