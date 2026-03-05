#!/bin/bash

echo "=========================================="
echo "TESTE DE LOGIN DIRETO NO SERVIDOR"
echo "=========================================="

# 1. Verificar se API está rodando
echo "1. Verificando se API está rodando..."
curl -s http://localhost:8000/docs > /dev/null && echo "✓ API está rodando" || echo "✗ API NÃO está rodando"

# 2. Verificar usuário admin
echo ""
echo "2. Verificando usuário admin no banco..."
docker compose exec -T postgres psql -U coruja -d coruja_monitor -c "SELECT id, email, is_active FROM users WHERE email = 'admin@coruja.com';"

# 3. Resetar senha
echo ""
echo "3. Resetando senha do admin..."
HASH='$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/qvQu6'
docker compose exec -T postgres psql -U coruja -d coruja_monitor <<EOF
UPDATE users 
SET hashed_password = '$HASH',
    is_active = true
WHERE email = 'admin@coruja.com';
EOF

# 4. Testar login via localhost
echo ""
echo "4. Testando login via localhost:8000..."
RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin@coruja.com","password":"admin123"}')

if echo "$RESPONSE" | grep -q "access_token"; then
    echo "✓ LOGIN FUNCIONOU via localhost!"
    echo "Token: $(echo $RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4 | head -c 50)..."
else
    echo "✗ LOGIN FALHOU via localhost"
    echo "Resposta: $RESPONSE"
fi

# 5. Testar login via IP
echo ""
echo "5. Testando login via 192.168.31.161:8000..."
RESPONSE2=$(curl -s -X POST http://192.168.31.161:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin@coruja.com","password":"admin123"}')

if echo "$RESPONSE2" | grep -q "access_token"; then
    echo "✓ LOGIN FUNCIONOU via IP!"
    echo "Token: $(echo $RESPONSE2 | grep -o '"access_token":"[^"]*' | cut -d'"' -f4 | head -c 50)..."
else
    echo "✗ LOGIN FALHOU via IP"
    echo "Resposta: $RESPONSE2"
fi

# 6. Verificar CORS na API
echo ""
echo "6. Verificando configuração CORS..."
docker compose logs api --tail=50 | grep -i "cors\|origin" | tail -10

echo ""
echo "=========================================="
echo "CONCLUSÃO"
echo "=========================================="
echo ""
echo "Se o login funcionou via localhost E via IP,"
echo "o problema é no FRONTEND (config.js ou cache)."
echo ""
echo "Se o login NÃO funcionou, o problema é na API"
echo "ou no banco de dados."
echo ""
