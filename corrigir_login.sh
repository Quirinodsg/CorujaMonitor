#!/bin/bash

echo "========================================"
echo "CORRIGIR PROBLEMA DE LOGIN"
echo "========================================"
echo ""

echo "Verificando problema..."
echo ""

# Verificar se API está respondendo
echo "1. Testando API..."
API_STATUS=$(curl -s http://localhost:8000/health)
echo "Status da API: $API_STATUS"

if [ "$API_STATUS" != '{"status":"healthy"}' ]; then
    echo "❌ API não está respondendo corretamente!"
    echo "Reiniciando API..."
    docker compose restart api
    sleep 10
fi

echo ""
echo "2. Verificando usuário admin..."
USER_EXISTS=$(docker compose exec -T postgres psql -U coruja -d coruja_monitor -t -c "SELECT COUNT(*) FROM users WHERE email = 'admin@coruja.com';" | tr -d ' ')

if [ "$USER_EXISTS" = "0" ]; then
    echo "❌ Usuário admin não existe!"
    echo "Criando usuário admin..."
    docker compose exec api python init_admin.py
else
    echo "✅ Usuário admin existe"
fi

echo ""
echo "3. Testando login via API..."
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@coruja.com","password":"admin123"}')

echo "Resposta do login:"
echo "$LOGIN_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$LOGIN_RESPONSE"

if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
    echo ""
    echo "✅ Login funcionando pela API!"
    echo ""
    echo "Problema pode ser no frontend. Verificando..."
    echo ""
    echo "4. Limpando cache do navegador..."
    echo "   - Pressione Ctrl+Shift+Delete no navegador"
    echo "   - Ou tente em modo anônimo"
    echo ""
    echo "5. Verificando configuração do frontend..."
    docker compose exec frontend env | grep REACT_APP_API_URL
    echo ""
    echo "6. Reiniciando frontend..."
    docker compose restart frontend
    sleep 10
    echo "✅ Frontend reiniciado"
else
    echo ""
    echo "❌ Login não está funcionando!"
    echo ""
    echo "Verificando logs de erro..."
    docker logs coruja-api --tail 50 | grep -i "error\|exception"
    echo ""
    echo "Reiniciando sistema completo..."
    docker compose restart
    sleep 30
    echo "✅ Sistema reiniciado"
fi

echo ""
echo "========================================"
echo "CORREÇÃO CONCLUÍDA"
echo "========================================"
echo ""
echo "Tente acessar novamente:"
echo "URL: http://localhost:3000"
echo "Email: admin@coruja.com"
echo "Senha: admin123"
echo ""
echo "Se ainda não funcionar:"
echo "1. Limpe o cache do navegador (Ctrl+Shift+Delete)"
echo "2. Tente em modo anônimo"
echo "3. Verifique o console do navegador (F12)"
echo ""
