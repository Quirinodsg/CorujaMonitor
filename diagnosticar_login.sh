#!/bin/bash

echo "========================================"
echo "DIAGNÓSTICO DO LOGIN"
echo "========================================"
echo ""

echo "1. Verificando logs da API..."
echo "========================================"
docker logs coruja-api --tail 100 | grep -i "error\|exception\|login\|auth"

echo ""
echo "2. Testando endpoint de login..."
echo "========================================"
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@coruja.com","password":"admin123"}' \
  -v

echo ""
echo ""
echo "3. Verificando usuário no banco..."
echo "========================================"
docker compose exec -T postgres psql -U coruja -d coruja_monitor -c "SELECT id, email, is_active, role FROM users WHERE email = 'admin@coruja.com';"

echo ""
echo "4. Verificando status dos containers..."
echo "========================================"
docker compose ps

echo ""
echo "5. Verificando logs do frontend..."
echo "========================================"
docker logs coruja-frontend --tail 50 | grep -i "error\|failed"

echo ""
echo "6. Testando conectividade API..."
echo "========================================"
curl http://localhost:8000/health

echo ""
echo ""
echo "========================================"
echo "DIAGNÓSTICO CONCLUÍDO"
echo "========================================"
