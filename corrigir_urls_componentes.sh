#!/bin/bash

echo "=========================================="
echo "CORRIGIR URLs NOS COMPONENTES"
echo "=========================================="

echo ""
echo "Problema: Componentes usam api.get('/api/v1/...')"
echo "Solução: Remover /api/v1 pois já está no baseURL"
echo ""

cd frontend/src/components

echo "Corrigindo arquivos..."

# Substituir /api/v1/ por / em todos os arquivos .js
find . -name "*.js" -type f -exec sed -i "s|'/api/v1/|'/|g" {} \;
find . -name "*.js" -type f -exec sed -i 's|"/api/v1/|"/|g' {} \;
find . -name "*.js" -type f -exec sed -i 's|`/api/v1/|`/|g' {} \;

echo "✓ Arquivos corrigidos!"

cd ../../..

echo ""
echo "Verificando mudanças..."
git diff frontend/src/components/ | head -50

echo ""
echo "=========================================="
echo "PRÓXIMO PASSO"
echo "=========================================="
echo ""
echo "Execute:"
echo "  git add frontend/src/components/"
echo "  git commit -m 'fix: Remover /api/v1 duplicado dos componentes'"
echo "  git push origin master"
echo ""
echo "Depois no servidor Linux:"
echo "  cd ~/CorujaMonitor"
echo "  git pull origin master"
echo "  ./corrigir_url_duplicada.sh"
echo ""
