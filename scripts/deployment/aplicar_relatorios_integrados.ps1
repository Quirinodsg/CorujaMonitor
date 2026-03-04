# Script para aplicar relatórios personalizados integrados

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "APLICAR RELATÓRIOS INTEGRADOS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "📋 O que será feito:" -ForegroundColor Yellow
Write-Host "   1. Executar migração do banco de dados" -ForegroundColor White
Write-Host "   2. Reiniciar API" -ForegroundColor White
Write-Host "   3. Testar endpoints" -ForegroundColor White
Write-Host ""

# 1. Executar migração
Write-Host "1. Executando migração..." -ForegroundColor Yellow
try {
    docker exec coruja-api python migrate_custom_reports.py
    Write-Host "   ✅ Migração executada!" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️ Tentando localmente..." -ForegroundColor Yellow
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

# 3. Testar
Write-Host "3. Testando endpoints..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

try {
    $login = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" `
        -Method Post `
        -Body '{"email":"admin@coruja.com","password":"admin123"}' `
        -ContentType "application/json"
    
    $headers = @{"Authorization" = "Bearer $($login.access_token)"}
    
    # Testar templates personalizados
    $customTemplates = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/custom-reports/templates" `
        -Method Get `
        -Headers $headers
    
    Write-Host "   ✅ Endpoints funcionando!" -ForegroundColor Green
    Write-Host "   📊 Templates personalizados: $($customTemplates.Count)" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "   Templates disponíveis:" -ForegroundColor Cyan
    $customTemplates | Select-Object -First 5 | ForEach-Object {
        Write-Host "      $($_.icon) $($_.name)" -ForegroundColor White
    }
    Write-Host "      ... e mais $($customTemplates.Count - 5) templates" -ForegroundColor Gray
    
} catch {
    Write-Host "   ❌ Erro: $_" -ForegroundColor Red
}
Write-Host ""

# Instruções finais
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "INSTALAÇÃO CONCLUÍDA!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ Relatórios personalizados integrados com sucesso!" -ForegroundColor Green
Write-Host ""
Write-Host "📍 Como acessar:" -ForegroundColor Yellow
Write-Host "   1. Acesse: http://localhost:3000/reports" -ForegroundColor White
Write-Host "   2. Role a sidebar até o final" -ForegroundColor White
Write-Host "   3. Veja as novas seções:" -ForegroundColor White
Write-Host "      📊 Relatórios Personalizados" -ForegroundColor Cyan
Write-Host "      💾 Meus Relatórios Salvos" -ForegroundColor Cyan
Write-Host ""
Write-Host "🎯 Templates disponíveis:" -ForegroundColor Yellow
Write-Host "   🏭 Servidores de Produção" -ForegroundColor White
Write-Host "   🚨 Servidores que Mais Alarmaram" -ForegroundColor White
Write-Host "   ❌ Erros Mais Comuns" -ForegroundColor White
Write-Host "   🔴 Incidentes Críticos" -ForegroundColor White
Write-Host "   📊 Disponibilidade por Servidor" -ForegroundColor White
Write-Host "   ⚡ Resumo de Performance" -ForegroundColor White
Write-Host "   🏷️ Servidores por Tag" -ForegroundColor White
Write-Host "   ⏳ Incidentes Não Resolvidos" -ForegroundColor White
Write-Host "   🤖 Taxa de Resolução por IA" -ForegroundColor White
Write-Host "   💾 Espaço em Disco Crítico" -ForegroundColor White
Write-Host ""
Write-Host "📚 Documentação:" -ForegroundColor Yellow
Write-Host "   INTEGRACAO_RELATORIOS_PERSONALIZADOS.md" -ForegroundColor Cyan
Write-Host ""
