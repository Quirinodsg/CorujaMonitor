#!/bin/bash

echo "=========================================="
echo "REBUILD FRONTEND - LIMPEZA COMPLETA"
echo "=========================================="

echo ""
echo "1. Parando frontend..."
docker-compose stop frontend

echo ""
echo "2. Removendo container..."
docker-compose rm -f frontend

echo ""
echo "3. Limpando cache do Docker (builder cache)..."
docker builder prune -af

echo ""
echo "4. Removendo imagens antigas do frontend..."
docker images | grep frontend | awk '{print $3}' | xargs -r docker rmi -f

echo ""
echo "5. Verificando config.js..."
cat frontend/src/config.js | grep API_URL

echo ""
echo "6. Reconstruindo frontend (SEM cache)..."
docker-compose build --no-cache frontend

echo ""
echo "7. Subindo frontend..."
docker-compose up -d frontend

echo ""
echo "8. Aguardando frontend iniciar (30 segundos)..."
sleep 30

echo ""
echo "9. Verificando logs do frontend..."
docker-compose logs frontend | tail -20

echo ""
echo "10. Testando se frontend está respondendo..."
curl -I http://localhost:3000 2>&1 | head -5

echo ""
echo "=========================================="
echo "✓ REBUILD CONCLUÍDO!"
echo "=========================================="
echo ""
echo "Acesse: http://192.168.31.161:3000"
echo "Login: admin@coruja.com / admin123"
echo ""
echo "IMPORTANTE: Limpe o cache do navegador!"
echo "  → Chrome/Edge: Ctrl+Shift+Delete"
echo "  → Ou use modo anônimo: Ctrl+Shift+N"
echo ""
