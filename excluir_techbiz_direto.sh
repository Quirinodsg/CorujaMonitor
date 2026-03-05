#!/bin/bash

echo "=========================================="
echo "EXCLUIR EMPRESA TECHBIZ DIRETAMENTE"
echo "=========================================="
echo ""

echo "ATENÇÃO: Este script vai excluir a empresa Techbiz diretamente no banco de dados!"
echo ""
read -p "Tem certeza? Digite 'SIM' para continuar: " confirmacao

if [ "$confirmacao" != "SIM" ]; then
    echo "Operação cancelada."
    exit 0
fi

echo ""
echo "1. Verificando se Techbiz existe..."
TECHBIZ_ID=$(docker compose exec -T postgres psql -U coruja -d coruja_monitor -t -c "SELECT id FROM tenants WHERE name = 'Techbiz' OR slug = 'techbiz';" | xargs)

if [ -z "$TECHBIZ_ID" ]; then
    echo "Empresa Techbiz não encontrada no banco de dados."
    exit 0
fi

echo "Empresa Techbiz encontrada com ID: $TECHBIZ_ID"
echo ""

echo "2. Buscando servidores da empresa..."
docker compose exec -T postgres psql -U coruja -d coruja_monitor -c "SELECT id, name FROM servers WHERE tenant_id = $TECHBIZ_ID;"

echo ""
echo "3. Excluindo dados relacionados..."

# Excluir métricas dos sensores dos servidores desta empresa
echo "   - Excluindo métricas..."
docker compose exec -T postgres psql -U coruja -d coruja_monitor -c "
DELETE FROM metrics 
WHERE sensor_id IN (
    SELECT s.id FROM sensors s 
    JOIN servers srv ON s.server_id = srv.id 
    WHERE srv.tenant_id = $TECHBIZ_ID
);"

# Excluir incidentes dos sensores dos servidores desta empresa
echo "   - Excluindo incidentes..."
docker compose exec -T postgres psql -U coruja -d coruja_monitor -c "
DELETE FROM incidents 
WHERE sensor_id IN (
    SELECT s.id FROM sensors s 
    JOIN servers srv ON s.server_id = srv.id 
    WHERE srv.tenant_id = $TECHBIZ_ID
);"

# Excluir sensores dos servidores desta empresa
echo "   - Excluindo sensores..."
docker compose exec -T postgres psql -U coruja -d coruja_monitor -c "
DELETE FROM sensors 
WHERE server_id IN (
    SELECT id FROM servers WHERE tenant_id = $TECHBIZ_ID
);"

# Excluir servidores desta empresa
echo "   - Excluindo servidores..."
docker compose exec -T postgres psql -U coruja -d coruja_monitor -c "DELETE FROM servers WHERE tenant_id = $TECHBIZ_ID;"

# Excluir probes desta empresa
echo "   - Excluindo probes..."
docker compose exec -T postgres psql -U coruja -d coruja_monitor -c "DELETE FROM probes WHERE tenant_id = $TECHBIZ_ID;"

# Excluir usuários desta empresa (exceto o admin atual)
echo "   - Excluindo usuários..."
docker compose exec -T postgres psql -U coruja -d coruja_monitor -c "DELETE FROM users WHERE tenant_id = $TECHBIZ_ID AND email != 'admin@coruja.com';"

# Finalmente, excluir a empresa
echo "   - Excluindo empresa..."
docker compose exec -T postgres psql -U coruja -d coruja_monitor -c "DELETE FROM tenants WHERE id = $TECHBIZ_ID;"

echo ""
echo "4. Verificando resultado..."
docker compose exec -T postgres psql -U coruja -d coruja_monitor -c "SELECT id, name, slug FROM tenants ORDER BY id;"

echo ""
echo "=========================================="
echo "EMPRESA TECHBIZ EXCLUÍDA COM SUCESSO!"
echo "=========================================="
echo ""
echo "Agora faça o rebuild do frontend:"
echo "chmod +x rebuild_frontend_linux.sh"
echo "./rebuild_frontend_linux.sh"
echo ""
