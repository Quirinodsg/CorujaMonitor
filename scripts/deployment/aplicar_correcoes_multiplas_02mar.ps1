#!/usr/bin/env pwsh
# Script para aplicar correções múltiplas - 02 de Março 2026

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "APLICANDO CORREÇÕES MÚLTIPLAS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "CORREÇÕES APLICADAS:" -ForegroundColor Yellow
Write-Host "✅ 1. Card de sensores melhorado (valor maior, status destacado)" -ForegroundColor Green
Write-Host "✅ 2. Notas ocultadas quando sensor está OK" -ForegroundColor Green
Write-Host "✅ 3. Card de métricas Grafana melhorado (padding, tamanhos)" -ForegroundColor Green
Write-Host ""

Write-Host "CORREÇÕES PENDENTES (requerem mais investigação):" -ForegroundColor Yellow
Write-Host "⏳ 4. Config > Teste de sensores sai da aba" -ForegroundColor Yellow
Write-Host "⏳ 5. Erro ao excluir probe (Not Found)" -ForegroundColor Yellow
Write-Host "⏳ 6. NOC: servidores somem quando tem alerta" -ForegroundColor Yellow
Write-Host ""

Write-Host "Reiniciando frontend..." -ForegroundColor Yellow
docker-compose restart frontend

Write-Host ""
Write-Host "Aguardando frontend iniciar..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "INSTRUÇÕES PARA TESTAR:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "1. LIMPAR CACHE DO NAVEGADOR:" -ForegroundColor Yellow
Write-Host "   Ctrl+Shift+R (hard refresh)" -ForegroundColor White
Write-Host ""

Write-Host "2. TESTAR CARD DE SENSORES:" -ForegroundColor Yellow
Write-Host "   - Acesse: Gestão > Servidores" -ForegroundColor White
Write-Host "   - Verifique se o valor está maior (42px)" -ForegroundColor White
Write-Host "   - Verifique se o status está mais destacado" -ForegroundColor White
Write-Host ""

Write-Host "3. TESTAR NOTAS OCULTAS:" -ForegroundColor Yellow
Write-Host "   - Acesse: Gestão > Servidores" -ForegroundColor White
Write-Host "   - Sensores com status OK não devem mostrar notas" -ForegroundColor White
Write-Host "   - Sensores com warning/critical ainda mostram notas" -ForegroundColor White
Write-Host ""

Write-Host "4. TESTAR CARD DE MÉTRICAS:" -ForegroundColor Yellow
Write-Host "   - Acesse: Métricas > Dashboard" -ForegroundColor White
Write-Host "   - Verifique se os cards estão mais espaçados" -ForegroundColor White
Write-Host "   - Verifique se os valores estão maiores (24px)" -ForegroundColor White
Write-Host ""

Write-Host "5. REPORTAR PROBLEMAS PENDENTES:" -ForegroundColor Yellow
Write-Host "   a) Config > Teste de sensores:" -ForegroundColor White
Write-Host "      - Acesse: Configurações > Teste de Sensores" -ForegroundColor White
Write-Host "      - Clique em 'Testar'" -ForegroundColor White
Write-Host "      - Verifique se sai da aba Config" -ForegroundColor White
Write-Host ""
Write-Host "   b) Excluir probe:" -ForegroundColor White
Write-Host "      - Acesse: Gestão > Sondas" -ForegroundColor White
Write-Host "      - Tente excluir uma sonda" -ForegroundColor White
Write-Host "      - Anote o erro exato" -ForegroundColor White
Write-Host ""
Write-Host "   c) NOC com alertas:" -ForegroundColor White
Write-Host "      - Acesse: NOC Real-Time" -ForegroundColor White
Write-Host "      - Verifique se servidores aparecem quando há alertas" -ForegroundColor White
Write-Host "      - Anote quantos servidores aparecem vs esperado" -ForegroundColor White
Write-Host ""

Write-Host "========================================" -ForegroundColor Green
Write-Host "CORREÇÕES PARCIAIS APLICADAS!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Próximo passo: Testar e reportar problemas pendentes" -ForegroundColor Yellow
