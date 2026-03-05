#!/bin/bash

echo "=========================================="
echo "TESTAR ENDPOINTS COM AUTENTICAÇÃO"
echo "=========================================="

echo ""
echo "1. Fazendo login para obter token..."
RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin@coruja.com","password":"admin123"}')

TOKEN=$(echo $RESPONSE | jq -r '.access_token')

if [ "$TOKEN" = "null" ] || [ -z "$TOKEN" ]; then
    echo "✗ ERRO: Não foi possível obter token"
    echo "Resposta: $RESPONSE"
    exit 1
fi

echo "✓ Token obtido: ${TOKEN:0:30}..."

echo ""
echo "2. Testando /api/v1/tenants com autenticação..."
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/tenants | jq '.'

echo ""
echo "3. Testando /api/v1/incidents com autenticação..."
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/incidents | jq '.'

echo ""
echo "4. Testando /api/v1/reports com autenticação..."
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/reports | jq '.'

echo ""
echo "5. Testando /api/v1/knowledge-base com autenticação..."
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/knowledge-base | jq '.'

echo ""
echo "6. Testando /api/v1/ai-activities com autenticação..."
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/ai-activities | jq '.'

echo ""
echo "7. Testando /api/v1/ai/config com autenticação..."
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/ai/config | jq '.'

echo ""
echo "=========================================="
echo "CONCLUSÃO"
echo "=========================================="
echo ""
echo "Se todos os endpoints retornaram dados:"
echo "  → API está funcionando corretamente"
echo "  → Problema está no FRONTEND"
echo ""
echo "Se algum endpoint retornou erro:"
echo "  → Anote qual endpoint falhou"
echo "  → Verifique os logs da API"
echo ""
