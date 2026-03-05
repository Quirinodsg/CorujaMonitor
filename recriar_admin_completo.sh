#!/bin/bash

echo "=========================================="
echo "RECRIAR USUÁRIO ADMIN COMPLETO"
echo "=========================================="

# 1. Deletar usuário admin existente
echo "1. Deletando usuário admin existente..."
docker compose exec -T postgres psql -U coruja -d coruja_monitor <<EOF
DELETE FROM users WHERE email = 'admin@coruja.com';
EOF

# 2. Verificar se tenant existe
echo ""
echo "2. Verificando tenant..."
docker compose exec -T postgres psql -U coruja -d coruja_monitor -c "SELECT id, name FROM tenants LIMIT 1;"

# 3. Criar tenant se não existir
echo ""
echo "3. Garantindo que tenant existe..."
docker compose exec -T postgres psql -U coruja -d coruja_monitor <<EOF
INSERT INTO tenants (name, is_active, created_at)
VALUES ('Default', true, NOW())
ON CONFLICT DO NOTHING;
EOF

# 4. Recriar usuário admin usando init_admin.py
echo ""
echo "4. Recriando usuário admin via init_admin.py..."
docker compose exec api python init_admin.py

# 5. Verificar usuário criado
echo ""
echo "5. Verificando usuário criado..."
docker compose exec -T postgres psql -U coruja -d coruja_monitor -c "SELECT id, email, is_active, tenant_id FROM users WHERE email = 'admin@coruja.com';"

# 6. Testar login
echo ""
echo "6. Testando login..."
RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin@coruja.com","password":"admin123"}')

if echo "$RESPONSE" | grep -q "access_token"; then
    echo "✓ LOGIN FUNCIONOU!"
    echo "Token: $(echo $RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4 | head -c 50)..."
else
    echo "✗ LOGIN FALHOU"
    echo "Resposta: $RESPONSE"
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
