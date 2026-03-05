#!/bin/bash

echo "=========================================="
echo "RESETAR SENHA DO ADMIN"
echo "=========================================="
echo ""

echo "Resetando senha para: admin123"
echo ""

# Hash bcrypt para "admin123"
# Gerado com: python -c "from passlib.hash import bcrypt; print(bcrypt.hash('admin123'))"
HASH='$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/qvQu6'

docker compose exec -T postgres psql -U coruja -d coruja_monitor <<EOF
UPDATE users 
SET password_hash = '$HASH',
    is_active = true,
    is_superuser = true
WHERE email = 'admin@coruja.com';

SELECT email, is_active, is_superuser, created_at 
FROM users 
WHERE email = 'admin@coruja.com';
EOF

echo ""
echo "=========================================="
echo "SENHA RESETADA!"
echo "=========================================="
echo ""
echo "Credenciais:"
echo "  Email: admin@coruja.com"
echo "  Senha: admin123"
echo ""
echo "Tente fazer login novamente!"
echo ""
