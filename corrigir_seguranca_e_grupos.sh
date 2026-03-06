#!/bin/bash

echo "========================================="
echo "🔧 CORRIGINDO SEGURANÇA E GRUPOS"
echo "========================================="
echo ""

# 1. Pull do Git
echo "📥 Baixando atualizações do Git..."
git pull origin master
echo ""

# 2. Criar tabela sensor_groups
echo "🗄️  Criando tabela sensor_groups..."
docker-compose exec -T api python migrate_sensor_groups.py
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

# 6. Rebuild do frontend SEM CACHE
echo "🔨 Reconstruindo frontend do zero..."
docker-compose build --no-cache frontend
echo ""

# 7. Subir frontend
echo "🚀 Subindo frontend..."
docker-compose up -d frontend
echo ""

# 8. Aguardar 10 segundos
echo "⏳ Aguardando 10 segundos para o frontend iniciar..."
sleep 10
echo ""

# 9. Verificar logs
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
echo "4. Teste as páginas:"
echo "   ✓ Configurações > Segurança"
echo "   ✓ Configurações > MFA"
echo "   ✓ Servidores (grupos)"
echo ""
