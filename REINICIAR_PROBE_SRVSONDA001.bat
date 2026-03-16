@echo off
echo ========================================
echo REINICIAR PROBE NA SRVSONDA001
echo ========================================
echo.

echo Parando servico CorujaProbe...
sc \\SRVSONDA001 stop CorujaProbe

echo Aguardando 5 segundos...
timeout /t 5 /nobreak

echo Iniciando servico CorujaProbe...
sc \\SRVSONDA001 start CorujaProbe

echo.
echo ========================================
echo SERVICO REINICIADO
echo ========================================
echo.
echo Aguarde 60 segundos e verifique:
echo 1. Dashboard - sensores devem aparecer
echo 2. Logs na SRVSONDA001
echo.

pause
