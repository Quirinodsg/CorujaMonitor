#!/bin/bash

echo "=========================================="
echo "CORRIGIR URL DUPLICADA NO FRONTEND"
echo "=========================================="

echo ""
echo "Problema identificado:"
echo "  URL estava: /api/v1/api/v1/..."
echo "  URL correta: /api/v1/..."
echo ""
echo "Solução: Remover /api/v1 do config.js"
echo ""

echo "1. Parando frontend..."
docker-compose stop frontend

echo ""
echo "2. Removendo container e imagem antiga..."
docker-compose rm -f frontend
docker rmi corujamonitor-frontend 2>/dev/null || true

echo ""
echo "3. Reconstruindo frontend..."
docker-compose build --no-cache frontend

echo ""
echo "4. Iniciando frontend..."
docker-compose up -d frontend

echo ""
echo "5. Aguardando frontend inicializar (15 segundos)..."
sleep 15

echo ""
echo "6. Verificando se frontend está rodando..."
if curl -s http://localhost:3000 > /dev/null; then
    echo "✓ Frontend está rodando!"
else
    echo "✗ Frontend NÃO está rodando"
    echo "Verificando logs..."
    docker-compose logs frontend | tail -20
fi

echo ""
echo "=========================================="
echo "CONCLUÍDO!"
echo "=========================================="
echo ""
echo "Agora:"
echo "1. Abra o navegador em modo anônimo (Ctrl+Shift+N)"
echo "2. Acesse: http://192.168.31.161:3000"
echo "3. Faça login: admin@coruja.com / admin123"
echo "4. Teste as páginas que estavam com erro"
echo ""
echo "Se ainda houver erro, limpe o cache:"
echo "  F12 > Application > Clear site data"
echo ""
