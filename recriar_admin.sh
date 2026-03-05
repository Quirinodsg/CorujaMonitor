#!/bin/bash

echo "=========================================="
echo "RECRIAR USUÁRIO ADMIN"
echo "=========================================="
echo ""

echo "1. Verificando se admin existe..."
EXISTE=$(docker compose exec -T postgres psql -U coruja -d coruja_monitor -t -c "SELECT COUNT(*) FROM users WHERE email = 'admin@coruja.com';" | tr -d ' ')

if [ "$EXISTE" -eq "0" ]; then
    echo "   Admin NÃO existe. Criando..."
    docker compose exec api python init_admin.py
else
    echo "   Admin existe. Resetando senha..."
    ./resetar_senha_admin.sh
fi

echo ""
echo "2. Verificando usuário criado:"
docker compose exec -T postgres psql -U coruja -d coruja_monitor -c "SELECT id, email, is_active, is_superuser, tenant_id FROM users WHERE email = 'admin@coruja.com';"

echo ""
echo "3. Testando login via API:"
RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@coruja.com","password":"admin123"}')

if echo "$RESPONSE" | grep -q "access_token"; then
    echo "   ✓ LOGIN FUNCIONANDO!"
else
    echo "   ✗ LOGIN FALHOU!"
    echo "   Resposta: $RESPONSE"
fi

echo ""
echo "=========================================="
echo "CONCLUÍDO!"
echo "=========================================="
echo ""
echo "Credenciais:"
echo "  Email: admin@coruja.com"
echo "  Senha: admin123"
echo ""
echo "Acesse: http://192.168.31.161:3000"
echo ""
