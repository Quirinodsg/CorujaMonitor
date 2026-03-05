#!/bin/bash

echo "=========================================="
echo "CORRIGIR TODOS OS LOCALHOST NO FRONTEND"
echo "=========================================="
echo ""

echo "Arquivos que usam localhost:8000 hardcoded:"
grep -r "localhost:8000" frontend/src/ --include="*.js" | wc -l

echo ""
echo "Substituindo localhost:8000 por \${API_URL} em todos os arquivos..."

# Criar arquivo temporário com função helper
cat > frontend/src/api.js << 'EOF'
import { API_URL } from './config';

// Helper para fazer requisições à API
export const apiRequest = async (endpoint, options = {}) => {
  const url = `${API_URL}${endpoint}`;
  const token = localStorage.getItem('token');
  
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` })
    }
  };
  
  const mergedOptions = {
    ...defaultOptions,
    ...options,
    headers: {
      ...defaultOptions.headers,
      ...options.headers
    }
  };
  
  return fetch(url, mergedOptions);
};

export { API_URL };
EOF

echo "✓ Arquivo api.js criado"

echo ""
echo "Agora você precisa atualizar manualmente os arquivos:"
echo "  - MFASetup.js"
echo "  - SecurityMonitor.js"
echo "  - KubernetesDashboard.js"
echo ""
echo "OU executar rebuild completo para forçar uso do config.js"
echo ""
echo "SOLUÇÃO RÁPIDA: Limpar TUDO e reconstruir"
echo ""

read -p "Deseja fazer rebuild completo agora? (s/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]
then
    echo "Parando frontend..."
    docker compose stop frontend
    
    echo "Removendo container e imagem..."
    docker compose rm -f frontend
    docker rmi corujamonitor-frontend:latest 2>/dev/null || true
    docker rmi coruja-frontend:latest 2>/dev/null || true
    
    echo "Limpando cache do Docker..."
    docker builder prune -af
    
    echo "Reconstruindo frontend..."
    docker compose build --no-cache frontend
    
    echo "Iniciando frontend..."
    docker compose up -d frontend
    
    echo ""
    echo "✓ Rebuild completo!"
    echo "Aguarde 30 segundos e acesse em aba anônima:"
    echo "http://192.168.31.161:3000"
fi
