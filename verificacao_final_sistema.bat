@echo off
echo ============================================================
echo VERIFICACAO FINAL DO SISTEMA - 25/FEV/2026
echo ============================================================
echo.

echo 1. Verificando status dos containers...
docker ps --filter "name=coruja" --format "table {{.Names}}\t{{.Status}}"
echo.

echo 2. Verificando sensores...
docker exec coruja-postgres psql -U coruja -d coruja_monitor -c "SELECT COUNT(*) as total_sensors, COUNT(CASE WHEN m.status = 'ok' THEN 1 END) as ok_sensors, COUNT(CASE WHEN m.status = 'warning' THEN 1 END) as warning_sensors, COUNT(CASE WHEN m.status = 'critical' THEN 1 END) as critical_sensors, COUNT(CASE WHEN m.id IS NULL THEN 1 END) as no_data FROM sensors s LEFT JOIN LATERAL (SELECT * FROM metrics WHERE sensor_id = s.id ORDER BY timestamp DESC LIMIT 1) m ON true WHERE s.server_id IN (SELECT id FROM servers WHERE tenant_id = 1);"
echo.

echo 3. Verificando incidentes...
docker exec coruja-postgres psql -U coruja -d coruja_monitor -c "SELECT COUNT(*) as total_incidents, COUNT(CASE WHEN status = 'open' THEN 1 END) as open_incidents, COUNT(CASE WHEN status = 'resolved' THEN 1 END) as resolved_incidents FROM incidents;"
echo.

echo 4. Verificando metricas simuladas...
docker exec coruja-postgres psql -U coruja -d coruja_monitor -c "SELECT COUNT(*) as simulated_metrics FROM metrics WHERE metadata->>'simulated' = 'true';"
echo.

echo 5. Verificando servidores...
docker exec coruja-postgres psql -U coruja -d coruja_monitor -c "SELECT COUNT(*) as total_servers, COUNT(CASE WHEN EXISTS (SELECT 1 FROM incidents i JOIN sensors s ON s.id = i.sensor_id WHERE s.server_id = servers.id AND i.status = 'open' AND i.severity = 'critical') THEN 1 END) as critical_servers, COUNT(CASE WHEN EXISTS (SELECT 1 FROM incidents i JOIN sensors s ON s.id = i.sensor_id WHERE s.server_id = servers.id AND i.status = 'open' AND i.severity = 'warning') THEN 1 END) as warning_servers FROM servers WHERE tenant_id = 1;"
echo.

echo 6. Verificando ultima coleta da probe...
docker exec coruja-postgres psql -U coruja -d coruja_monitor -c "SELECT MAX(timestamp) as last_collection, NOW() - MAX(timestamp) as time_since_last FROM metrics WHERE sensor_id IN (SELECT id FROM sensors WHERE server_id IN (SELECT id FROM servers WHERE tenant_id = 1));"
echo.

echo 7. Verificando probes ativas...
docker exec coruja-postgres psql -U coruja -d coruja_monitor -c "SELECT id, name, is_active, last_heartbeat, NOW() - last_heartbeat as time_since_heartbeat FROM probes WHERE tenant_id = 1;"
echo.

echo ============================================================
echo RESULTADO DA VERIFICACAO
echo ============================================================
echo.
echo Esperado:
echo - Todos os containers rodando
echo - 28 sensores OK, 0 warning, 0 critical, 0 sem dados
echo - 0 incidentes abertos
echo - 0 metricas simuladas
echo - 1 servidor total, 0 criticos, 0 avisos
echo - Ultima coleta ha menos de 2 minutos
echo - Probe ativa com heartbeat recente
echo.
echo ============================================================
pause
