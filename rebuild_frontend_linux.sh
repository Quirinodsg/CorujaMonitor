#!/bin/bash

echo "=========================================="
echo "REBUILD COMPLETO DO FRONTEND NO LINUX"
echo "=========================================="
echo ""

# Parar containers
echo "1. Parando containers..."
docker compose down

# Remover imagem antiga do frontend
echo ""
echo "2. Removendo imagem antiga do frontend..."
docker rmi coruja-frontend 2>/dev/null || echo "Imagem não encontrada (ok)"

# Limpar cache do Docker
echo ""
echo "3. Limpando cache do Docker..."
docker builder prune -f

# Rebuild do frontend sem cache
echo ""
echo "4. Reconstruindo frontend sem cache..."
docker compose build --no-cache frontend

# Subir todos os containers
echo ""
echo "5. Subindo todos os containers..."
docker compose up -d

# Aguardar containers iniciarem
echo ""
echo "6. Aguardando containers iniciarem..."
sleep 10

# Verificar status
echo ""
echo "7. Status dos containers:"
docker compose ps

echo ""
echo "=========================================="
echo "REBUILD CONCLUÍDO!"
echo "=========================================="
echo ""
echo "Acesse: http://192.168.31.161:3000"
echo ""
echo "IMPORTANTE: Limpe o cache do navegador:"
echo "- Chrome/Edge: Ctrl+Shift+Delete"
echo "- Ou abra em aba anônima: Ctrl+Shift+N"
echo ""
