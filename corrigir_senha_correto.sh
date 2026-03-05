#!/bin/bash

echo "=========================================="
echo "CORREÇÃO SENHA ADMIN - VERSÃO CORRETA"
echo "=========================================="
echo ""

# Hash correto para senha 'admin123'
HASH='$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/qvQu6'

echo "1. Resetando senha do admin (coluna CORRETA: hashed_password)..."
docker compose exec -T postgres psql -U coruja -d coruja_monitor <<EOF
UPDATE users 
SET hashed_password = '$HASH',
    is_active = true
WHERE email = 'admin@coruja.com';
EOF

echo ""
echo "2. Verificando usuário..."
docker compose exec -T postgres psql -U coruja -d coruja_monitor -c "SELECT id, email, is_active FROM users WHERE email = 'admin@coruja.com';"

echo ""
echo "3. Testando login via API..."
RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin@coruja.com","password":"admin123"}')

if echo "$RESPONSE" | grep -q "access_token"; then
    echo "   ✓ LOGIN FUNCIONANDO!"
else
    echo "   ✗ Resposta: $RESPONSE"
fi

echo ""
echo "=========================================="
echo "Credenciais:"
echo "  Email: admin@coruja.com"
echo "  Senha: admin123"
echo "=========================================="
