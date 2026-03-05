#!/bin/bash

echo "=========================================="
echo "CORRIGIR TABELAS DO BANCO DE DADOS"
echo "=========================================="

echo ""
echo "1. Verificando tabelas existentes..."
docker-compose exec -T db psql -U postgres -d coruja_monitor -c "
SELECT tablename 
FROM pg_tables 
WHERE schemaname = 'public' 
ORDER BY tablename;
"

echo ""
echo "2. Criando/atualizando TODAS as tabelas via models.py..."
docker-compose exec -T api python3 << 'PYTHON'
from database import engine, Base
from models import *

print("Criando todas as tabelas...")
Base.metadata.create_all(bind=engine)
print("✓ Tabelas criadas/atualizadas!")
PYTHON

echo ""
echo "3. Verificando tabelas após criação..."
docker-compose exec -T db psql -U postgres -d coruja_monitor -c "
SELECT tablename 
FROM pg_tables 
WHERE schemaname = 'public' 
ORDER BY tablename;
"

echo ""
echo "4. Verificando estrutura da tabela incidents..."
docker-compose exec -T db psql -U postgres -d coruja_monitor -c "
\d incidents
"

echo ""
echo "5. Verificando estrutura da tabela knowledge_base..."
docker-compose exec -T db psql -U postgres -d coruja_monitor -c "
\d knowledge_base
"

echo ""
echo "6. Verificando estrutura da tabela ai_activities..."
docker-compose exec -T db psql -U postgres -d coruja_monitor -c "
\d ai_activities
"

echo ""
echo "7. Populando Knowledge Base com dados iniciais..."
docker-compose exec -T api python3 << 'PYTHON'
from database import SessionLocal
from models import KnowledgeBaseEntry
from datetime import datetime

db = SessionLocal()

# Verificar se já existem entradas
count = db.query(KnowledgeBaseEntry).count()
print(f"Entradas existentes: {count}")

if count == 0:
    print("Criando entradas iniciais...")
    
    entries = [
        {
            "title": "Servidor não responde a ping",
            "category": "network",
            "problem_description": "Servidor não responde a requisições ICMP (ping)",
            "solution": "1. Verificar se o servidor está ligado\n2. Verificar firewall\n3. Verificar cabo de rede\n4. Verificar configuração de rede",
            "tags": ["ping", "network", "connectivity"],
            "severity": "high"
        },
        {
            "title": "CPU alta",
            "category": "performance",
            "problem_description": "Uso de CPU acima de 80%",
            "solution": "1. Identificar processo consumindo CPU\n2. Verificar se é comportamento esperado\n3. Considerar upgrade de hardware\n4. Otimizar aplicação",
            "tags": ["cpu", "performance"],
            "severity": "medium"
        },
        {
            "title": "Memória RAM alta",
            "category": "performance",
            "problem_description": "Uso de memória RAM acima de 90%",
            "solution": "1. Identificar processo consumindo memória\n2. Verificar memory leaks\n3. Reiniciar serviços se necessário\n4. Considerar upgrade de RAM",
            "tags": ["memory", "ram", "performance"],
            "severity": "medium"
        },
        {
            "title": "Disco cheio",
            "category": "storage",
            "problem_description": "Espaço em disco acima de 90%",
            "solution": "1. Limpar arquivos temporários\n2. Remover logs antigos\n3. Mover dados para outro disco\n4. Expandir disco",
            "tags": ["disk", "storage", "space"],
            "severity": "high"
        },
        {
            "title": "Serviço parado",
            "category": "service",
            "problem_description": "Serviço crítico não está rodando",
            "solution": "1. Verificar logs do serviço\n2. Tentar reiniciar o serviço\n3. Verificar dependências\n4. Verificar configuração",
            "tags": ["service", "windows", "linux"],
            "severity": "critical"
        }
    ]
    
    for entry_data in entries:
        entry = KnowledgeBaseEntry(
            **entry_data,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            is_active=True,
            view_count=0,
            helpful_count=0
        )
        db.add(entry)
    
    db.commit()
    print(f"✓ {len(entries)} entradas criadas!")
else:
    print("Knowledge Base já possui dados")

db.close()
PYTHON

echo ""
echo "8. Reiniciando API para aplicar mudanças..."
docker-compose restart api

echo ""
echo "9. Aguardando API reiniciar (10 segundos)..."
sleep 10

echo ""
echo "10. Testando endpoints..."

echo ""
echo "  → Testando /api/v1/tenants..."
curl -s http://localhost:8000/api/v1/tenants | head -c 100
echo ""

echo ""
echo "  → Testando /api/v1/incidents..."
curl -s http://localhost:8000/api/v1/incidents | head -c 100
echo ""

echo ""
echo "  → Testando /api/v1/knowledge-base..."
curl -s http://localhost:8000/api/v1/knowledge-base | head -c 100
echo ""

echo ""
echo "=========================================="
echo "CONCLUÍDO!"
echo "=========================================="
echo ""
echo "Recarregue o navegador (Ctrl+Shift+R)"
echo "Acesse: http://192.168.31.161:3000"
echo ""
