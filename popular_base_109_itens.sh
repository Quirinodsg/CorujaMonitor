#!/bin/bash

echo "========================================"
echo "📚 POPULAR BASE DE CONHECIMENTO"
echo "   109+ ITENS COMPLETOS"
echo "========================================"
echo ""

cd /home/administrador/CorujaMonitor

echo "🗑️  Limpando base atual..."
docker-compose exec -T db psql -U coruja_user -d coruja_monitor -c "DELETE FROM knowledge_base_entries;"
echo ""

echo "📚 Populando base completa (109+ itens)..."
docker-compose exec -T api python popular_109_itens_completo.py
echo ""

echo "✅ BASE COMPLETA POPULADA!"
echo ""

echo "📊 Verificando total de itens:"
docker-compose exec -T db psql -U coruja_user -d coruja_monitor -c "SELECT COUNT(*) as total_itens FROM knowledge_base_entries;"
echo ""

echo "========================================"
echo "✅ CONCLUÍDO!"
echo "========================================"
echo ""
echo "🌐 Acesse: http://192.168.31.161:3000"
echo "👤 Login: admin@coruja.com"
echo "🔑 Senha: admin123"
echo ""
echo "📖 Vá em 'Base de Conhecimento' para ver os 109+ itens"
echo ""
