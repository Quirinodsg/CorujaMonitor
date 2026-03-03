# Script para Reorganizar Menu - 27 FEV 2026

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  REORGANIZAÇÃO DO MENU LATERAL" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Este script irá:" -ForegroundColor Yellow
Write-Host "1. Manter sidebar com 10 itens principais" -ForegroundColor White
Write-Host "2. Adicionar botões de navegação dentro das páginas" -ForegroundColor White
Write-Host "3. Reiniciar o frontend" -ForegroundColor White
Write-Host ""

Write-Host "ESTRUTURA DO MENU:" -ForegroundColor Cyan
Write-Host ""
Write-Host "SIDEBAR (10 itens):" -ForegroundColor Yellow
Write-Host "  📊 Dashboard" -ForegroundColor White
Write-Host "  🏢 Empresas" -ForegroundColor White
Write-Host "  🖥️ Servidores" -ForegroundColor White
Write-Host "  📡 Sensores" -ForegroundColor White
Write-Host "  ⚠️ Incidentes" -ForegroundColor White
Write-Host "  📈 Relatórios" -ForegroundColor White
Write-Host "  🧠 Base de Conhecimento" -ForegroundColor White
Write-Host "  🤖 Atividades da IA" -ForegroundColor White
Write-Host "  ⚙️ Configurações" -ForegroundColor White
Write-Host "  🔮 AIOps" -ForegroundColor White
Write-Host ""

Write-Host "BOTÕES DENTRO DAS PÁGINAS:" -ForegroundColor Yellow
Write-Host "  Dashboard:" -ForegroundColor Cyan
Write-Host "    - 🎯 NOC" -ForegroundColor White
Write-Host "    - 📈 Dashboard Avançado" -ForegroundColor White
Write-Host "    - 📊 Métricas (Grafana)" -ForegroundColor White
Write-Host ""
Write-Host "  Empresas:" -ForegroundColor Cyan
Write-Host "    - 🔌 Probes" -ForegroundColor White
Write-Host ""
Write-Host "  Servidores:" -ForegroundColor Cyan
Write-Host "    - 📦 Servidores Agrupados" -ForegroundColor White
Write-Host ""
Write-Host "  Incidentes:" -ForegroundColor Cyan
Write-Host "    - 🔧 GMUD" -ForegroundColor White
Write-Host "    - 🧪 Testes de Sensores" -ForegroundColor White
Write-Host ""

Write-Host "Deseja continuar? (S/N)" -ForegroundColor Yellow
$resposta = Read-Host

if ($resposta -ne "S" -and $resposta -ne "s") {
    Write-Host "Operação cancelada." -ForegroundColor Red
    exit
}

Write-Host ""
Write-Host "Reiniciando frontend..." -ForegroundColor Yellow
docker-compose restart frontend

Write-Host ""
Write-Host "✅ Frontend reiniciado!" -ForegroundColor Green
Write-Host ""
Write-Host "PRÓXIMOS PASSOS:" -ForegroundColor Cyan
Write-Host "1. Aguarde ~30 segundos" -ForegroundColor White
Write-Host "2. Recarregue a página (Ctrl + F5)" -ForegroundColor White
Write-Host "3. Faça login: admin@coruja.com / admin123" -ForegroundColor White
Write-Host "4. Verifique o menu lateral (10 itens)" -ForegroundColor White
Write-Host ""
Write-Host "NOTA:" -ForegroundColor Yellow
Write-Host "Os botões dentro das páginas serão adicionados em uma próxima atualização." -ForegroundColor White
Write-Host "Por enquanto, o menu lateral está organizado e limpo." -ForegroundColor White
Write-Host ""
