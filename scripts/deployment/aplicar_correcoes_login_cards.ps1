# Script para Aplicar Correções - Login e Cards
# Data: 03 de Março de 2026

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CORUJA MONITOR - APLICAR CORRECOES" -ForegroundColor Cyan
Write-Host "  Login (Cores Logo) + Cards" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se Docker está rodando
Write-Host "[1/5] Verificando Docker..." -ForegroundColor Yellow
try {
    $dockerStatus = docker ps 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERRO: Docker Desktop nao esta rodando!" -ForegroundColor Red
        Write-Host "Por favor, inicie o Docker Desktop e execute este script novamente." -ForegroundColor Red
        Write-Host ""
        Read-Host "Pressione Enter para sair"
        exit 1
    }
    Write-Host "OK: Docker esta rodando!" -ForegroundColor Green
} catch {
    Write-Host "ERRO: Nao foi possivel verificar o Docker!" -ForegroundColor Red
    Write-Host "Por favor, inicie o Docker Desktop e execute este script novamente." -ForegroundColor Red
    Write-Host ""
    Read-Host "Pressione Enter para sair"
    exit 1
}

Write-Host ""

# Mostrar status dos containers
Write-Host "[2/5] Status dos containers:" -ForegroundColor Yellow
docker ps --format "table {{.Names}}\t{{.Status}}" | Select-Object -First 8
Write-Host ""

# Fazer rebuild do frontend sem cache
Write-Host "[3/5] Fazendo rebuild do frontend (sem cache)..." -ForegroundColor Yellow
Write-Host "Isso pode levar alguns minutos..." -ForegroundColor Gray
Write-Host ""

docker-compose build --no-cache frontend

if ($LASTEXITCODE -eq 0) {
    Write-Host "OK: Rebuild concluido com sucesso!" -ForegroundColor Green
} else {
    Write-Host "ERRO: Falha no rebuild do frontend!" -ForegroundColor Red
    Write-Host "Verifique os logs acima para mais detalhes." -ForegroundColor Red
    Write-Host ""
    Read-Host "Pressione Enter para sair"
    exit 1
}

Write-Host ""

# Reiniciar o container frontend
Write-Host "[4/5] Reiniciando container frontend..." -ForegroundColor Yellow
docker-compose restart frontend

if ($LASTEXITCODE -eq 0) {
    Write-Host "OK: Frontend reiniciado com sucesso!" -ForegroundColor Green
} else {
    Write-Host "ERRO: Falha ao reiniciar frontend!" -ForegroundColor Red
    Write-Host ""
    Read-Host "Pressione Enter para sair"
    exit 1
}

Write-Host ""

# Aguardar alguns segundos
Write-Host "[5/5] Aguardando frontend inicializar..." -ForegroundColor Yellow
Start-Sleep -Seconds 5
Write-Host "OK: Frontend deve estar pronto!" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  CORRECOES APLICADAS COM SUCESSO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Write-Host "PROXIMOS PASSOS:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. LIMPAR CACHE DO NAVEGADOR:" -ForegroundColor Yellow
Write-Host "   - Abra: http://localhost:3000" -ForegroundColor White
Write-Host "   - Pressione: Ctrl+Shift+R (hard refresh)" -ForegroundColor White
Write-Host "   - Ou abra aba anonima: Ctrl+Shift+N" -ForegroundColor White
Write-Host ""

Write-Host "2. TESTAR TELA DE LOGIN:" -ForegroundColor Yellow
Write-Host "   [ ] Cores da logo (azul e cinza)" -ForegroundColor White
Write-Host "   [ ] Logo limpo (sem olhos)" -ForegroundColor White
Write-Host "   [ ] Coruja aparece no topo" -ForegroundColor White
Write-Host "   [ ] Terminal em cinza" -ForegroundColor White
Write-Host "   [ ] Formulario em azul" -ForegroundColor White
Write-Host "   [ ] Labels visiveis acima dos campos" -ForegroundColor White
Write-Host "   [ ] Icones a direita (nao tapam texto)" -ForegroundColor White
Write-Host "   [ ] Animacoes suaves e epicas" -ForegroundColor White
Write-Host ""

Write-Host "3. TESTAR CARDS DE CATEGORIAS:" -ForegroundColor Yellow
Write-Host "   - Va para: Servidores" -ForegroundColor White
Write-Host "   [ ] Cards alinhados em 3 colunas (desktop)" -ForegroundColor White
Write-Host "   [ ] Espacamento de 20px entre cards" -ForegroundColor White
Write-Host "   [ ] Nao ha sobreposicao" -ForegroundColor White
Write-Host "   [ ] Responsivo (2 colunas tablet, 1 mobile)" -ForegroundColor White
Write-Host ""

Write-Host "4. SE AINDA HOUVER PROBLEMAS:" -ForegroundColor Yellow
Write-Host "   - Abra o console do navegador (F12)" -ForegroundColor White
Write-Host "   - Verifique se ha erros" -ForegroundColor White
Write-Host "   - Teste em aba anonima (Ctrl+Shift+N)" -ForegroundColor White
Write-Host "   - Verifique os logs: docker logs coruja-frontend" -ForegroundColor White
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  DOCUMENTACAO CRIADA:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "- STATUS_COMPLETO_LOGIN_CARDS_03MAR.md" -ForegroundColor White
Write-Host "  (Status completo de ambas as tarefas)" -ForegroundColor Gray
Write-Host ""
Write-Host "- CORRECAO_LOGIN_03MAR.md" -ForegroundColor White
Write-Host "  (Detalhes das correcoes do login)" -ForegroundColor Gray
Write-Host ""
Write-Host "- SITUACAO_CARDS_03MAR.md" -ForegroundColor White
Write-Host "  (Situacao dos cards de categorias)" -ForegroundColor Gray
Write-Host ""

Write-Host "Pressione Enter para abrir o navegador..." -ForegroundColor Yellow
Read-Host

# Abrir navegador
Start-Process "http://localhost:3000"

Write-Host ""
Write-Host "Navegador aberto! Lembre-se de pressionar Ctrl+Shift+R!" -ForegroundColor Green
Write-Host ""
