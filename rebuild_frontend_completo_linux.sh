#!/bin/bash

echo "=========================================="
echo "REBUILD COMPLETO DO FRONTEND - FORÇA TOTAL"
echo "=========================================="
echo ""

# Parar TODOS os containers
echo "1. Parando TODOS os containers..."
docker compose down -v

# Remover TODAS as imagens do projeto
echo ""
echo "2. Removendo TODAS as imagens antigas..."
docker rmi coruja-frontend coruja-api coruja-worker coruja-ai-agent 2>/dev/null || echo "Algumas imagens não encontradas (ok)"

# Limpar TODO o cache do Docker
echo ""
echo "3. Limpando TODO o cache do Docker..."
docker system prune -af --volumes

# Rebuild de TUDO sem cache
echo ""
echo "4. Reconstruindo TUDO sem cache..."
docker compose build --no-cache

# Subir todos os containers
echo ""
echo "5. Subindo todos os containers..."
docker compose up -d

# Aguardar containers iniciarem
echo ""
echo "6. Aguardando containers iniciarem..."
sleep 15

# Verificar status
echo ""
echo "7. Status dos containers:"
docker compose ps

# Verificar logs do frontend
echo ""
echo "8. Últimas linhas do log do frontend:"
docker compose logs --tail=20 frontend

echo ""
echo "=========================================="
echo "REBUILD COMPLETO CONCLUÍDO!"
echo "=========================================="
echo ""
echo "IMPORTANTE: LIMPE O CACHE DO NAVEGADOR!"
echo ""
echo "Chrome/Edge:"
echo "1. Pressione F12 (abrir DevTools)"
echo "2. Clique com botão direito no botão Atualizar"
echo "3. Selecione 'Esvaziar cache e atualizar forçadamente'"
echo ""
echo "OU abra em aba anônima: Ctrl+Shift+N"
echo ""
echo "Acesse: http://192.168.31.161:3000"
echo ""
