#!/bin/bash
# Script para deploy da correção de contagem de incidentes no dashboard
# Uso: ./scripts/deploy-dashboard-fix.sh

set -e  # Parar em caso de erro

echo "🚀 Deploy: Correção Dashboard Incidentes"
echo "========================================"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar se está no diretório correto
if [ ! -f "api/routers/dashboard.py" ]; then
    echo -e "${RED}❌ Erro: Execute este script da raiz do projeto CorujaMonitor${NC}"
    exit 1
fi

# Backup
echo -e "${YELLOW}📦 Criando backup...${NC}"
BACKUP_DIR="backups/dashboard-fix-$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp api/routers/dashboard.py "$BACKUP_DIR/"
cp frontend/src/components/Incidents.js "$BACKUP_DIR/"
echo -e "${GREEN}✅ Backup criado em: $BACKUP_DIR${NC}"

# Verificar se há alterações não commitadas
if [ -n "$(git status --porcelain)" ]; then
    echo -e "${YELLOW}⚠️  Há alterações não commitadas${NC}"
    git status --short
    read -p "Deseja continuar? (s/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        exit 1
    fi
fi

# Pull das alterações
echo -e "${YELLOW}📥 Atualizando código...${NC}"
git pull origin main

# Verificar se os arquivos foram alterados
if git diff HEAD~1 HEAD --name-only | grep -q "api/routers/dashboard.py"; then
    echo -e "${GREEN}✅ dashboard.py atualizado${NC}"
else
    echo -e "${YELLOW}⚠️  dashboard.py não foi alterado${NC}"
fi

if git diff HEAD~1 HEAD --name-only | grep -q "frontend/src/components/Incidents.js"; then
    echo -e "${GREEN}✅ Incidents.js atualizado${NC}"
else
    echo -e "${YELLOW}⚠️  Incidents.js não foi alterado${NC}"
fi

# Reiniciar API
echo -e "${YELLOW}🔄 Reiniciando API...${NC}"
if systemctl is-active --quiet coruja-api; then
    sudo systemctl restart coruja-api
    sleep 2
    if systemctl is-active --quiet coruja-api; then
        echo -e "${GREEN}✅ API reiniciada com sucesso${NC}"
    else
        echo -e "${RED}❌ Erro ao reiniciar API${NC}"
        sudo journalctl -u coruja-api -n 20 --no-pager
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️  Serviço coruja-api não está rodando${NC}"
fi

# Rebuild frontend
echo -e "${YELLOW}🏗️  Rebuilding frontend...${NC}"
cd frontend

if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📦 Instalando dependências...${NC}"
    npm install
fi

npm run build

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Frontend buildado com sucesso${NC}"
    
    # Copiar para nginx (ajustar caminho conforme necessário)
    if [ -d "/var/www/coruja-monitor" ]; then
        echo -e "${YELLOW}📋 Copiando para nginx...${NC}"
        sudo cp -r build/* /var/www/coruja-monitor/
        sudo systemctl reload nginx
        echo -e "${GREEN}✅ Frontend deployado${NC}"
    else
        echo -e "${YELLOW}⚠️  Diretório /var/www/coruja-monitor não encontrado${NC}"
        echo "   Copie manualmente: sudo cp -r build/* /caminho/do/nginx/"
    fi
else
    echo -e "${RED}❌ Erro no build do frontend${NC}"
    exit 1
fi

cd ..

# Verificação
echo ""
echo -e "${GREEN}✅ Deploy concluído!${NC}"
echo ""
echo "📊 Verificação:"
echo "1. Acesse o dashboard e verifique a contagem de incidentes"
echo "2. Acesse a página de incidentes e compare os números"
echo "3. Verifique os logs: sudo journalctl -u coruja-api -f"
echo ""
echo "🔙 Rollback (se necessário):"
echo "   cp $BACKUP_DIR/dashboard.py api/routers/dashboard.py"
echo "   sudo systemctl restart coruja-api"
echo ""

# Mostrar contagem atual de incidentes
echo -e "${YELLOW}📈 Contagem atual de incidentes:${NC}"
sudo -u postgres psql coruja_monitor -c "
SELECT 
    status, 
    COUNT(*) as total 
FROM incidents 
WHERE status IN ('open', 'acknowledged', 'resolved') 
GROUP BY status 
ORDER BY 
    CASE status 
        WHEN 'open' THEN 1 
        WHEN 'acknowledged' THEN 2 
        ELSE 3 
    END;
" 2>/dev/null || echo "⚠️  Não foi possível consultar o banco de dados"

echo ""
echo -e "${GREEN}🎉 Deploy finalizado!${NC}"