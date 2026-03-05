#!/bin/bash

echo "=========================================="
echo "VERIFICAR EMPRESA TECHBIZ NO BANCO"
echo "=========================================="
echo ""

echo "1. Listando todas as empresas:"
docker compose exec -T postgres psql -U coruja -d coruja_monitor -c "SELECT id, name, slug, is_active, created_at FROM tenants ORDER BY id;"

echo ""
echo "2. Verificando se Techbiz existe:"
docker compose exec -T postgres psql -U coruja -d coruja_monitor -c "SELECT id, name, slug FROM tenants WHERE name = 'Techbiz' OR slug = 'techbiz';"

echo ""
echo "3. Contando total de empresas:"
docker compose exec -T postgres psql -U coruja -d coruja_monitor -c "SELECT COUNT(*) as total FROM tenants;"

echo ""
echo "=========================================="
echo "VERIFICAÇÃO CONCLUÍDA"
echo "=========================================="
