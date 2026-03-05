#!/bin/bash

echo "=========================================="
echo "DIAGNÓSTICO E CORREÇÃO - LOGIN TRAVADO"
echo "=========================================="
echo ""

# 1. Ver logs da API
echo "1. Logs da API (últimas 50 linhas):"
echo "=========================================="
docker compose logs --tail=50 api

echo ""
echo "2. Status dos containers:"
echo "=========================================="
docker compose ps

echo ""
echo "3. Verificar banco de dados:"
echo "=========================================="
docker compose exec -T postgres psql -U coruja -d coruja_monitor -c "SELECT email, is_active, is_superuser FROM users WHERE email = 'admin@coruja.com';"

echo ""
echo "4. Verificar se API está respondendo:"
echo "=========================================="
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@coruja.com","password":"admin123"}' \
  -v

echo ""
echo "=========================================="
echo "POSSÍVEIS SOLUÇÕES:"
echo "=========================================="
echo ""
echo "Se usuário não existe:"
echo "  docker compose exec api python init_admin.py"
echo ""
echo "Se senha está errada:"
echo "  docker compose exec -T postgres psql -U coruja -d coruja_monitor -c \"UPDATE users SET password_hash = '\$2b\$12\$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/qvQu6' WHERE email = 'admin@coruja.com';\""
echo ""
echo "Se API não está rodando:"
echo "  docker compose restart api"
echo ""
echo "Se tudo falhar (CUIDADO - apaga dados):"
echo "  docker compose down -v"
echo "  docker compose up -d"
echo "  docker compose exec api python init_admin.py"
echo ""
