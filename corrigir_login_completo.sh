#!/bin/bash

echo "=========================================="
echo "CORREÇÃO COMPLETA DO LOGIN"
echo "=========================================="
echo ""

# 1. Dar permissão aos scripts
echo "1. Dando permissão aos scripts..."
chmod +x resetar_senha_admin.sh
chmod +x recriar_admin.sh
chmod +x CORRIGIR_LOGIN_URGENTE.sh
echo "   ✓ Permissões configuradas"

# 2. Verificar estrutura do banco
echo ""
echo "2. Verificando estrutura da tabela users..."
docker compose exec -T postgres psql -U coruja -d coruja_monitor -c "\d users"

# 3. Verificar se admin existe
echo ""
echo "3. Verificando usuário admin..."
docker compose exec -T postgres psql -U coruja -d coruja_monitor -c "SELECT id, email, is_active, tenant_id FROM users WHERE email = 'admin@coruja.com';"

# 4. Resetar senha do admin
echo ""
echo "4. Resetando senha do admin..."
HASH='$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/qvQu6'
docker compose exec -T postgres psql -U coruja -d coruja_monitor <<EOF
UPDATE users 
SET password_hash = '$HASH',
    is_active = true
WHERE email = 'admin@coruja.com';
EOF
echo "   ✓ Senha resetada"

# 5. Verificar usuário após reset
echo ""
echo "5. Verificando usuário após reset..."
docker compose exec -T postgres psql -U coruja -d coruja_monitor -c "SELECT id, email, is_active, created_at FROM users WHERE email = 'admin@coruja.com';"

# 6. Testar login via API (formato correto)
echo ""
echo "6. Testando login via API..."
RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@coruja.com","password":"admin123"}')

if echo "$RESPONSE" | grep -q "access_token"; then
    echo "   ✓ LOGIN FUNCIONANDO!"
    echo "   Token recebido com sucesso"
else
    echo "   ✗ LOGIN FALHOU!"
    echo "   Resposta: $RESPONSE"
    echo ""
    echo "   Tentando formato alternativo (username)..."
    RESPONSE2=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
      -H "Content-Type: application/json" \
      -d '{"username":"admin@coruja.com","password":"admin123"}')
    
    if echo "$RESPONSE2" | grep -q "access_token"; then
        echo "   ✓ LOGIN FUNCIONANDO com username!"
    else
        echo "   ✗ Ainda falhou: $RESPONSE2"
    fi
fi

# 7. Verificar logs da API
echo ""
echo "7. Últimas linhas do log da API:"
docker compose logs --tail=20 api | grep -i "login\|error\|auth"

echo ""
echo "=========================================="
echo "CORREÇÃO CONCLUÍDA!"
echo "=========================================="
echo ""
echo "Credenciais:"
echo "  Email: admin@coruja.com"
echo "  Senha: admin123"
echo ""
echo "Acesse: http://192.168.31.161:3000"
echo ""
echo "Se ainda não funcionar:"
echo "  1. Ver logs completos: docker compose logs api"
echo "  2. Reiniciar API: docker compose restart api"
echo "  3. Recriar admin: docker compose exec api python init_admin.py"
echo ""
