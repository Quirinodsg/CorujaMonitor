Write-Host "Enviando correção de erros para o Git..." -ForegroundColor Cyan

git add corrigir_tabelas_banco.sh
git add EXECUTAR_AGORA_CORRIGIR_ERROS.txt
git add diagnostico_login_completo.sh
git add corrigir_login_definitivo.sh
git add commit_correcao_erros_paginas.sh
git add COMANDOS_GIT_CORRECAO_ERROS.txt
git add enviar_correcao_erros.ps1

git commit -m "fix: Corrigir erros nas páginas (Empresas, Incidentes, Relatórios, KB, IA)

- Script para criar todas as tabelas necessárias no banco
- Popular Knowledge Base com dados iniciais
- Diagnóstico completo de login
- Correção definitiva de login com senha correta"

git push origin master

Write-Host ""
Write-Host "Arquivos enviados para o GitHub!" -ForegroundColor Green
Write-Host ""
Write-Host "Agora execute no servidor Linux:" -ForegroundColor Yellow
Write-Host "  cd ~/CorujaMonitor" -ForegroundColor White
Write-Host "  git pull origin master" -ForegroundColor White
Write-Host "  chmod +x corrigir_tabelas_banco.sh" -ForegroundColor White
Write-Host "  ./corrigir_tabelas_banco.sh" -ForegroundColor White
Write-Host ""
