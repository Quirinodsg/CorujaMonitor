#!/bin/bash
# ════════════════════════════════════════════════════════════════
# DELETAR SENSOR DISCO D - SCRIPT COMPLETO
# ════════════════════════════════════════════════════════════════

echo "════════════════════════════════════════════════════════════════"
echo "PASSO 1: Listar todos os sensores de disco"
echo "════════════════════════════════════════════════════════════════"

docker-compose exec postgres psql -U coruja -d coruja_monitor -c "SELECT id, name, sensor_type, server_id, is_active FROM sensors WHERE sensor_type = 'disk' ORDER BY name;"

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "PASSO 2: Buscar sensor com 'D' no nome"
echo "════════════════════════════════════════════════════════════════"

docker-compose exec postgres psql -U coruja -d coruja_monitor -c "SELECT id, name, sensor_type FROM sensors WHERE name ILIKE '%D%' AND sensor_type = 'disk';"

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "PASSO 3: Deletar sensor Disco D (todas as variações)"
echo "════════════════════════════════════════════════════════════════"

# Tentar várias variações do nome
docker-compose exec postgres psql -U coruja -d coruja_monitor -c "DELETE FROM metrics WHERE sensor_id IN (SELECT id FROM sensors WHERE name ILIKE 'Disco D' AND sensor_type = 'disk');"

docker-compose exec postgres psql -U coruja -d coruja_monitor -c "DELETE FROM incidents WHERE sensor_id IN (SELECT id FROM sensors WHERE name ILIKE 'Disco D' AND sensor_type = 'disk');"

docker-compose exec postgres psql -U coruja -d coruja_monitor -c "DELETE FROM sensor_notes WHERE sensor_id IN (SELECT id FROM sensors WHERE name ILIKE 'Disco D' AND sensor_type = 'disk');"

docker-compose exec postgres psql -U coruja -d coruja_monitor -c "DELETE FROM sensors WHERE name ILIKE 'Disco D' AND sensor_type = 'disk';"

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "PASSO 4: Verificar se foi deletado"
echo "════════════════════════════════════════════════════════════════"

docker-compose exec postgres psql -U coruja -d coruja_monitor -c "SELECT id, name FROM sensors WHERE sensor_type = 'disk';"

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "CONCLUÍDO!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "PRÓXIMOS PASSOS:"
echo "1. Recarregar dashboard (Ctrl+F5)"
echo "2. Aguardar 60 segundos"
echo "3. Recarregar novamente"
echo ""
echo "Se Disco D reaparecer, o filtro não está sendo aplicado."
echo "════════════════════════════════════════════════════════════════"
