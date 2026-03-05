#!/bin/bash

echo "========================================================================"
echo "  RESETAR SISTEMA COMPLETO - Coruja Monitor"
echo "========================================================================"
echo ""
echo "⚠️  ATENÇÃO: Este script irá:"
echo "   - Parar todos os containers"
echo "   - Remover TODOS os volumes (dados serão perdidos!)"
echo "   - Recriar todo o sistema do zero"
echo ""
echo "Use este script se:"
echo "   - Erro de autenticação do PostgreSQL"
echo "   - Sistema não inicia corretamente"
echo "   - Quer começar do zero"
echo ""

read -p "Deseja continuar? (digite 'sim' para confirmar): " resposta

if [ "$resposta" != "sim" ]; then
    echo ""
    echo "❌ Operação cancelada."
    exit 0
fi

echo ""
echo "========================================================================"
echo "PASSO 1: Parando containers..."
echo "========================================================================"
docker compose down

echo ""
echo "✅ Containers parados"

echo ""
echo "========================================================================"
echo "PASSO 2: Removendo volumes..."
echo "========================================================================"

# Tentar diferentes nomes de volumes
docker volume rm corujamonitor_postgres_data 2>/dev/null && echo "✅ Volume corujamonitor_postgres_data removido" || echo "⚠️  Volume corujamonitor_postgres_data não encontrado"
docker volume rm coruja-monitor_postgres_data 2>/dev/null && echo "✅ Volume coruja-monitor_postgres_data removido" || echo "⚠️  Volume coruja-monitor_postgres_data não encontrado"
docker volume rm CorujaMonitor_postgres_data 2>/dev/null && echo "✅ Volume CorujaMonitor_postgres_data removido" || echo "⚠️  Volume CorujaMonitor_postgres_data não encontrado"

# Remover outros volumes
docker volume rm corujamonitor_redis_data 2>/dev/null || true
docker volume rm corujamonitor_ollama_data 2>/dev/null || true
docker volume rm corujamonitor_api_logs 2>/dev/null || true
docker volume rm corujamonitor_worker_logs 2>/dev/null || true
docker volume rm corujamonitor_ai_logs 2>/dev/null || true

echo ""
echo "✅ Volumes removidos"

echo ""
echo "========================================================================"
echo "PASSO 3: Verificando arquivo .env..."
echo "========================================================================"

if [ ! -f .env ]; then
    echo "❌ Arquivo .env não encontrado!"
    echo "Criando .env a partir de .env.example..."
    cp .env.example .env
    echo "✅ Arquivo .env criado"
    echo ""
    echo "⚠️  IMPORTANTE: Edite o arquivo .env antes de continuar!"
    echo "Execute: nano .env"
    exit 1
fi

echo "✅ Arquivo .env encontrado"
echo ""
echo "Configurações do PostgreSQL:"
grep "POSTGRES_" .env | grep -v "^#"

echo ""
echo "========================================================================"
echo "PASSO 4: Recriando containers..."
echo "========================================================================"

docker compose up -d

echo ""
echo "✅ Containers criados"

echo ""
echo "========================================================================"
echo "PASSO 5: Aguardando inicialização..."
echo "========================================================================"

echo "Aguardando PostgreSQL (30 segundos)..."
for i in {1..30}; do
    echo -n "."
    sleep 1
done
echo ""

echo ""
echo "✅ Inicialização concluída"

echo ""
echo "========================================================================"
echo "PASSO 6: Verificando status..."
echo "========================================================================"

docker compose ps

echo ""
echo "========================================================================"
echo "PASSO 7: Verificando logs da API..."
echo "========================================================================"

docker logs coruja-api --tail 30

echo ""
echo "========================================================================"
echo "PASSO 8: Testando conectividade..."
echo "========================================================================"

echo "Testando PostgreSQL..."
docker compose exec -T postgres pg_isready -U coruja && echo "✅ PostgreSQL OK" || echo "❌ PostgreSQL com problema"

echo ""
echo "Testando Redis..."
docker compose exec -T redis redis-cli ping && echo "✅ Redis OK" || echo "❌ Redis com problema"

echo ""
echo "Testando API..."
sleep 5
curl -s http://localhost:8000/health && echo "" && echo "✅ API OK" || echo "❌ API com problema"

echo ""
echo "========================================================================"
echo "PASSO 9: Criando usuário admin..."
echo "========================================================================"

docker compose exec api python init_admin.py 2>/dev/null || echo "⚠️  Script init_admin.py não encontrado (normal se não existir)"

echo ""
echo "========================================================================"
echo "✅ SISTEMA RESETADO COM SUCESSO!"
echo "========================================================================"
echo ""
echo "Próximos passos:"
echo ""
echo "1. Acesse: http://localhost:3000"
echo "2. Login padrão:"
echo "   Email: admin@coruja.com"
echo "   Senha: admin123"
echo ""
echo "3. MUDE A SENHA após primeiro login!"
echo ""
echo "Comandos úteis:"
echo "  - Ver logs: docker logs coruja-api --tail 50"
echo "  - Ver status: docker compose ps"
echo "  - Parar: docker compose down"
echo "  - Iniciar: docker compose up -d"
echo ""
