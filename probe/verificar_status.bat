@echo off
title Verificar Status do Probe
color 0A

echo.
echo ========================================
echo   STATUS DO PROBE
echo ========================================
echo.

echo [1] Status do servico:
sc query CorujaProbe
echo.

echo [2] Verificando log do probe:
if exist probe.log (
    echo [OK] Log encontrado - Ultimas 20 linhas:
    echo.
    powershell -Command "Get-Content probe.log -Tail 20"
) else (
    echo [AVISO] Arquivo probe.log ainda nao foi criado
    echo O servico pode estar iniciando...
)
echo.

echo [3] Verificando log do servico:
if exist probe_service.log (
    echo [OK] Log do servico encontrado:
    echo.
    type probe_service.log
) else (
    echo [INFO] Log do servico nao encontrado
)
echo.

echo ========================================
echo   PROXIMOS PASSOS
echo ========================================
echo.
echo 1. Aguarde 1-2 minutos para o probe coletar dados
echo 2. Acesse o frontend: http://localhost:3000
echo 3. Va em "Probes" no menu lateral
echo 4. Verifique se o probe aparece com status verde
echo.
pause
