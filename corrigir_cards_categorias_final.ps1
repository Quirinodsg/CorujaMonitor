# Script para corrigir sobreposição dos cards de categorias
# Data: 03/03/2026

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CORREÇÃO FINAL - CARDS DE CATEGORIAS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/3] Reiniciando frontend..." -ForegroundColor Yellow
docker-compose restart frontend | Out-Null

Write-Host "[2/3] Aguardando 15 segundos para o frontend reiniciar..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

Write-Host "[3/3] Verificando status..." -ForegroundColor Yellow
$status = docker ps --filter "name=frontend" --format "{{.Status}}"
Write-Host "Status do frontend: $status" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "CORREÇÃO APLICADA COM SUCESSO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "PRÓXIMOS PASSOS:" -ForegroundColor Cyan
Write-Host "1. Abra o navegador e acesse: http://localhost:3000" -ForegroundColor White
Write-Host "2. Pressione Ctrl+Shift+R para limpar o cache" -ForegroundColor White
Write-Host "3. Vá para a página de Servidores" -ForegroundColor White
Write-Host "4. Verifique se os cards de categorias estão alinhados:" -ForegroundColor White
Write-Host "   - Sistema, Docker, Serviços (primeira linha)" -ForegroundColor White
Write-Host "   - Aplicações, Rede (segunda linha)" -ForegroundColor White
Write-Host ""
Write-Host "Se ainda houver problema, abra uma aba anônima (Ctrl+Shift+N)" -ForegroundColor Yellow
Write-Host ""
