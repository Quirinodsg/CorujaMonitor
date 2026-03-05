#!/bin/bash

echo "=========================================="
echo "  CORRIGIR LOGIN - Servidor Linux"
echo "=========================================="
echo ""

# Verificar se está no diretório correto
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Erro: Execute este script no diretório CorujaMonitor"
    exit 1
fi

echo "✅ Diretório correto encontrado"
echo ""

# Fazer backup
echo "📦 Fazendo backup do Login.js..."
cp frontend/src/components/Login.js frontend/src/components/Login.js.bak
echo "✅ Backup criado: Login.js.bak"
echo ""

# Aplicar correção
echo "🔧 Aplicando correção no Login.js..."
sed -i '74s|const response = await axios.post.*|const API_URL = process.env.REACT_APP_API_URL || window.location.origin.replace('\'':3000'\'', '\'':8000'\'');\n      const response = await axios.post(`${API_URL}/api/v1/auth/login`, payload);|' frontend/src/components/Login.js

echo "✅ Correção aplicada"
echo ""

# Rebuild frontend
echo "🔨 Rebuilding frontend (pode demorar 2-3 minutos)..."
docker compose build --no-cache frontend

if [ $? -ne 0 ]; then
    echo "❌ Erro ao fazer build do frontend"
    exit 1
fi

echo "✅ Build concluído"
echo ""

# Reiniciar frontend
echo "🔄 Reiniciando frontend..."
docker compose up -d frontend

echo "✅ Frontend reiniciado"
echo ""

# Aguardar
echo "⏳ Aguardando 30 segundos para o frontend inicializar..."
sleep 30

echo ""
echo "=========================================="
echo "  ✅ CORREÇÃO CONCLUÍDA!"
echo "=========================================="
echo ""
echo "Agora teste no navegador:"
echo "  URL: http://192.168.31.161:3000"
echo "  Email: admin@coruja.com"
echo "  Senha: admin123"
echo ""
