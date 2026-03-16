#!/bin/bash
# Backup Automático do Banco de Dados PostgreSQL
# Mantém últimos 7 backups diários

BACKUP_DIR="/home/administrador/CorujaMonitor/api/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="coruja_backup_${TIMESTAMP}.sql"
CONTAINER_NAME="coruja-postgres"
DB_NAME="coruja_monitor"
DB_USER="coruja_user"

# Criar diretório se não existir
mkdir -p "$BACKUP_DIR"

# Fazer backup
echo "Iniciando backup do banco de dados..."
docker exec -t $CONTAINER_NAME pg_dump -U $DB_USER -d $DB_NAME > "$BACKUP_DIR/$BACKUP_FILE"

# Verificar se backup foi criado
if [ -f "$BACKUP_DIR/$BACKUP_FILE" ]; then
    SIZE=$(du -h "$BACKUP_DIR/$BACKUP_FILE" | cut -f1)
    echo "✓ Backup criado: $BACKUP_FILE ($SIZE)"
    
    # Remover backups antigos (manter últimos 7)
    cd "$BACKUP_DIR"
    ls -t coruja_backup_*.sql | tail -n +8 | xargs -r rm
    echo "✓ Backups antigos removidos (mantidos últimos 7)"
    
    # Listar backups disponíveis
    echo ""
    echo "Backups disponíveis:"
    ls -lh coruja_backup_*.sql | tail -7
else
    echo "✗ Erro ao criar backup!"
    exit 1
fi
