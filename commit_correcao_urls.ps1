# Script para commitar correção de URLs duplicadas

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "📤 ENVIANDO CORREÇÃO PARA GIT" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se Git Bash está instalado
$gitBashPath = "C:\Program Files\Git\bin\bash.exe"
if (-not (Test-Path $gitBashPath)) {
    Write-Host "❌ Git Bash não encontrado em: $gitBashPath" -ForegroundColor Red
    Write-Host ""
    Write-Host "Por favor, use o GitHub Desktop ou instale o Git:" -ForegroundColor Yellow
    Write-Host "https://git-scm.com/download/win" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Git Bash encontrado" -ForegroundColor Green
Write-Host ""

# Comandos Git
$commands = @"
cd '/c/Users/andre.quirino/Coruja Monitor'
git add frontend/src/config.js
git add corrigir_urls_duplicadas.sh
git add CORRECAO_FINAL_URL_DUPLICADA.txt
git add commit_correcao_urls.ps1
git commit -m "fix: Corrigir URLs duplicadas /api/v1/api/v1 - CACHE_VERSION v10.0"
git push origin master
"@

Write-Host "📝 Executando comandos Git..." -ForegroundColor Yellow
& $gitBashPath -c $commands

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=========================================" -ForegroundColor Green
    Write-Host "✅ COMMIT ENVIADO COM SUCESSO!" -ForegroundColor Green
    Write-Host "=========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 PRÓXIMOS PASSOS NO LINUX:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "cd /home/administrador/CorujaMonitor" -ForegroundColor White
    Write-Host "chmod +x corrigir_urls_duplicadas.sh" -ForegroundColor White
    Write-Host "./corrigir_urls_duplicadas.sh" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "❌ Erro ao enviar commit" -ForegroundColor Red
    Write-Host "Verifique os erros acima" -ForegroundColor Yellow
}
