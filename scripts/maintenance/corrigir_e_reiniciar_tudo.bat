@echo off
echo ============================================================
echo CORRIGIR E REINICIAR TODO O SISTEMA
echo ============================================================
echo.

echo 1. Parando probe...
taskkill /F /IM python.exe /T 2>nul
timeout /t 2 /nobreak > nul

echo.
echo 2. Reiniciando API...
docker restart coruja-api
timeout /t 5 /nobreak > nul

echo.
echo 3. Reiniciando Frontend...
docker restart coruja-frontend
timeout /t 5 /nobreak > nul

echo.
echo 4. Iniciando probe...
cd probe
start /MIN python probe_core.py
cd ..

echo.
echo 5. Aguardando 70 segundos para primeira coleta...
echo    (A probe coleta a cada 60 segundos)
for /L %%i in (70,-10,10) do (
    echo    Aguardando %%i segundos...
    timeout /t 10 /nobreak > nul
)

echo.
echo 6. Verificando se metricas foram coletadas...
docker exec coruja-postgres psql -U coruja -d coruja_monitor -c "SELECT MAX(timestamp) as last_metric, NOW() - MAX(timestamp) as time_ago, COUNT(*) as total FROM metrics WHERE timestamp > NOW() - INTERVAL '2 minutes';"

echo.
echo 7. Verificando status geral...
docker exec coruja-postgres psql -U coruja -d coruja_monitor -c "SELECT (SELECT COUNT(*) FROM servers WHERE tenant_id = 1) as servers, (SELECT COUNT(*) FROM sensors WHERE server_id IN (SELECT id FROM servers WHERE tenant_id = 1)) as sensors, (SELECT COUNT(*) FROM incidents WHERE status = 'open') as open_incidents;"

echo.
echo ============================================================
echo SISTEMA REINICIADO!
echo ============================================================
echo.
echo Acesse: http://192.168.30.189:3000
echo Login: admin@coruja.com
echo Senha: admin123
echo.
echo IMPORTANTE:
echo - Faca logout e login novamente no navegador
echo - Limpe o cache se necessario (Ctrl+Shift+Del)
echo - Aguarde 30 segundos para dashboard atualizar
echo.
echo ============================================================
pause
