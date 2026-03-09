# Script para fazer commit e push das alterações
# Execute este script no PowerShell

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  COMMIT E PUSH - SISTEMA DE RESET" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se estamos no diretório correto
if (!(Test-Path ".git")) {
    Write-Host "[ERRO] Não estamos em um repositório Git!" -ForegroundColor Red
    Write-Host "Execute este script na pasta CorujaMonitor" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host "[1/4] Adicionando arquivos..." -ForegroundColor Yellow
git add .

Write-Host "[2/4] Fazendo commit..." -ForegroundColor Yellow
git commit -m "Sistema de Reset Completo implementado

- Endpoint /api/v1/system/reset para apagar tudo
- Componente SystemReset.js no frontend
- Integrado em Settings -> Ferramentas Admin
- Script reset_sistema.py para linha de comando
- Apaga: metricas, incidentes, sensores, servidores, probes, empresas
- Mantem: usuario admin
- Confirmacao requer digitar RESETAR
- Guias de instalacao e uso"

Write-Host "[3/4] Enviando para GitHub (branch master)..." -ForegroundColor Yellow
git push origin master

Write-Host "[4/4] Concluído!" -ForegroundColor Green
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  PRÓXIMO PASSO: ATUALIZAR NO LINUX" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Execute no servidor Linux:" -ForegroundColor Yellow
Write-Host ""
Write-Host "cd /home/administrador/CorujaMonitor && \" -ForegroundColor White
Write-Host "git fetch origin && \" -ForegroundColor White
Write-Host "git checkout master && \" -ForegroundColor White
Write-Host "git pull origin master && \" -ForegroundColor White
Write-Host "docker-compose restart" -ForegroundColor White
Write-Host ""
Write-Host "Aguarde 30 segundos e acesse:" -ForegroundColor Yellow
Write-Host "http://192.168.31.161:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Veja o arquivo: EXECUTAR_NO_LINUX_AGORA.txt" -ForegroundColor Green
Write-Host ""
pause
