#!/bin/bash

echo "=========================================="
echo "DIAGNÓSTICO COMPLETO DE LOGIN"
echo "=========================================="

echo ""
echo "1. Verificando se API está rodando..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✓ API está rodando"
else
    echo "✗ API NÃO está rodando"
    exit 1
fi

echo ""
echo "2. Verificando usuário admin no banco..."
docker-compose exec -T db psql -U postgres -d coruja_monitor -c "
SELECT id, email, is_active, tenant_id, role, 
       CASE WHEN mfa_enabled THEN 'SIM' ELSE 'NÃO' END as mfa_ativo,
       LENGTH(hashed_password) as tamanho_hash
FROM users 
WHERE email = 'admin@coruja.com';
"

echo ""
echo "3. Testando hash da senha 'admin123'..."
docker-compose exec -T api python3 << 'PYTHON'
from auth import get_password_hash, verify_password

# Gerar hash correto
correct_hash = get_password_hash("admin123")
print(f"Hash correto para 'admin123':")
print(correct_hash[:50] + "...")

# Buscar hash do banco
from database import SessionLocal
from models import User

db = SessionLocal()
user = db.query(User).filter(User.email == "admin@coruja.com").first()

if user:
    print(f"\nHash no banco:")
    print(user.hashed_password[:50] + "...")
    
    # Testar verificação
    is_valid = verify_password("admin123", user.hashed_password)
    print(f"\nSenha 'admin123' é válida? {is_valid}")
    
    if not is_valid:
        print("\n⚠️  SENHA INCORRETA NO BANCO!")
        print("Atualizando senha...")
        user.hashed_password = correct_hash
        db.commit()
        print("✓ Senha atualizada!")
else:
    print("\n✗ Usuário não encontrado!")

db.close()
PYTHON

echo ""
echo "4. Testando login via API (localhost)..."
RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin@coruja.com","password":"admin123"}')

if echo "$RESPONSE" | grep -q "access_token"; then
    echo "✓ LOGIN FUNCIONOU via localhost!"
    echo "Token: $(echo $RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4 | cut -c1-30)..."
else
    echo "✗ LOGIN FALHOU via localhost"
    echo "Resposta: $RESPONSE"
fi

echo ""
echo "5. Testando login via API (IP 192.168.31.161)..."
RESPONSE=$(curl -s -X POST http://192.168.31.161:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin@coruja.com","password":"admin123"}')

if echo "$RESPONSE" | grep -q "access_token"; then
    echo "✓ LOGIN FUNCIONOU via IP!"
    echo "Token: $(echo $RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4 | cut -c1-30)..."
else
    echo "✗ LOGIN FALHOU via IP"
    echo "Resposta: $RESPONSE"
fi

echo ""
echo "6. Verificando CORS no container API..."
docker-compose logs api | grep -i cors | tail -5

echo ""
echo "7. Verificando logs recentes da API..."
docker-compose logs api | tail -20

echo ""
echo "=========================================="
echo "CONCLUSÃO"
echo "=========================================="
echo ""
echo "Se login funcionou via curl mas não no navegador:"
echo "  → Problema é CORS ou cache do navegador"
echo ""
echo "Se login NÃO funcionou via curl:"
echo "  → Problema é senha incorreta no banco"
echo ""
echo "Credenciais para teste:"
echo "  Email: admin@coruja.com"
echo "  Senha: admin123"
echo ""
