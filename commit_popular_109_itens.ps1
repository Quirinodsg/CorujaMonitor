# Script para fazer commit dos arquivos de popular 109 itens
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "📚 COMMIT - POPULAR 109 ITENS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Ir para o diretório do projeto
Set-Location "C:\Users\Administrador\CorujaMonitor"

Write-Host "📁 Adicionando arquivos ao Git..." -ForegroundColor Yellow
git add api/popular_109_itens_completo.py
git add popular_base_109_itens.sh
git add EXECUTAR_POPULAR_109_ITENS.txt
git add commit_popular_109_itens.ps1

Write-Host ""
Write-Host "💾 Fazendo commit..." -ForegroundColor Yellow
git commit -m "feat: Script para popular 109+ itens na base de conhecimento

- Criado popular_109_itens_completo.py com 109+ entradas
- Script shell popular_base_109_itens.sh para executar no Linux
- Instruções completas em EXECUTAR_POPULAR_109_ITENS.txt
- Categorias: Windows, Linux, Docker, Azure, Rede, UPS, AC, Web, DB
- Total: 109 itens cobrindo toda infraestrutura de TI"

Write-Host ""
Write-Host "🚀 Enviando para GitHub..." -ForegroundColor Yellow
git push origin master

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✅ COMMIT CONCLUÍDO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "🐧 PRÓXIMO PASSO: EXECUTAR NO LINUX" -ForegroundColor Cyan
Write-Host ""
Write-Host "Copie e cole no terminal Linux:" -ForegroundColor White
Write-Host ""
Write-Host "cd /home/administrador/CorujaMonitor && git pull && chmod +x popular_base_109_itens.sh && ./popular_base_109_itens.sh" -ForegroundColor Yellow
Write-Host ""
