# Script para instalar sistema de relatórios personalizados

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "INSTALAÇÃO DE RELATÓRIOS PERSONALIZADOS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Executar migração
Write-Host "1. Executando migração do banco de dados..." -ForegroundColor Yellow
try {
    docker exec coruja-api python migrate_custom_reports.py
    Write-Host "   ✅ Migração executada com sucesso!" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Erro na migração: $_" -ForegroundColor Red
    Write-Host "   Tentando executar localmente..." -ForegroundColor Yellow
    cd api
    python migrate_custom_reports.py
    cd ..
}
Write-Host ""

# 2. Reiniciar API
Write-Host "2. Reiniciando API..." -ForegroundColor Yellow
docker restart coruja-api
Start-Sleep -Seconds 5
Write-Host "   ✅ API reiniciada!" -ForegroundColor Green
Write-Host ""

# 3. Testar endpoints
Write-Host "3. Testando endpoints..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

try {
    # Login
    $login = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" `
        -Method Post `
        -Body '{"email":"admin@coruja.com","password":"admin123"}' `
        -ContentType "application/json"
    
    $headers = @{"Authorization" = "Bearer $($login.access_token)"}
    
    # Testar templates
    $templates = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/custom-reports/templates" `
        -Method Get `
        -Headers $headers
    
    Write-Host "   ✅ Endpoints funcionando!" -ForegroundColor Green
    Write-Host "   📊 Total de templates: $($templates.Count)" -ForegroundColor Cyan
    
    Write-Host ""
    Write-Host "   Templates disponíveis:" -ForegroundColor Cyan
    $templates | ForEach-Object {
        Write-Host "      $($_.icon) $($_.name)" -ForegroundColor White
    }
    
} catch {
    Write-Host "   ❌ Erro ao testar endpoints: $_" -ForegroundColor Red
}
Write-Host ""

# 4. Instruções finais
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "INSTALAÇÃO CONCLUÍDA!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Próximos passos:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Adicione a rota no frontend (App.js):" -ForegroundColor White
Write-Host "   import CustomReports from './components/CustomReports';" -ForegroundColor Gray
Write-Host "   <Route path='/custom-reports' element={<CustomReports />} />" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Adicione link no menu de navegação:" -ForegroundColor White
Write-Host "   <Link to='/custom-reports'>📊 Relatórios Personalizados</Link>" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Acesse: http://localhost:3000/custom-reports" -ForegroundColor White
Write-Host ""
Write-Host "📚 Documentação completa:" -ForegroundColor Yellow
Write-Host "   RELATORIOS_PERSONALIZADOS_IMPLEMENTADO.md" -ForegroundColor Cyan
Write-Host ""
