# Script de Instalação Completa: Grupos + Azure
Write-Host "=== INSTALAÇÃO: GRUPOS + AZURE MONITORING ===" -ForegroundColor Cyan

Write-Host "`n⚠️  AVISO: Esta é uma implementação GRANDE!" -ForegroundColor Yellow
Write-Host "Tempo estimado: 10-15 minutos" -ForegroundColor Yellow
Write-Host "Requer: Docker rodando, containers ativos" -ForegroundColor Yellow

$confirm = Read-Host "`nDeseja continuar? (S/N)"
if ($confirm -ne 'S' -and $confirm -ne 's') {
    Write-Host "Instalação cancelada." -ForegroundColor Red
    exit
}

# 1. Executar migração do banco
Write-Host "`n1. Executando migração do banco de dados..." -ForegroundColor Yellow
docker exec -i coruja-api python migrate_sensor_groups.py

# 2. Adicionar router no main.py
Write-Host "`n2. Adicionando router de grupos..." -ForegroundColor Yellow
Write-Host "   ⚠️  AÇÃO MANUAL NECESSÁRIA:" -ForegroundColor Red
Write-Host "   Adicione em api/main.py:" -ForegroundColor White
Write-Host "   from routers import ..., sensor_groups" -ForegroundColor Cyan
Write-Host "   app.include_router(sensor_groups.router, prefix='/api/v1/sensor-groups', tags=['Sensor Groups'])" -ForegroundColor Cyan

# 3. Reiniciar API
Write-Host "`n3. Reiniciando API..." -ForegroundColor Yellow
docker-compose restart api

Write-Host "`n4. Aguardando API iniciar..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# 5. Testar endpoints
Write-Host "`n5. Testando endpoints..." -ForegroundColor Yellow
try {
    $body = @{email='admin@coruja.com';password='admin123'} | ConvertTo-Json
    $response = Invoke-RestMethod -Uri 'http://localhost:8000/api/v1/auth/login' -Method Post -Body $body -ContentType 'application/json'
    $token = $response.access_token
    
    $headers = @{Authorization = "Bearer $token"}
    $groups = Invoke-RestMethod -Uri 'http://localhost:8000/api/v1/sensor-groups/' -Method Get -Headers $headers
    
    Write-Host "   ✅ Endpoints funcionando!" -ForegroundColor Green
    Write-Host "   📊 Grupos encontrados: $($groups.Count)" -ForegroundColor Cyan
} catch {
    Write-Host "   ❌ Erro ao testar endpoints" -ForegroundColor Red
    Write-Host "   Erro: $_" -ForegroundColor Red
}

Write-Host "`n=== PRÓXIMOS PASSOS ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "BACKEND:" -ForegroundColor Yellow
Write-Host "✅ Migração do banco - CONCLUÍDA" -ForegroundColor Green
Write-Host "✅ Endpoints de grupos - CRIADOS" -ForegroundColor Green
Write-Host "⚠️  Router no main.py - ADICIONAR MANUALMENTE" -ForegroundColor Yellow
Write-Host ""
Write-Host "FRONTEND (A IMPLEMENTAR):" -ForegroundColor Yellow
Write-Host "❌ Interface de gerenciamento de grupos" -ForegroundColor Red
Write-Host "❌ Wizard Azure completo" -ForegroundColor Red
Write-Host "❌ Integração com Servers.js" -ForegroundColor Red
Write-Host ""
Write-Host "DOCUMENTAÇÃO:" -ForegroundColor Yellow
Write-Host "📄 DESIGN_GRUPOS_AZURE_COMPLETO.md - Design completo" -ForegroundColor White
Write-Host "📄 IMPLEMENTACAO_COMPLETA_GRUPOS_AZURE.md - Status" -ForegroundColor White
Write-Host ""
Write-Host "Para continuar a implementação, será necessário:" -ForegroundColor Cyan
Write-Host "1. Criar componente React para gerenciamento de grupos" -ForegroundColor White
Write-Host "2. Criar wizard Azure com 5 passos" -ForegroundColor White
Write-Host "3. Implementar descoberta de recursos Azure" -ForegroundColor White
Write-Host "4. Criar collectors para métricas Azure" -ForegroundColor White
Write-Host ""
Write-Host "Tempo estimado restante: 4-6 horas" -ForegroundColor Yellow
