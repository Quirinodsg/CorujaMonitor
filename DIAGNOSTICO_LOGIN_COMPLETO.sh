#!/bin/bash

echo "=========================================="
echo "  DIAGNÓSTICO COMPLETO - Login"
echo "=========================================="
echo ""

echo "1️⃣  Verificando código do Login.js..."
echo "----------------------------------------"
if grep -q "API_URL" ~/CorujaMonitor/frontend/src/components/Login.js; then
    echo "✅ Correção ENCONTRADA no código"
    echo ""
    echo "Linhas com API_URL:"
    grep -n "API_URL" ~/CorujaMonitor/frontend/src/components/Login.js
else
    echo "❌ Correção NÃO ENCONTRADA no código"
    echo ""
    echo "Linha 74 atual:"
    sed -n '74p' ~/CorujaMonitor/frontend/src/components/Login.js
fi
echo ""

echo "2️⃣  Verificando último commit do Git..."
echo "----------------------------------------"
cd ~/CorujaMonitor
git log --oneline -1
echo ""

echo "3️⃣  Verificando status dos containers..."
echo "----------------------------------------"
docker compose ps
echo ""

echo "4️⃣  Testando API..."
echo "----------------------------------------"
curl -s -X POST http://192.168.31.161:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin@coruja.com","password":"admin123"}' | head -c 100
echo ""
echo ""

echo "5️⃣  Verificando logs do frontend (últimas 10 linhas)..."
echo "----------------------------------------"
docker logs coruja-frontend --tail 10
echo ""

echo "=========================================="
echo "  CONCLUSÃO"
echo "=========================================="
echo ""

if grep -q "API_URL" ~/CorujaMonitor/frontend/src/components/Login.js; then
    echo "✅ Código está correto"
    echo ""
    echo "Teste no navegador:"
    echo "  http://192.168.31.161:3000"
    echo "  Email: admin@coruja.com"
    echo "  Senha: admin123"
    echo ""
    echo "Se ainda não funcionar:"
    echo "  1. Limpe o cache do navegador (Ctrl+Shift+Delete)"
    echo "  2. Abra aba anônima"
    echo "  3. Tente novamente"
else
    echo "❌ Código NÃO foi atualizado"
    echo ""
    echo "SOLUÇÃO:"
    echo "  1. No Windows, faça o commit:"
    echo "     cd \"C:\\Users\\andre.quirino\\Coruja Monitor\""
    echo "     .\\commit_correcao_login.ps1"
    echo ""
    echo "  2. No Linux, atualize:"
    echo "     cd ~/CorujaMonitor"
    echo "     git pull origin master"
    echo "     docker compose restart frontend"
fi
echo ""
