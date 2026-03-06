#!/bin/bash

echo "========================================="
echo "📚 POPULANDO BASE DE CONHECIMENTO"
echo "========================================="
echo ""

cd /home/administrador/CorujaMonitor

echo "1️⃣  Criando tabelas da base de conhecimento..."
docker-compose exec -T api python migrate_knowledge_base.py
echo ""

echo "2️⃣  Populando com 80 itens..."
docker-compose exec -T api python seed_kb_80_items.py
echo ""

echo "3️⃣  Verificando quantidade de itens..."
docker-compose exec -T db psql -U coruja_user -d coruja_monitor -c "SELECT COUNT(*) as total_itens FROM knowledge_base_entries;"
echo ""

echo "========================================="
echo "✅ BASE DE CONHECIMENTO POPULADA!"
echo "========================================="
echo ""
echo "🌐 Acesse: http://192.168.31.161:3000"
echo "📚 Vá em: Base de Conhecimento"
echo ""
echo "Você deve ver 80 itens organizados por:"
echo "- Windows (10 itens)"
echo "- Linux (10 itens)"
echo "- Docker (10 itens)"
echo "- Rede (10 itens)"
echo "- Banco de Dados (10 itens)"
echo "- Aplicações Web (10 itens)"
echo "- Segurança (10 itens)"
echo "- Hardware (10 itens)"
echo ""
