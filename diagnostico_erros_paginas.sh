#!/bin/bash

echo "=========================================="
echo "DIAGNÓSTICO DE ERROS NAS PÁGINAS"
echo "=========================================="

echo ""
echo "1. Testando endpoint /api/v1/tenants..."
curl -s http://localhost:8000/api/v1/tenants | jq '.' || echo "ERRO: Endpoint não responde ou JSON inválido"

echo ""
echo "2. Testando endpoint /api/v1/incidents..."
curl -s http://localhost:8000/api/v1/incidents | jq '.' || echo "ERRO: Endpoint não responde ou JSON inválido"

echo ""
echo "3. Testando endpoint /api/v1/knowledge-base..."
curl -s http://localhost:8000/api/v1/knowledge-base | jq '.' || echo "ERRO: Endpoint não responde ou JSON inválido"

echo ""
echo "4. Testando endpoint /api/v1/ai-activities..."
curl -s http://localhost:8000/api/v1/ai-activities | jq '.' || echo "ERRO: Endpoint não responde ou JSON inválido"

echo ""
echo "5. Verificando logs da API (últimas 50 linhas)..."
docker-compose logs api | tail -50

echo ""
echo "6. Verificando tabelas no banco..."
docker-compose exec -T db psql -U postgres -d coruja_monitor -c "
SELECT tablename 
FROM pg_tables 
WHERE schemaname = 'public' 
ORDER BY tablename;
"

echo ""
echo "7. Verificando se tabela tenants existe e tem dados..."
docker-compose exec -T db psql -U postgres -d coruja_monitor -c "
SELECT COUNT(*) as total FROM tenants;
"

echo ""
echo "8. Verificando se tabela incidents existe..."
docker-compose exec -T db psql -U postgres -d coruja_monitor -c "
SELECT COUNT(*) as total FROM incidents;
" 2>&1

echo ""
echo "9. Verificando se tabela knowledge_base existe..."
docker-compose exec -T db psql -U postgres -d coruja_monitor -c "
SELECT COUNT(*) as total FROM knowledge_base;
" 2>&1

echo ""
echo "10. Verificando se tabela ai_activities existe..."
docker-compose exec -T db psql -U postgres -d coruja_monitor -c "
SELECT COUNT(*) as total FROM ai_activities;
" 2>&1

echo ""
echo "=========================================="
echo "ANÁLISE"
echo "=========================================="
echo ""
echo "Se algum endpoint retornar erro 404 ou 500:"
echo "  → Problema na API ou rota não registrada"
echo ""
echo "Se alguma tabela não existir:"
echo "  → Execute: ./corrigir_tabelas_banco.sh"
echo ""
echo "Se os endpoints funcionam mas frontend dá erro:"
echo "  → Problema de CORS ou autenticação"
echo ""
