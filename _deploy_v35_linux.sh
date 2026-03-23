#!/bin/bash
# Deploy v3.5 Enterprise Hardening no servidor Linux
# Executar em: /home/administrador/CorujaMonitor

set -e
PROJ="/home/administrador/CorujaMonitor"

echo "=== 1. Copiar arquivos modificados para containers ==="

# API: models, migration, routers, main
docker cp "$PROJ/api/models.py"                                    coruja-api:/app/models.py
docker cp "$PROJ/api/migrate_v35_hardening.py"                     coruja-api:/app/migrate_v35_hardening.py
docker cp "$PROJ/api/routers/sensor_controls.py"                   coruja-api:/app/routers/sensor_controls.py
docker cp "$PROJ/api/routers/default_sensor_profiles.py"           coruja-api:/app/routers/default_sensor_profiles.py
docker cp "$PROJ/api/routers/servers.py"                           coruja-api:/app/routers/servers.py
docker cp "$PROJ/api/main.py"                                      coruja-api:/app/main.py

# Worker
docker cp "$PROJ/worker/tasks.py"                                  coruja-worker:/app/tasks.py

# Alert Engine
docker cp "$PROJ/alert_engine/engine.py"                           coruja-api:/app/alert_engine/engine.py

echo "=== 2. Executar migration SQL ==="
docker exec coruja-api python migrate_v35_hardening.py

echo "=== 3. Recarregar API (touch para uvicorn reload) ==="
docker exec coruja-api touch /app/routers/sensor_controls.py

echo "=== 4. Reiniciar worker ==="
docker-compose -f "$PROJ/docker-compose.yml" restart worker

echo "=== 5. Gerar certificado SSL self-signed ==="
mkdir -p "$PROJ/nginx/ssl"
openssl req -x509 -nodes -days 365 \
    -newkey rsa:2048 \
    -keyout "$PROJ/nginx/ssl/coruja.key" \
    -out "$PROJ/nginx/ssl/coruja.crt" \
    -subj "/C=BR/ST=SP/L=SaoPaulo/O=TechBiz/OU=IT/CN=coruja.techbiz.com.br" 2>/dev/null
echo "Certificado gerado."

echo "=== 6. Subir serviço nginx ==="
docker-compose -f "$PROJ/docker-compose.yml" up -d nginx
sleep 5
docker logs coruja-nginx --tail 10

echo "=== 7. Verificar nginx config ==="
docker exec coruja-nginx nginx -t

echo "=== 8. Verificar logs do worker ==="
docker logs coruja-worker --tail 20

echo ""
echo "✅ Deploy v3.5 Enterprise Hardening concluído!"
echo "   - API: http://192.168.31.161:8000"
echo "   - HTTPS: https://coruja.techbiz.com.br (ou https://192.168.31.161)"
echo "   - HTTP redireciona para HTTPS automaticamente"
