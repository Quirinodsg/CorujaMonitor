@echo off
echo ============================================================
echo DIAGNOSTICO COMPLETO DA PROBE
echo ============================================================

echo 1. Verificando processo da probe...
tasklist | findstr /i "python"

echo.
echo 2. Verificando arquivos de configuracao...
if exist "probe\probe_config.json" (
    echo [OK] probe_config.json existe
    type probe\probe_config.json
) else (
    echo [ERRO] probe_config.json NAO ENCONTRADO!
)

echo.
echo 3. Verificando logs da probe (ultimas 50 linhas)...
if exist "probe\logs\probe.log" (
    powershell -Command "Get-Content probe\logs\probe.log -Tail 50"
) else (
    echo [AVISO] Log nao encontrado
)

echo.
echo 4. Testando conectividade com API...
curl -X GET "http://192.168.30.189:8000/health" -w "\nStatus: %%{http_code}\n"

echo.
echo 5. Verificando ultima metrica no banco...
docker exec coruja-postgres psql -U coruja -d coruja_monitor -c "SELECT MAX(timestamp) as last_metric, NOW() - MAX(timestamp) as time_ago FROM metrics WHERE sensor_id IN (SELECT id FROM sensors WHERE server_id IN (SELECT id FROM servers WHERE probe_id = 3));"

echo.
echo 6. Verificando heartbeat da probe...
docker exec coruja-postgres psql -U coruja -d coruja_monitor -c "SELECT id, name, last_heartbeat, NOW() - last_heartbeat as time_ago FROM probes WHERE id = 3;"

echo.
echo 7. Verificando metricas na ultima hora...
docker exec coruja-postgres psql -U coruja -d coruja_monitor -c "SELECT COUNT(*) as metrics_last_hour FROM metrics WHERE sensor_id IN (SELECT id FROM sensors WHERE server_id IN (SELECT id FROM servers WHERE probe_id = 3)) AND timestamp > NOW() - INTERVAL '1 hour';"

echo.
echo ============================================================
echo ANALISE:
echo - Se heartbeat esta OK mas metricas antigas = PROBE TRAVADA
echo - Se heartbeat antigo = PROBE PARADA
echo - Se nenhum processo Python = PROBE NAO ESTA RODANDO
echo ============================================================
pause
