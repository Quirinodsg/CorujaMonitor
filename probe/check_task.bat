@echo off
title Verificar Tarefa do Probe
color 0A

echo.
echo ========================================
echo   STATUS DA TAREFA
echo ========================================
echo.

echo [1] Verificando se a tarefa existe:
schtasks /query /tn "CorujaProbe" /fo LIST /v
echo.

echo [2] Verificando se Python esta rodando:
tasklist | findstr python
echo.

echo [3] Verificando log do probe:
if exist probe.log (
    echo === Ultimas 30 linhas do probe.log ===
    powershell -Command "Get-Content probe.log -Tail 30"
) else (
    echo [AVISO] probe.log nao encontrado
)
echo.

echo [4] Testando manualmente:
echo Executando probe por 10 segundos...
timeout /t 2 /nobreak
start /B python probe_core.py
timeout /t 10 /nobreak
taskkill /F /IM python.exe 2>nul
echo.

echo [5] Verificando log apos teste:
if exist probe.log (
    powershell -Command "Get-Content probe.log -Tail 10"
)
echo.

pause
