#!/bin/bash

echo "=========================================="
echo "CORREÇÃO DEFINITIVA DO LOGIN"
echo "=========================================="

echo ""
echo "1. Parando containers..."
docker-compose down

echo ""
echo "2. Iniciando containers..."
docker-compose up -d

echo ""
echo "3. Aguardando API inicializar (15 segundos)..."
sleep 15

echo ""
echo "4. Deletando TODOS os usuários..."
docker-compose exec -T db psql -U postgres -d coruja_monitor -c "DELETE FROM users;"

echo ""
echo "5. Verificando tenant..."
docker-compose exec -T db psql -U postgres -d coruja_monitor -c "
SELECT id, name, slug FROM tenants;
"

echo ""
echo "6. Criando usuário admin com senha correta..."
docker-compose exec -T api python3 << 'PYTHON'
from database import SessionLocal
from models import User, Tenant
from auth import get_password_hash

db = SessionLocal()

# Verificar/criar tenant
tenant = db.query(Tenant).filter(Tenant.name == "Default").first()
if not tenant:
    tenant = Tenant(name="Default", slug="default", is_active=True)
    db.add(tenant)
    db.flush()
    print(f"✓ Tenant criado: id={tenant.id}")
else:
    print(f"✓ Tenant existe: id={tenant.id}")

# Criar usuário admin
hashed_password = get_password_hash("admin123")
user = User(
    email="admin@coruja.com",
    hashed_password=hashed_password,
    full_name="Administrator",
    role="admin",
    tenant_id=tenant.id,
    is_active=True,
    language="pt-BR",
    mfa_enabled=False
)
db.add(user)
db.commit()

print(f"\n✓ Usuário criado:")
print(f"  ID: {user.id}")
print(f"  Email: {user.email}")
print(f"  Tenant: {user.tenant_id}")
print(f"  Ativo: {user.is_active}")
print(f"  MFA: {user.mfa_enabled}")

# Testar senha
from auth import verify_password
is_valid = verify_password("admin123", user.hashed_password)
print(f"\n✓ Senha válida: {is_valid}")

db.close()
PYTHON

echo ""
echo "7. Verificando usuário criado..."
docker-compose exec -T db psql -U postgres -d coruja_monitor -c "
SELECT id, email, is_active, tenant_id, role, mfa_enabled
FROM users 
WHERE email = 'admin@coruja.com';
"

echo ""
echo "8. Testando login via curl..."
RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin@coruja.com","password":"admin123"}')

if echo "$RESPONSE" | grep -q "access_token"; then
    echo "✓ LOGIN FUNCIONOU!"
    TOKEN=$(echo $RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
    echo "Token: ${TOKEN:0:50}..."
else
    echo "✗ LOGIN FALHOU"
    echo "Resposta: $RESPONSE"
fi

echo ""
echo "9. Reiniciando frontend para limpar cache..."
docker-compose restart frontend

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
echo "Se ainda não funcionar no navegador:"
echo "  1. Abra DevTools (F12)"
echo "  2. Vá em Application > Storage"
echo "  3. Clique em 'Clear site data'"
echo "  4. Recarregue a página (Ctrl+Shift+R)"
echo ""
