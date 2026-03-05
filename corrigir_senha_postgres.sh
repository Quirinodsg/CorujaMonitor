#!/bin/bash

echo "========================================"
echo "CORRIGIR SENHA DO POSTGRESQL"
echo "========================================"
echo ""

echo "Este script irá:"
echo "1. Parar todos os containers"
echo "2. Remover o volume do PostgreSQL"
echo "3. Recriar o banco com a senha correta"
echo ""

read -p "Deseja continuar? (s/n): " resposta

if [ "$resposta" != "s" ] && [ "$resposta" != "S" ]; then
    echo "Operação cancelada."
    exit 0
fi

echo ""
echo "Parando containers..."
docker compose down

echo ""
echo "Removendo volume do PostgreSQL..."
docker volume rm corujamonitor_postgres_data 2>/dev/null || docker volume rm coruja-monitor_postgres_data 2>/dev/null || true

echo ""
echo "Recriando containers..."
docker compose up -d postgres redis

echo ""
echo "Aguardando PostgreSQL inicializar (30 segundos)..."
sleep 30

echo ""
echo "Verificando PostgreSQL..."
docker compose exec postgres pg_isready -U coruja

echo ""
echo "Iniciando demais containers..."
docker compose up -d

echo ""
echo "Aguardando inicialização completa (30 segundos)..."
sleep 30

echo ""
echo "Verificando status dos containers..."
docker compose ps

echo ""
echo "========================================"
echo "✅ CORREÇÃO CONCLUÍDA!"
echo "========================================"
echo ""
echo "Verificando logs da API..."
docker logs coruja-api --tail 20

echo ""
echo "Se ainda houver erro, execute:"
echo "docker logs coruja-api --tail 50"
