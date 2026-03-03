#!/usr/bin/env pwsh
# Script para aplicar correções de layout e NOC - 02 de Março 2026

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "APLICANDO CORREÇÕES DE LAYOUT E NOC" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "CORREÇÕES APLICADAS:" -ForegroundColor Yellow
Write-Host "1. Barras de métricas - Adicionado padding e box-sizing" -ForegroundColor Green
Write-Host "2. Cards empilhados - Reduzido minmax de 400px para 320px" -ForegroundColor Green
Write-Host "3. NOC zerado - Adicionados logs de debug" -ForegroundColor Green
Write-Host ""

Write-Host "Reiniciando serviços..." -ForegroundColor Yellow
docker-compose restart api frontend

Write-Host ""
Write-Host "Aguardando serviços iniciarem..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "Verificando status dos serviços..." -ForegroundColor Yellow
docker-compose ps

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "INSTRUÇÕES PARA TESTAR:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. LIMPAR CACHE DO NAVEGADOR:" -ForegroundColor Yellow
Write-Host "   - Pressione Ctrl+Shift+R (hard refresh)" -ForegroundColor White
Write-Host "   - Ou abra em aba anônima (Ctrl+Shift+N)" -ForegroundColor White
Write-Host ""
Write-Host "2. VERIFICAR BARRAS DE MÉTRICAS:" -ForegroundColor Yellow
Write-Host "   - Acesse: Métricas > Dashboard" -ForegroundColor White
Write-Host "   - Verifique se as barras de CPU/Memória/Disco estão dentro do card" -ForegroundColor White
Write-Host ""
Write-Host "3. VERIFICAR CARDS LADO A LADO:" -ForegroundColor Yellow
Write-Host "   - Acesse: Gestão > Servidores" -ForegroundColor White
Write-Host "   - Verifique se os cards aparecem lado a lado (não empilhados)" -ForegroundColor White
Write-Host "   - Largura mínima: 320px por card" -ForegroundColor White
Write-Host ""
Write-Host "4. VERIFICAR NOC:" -ForegroundColor Yellow
Write-Host "   - Acesse: NOC Real-Time" -ForegroundColor White
Write-Host "   - Verifique se mostra o número correto de servidores OK" -ForegroundColor White
Write-Host "   - Verifique os logs da API para ver os contadores" -ForegroundColor White
Write-Host ""
Write-Host "5. VER LOGS DA API (para debug do NOC):" -ForegroundColor Yellow
Write-Host "   docker-compose logs -f api | Select-String 'Contadores finais'" -ForegroundColor White
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "CORREÇÕES APLICADAS COM SUCESSO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
