#!/bin/bash
# Script de Verificação Completa do Sistema Coruja Monitor

echo "═══════════════════════════════════════════════════════════════"
echo "  VERIFICAÇÃO COMPLETA DO SISTEMA CORUJA MONITOR"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. VERIFICAR CONTAINERS DOCKER
echo "1. VERIFICANDO CONTAINERS DOCKER..."
echo "-----------------------------------"
CONTAINERS=$(docker ps --format "table {{.Names}}\t{{.Status}}" | grep coruja)
if [ -z "$CONTAINERS" ]; then
    echo -e "${RED}✗ Nenhum container rodando!${NC}"
else
    echo -e "${GREEN}✓ Containers rodando:${NC}"
    docker ps --format "table {{.Names}}\t{{.Status}}" | grep coruja
fi
echo ""

# 2. VERIFICAR API
echo "2. VERIFICANDO API..."
echo "---------------------"
API_HEALTH=$(curl -s http://localhost:8000/health)
if [[ $API_HEALTH == *"healthy"* ]]; then
    echo -e "${GREEN}✓ API funcionando: $API_HEALTH${NC}"
else
    echo -e "${RED}✗ API não responde!${NC}"
fi
echo ""

# 3. VERIFICAR FRONTEND
echo "3. VERIFICANDO FRONTEND..."
echo "--------------------------"
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000)
if [ "$FRONTEND_STATUS" == "200" ]; then
    echo -e "${GREEN}✓ Frontend funcionando (HTTP $FRONTEND_STATUS)${NC}"
else
    echo -e "${RED}✗ Frontend não responde (HTTP $FRONTEND_STATUS)${NC}"
fi
echo ""

# 4. VERIFICAR BANCO DE DADOS
echo "4. VERIFICANDO BANCO DE DADOS..."
echo "--------------------------------"
DB_CHECK=$(docker exec coruja-postgres psql -U coruja_user -d coruja_monitor -c "SELECT COUNT(*) FROM users;" 2>&1)
if [[ $DB_CHECK == *"1"* ]] || [[ $DB_CHECK == *"count"* ]]; then
    echo -e "${GREEN}✓ Banco de dados acessível${NC}"
    echo "   Usuários cadastrados: $(echo "$DB_CHECK" | grep -oP '\d+' | head -1)"
else
    echo -e "${RED}✗ Erro ao acessar banco: $DB_CHECK${NC}"
fi
echo ""

# 5. VERIFICAR SNMPD
echo "5. VERIFICANDO SNMPD..."
echo "-----------------------"
SNMPD_STATUS=$(systemctl is-active snmpd)
if [ "$SNMPD_STATUS" == "active" ]; then
    echo -e "${GREEN}✓ SNMPD rodando${NC}"
    # Testar SNMP
    SNMP_TEST=$(snmpget -v2c -c public localhost sysDescr.0 2>&1)
    if [[ $SNMP_TEST == *"Linux"* ]]; then
        echo -e "${GREEN}✓ SNMP respondendo${NC}"
    else
        echo -e "${YELLOW}⚠ SNMP não responde: $SNMP_TEST${NC}"
    fi
else
    echo -e "${RED}✗ SNMPD não está rodando${NC}"
fi
echo ""

# 6. VERIFICAR BACKUPS
echo "6. VERIFICANDO BACKUPS..."
echo "-------------------------"
BACKUP_DIR="/home/administrador/CorujaMonitor/api/backups"
if [ -d "$BACKUP_DIR" ]; then
    BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/coruja_backup_*.sql 2>/dev/null | wc -l)
    if [ "$BACKUP_COUNT" -gt 0 ]; then
        echo -e "${GREEN}✓ $BACKUP_COUNT backup(s) encontrado(s)${NC}"
        echo "   Último backup:"
        ls -lh "$BACKUP_DIR"/coruja_backup_*.sql | tail -1
    else
        echo -e "${YELLOW}⚠ Nenhum backup encontrado${NC}"
    fi
else
    echo -e "${RED}✗ Diretório de backup não existe${NC}"
fi
echo ""

# 7. VERIFICAR CRON
echo "7. VERIFICANDO CRON (BACKUP AUTOMÁTICO)..."
echo "------------------------------------------"
CRON_CHECK=$(sudo crontab -l 2>/dev/null | grep backup_automatico)
if [ -z "$CRON_CHECK" ]; then
    echo -e "${YELLOW}⚠ Backup automático NÃO configurado no cron${NC}"
else
    echo -e "${GREEN}✓ Backup automático configurado:${NC}"
    echo "   $CRON_CHECK"
fi
echo ""

# 8. VERIFICAR ESPAÇO EM DISCO
echo "8. VERIFICANDO ESPAÇO EM DISCO..."
echo "---------------------------------"
DISK_USAGE=$(df -h / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -lt 80 ]; then
    echo -e "${GREEN}✓ Espaço em disco OK: ${DISK_USAGE}% usado${NC}"
elif [ "$DISK_USAGE" -lt 90 ]; then
    echo -e "${YELLOW}⚠ Espaço em disco: ${DISK_USAGE}% usado${NC}"
else
    echo -e "${RED}✗ CRÍTICO: Espaço em disco: ${DISK_USAGE}% usado${NC}"
fi
echo ""

# 9. VERIFICAR LOGS DE ERRO
echo "9. VERIFICANDO LOGS DE ERRO (ÚLTIMAS 24H)..."
echo "---------------------------------------------"
ERROR_COUNT=$(docker logs coruja-api --since 24h 2>&1 | grep -i error | wc -l)
if [ "$ERROR_COUNT" -eq 0 ]; then
    echo -e "${GREEN}✓ Nenhum erro nos logs (últimas 24h)${NC}"
elif [ "$ERROR_COUNT" -lt 10 ]; then
    echo -e "${YELLOW}⚠ $ERROR_COUNT erro(s) encontrado(s) nos logs${NC}"
else
    echo -e "${RED}✗ $ERROR_COUNT erro(s) encontrado(s) nos logs!${NC}"
fi
echo ""

# 10. RESUMO FINAL
echo "═══════════════════════════════════════════════════════════════"
echo "  RESUMO DA VERIFICAÇÃO"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "URLs de Acesso:"
echo "  - API: http://192.168.31.161:8000"
echo "  - Frontend: http://192.168.31.161:3000"
echo "  - Login: admin@coruja.com / admin123"
echo ""
echo "Comandos Úteis:"
echo "  - Backup manual: ./backup_automatico.sh"
echo "  - Restaurar backup: ./restaurar_backup.sh"
echo "  - Logs API: docker logs -f coruja-api"
echo "  - Reiniciar: docker-compose restart"
echo ""
echo "═══════════════════════════════════════════════════════════════"
