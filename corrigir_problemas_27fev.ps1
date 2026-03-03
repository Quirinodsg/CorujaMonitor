# Script para Corrigir Problemas - 27 FEV 2026
# 1. Backups automáticos não estão sendo feitos
# 2. Sensores resolvidos ainda aparecem com anotação "Resolvido"

Write-Host "🔧 Corrigindo Problemas do Sistema..." -ForegroundColor Cyan
Write-Host ""

# Problema 1: Testar backup automático
Write-Host "📦 Problema 1: Backups Automáticos" -ForegroundColor Yellow
Write-Host "Testando criação de backup manual..."

$response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/backup/create" `
    -Method POST `
    -Headers @{
        "Authorization" = "Bearer YOUR_TOKEN_HERE"
        "Content-Type" = "application/json"
    } `
    -UseBasicParsing `
    -ErrorAction SilentlyContinue

if ($response.StatusCode -eq 200) {
    Write-Host "✅ Backup manual criado com sucesso!" -ForegroundColor Green
    $response.Content | ConvertFrom-Json | Format-List
} else {
    Write-Host "❌ Erro ao criar backup: $($response.StatusCode)" -ForegroundColor Red
}

Write-Host ""

# Problema 2: Limpar anotações de sensores resolvidos
Write-Host "🧹 Problema 2: Sensores Resolvidos" -ForegroundColor Yellow
Write-Host "Limpando anotações de sensores resolvidos..."

# Script SQL para limpar anotações
$sqlScript = @"
-- Limpar anotações de sensores que estão OK
UPDATE sensors 
SET 
    last_note = NULL,
    last_note_by = NULL,
    last_note_at = NULL,
    verification_status = NULL
WHERE id IN (
    SELECT DISTINCT s.id
    FROM sensors s
    LEFT JOIN metrics m ON m.sensor_id = s.id
    WHERE s.last_note LIKE '%Resolvido%'
    AND m.status = 'ok'
    AND m.id = (
        SELECT id FROM metrics 
        WHERE sensor_id = s.id 
        ORDER BY timestamp DESC 
        LIMIT 1
    )
);
"@

# Salvar script SQL
$sqlScript | Out-File -FilePath "limpar_sensores_resolvidos.sql" -Encoding UTF8

Write-Host "Script SQL criado: limpar_sensores_resolvidos.sql"
Write-Host ""
Write-Host "Execute o script no banco de dados:"
Write-Host "docker-compose exec postgres psql -U coruja -d coruja_monitor -f /app/limpar_sensores_resolvidos.sql" -ForegroundColor Cyan
Write-Host ""

# Verificar worker
Write-Host "🔍 Verificando Worker (Celery Beat)..." -ForegroundColor Yellow
docker-compose logs worker --tail 20 | Select-String -Pattern "backup|Beat"

Write-Host ""
Write-Host "✅ Diagnóstico concluído!" -ForegroundColor Green
Write-Host ""
Write-Host "Próximos passos:" -ForegroundColor Cyan
Write-Host "1. Verificar se o worker está rodando: docker-compose ps worker"
Write-Host "2. Reiniciar worker se necessário: docker-compose restart worker"
Write-Host "3. Executar script SQL para limpar sensores resolvidos"
Write-Host "4. Verificar logs do worker: docker-compose logs worker -f"
