#!/bin/bash

echo "========================================"
echo "TESTE RÁPIDO DE LOGIN"
echo "========================================"
echo ""

echo "1. Testando API..."
API_HEALTH=$(curl -s http://localhost:8000/health)
echo "Health: $API_HEALTH"

if [ "$API_HEALTH" = '{"status":"healthy"}' ]; then
    echo "✅ API está saudável"
else
    echo "❌ API com problema!"
    exit 1
fi

echo ""
echo "2. Testando login..."
LOGIN_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@coruja.com","password":"admin123"}')

HTTP_CODE=$(echo "$LOGIN_RESPONSE" | tail -n1)
RESPONSE_BODY=$(echo "$LOGIN_RESPONSE" | head -n-1)

echo "HTTP Code: $HTTP_CODE"
echo "Response:"
echo "$RESPONSE_BODY" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE_BODY"

if [ "$HTTP_CODE" = "200" ]; then
    echo ""
    echo "✅ LOGIN FUNCIONANDO!"
    echo ""
    echo "O problema está no frontend ou navegador."
    echo ""
    echo "Soluções:"
    echo "1. Limpe o cache do navegador (Ctrl+Shift+Delete)"
    echo "2. Tente em modo anônimo"
    echo "3. Abra o console do navegador (F12) e veja os erros"
    echo "4. Verifique se a URL está correta: http://localhost:3000"
    echo ""
    echo "Reiniciando frontend..."
    docker compose restart frontend
    echo "✅ Frontend reiniciado"
    echo ""
    echo "Aguarde 10 segundos e tente novamente"
else
    echo ""
    echo "❌ LOGIN NÃO ESTÁ FUNCIONANDO!"
    echo ""
    echo "Verificando logs da API..."
    docker logs coruja-api --tail 30 | grep -i "error\|exception"
    echo ""
    echo "Reiniciando API..."
    docker compose restart api
    echo "✅ API reiniciada"
    echo ""
    echo "Aguarde 10 segundos e execute este script novamente"
fi

echo ""
echo "========================================"
