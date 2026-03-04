# Script para restaurar banco de dados completo
Write-Host "=== RESTAURANDO BANCO DE DADOS CORUJA ===" -ForegroundColor Cyan

# 1. Verificar se containers estão rodando
Write-Host "`n1. Verificando containers..." -ForegroundColor Yellow
docker ps --filter "name=coruja" --format "table {{.Names}}\t{{.Status}}"

# 2. Restaurar backup mais recente
Write-Host "`n2. Restaurando backup mais recente (26/02/2026 19:56:27)..." -ForegroundColor Yellow
$backupFile = "coruja_backup_20260226_195627.sql"

# Copiar backup para dentro do container
Write-Host "   Copiando backup para container..." -ForegroundColor Gray
docker cp "api/backups/$backupFile" coruja-postgres:/tmp/restore.sql

# Restaurar banco
Write-Host "   Restaurando banco de dados..." -ForegroundColor Gray
docker exec -i coruja-postgres psql -U coruja -d coruja_monitor -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
docker exec -i coruja-postgres psql -U coruja -d coruja_monitor -f /tmp/restore.sql

Write-Host "   ✅ Banco restaurado!" -ForegroundColor Green

# 3. Executar migração da biblioteca de sensores
Write-Host "`n3. Aplicando migração da biblioteca de sensores..." -ForegroundColor Yellow
docker exec -i coruja-api python migrate_standalone_sensors.py

# 4. Popular base de conhecimento
Write-Host "`n4. Populando base de conhecimento..." -ForegroundColor Yellow
docker exec -i coruja-api python seed_kb_80_items.py

# 5. Verificar dados
Write-Host "`n5. Verificando dados restaurados..." -ForegroundColor Yellow
docker exec -i coruja-postgres psql -U coruja -d coruja_monitor -c "SELECT 'Servidores: ' || COUNT(*) FROM servers UNION ALL SELECT 'Sensores: ' || COUNT(*) FROM sensors UNION ALL SELECT 'Incidentes: ' || COUNT(*) FROM incidents UNION ALL SELECT 'KB Itens: ' || COUNT(*) FROM knowledge_base_entries;"

Write-Host "`n=== RESTAURAÇÃO COMPLETA ===" -ForegroundColor Green
Write-Host "Acesse: http://localhost:3000" -ForegroundColor Cyan
Write-Host "Login: admin@coruja.com / admin123" -ForegroundColor Cyan
