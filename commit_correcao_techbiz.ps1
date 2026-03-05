# Script para commit da correção da empresa Techbiz

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "COMMIT: Correção Empresa Techbiz" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Adicionar arquivos
Write-Host "Adicionando arquivos..." -ForegroundColor Yellow
git add rebuild_frontend_linux.sh
git add CORRIGIR_EMPRESA_TECHBIZ.md
git add COMANDOS_CORRIGIR_TECHBIZ.txt
git add commit_correcao_techbiz.ps1

# Commit
Write-Host ""
Write-Host "Fazendo commit..." -ForegroundColor Yellow
git commit -m "fix: Adiciona script para rebuild do frontend e corrigir empresa Techbiz fantasma

- Script rebuild_frontend_linux.sh para reconstruir frontend sem cache
- Documentação do problema e solução
- Comandos prontos para execução no servidor Linux
- Problema: Frontend em cache mostrando dados antigos
- Solução: Rebuild completo da imagem Docker do frontend"

# Push
Write-Host ""
Write-Host "Enviando para GitHub..." -ForegroundColor Yellow
git push origin master

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "COMMIT CONCLUÍDO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "PRÓXIMOS PASSOS NO SERVIDOR LINUX:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. git pull origin master" -ForegroundColor White
Write-Host "2. chmod +x rebuild_frontend_linux.sh" -ForegroundColor White
Write-Host "3. ./rebuild_frontend_linux.sh" -ForegroundColor White
Write-Host ""
