# Script para reiniciar frontend com limpeza de cache
Write-Host "=== Reiniciando Frontend com Limpeza de Cache ===" -ForegroundColor Cyan

# Parar processos Node.js do frontend
Write-Host "`nParando processos Node.js..." -ForegroundColor Yellow
Get-Process -Name "node" -ErrorAction SilentlyContinue | Where-Object { 
    $_.Path -like "*frontend*" 
} | Stop-Process -Force

Start-Sleep -Seconds 2

# Limpar cache do npm
Write-Host "`nLimpando cache do build..." -ForegroundColor Yellow
if (Test-Path "frontend/build") {
    Remove-Item -Path "frontend/build" -Recurse -Force
    Write-Host "Cache do build removido" -ForegroundColor Green
}

if (Test-Path "frontend/.cache") {
    Remove-Item -Path "frontend/.cache" -Recurse -Force
    Write-Host "Cache do webpack removido" -ForegroundColor Green
}

# Iniciar frontend
Write-Host "`nIniciando frontend..." -ForegroundColor Yellow
Set-Location frontend

# Usar npm através do caminho completo
$npmPath = (Get-Command npm -ErrorAction SilentlyContinue).Source
if ($npmPath) {
    Start-Process -FilePath $npmPath -ArgumentList "start" -NoNewWindow
    Write-Host "Frontend iniciado!" -ForegroundColor Green
} else {
    Write-Host "ERRO: npm não encontrado no PATH" -ForegroundColor Red
    Write-Host "Tentando iniciar com comando direto..." -ForegroundColor Yellow
    cmd /c "npm start"
}

Set-Location ..

Write-Host "`n=== INSTRUÇÕES ===" -ForegroundColor Cyan
Write-Host "1. Aguarde o frontend carregar (pode levar 30-60 segundos)" -ForegroundColor White
Write-Host "2. Abra o navegador em http://localhost:3000" -ForegroundColor White
Write-Host "3. Pressione Ctrl+Shift+R para limpar cache do navegador" -ForegroundColor Yellow
Write-Host "4. Faça login e verifique as cores dos incidentes" -ForegroundColor White
Write-Host "`nCores esperadas:" -ForegroundColor Cyan
Write-Host "  🔴 Incidentes ABERTOS críticos: Vermelho claro" -ForegroundColor Red
Write-Host "  🟠 Incidentes ABERTOS avisos: Laranja claro" -ForegroundColor Yellow
Write-Host "  🔵 Incidentes RECONHECIDOS: Azul claro" -ForegroundColor Blue
Write-Host "  🟢 Incidentes RESOLVIDOS: Verde claro" -ForegroundColor Green
