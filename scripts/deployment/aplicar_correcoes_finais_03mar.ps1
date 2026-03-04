#!/usr/bin/env pwsh
# Script para aplicar correções finais - 03 de Março 2026
# Correções: Teste de sensores, exclusão de probe, card de métricas

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CORUJA MONITOR - CORREÇÕES FINAIS" -ForegroundColor Cyan
Write-Host "  Data: 03 de Março de 2026" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "📋 Correções que serão aplicadas:" -ForegroundColor Yellow
Write-Host "  1. ✅ Card de sensores - valor maior (42px)" -ForegroundColor Green
Write-Host "  2. ✅ Notas ocultas quando sensor OK" -ForegroundColor Green
Write-Host "  3. ✅ Card de métricas Grafana aumentado" -ForegroundColor Green
Write-Host "  4. ✅ Config > Teste de sensores não sai da aba" -ForegroundColor Green
Write-Host "  5. ✅ Endpoint DELETE para excluir probe" -ForegroundColor Green
Write-Host "  6. ✅ NOC: servidores não somem com alertas" -ForegroundColor Green
Write-Host ""

# Verificar se Docker está rodando
Write-Host "🔍 Verificando Docker..." -ForegroundColor Cyan
$dockerRunning = docker ps 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker não está rodando!" -ForegroundColor Red
    Write-Host "   Inicie o Docker Desktop e tente novamente." -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ Docker está rodando" -ForegroundColor Green
Write-Host ""

# Reiniciar API para aplicar endpoint DELETE
Write-Host "🔄 Reiniciando API..." -ForegroundColor Cyan
docker-compose restart api
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ API reiniciada com sucesso" -ForegroundColor Green
} else {
    Write-Host "❌ Erro ao reiniciar API" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Aguardar API inicializar
Write-Host "⏳ Aguardando API inicializar (10 segundos)..." -ForegroundColor Yellow
Start-Sleep -Seconds 10
Write-Host ""

# Reiniciar Frontend para aplicar correção do teste de sensores
Write-Host "🔄 Reiniciando Frontend..." -ForegroundColor Cyan
docker-compose restart frontend
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Frontend reiniciado com sucesso" -ForegroundColor Green
} else {
    Write-Host "❌ Erro ao reiniciar Frontend" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Aguardar Frontend inicializar
Write-Host "⏳ Aguardando Frontend inicializar (15 segundos)..." -ForegroundColor Yellow
Start-Sleep -Seconds 15
Write-Host ""

Write-Host "========================================" -ForegroundColor Green
Write-Host "  ✅ CORREÇÕES APLICADAS COM SUCESSO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Write-Host "📝 PRÓXIMOS PASSOS:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1️⃣  Abra o navegador em: http://localhost:3000" -ForegroundColor White
Write-Host "2️⃣  Pressione Ctrl+Shift+R para limpar cache" -ForegroundColor White
Write-Host "3️⃣  Faça login no sistema" -ForegroundColor White
Write-Host ""

Write-Host "🧪 TESTES A REALIZAR:" -ForegroundColor Yellow
Write-Host ""
Write-Host "✓ Card de Sensores:" -ForegroundColor Cyan
Write-Host "  - Vá em Servidores > Selecione um servidor" -ForegroundColor White
Write-Host "  - Verifique se o valor está maior (42px)" -ForegroundColor White
Write-Host "  - Adicione uma nota em um sensor com problema" -ForegroundColor White
Write-Host "  - Resolva o problema e veja se a nota sumiu" -ForegroundColor White
Write-Host ""

Write-Host "✓ Card de Métricas Grafana:" -ForegroundColor Cyan
Write-Host "  - Vá em Métricas Grafana" -ForegroundColor White
Write-Host "  - Verifique se os cards estão maiores" -ForegroundColor White
Write-Host "  - Texto deve estar visível e dentro do card" -ForegroundColor White
Write-Host ""

Write-Host "✓ Teste de Sensores:" -ForegroundColor Cyan
Write-Host "  - Vá em Configurações" -ForegroundColor White
Write-Host "  - Clique na aba 'Testes de Sensores'" -ForegroundColor White
Write-Host "  - Verifique se NÃO sai da página de Config" -ForegroundColor White
Write-Host ""

Write-Host "✓ Excluir Probe:" -ForegroundColor Cyan
Write-Host "  - Vá em Empresas > Selecione uma empresa" -ForegroundColor White
Write-Host "  - Tente excluir uma probe" -ForegroundColor White
Write-Host "  - Deve funcionar sem erro 'Not Found'" -ForegroundColor White
Write-Host ""

Write-Host "✓ NOC Real-Time:" -ForegroundColor Cyan
Write-Host "  - Vá em NOC Real-Time" -ForegroundColor White
Write-Host "  - Crie um alerta em um servidor" -ForegroundColor White
Write-Host "  - Verifique se os servidores OK continuam visíveis" -ForegroundColor White
Write-Host "  - Contador 'SERVIDORES OK' deve estar correto" -ForegroundColor White
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Sistema pronto para uso!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
