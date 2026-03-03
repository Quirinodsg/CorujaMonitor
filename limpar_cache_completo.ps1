# Script para Limpar Cache Completo - 02 MAR 2026
# Este script ajuda a resolver o problema de cache do navegador

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "LIMPEZA DE CACHE - CORUJA MONITOR" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "PROBLEMA IDENTIFICADO:" -ForegroundColor Yellow
Write-Host "O navegador está usando uma versão CACHEADA dos arquivos JavaScript." -ForegroundColor Yellow
Write-Host "A URL da API está sem o '/api/v1' por causa do cache antigo." -ForegroundColor Yellow
Write-Host ""

Write-Host "SOLUCAO:" -ForegroundColor Green
Write-Host "1. Limpar o cache do navegador completamente" -ForegroundColor White
Write-Host "2. Fechar TODAS as abas do Coruja Monitor" -ForegroundColor White
Write-Host "3. Fechar o navegador completamente" -ForegroundColor White
Write-Host "4. Abrir novamente e testar" -ForegroundColor White
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "OPCOES DE LIMPEZA" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "OPCAO 1 - Limpeza Manual (RECOMENDADO):" -ForegroundColor Yellow
Write-Host "  1. Pressione Ctrl + Shift + Delete" -ForegroundColor White
Write-Host "  2. Selecione 'Todo o periodo'" -ForegroundColor White
Write-Host "  3. Marque:" -ForegroundColor White
Write-Host "     - Cookies e dados de sites" -ForegroundColor White
Write-Host "     - Imagens e arquivos em cache" -ForegroundColor White
Write-Host "     - Dados de aplicativos hospedados" -ForegroundColor White
Write-Host "  4. Clique em 'Limpar dados'" -ForegroundColor White
Write-Host "  5. Feche TODAS as abas do Coruja" -ForegroundColor White
Write-Host "  6. Feche o navegador" -ForegroundColor White
Write-Host "  7. Abra novamente: http://localhost:3000" -ForegroundColor White
Write-Host ""

Write-Host "OPCAO 2 - Modo Anonimo (TESTE RAPIDO):" -ForegroundColor Yellow
Write-Host "  1. Pressione Ctrl + Shift + N" -ForegroundColor White
Write-Host "  2. Acesse: http://localhost:3000" -ForegroundColor White
Write-Host "  3. Faca login e teste as metricas" -ForegroundColor White
Write-Host ""

Write-Host "OPCAO 3 - DevTools (DESENVOLVEDOR):" -ForegroundColor Yellow
Write-Host "  1. Pressione F12" -ForegroundColor White
Write-Host "  2. Clique com botao direito no icone de recarregar" -ForegroundColor White
Write-Host "  3. Selecione 'Limpar cache e recarregar forcado'" -ForegroundColor White
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "VERIFICACAO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Apos limpar o cache, verifique no console do navegador:" -ForegroundColor Yellow
Write-Host ""
Write-Host "CORRETO:" -ForegroundColor Green
Write-Host "  URL completa: http://localhost:8000/api/v1/metrics/dashboard/servers" -ForegroundColor Green
Write-Host "  baseURL: http://localhost:8000/api/v1" -ForegroundColor Green
Write-Host ""
Write-Host "ERRADO (cache antigo):" -ForegroundColor Red
Write-Host "  URL completa: http://localhost:8000/metrics/dashboard/servers" -ForegroundColor Red
Write-Host "  baseURL: http://localhost:8000" -ForegroundColor Red
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TESTE DIRETO DA API" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Testando endpoint diretamente..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/metrics/dashboard/servers?range=24h" -Method GET -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "SUCESSO! API esta funcionando corretamente!" -ForegroundColor Green
        Write-Host "O problema e APENAS o cache do navegador." -ForegroundColor Green
    }
} catch {
    if ($_.Exception.Response.StatusCode -eq 401) {
        Write-Host "API funcionando! (401 = precisa de autenticacao)" -ForegroundColor Green
        Write-Host "O problema e APENAS o cache do navegador." -ForegroundColor Green
    } else {
        Write-Host "Erro ao testar API: $($_.Exception.Message)" -ForegroundColor Red
    }
}
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "STATUS DOS CONTAINERS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

docker-compose ps

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PROXIMOS PASSOS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Limpe o cache do navegador (Ctrl + Shift + Delete)" -ForegroundColor Yellow
Write-Host "2. Feche TODAS as abas do Coruja Monitor" -ForegroundColor Yellow
Write-Host "3. Feche o navegador completamente" -ForegroundColor Yellow
Write-Host "4. Abra novamente e acesse: http://localhost:3000" -ForegroundColor Yellow
Write-Host "5. Verifique no console se a URL tem '/api/v1'" -ForegroundColor Yellow
Write-Host ""
Write-Host "Se o problema persistir, execute:" -ForegroundColor Red
Write-Host "  docker-compose down" -ForegroundColor White
Write-Host "  docker-compose build --no-cache frontend" -ForegroundColor White
Write-Host "  docker-compose up -d" -ForegroundColor White
Write-Host ""
