#!/bin/bash
# Restaurar Backup do Banco de Dados PostgreSQL

BACKUP_DIR="/home/administrador/CorujaMonitor/api/backups"
CONTAINER_NAME="coruja-postgres"
DB_NAME="coruja_monitor"
DB_USER="coruja_user"

# Listar backups disponíveis
echo "Backups disponíveis:"
echo "===================="
ls -lh "$BACKUP_DIR"/coruja_backup_*.sql | nl
echo ""

# Solicitar qual backup restaurar
read -p "Digite o número do backup para restaurar (ou ENTER para o mais recente): " CHOICE

if [ -z "$CHOICE" ]; then
    # Usar backup mais recente
    BACKUP_FILE=$(ls -t "$BACKUP_DIR"/coruja_backup_*.sql | head -1)
else
    # Usar backup escolhido
    BACKUP_FILE=$(ls -t "$BACKUP_DIR"/coruja_backup_*.sql | sed -n "${CHOICE}p")
fi

if [ -z "$BACKUP_FILE" ]; then
    echo "✗ Backup não encontrado!"
    exit 1
fi

echo ""
echo "Backup selecionado: $(basename $BACKUP_FILE)"
echo ""
read -p "ATENÇÃO: Isso vai SOBRESCREVER o banco atual. Continuar? (sim/não): " CONFIRM

if [ "$CONFIRM" != "sim" ]; then
    echo "Operação cancelada."
    exit 0
fi

echo ""
echo "Restaurando backup..."

# Parar containers que usam o banco
docker stop coruja-api coruja-worker coruja-ai-agent

# Dropar e recriar banco
docker exec -t $CONTAINER_NAME psql -U $DB_USER -c "DROP DATABASE IF EXISTS $DB_NAME;"
docker exec -t $CONTAINER_NAME psql -U $DB_USER -c "CREATE DATABASE $DB_NAME;"

# Restaurar backup
cat "$BACKUP_FILE" | docker exec -i $CONTAINER_NAME psql -U $DB_USER -d $DB_NAME

# Reiniciar containers
docker start coruja-api coruja-worker coruja-ai-agent

echo ""
echo "✓ Backup restaurado com sucesso!"
echo "✓ Containers reiniciados"
