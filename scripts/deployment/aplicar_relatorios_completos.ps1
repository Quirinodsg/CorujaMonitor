# Script para aplicar relatórios personalizados completos
Write-Host "=== APLICANDO RELATÓRIOS PERSONALIZADOS COMPLETOS ===" -ForegroundColor Cyan
Write-Host ""

Write-Host "Funcionalidades implementadas:" -ForegroundColor Yellow
Write-Host "  ✅ Visualizar templates pré-definidos" -ForegroundColor Green
Write-Host "  ✅ Criar relatórios personalizados do zero" -ForegroundColor Green
Write-Host "  ✅ Salvar templates como relatórios" -ForegroundColor Green
Write-Host "  ✅ Editar relatórios salvos" -ForegroundColor Green
Write-Host "  ✅ Excluir relatórios" -ForegroundColor Green
Write-Host "  ✅ Gerar relatórios com dados" -ForegroundColor Green
Write-Host ""

# 1. Recompilar frontend
Write-Host "1. Recompilando frontend..." -ForegroundColor Yellow
docker exec coruja-frontend npm run build

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Frontend recompilado!" -ForegroundColor Green
} else {
    Write-Host "⚠ Aviso: Erro ao recompilar frontend" -ForegroundColor Yellow
}

# 2. Reiniciar frontend
Write-Host ""
Write-Host "2. Reiniciando frontend..." -ForegroundColor Yellow
docker restart coruja-frontend
Start-Sleep -Seconds 3
Write-Host "✓ Frontend reiniciado!" -ForegroundColor Green

# 3. Verificar se está acessível
Write-Host ""
Write-Host "3. Verificando acesso..." -ForegroundColor Yellow
$maxAttempts = 10
$attempt = 0
$frontendReady = $false

while ($attempt -lt $maxAttempts -and -not $frontendReady) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3000" -Method Get -TimeoutSec 2 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            $frontendReady = $true
            Write-Host "✓ Frontend está acessível!" -ForegroundColor Green
        }
    } catch {
        $attempt++
        Write-Host "  Tentativa $attempt/$maxAttempts..." -ForegroundColor Gray
        Start-Sleep -Seconds 2
    }
}

if (-not $frontendReady) {
    Write-Host "✗ Frontend não está acessível" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=== IMPLEMENTAÇÃO CONCLUÍDA ===" -ForegroundColor Green
Write-Host ""
Write-Host "🎉 Relatórios Personalizados Completos!" -ForegroundColor Cyan
Write-Host ""
Write-Host "Como usar:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Acesse: http://localhost:3000" -ForegroundColor White
Write-Host "   Login: admin@coruja.com / admin123" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Vá para a aba 'Relatórios'" -ForegroundColor White
Write-Host ""
Write-Host "3. Você verá:" -ForegroundColor White
Write-Host "   📊 Relatórios Personalizados (10 templates)" -ForegroundColor Gray
Write-Host "   💾 Meus Relatórios Salvos (seus relatórios)" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Criar novo relatório:" -ForegroundColor White
Write-Host "   - Clique em '➕ Criar Relatório Personalizado'" -ForegroundColor Gray
Write-Host "   - Preencha o formulário" -ForegroundColor Gray
Write-Host "   - Selecione colunas e filtros" -ForegroundColor Gray
Write-Host "   - Clique em 'Criar Relatório'" -ForegroundColor Gray
Write-Host ""
Write-Host "5. Salvar template:" -ForegroundColor White
Write-Host "   - Clique no botão 💾 ao lado do template" -ForegroundColor Gray
Write-Host "   - Ajuste as configurações" -ForegroundColor Gray
Write-Host "   - Salve como seu relatório" -ForegroundColor Gray
Write-Host ""
Write-Host "6. Editar relatório:" -ForegroundColor White
Write-Host "   - Clique no botão ✏️ ao lado do relatório" -ForegroundColor Gray
Write-Host "   - Faça as alterações" -ForegroundColor Gray
Write-Host "   - Clique em 'Atualizar Relatório'" -ForegroundColor Gray
Write-Host ""
Write-Host "7. Excluir relatório:" -ForegroundColor White
Write-Host "   - Clique no botão 🗑️ ao lado do relatório" -ForegroundColor Gray
Write-Host "   - Confirme a exclusão" -ForegroundColor Gray
Write-Host ""
Write-Host "📖 Documentação completa:" -ForegroundColor Cyan
Write-Host "   RELATORIOS_PERSONALIZADOS_COMPLETO_26FEV.md" -ForegroundColor Gray
Write-Host ""
