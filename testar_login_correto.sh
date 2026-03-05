#!/bin/bash

echo "========================================"
echo "TESTE DE LOGIN - URL CORRETA"
echo "========================================"
echo ""

echo "Testando login com URL correta..."
echo ""

curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@coruja.com","password":"admin123"}' \
  -w "\nHTTP Code: %{http_code}\n"

echo ""
echo "========================================"
echo ""
echo "Se retornou 'access_token', o login está funcionando!"
echo "Se retornou erro, veja os logs:"
echo "docker logs coruja-api --tail 50"
echo ""
