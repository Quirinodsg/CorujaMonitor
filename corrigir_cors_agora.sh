#!/bin/bash

echo "=========================================="
echo "DIAGNÓSTICO E CORREÇÃO CORS"
echo "=========================================="

# 1. Verificar usuário admin
echo "1. Verificando usuário admin..."
docker compose exec -T postgres psql -U coruja -d coruja_monitor -c "SELECT id, email, is_active FROM users WHERE email = 'admin@coruja.com';"

# 2. Resetar senha
echo ""
echo "2. Resetando senha..."
HASH='$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/qvQu6'
docker compose exec -T postgres psql -U coruja -d coruja_monitor <<EOF
UPDATE users 
SET hashed_password = '$HASH',
    is_active = true
WHERE email = 'admin@coruja.com';
EOF

# 3. Verificar config.js no container
echo ""
echo "3. Verificando config.js no container do frontend..."
docker compose exec frontend cat /app/src/config.js | grep -A 5 "getApiUrl"

# 4. Verificar CORS na API
echo ""
echo "4. Verificando configuração CORS na API..."
docker compose exec api grep -A 10 "CORSMiddleware" main.py

# 5. Testar API diretamente
echo ""
echo "5. Testando API..."
curl -s -X POST http://192.168.31.161:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin@coruja.com","password":"admin123"}' | head -c 200

echo ""
echo ""
echo "=========================================="
echo "CORREÇÃO"
echo "=========================================="

# 6. Adicionar variável de ambiente
echo ""
echo "6. Configurando variável de ambiente..."
cat >> .env << 'ENVEOF'

# Frontend API URL
REACT_APP_API_URL=http://192.168.31.161:8000/api/v1
ENVEOF

# 7. Rebuild apenas frontend
echo ""
echo "7. Rebuild do frontend..."
docker compose stop frontend
docker compose rm -f frontend
docker rmi corujamonitor-frontend:latest 2>/dev/null || true
docker compose build --no-cache frontend
docker compose up -d frontend

echo ""
echo "Aguardando 20 segundos..."
sleep 20

echo ""
echo "=========================================="
echo "TESTE FINAL"
echo "=========================================="
echo ""
echo "Acesse: http://192.168.31.161:3000"
echo "Email: admin@coruja.com"
echo "Senha: admin123"
echo ""
