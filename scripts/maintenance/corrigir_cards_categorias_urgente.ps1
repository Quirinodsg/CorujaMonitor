# Script de Correção URGENTE - Cards de Categorias Sobrepostos
# Data: 04 de Março de 2026

Write-Host "========================================" -ForegroundColor Red
Write-Host "  CORRECAO URGENTE - CARDS CATEGORIAS" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Red
Write-Host ""

Write-Host "Problema: Cards de Sistema, Docker, Servicos, Aplicacoes e Rede sobrepostos" -ForegroundColor Yellow
Write-Host "Solucao: CSS para .docker-summary adicionado" -ForegroundColor Green
Write-Host ""

# Verificar se Docker está rodando
Write-Host "[1/4] Verificando Docker..." -ForegroundColor Cyan
$dockerRunning = docker ps 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRO: Docker nao esta rodando!" -ForegroundColor Red
    Write-Host "Inicie o Docker Desktop e tente novamente." -ForegroundColor Yellow
    exit 1
}
Write-Host "OK: Docker rodando!" -ForegroundColor Green
Write-Host ""

# Rebuild do frontend
Write-Host "[2/4] Rebuild do frontend (sem cache)..." -ForegroundColor Cyan
Write-Host "Isso pode levar 2-3 minutos..." -ForegroundColor Gray
docker-compose build --no-cache frontend

if ($LASTEXITCODE -eq 0) {
    Write-Host "OK: Frontend rebuilded!" -ForegroundColor Green
} else {
    Write-Host "ERRO: Falha no rebuild!" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Reiniciar container
Write-Host "[3/4] Reiniciando container frontend..." -ForegroundColor Cyan
docker-compose restart frontend

if ($LASTEXITCODE -eq 0) {
    Write-Host "OK: Frontend reiniciado!" -ForegroundColor Green
} else {
    Write-Host "ERRO: Falha ao reiniciar!" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Aguardar container iniciar
Write-Host "[4/4] Aguardando container iniciar..." -ForegroundColor Cyan
Start-Sleep -Seconds 5
Write-Host "OK: Container iniciado!" -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Green
Write-Host "  CORRECAO APLICADA COM SUCESSO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Write-Host "PROXIMOS PASSOS:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Abra o navegador em: http://localhost:3000" -ForegroundColor White
Write-Host "2. Pressione Ctrl+Shift+R para limpar cache" -ForegroundColor White
Write-Host "3. Faca login: admin@coruja.com / admin123" -ForegroundColor White
Write-Host "4. Va em Gerenciamento > Servidores" -ForegroundColor White
Write-Host "5. Verifique os cards de categorias:" -ForegroundColor White
Write-Host "   - Sistema" -ForegroundColor Gray
Write-Host "   - Docker" -ForegroundColor Gray
Write-Host "   - Servicos" -ForegroundColor Gray
Write-Host "   - Aplicacoes" -ForegroundColor Gray
Write-Host "   - Rede" -ForegroundColor Gray
Write-Host ""
Write-Host "Os cards devem estar alinhados SEM sobreposicao!" -ForegroundColor Green
Write-Host ""

# Abrir navegador automaticamente
Write-Host "Abrindo navegador..." -ForegroundColor Cyan
Start-Process "http://localhost:3000"

Write-Host ""
Write-Host "Pressione qualquer tecla para sair..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
