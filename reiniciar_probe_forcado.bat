@echo off
echo ============================================================
echo REINICIO FORCADO DA PROBE
echo ============================================================

echo 1. Parando todos os processos Python...
taskkill /F /IM python.exe /T 2>nul
taskkill /F /IM pythonw.exe /T 2>nul
timeout /t 3 /nobreak > nul

echo.
echo 2. Verificando se probe parou...
tasklist | findstr /i "python"
if %ERRORLEVEL% EQU 0 (
    echo [AVISO] Ainda ha processos Python rodando
) else (
    echo [OK] Todos os processos Python foram parados
)

echo.
echo 3. Limpando arquivos de lock (se existirem)...
if exist "probe\*.lock" del /F /Q probe\*.lock
if exist "probe\*.pid" del /F /Q probe\*.pid

echo.
echo 4. Iniciando probe novamente...
cd probe
start /MIN python probe_core.py
cd ..

echo.
echo 5. Aguardando 5 segundos para probe iniciar...
timeout /t 5 /nobreak > nul

echo.
echo 6. Verificando se probe iniciou...
tasklist | findstr /i "python"
if %ERRORLEVEL% EQU 0 (
    echo [OK] Probe esta rodando
) else (
    echo [ERRO] Probe NAO iniciou! Verifique os logs
    pause
    exit /b 1
)

echo.
echo 7. Aguardando primeira coleta (70 segundos)...
echo    A probe coleta a cada 60 segundos...
for /L %%i in (70,-10,10) do (
    echo    Aguardando %%i segundos...
    timeout /t 10 /nobreak > nul
)

echo.
echo 8. Verificando se metricas foram enviadas...
docker exec coruja-postgres psql -U coruja -d coruja_monitor -c "SELECT MAX(timestamp) as last_metric, NOW() - MAX(timestamp) as time_ago, COUNT(*) as total FROM metrics WHERE sensor_id IN (SELECT id FROM sensors WHERE server_id IN (SELECT id FROM servers WHERE probe_id = 3)) AND timestamp > NOW() - INTERVAL '2 minutes';"

echo.
echo ============================================================
echo PROBE REINICIADA!
echo Verifique se metricas foram coletadas acima.
echo Se time_ago for menor que 2 minutos = SUCESSO!
echo ============================================================
pause
