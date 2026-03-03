# Script para corrigir relatórios personalizados
Write-Host "=== CORREÇÃO DE RELATÓRIOS PERSONALIZADOS ===" -ForegroundColor Cyan
Write-Host ""

# 1. Executar migração
Write-Host "1. Executando migração do banco de dados..." -ForegroundColor Yellow
docker exec coruja-api python migrate_custom_reports.py
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Migração executada com sucesso!" -ForegroundColor Green
} else {
    Write-Host "✗ Erro na migração" -ForegroundColor Red
}

# 2. Reiniciar API
Write-Host ""
Write-Host "2. Reiniciando API..." -ForegroundColor Yellow
docker restart coruja-api
Start-Sleep -Seconds 5
Write-Host "✓ API reiniciada!" -ForegroundColor Green

# 3. Verificar se API está respondendo
Write-Host ""
Write-Host "3. Verificando se API está respondendo..." -ForegroundColor Yellow
$maxAttempts = 10
$attempt = 0
$apiReady = $false

while ($attempt -lt $maxAttempts -and -not $apiReady) {
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 2
        if ($response.status -eq "healthy") {
            $apiReady = $true
            Write-Host "✓ API está respondendo!" -ForegroundColor Green
        }
    } catch {
        $attempt++
        Write-Host "  Tentativa $attempt/$maxAttempts..." -ForegroundColor Gray
        Start-Sleep -Seconds 2
    }
}

if (-not $apiReady) {
    Write-Host "✗ API não está respondendo" -ForegroundColor Red
    Write-Host "Verificando logs:" -ForegroundColor Yellow
    docker logs coruja-api --tail 30
    exit 1
}

# 4. Testar endpoint de templates
Write-Host ""
Write-Host "4. Testando endpoint de templates..." -ForegroundColor Yellow

# Fazer login para obter token
try {
    $loginResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" `
        -Method Post `
        -ContentType "application/x-www-form-urlencoded" `
        -Body "username=admin@coruja.com&password=admin123"
    
    $token = $loginResponse.access_token
    Write-Host "✓ Login realizado com sucesso!" -ForegroundColor Green
    
    # Testar endpoint de templates
    $templatesResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/custom-reports/templates" `
        -Method Get `
        -Headers @{
            "Authorization" = "Bearer $token"
            "Content-Type" = "application/json"
        }
    
    Write-Host "✓ Endpoint de templates funcionando!" -ForegroundColor Green
    Write-Host "Templates encontrados: $($templatesResponse.Count)" -ForegroundColor Green
    
    # Listar templates
    Write-Host ""
    Write-Host "Templates disponíveis:" -ForegroundColor Cyan
    $templatesResponse | ForEach-Object {
        Write-Host "  $($_.icon) $($_.name)" -ForegroundColor White
        Write-Host "     $($_.description)" -ForegroundColor Gray
    }
    
} catch {
    Write-Host "✗ Erro ao testar endpoint:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    Write-Host "Detalhes do erro:" -ForegroundColor Yellow
    Write-Host $_.ErrorDetails.Message -ForegroundColor Gray
}

# 5. Recompilar frontend
Write-Host ""
Write-Host "5. Recompilando frontend..." -ForegroundColor Yellow
docker exec coruja-frontend npm run build
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Frontend recompilado!" -ForegroundColor Green
} else {
    Write-Host "⚠ Aviso: Erro ao recompilar frontend" -ForegroundColor Yellow
    Write-Host "  O frontend pode estar usando cache antigo" -ForegroundColor Gray
}

# 6. Reiniciar frontend
Write-Host ""
Write-Host "6. Reiniciando frontend..." -ForegroundColor Yellow
docker restart coruja-frontend
Start-Sleep -Seconds 3
Write-Host "✓ Frontend reiniciado!" -ForegroundColor Green

Write-Host ""
Write-Host "=== CORREÇÃO CONCLUÍDA ===" -ForegroundColor Green
Write-Host ""
Write-Host "Próximos passos:" -ForegroundColor Cyan
Write-Host "1. Acesse: http://localhost:3000" -ForegroundColor White
Write-Host "2. Faça login com: admin@coruja.com / admin123" -ForegroundColor White
Write-Host "3. Vá para a aba 'Relatórios'" -ForegroundColor White
Write-Host "4. Você deve ver as seções:" -ForegroundColor White
Write-Host "   - 📊 Relatórios Personalizados (10 templates)" -ForegroundColor Gray
Write-Host "   - 💾 Meus Relatórios Salvos (se houver)" -ForegroundColor Gray
Write-Host ""
Write-Host "5. Abra o Console do navegador (F12) para ver logs de debug" -ForegroundColor White
Write-Host ""
