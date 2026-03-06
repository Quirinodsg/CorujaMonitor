#!/bin/bash

echo "========================================="
echo "🔧 CORRIGINDO URLs DUPLICADAS"
echo "========================================="
echo ""

# 1. Stash mudanças locais
echo "📦 Salvando mudanças locais..."
git stash
echo ""

# 2. Pull do Git
echo "📥 Baixando atualizações do Git..."
git pull origin master
echo ""

# 3. Parar frontend
echo "⏸️  Parando frontend..."
docker-compose stop frontend
echo ""

# 4. Remover container antigo
echo "🗑️  Removendo container antigo..."
docker-compose rm -f frontend
echo ""

# 5. Limpar cache do Docker
echo "🧹 Limpando cache do Docker..."
docker builder prune -af
echo ""

# 6. Remover imagens antigas do frontend
echo "🗑️  Removendo imagens antigas..."
docker rmi $(docker images | grep 'corujamonitor[_-]frontend' | awk '{print $3}') 2>/dev/null || echo "Nenhuma imagem antiga encontrada"
echo ""

# 7. Rebuild do frontend SEM CACHE
echo "🔨 Reconstruindo frontend do zero..."
docker-compose build --no-cache frontend
echo ""

# 8. Subir frontend
echo "🚀 Subindo frontend..."
docker-compose up -d frontend
echo ""

# 9. Aguardar 10 segundos
echo "⏳ Aguardando 10 segundos para o frontend iniciar..."
sleep 10
echo ""

# 10. Verificar logs
echo "📋 Logs do frontend:"
docker-compose logs --tail=30 frontend
echo ""

echo "========================================="
echo "✅ CORREÇÃO CONCLUÍDA!"
echo "========================================="
echo ""
echo "🌐 Acesse: http://192.168.31.161:3000"
echo ""
echo "⚠️  IMPORTANTE:"
echo "1. Abra o navegador em MODO ANÔNIMO (Ctrl+Shift+N)"
echo "2. Ou limpe o cache: Ctrl+Shift+Delete"
echo "3. Faça login: admin@coruja.com / admin123"
echo "4. Teste TODAS as páginas"
echo ""
