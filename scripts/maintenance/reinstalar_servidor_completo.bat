@echo off
echo ========================================
echo REINSTALACAO COMPLETA - Coruja Monitor
echo ========================================
echo.
echo Este script vai:
echo 1. Excluir servidor DESKTOP-P9VGN04 e todos os sensores
echo 2. Limpar metricas antigas
echo 3. Limpar incidentes de teste
echo 4. Recriar servidor com sensores padrao
echo 5. Configurar probe corretamente
echo.
echo ATENCAO: Esta acao nao pode ser desfeita!
echo.
pause

echo.
echo ========================================
echo Passo 1: Limpando dados antigos
echo ========================================
echo.

docker exec coruja-api python -c "from database import SessionLocal; from models import Server, Sensor, Metric, Incident; db = SessionLocal(); print('Excluindo servidor e dados...'); server = db.query(Server).filter(Server.hostname == 'DESKTOP-P9VGN04').first(); if server: sensors = db.query(Sensor).filter(Sensor.server_id == server.id).all(); sensor_ids = [s.id for s in sensors]; if sensor_ids: db.query(Incident).filter(Incident.sensor_id.in_(sensor_ids)).delete(synchronize_session=False); db.query(Metric).filter(Metric.sensor_id.in_(sensor_ids)).delete(synchronize_session=False); db.query(Sensor).filter(Sensor.server_id == server.id).delete(synchronize_session=False); db.delete(server); db.commit(); print('✓ Servidor excluido com sucesso'); else: print('Servidor nao encontrado'); db.close()"

echo.
echo ========================================
echo Passo 2: Criando novo servidor
echo ========================================
echo.

docker exec coruja-api python -c "from database import SessionLocal; from models import Server, Sensor, Probe; import socket; db = SessionLocal(); probe = db.query(Probe).filter(Probe.name == 'Quirino-Matriz').first(); if not probe: print('ERRO: Probe nao encontrada!'); exit(1); hostname = socket.gethostname(); import requests; try: ip = requests.get('https://api.ipify.org').text; except: ip = '0.0.0.0'; server = Server(tenant_id=probe.tenant_id, probe_id=probe.id, hostname=hostname, ip_address='192.168.0.9', public_ip=ip, os_type='Windows', device_type='server', monitoring_protocol='wmi'); db.add(server); db.commit(); db.refresh(server); print(f'✓ Servidor criado: {server.hostname} (ID: {server.id})'); sensors_data = [{'name': 'PING', 'sensor_type': 'ping', 'threshold_warning': 100, 'threshold_critical': 200}, {'name': 'CPU', 'sensor_type': 'cpu', 'threshold_warning': 80, 'threshold_critical': 95}, {'name': 'Memória', 'sensor_type': 'memory', 'threshold_warning': 80, 'threshold_critical': 95}, {'name': 'Disco C', 'sensor_type': 'disk', 'threshold_warning': 80, 'threshold_critical': 95}, {'name': 'Uptime', 'sensor_type': 'system', 'threshold_warning': 80, 'threshold_critical': 95}, {'name': 'Network IN', 'sensor_type': 'network', 'threshold_warning': 80, 'threshold_critical': 95}, {'name': 'Network OUT', 'sensor_type': 'network', 'threshold_warning': 80, 'threshold_critical': 95}]; for s_data in sensors_data: sensor = Sensor(server_id=server.id, name=s_data['name'], sensor_type=s_data['sensor_type'], threshold_warning=s_data['threshold_warning'], threshold_critical=s_data['threshold_critical'], is_active=True); db.add(sensor); db.commit(); print(f'✓ {len(sensors_data)} sensores padrão criados'); db.close()"

echo.
echo ========================================
echo Passo 3: Configurando probe
echo ========================================
echo.

cd "C:\Users\andre.quirino\OneDrive - Techbiz Forense Digital Ltda\Desktop\Coruja Monitor\probe"

echo Criando probe_config.json...
(
echo {
echo   "api_url": "http://localhost:8000",
echo   "probe_token": "W_YxHARNTlE3G8bxoXhWt0FknTPysGnKFX_visaP_G4",
echo   "collection_interval": 60,
echo   "log_level": "INFO"
echo }
) > probe_config.json

echo ✓ Configuracao criada
echo.

echo ========================================
echo Passo 4: Verificando instalacao
echo ========================================
echo.

docker exec coruja-api python -c "from database import SessionLocal; from models import Server, Sensor, Probe; db = SessionLocal(); server = db.query(Server).filter(Server.hostname.like('DESKTOP%%')).first(); if server: print(f'✓ Servidor: {server.hostname} (ID: {server.id})'); print(f'  Tenant: {server.tenant_id}'); print(f'  Probe: {server.probe_id}'); sensors = db.query(Sensor).filter(Sensor.server_id == server.id).all(); print(f'✓ Sensores: {len(sensors)}'); for s in sensors: print(f'  - {s.name} ({s.sensor_type})'); else: print('ERRO: Servidor nao encontrado!'); db.close()"

echo.
echo ========================================
echo INSTALACAO CONCLUIDA!
echo ========================================
echo.
echo Proximo passo: Iniciar a probe
echo Execute: iniciar_probe.bat
echo.
echo Ou manualmente:
echo cd "C:\Users\andre.quirino\OneDrive - Techbiz Forense Digital Ltda\Desktop\Coruja Monitor\probe"
echo python probe_core.py
echo.
pause
