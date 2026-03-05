#!/bin/bash

echo "=========================================="
echo "VERIFICAR EMPRESAS NO BANCO DE DADOS"
echo "=========================================="
echo ""

echo "Listando TODAS as empresas:"
docker compose exec -T postgres psql -U coruja -d coruja_monitor -c "SELECT id, name, slug, is_active, created_at FROM tenants ORDER BY id;"

echo ""
echo "=========================================="
