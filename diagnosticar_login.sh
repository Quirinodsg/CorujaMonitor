#!/bin/bash

echo "=========================================="
echo "DIAGNÓSTICO DO PROBLEMA DE LOGIN"
echo "=========================================="
echo ""

echo "1. Verificando versão do código no servidor..."
echo "   Última linha do Login.js:"
tail -5 frontend/src/components/Login.js | head -1

echo ""
echo "2. Verificando se import do config.js existe:"
grep "import.*API_URL.*config" frontend/src/components/Login.js

echo ""
echo "3. Verificando config.js:"
grep "API_URL" frontend/src/config.js

echo ""
echo "4. Verificando containers em execução:"
docker compose ps

echo ""
echo "5. Verificando quando a imagem do frontend foi criada:"
docker images | grep coruja-frontend

echo ""
echo "6. Testando API diretamente:"
curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin@coruja.com","password":"admin123"}' | head -c 200

echo ""
echo ""
echo "=========================================="
echo "DIAGNÓSTICO COMPLETO"
echo "=========================================="
echo ""
echo "Se o import do config.js NÃO aparecer acima,"
echo "significa que o git pull não foi executado ainda."
echo ""
echo "Se aparecer mas a imagem é antiga (mais de 10 min),"
echo "significa que o rebuild não foi feito."
echo ""
echo "SOLUÇÃO:"
echo "  chmod +x corrigir_login_final.sh"
echo "  ./corrigir_login_final.sh"
echo ""
