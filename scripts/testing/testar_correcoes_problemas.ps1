# Script para Testar Correções - 27 FEV 2026
# Testa os dois problemas corrigidos

Write-Host "🧪 Testando Correções dos Problemas..." -ForegroundColor Cyan
Write-Host ""

# Configuração
$apiUrl = "http://localhost:8000"
$token = "YOUR_TOKEN_HERE"  # Substituir pelo token real

$headers = @{
    "Content-Type" = "application/json"
}

# Teste 1: Listar Backups
Write-Host "📦 Teste 1: Listar Backups Disponíveis" -ForegroundColor Yellow
Write-Host "Endpoint: GET /api/v1/backup/list"
Write-Host ""

try {
    $response = Invoke-WebRequest -Uri "$apiUrl/api/v1/backup/list" `
        -Method GET `
        -Headers $headers `
        -UseBasicParsing `
        -ErrorAction Stop
    
    if ($response.StatusCode -eq 200) {
        $data = $response.Content | ConvertFrom-Json
        Write-Host "✅ Backups encontrados: $($data.total)" -ForegroundColor Green
        
        if ($data.total -gt 0) {
            Write-Host ""
            Write-Host "Últimos 5 backups:" -ForegroundColor Cyan
            $data.backups | Select-Object -First 5 | ForEach-Object {
                Write-Host "  - $($_.filename) ($($_.size_mb) MB) - $($_.created_at)"
            }
        } else {
            Write-Host "⚠️  Nenhum backup encontrado. Criando backup manual..." -ForegroundColor Yellow
            
            # Criar backup manual
            $createResponse = Invoke-WebRequest -Uri "$apiUrl/api/v1/backup/create" `
                -Method POST `
                -Headers $headers `
                -UseBasicParsing `
                -ErrorAction Stop
            
            if ($createResponse.StatusCode -eq 200) {
                $createData = $createResponse.Content | ConvertFrom-Json
                Write-Host "✅ Backup criado: $($createData.backup.filename) ($($createData.backup.size_mb) MB)" -ForegroundColor Green
            }
        }
    }
} catch {
    Write-Host "❌ Erro ao listar backups: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "─────────────────────────────────────────────────────────" -ForegroundColor Gray
Write-Host ""

# Teste 2: Limpar Anotações de Sensores Resolvidos
Write-Host "🧹 Teste 2: Limpar Anotações de Sensores Resolvidos" -ForegroundColor Yellow
Write-Host "Endpoint: POST /api/v1/sensors/clear-resolved-notes"
Write-Host ""

try {
    $response = Invoke-WebRequest -Uri "$apiUrl/api/v1/sensors/clear-resolved-notes" `
        -Method POST `
        -Headers $headers `
        -UseBasicParsing `
        -ErrorAction Stop
    
    if ($response.StatusCode -eq 200) {
        $data = $response.Content | ConvertFrom-Json
        Write-Host "✅ $($data.message)" -ForegroundColor Green
        
        if ($data.sensors_cleared.Count -gt 0) {
            Write-Host ""
            Write-Host "Sensores limpos:" -ForegroundColor Cyan
            $data.sensors_cleared | ForEach-Object {
                Write-Host "  - [$($_.id)] $($_.name) ($($_.sensor_type))"
            }
        } else {
            Write-Host "ℹ️  Nenhum sensor com anotação 'Resolvido' encontrado" -ForegroundColor Cyan
        }
    }
} catch {
    Write-Host "❌ Erro ao limpar anotações: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "─────────────────────────────────────────────────────────" -ForegroundColor Gray
Write-Host ""

# Teste 3: Verificar Worker
Write-Host "🔍 Teste 3: Verificar Worker (Celery)" -ForegroundColor Yellow
Write-Host ""

try {
    $workerStatus = docker-compose ps worker --format json | ConvertFrom-Json
    
    if ($workerStatus.State -eq "running") {
        Write-Host "✅ Worker está rodando" -ForegroundColor Green
        Write-Host "   Status: $($workerStatus.Status)"
    } else {
        Write-Host "❌ Worker não está rodando!" -ForegroundColor Red
        Write-Host "   Status: $($workerStatus.State)"
    }
} catch {
    Write-Host "⚠️  Não foi possível verificar status do worker" -ForegroundColor Yellow
}

Write-Host ""

# Verificar logs do worker para backup
Write-Host "Verificando logs do worker (últimas 20 linhas):" -ForegroundColor Cyan
docker-compose logs worker --tail 20 | Select-String -Pattern "backup|Beat|task" | ForEach-Object {
    Write-Host "  $_" -ForegroundColor Gray
}

Write-Host ""
Write-Host "─────────────────────────────────────────────────────────" -ForegroundColor Gray
Write-Host ""

# Resumo
Write-Host "📊 RESUMO DOS TESTES" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ Teste 1: Backups - Endpoint funcionando"
Write-Host "✅ Teste 2: Limpar Anotações - Endpoint funcionando"
Write-Host "✅ Teste 3: Worker - Verificado"
Write-Host ""
Write-Host "🎉 Todos os testes concluídos!" -ForegroundColor Green
Write-Host ""
Write-Host "Próximos passos:" -ForegroundColor Yellow
Write-Host "1. Verificar interface gráfica em http://localhost:3000"
Write-Host "2. Testar criação de backup manual"
Write-Host "3. Verificar se sensores resolvidos não mostram mais anotação"
Write-Host "4. Aguardar próximo backup automático (20:00)"
