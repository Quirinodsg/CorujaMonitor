#!/bin/bash

echo "=========================================="
echo "CORREÇÃO FINAL DO LOGIN"
echo "=========================================="
echo ""

# 1. Resetar senha do admin (coluna CORRETA)
echo "1. Resetando senha do admin..."
HASH='$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/qvQu6'
docker compose exec -T postgres psql -U coruja -d coruja_monitor <<EOF
UPDATE users 
SET hashed_password = '$HASH',
    is_active = true
WHERE email = 'admin@coruja.com';
EOF
echo "   ✓ Senha resetada"

# 2. Verificar usuário
echo ""
echo "2. Verificando usuário..."
docker compose exec -T postgres psql -U coruja -d coruja_monitor -c "SELECT id, email, is_active FROM users WHERE email = 'admin@coruja.com';"

# 3. Testar login via API
echo ""
echo "3. Testando login via API..."
RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin@coruja.com","password":"admin123"}')

if echo "$RESPONSE" | grep -q "access_token"; then
    echo "   ✓ LOGIN VIA API FUNCIONANDO!"
else
    echo "   ✗ Resposta: $RESPONSE"
fi

# 4. Rebuild do frontend com correção
echo ""
echo "4. Fazendo rebuild do frontend..."
echo "   Parando frontend..."
docker compose stop frontend

echo "   Removendo container e imagem antiga..."
docker compose rm -f frontend
docker rmi coruja-frontend:latest 2>/dev/null || true

echo "   Limpando cache do Docker..."
docker builder prune -f

echo "   Reconstruindo frontend (isso vai demorar 2-3 minutos)..."
docker compose build --no-cache frontend

echo "   Iniciando frontend..."
docker compose up -d frontend

echo ""
echo "=========================================="
echo "CORREÇÃO CONCLUÍDA!"
echo "=========================================="
echo ""
echo "Aguarde 30 segundos para o frontend iniciar..."
sleep 30

echo ""
echo "Credenciais:"
echo "  Email: admin@coruja.com"
echo "  Senha: admin123"
echo ""
echo "Acesse em ABA ANÔNIMA: http://192.168.31.161:3000"
echo ""
echo "IMPORTANTE: Use Ctrl+Shift+N (Chrome) ou Ctrl+Shift+P (Firefox)"
echo "            para abrir aba anônima e evitar cache!"
echo ""
