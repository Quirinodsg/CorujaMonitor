#!/bin/bash

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║           REBUILD COMPLETO DO DOCKER - CORUJA MONITOR          ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Ir para pasta do projeto
cd /home/administrador/CorujaMonitor || cd /root/CorujaMonitor

echo "📍 Pasta atual: $(pwd)"
echo ""

echo "🛑 PASSO 1: Parando containers..."
docker-compose down
echo "   ✅ Containers parados"
echo ""

echo "🧹 PASSO 2: Limpando cache do Docker..."
docker system prune -f
echo "   ✅ Cache limpo"
echo ""

echo "🔨 PASSO 3: Rebuild da API (sem cache)..."
docker-compose build --no-cache api
echo "   ✅ API rebuilded"
echo ""

echo "🔨 PASSO 4: Rebuild do Frontend (sem cache)..."
docker-compose build --no-cache frontend
echo "   ✅ Frontend rebuilded"
echo ""

echo "🚀 PASSO 5: Subindo containers..."
docker-compose up -d
echo "   ✅ Containers iniciados"
echo ""

echo "⏳ PASSO 6: Aguardando 60 segundos para containers iniciarem..."
sleep 60
echo "   ✅ Aguardado"
echo ""

echo "📊 PASSO 7: Status dos containers..."
docker-compose ps
echo ""

echo "📝 PASSO 8: Logs da API (últimas 30 linhas)..."
docker-compose logs api | tail -30
echo ""

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║                    TESTANDO ENDPOINTS                          ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

echo "🧪 Testando endpoint /probes/heartbeat..."
curl -X POST "http://localhost:3000/api/v1/probes/heartbeat?probe_token=V-PTetiHvbNsZgrkY14PFGRfyv6jPBZxdTb76Z2M7YY&version=1.0.0"
echo ""
echo ""

echo "🧪 Testando endpoint /servers/check..."
curl -X GET "http://localhost:3000/api/v1/servers/check?probe_token=V-PTetiHvbNsZgrkY14PFGRfyv6jPBZxdTb76Z2M7YY&hostname=SRVSONDA001"
echo ""
echo ""

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║                    REBUILD CONCLUIDO!                          ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Agora teste a probe no Windows:"
echo "  C:\Program Files\CorujaMonitor\Probe\INICIAR_PROBE.bat"
echo ""
