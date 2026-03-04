Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CORRECAO DE INCIDENTES E NOC" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Passo 1: Fechar incidentes resolvidos
Write-Host "[1/3] Fechando incidentes resolvidos..." -ForegroundColor Yellow
$output = docker-compose exec -T api python fechar_incidentes_resolvidos.py 2>&1 | Out-String
$output -split "`n" | Where-Object { $_ -match "Encontrados|Fechando|Fechados|Ainda ativos|incidente" -and $_ -notmatch "DEBUG|httpx|httpcore" } | ForEach-Object {
    Write-Host $_ -ForegroundColor Green
}

# Passo 2: Reiniciar worker
Write-Host ""
Write-Host "[2/3] Reiniciando worker..." -ForegroundColor Yellow
docker-compose restart worker | Out-Null
Write-Host "Worker reiniciado!" -ForegroundColor Green

# Passo 3: Reiniciar API
Write-Host ""
Write-Host "[3/3] Reiniciando API..." -ForegroundColor Yellow
docker-compose restart api | Out-Null
Write-Host "API reiniciada!" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CORRECOES APLICADAS!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Aguarde 10 segundos para os servicos iniciarem..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "Proximo passo:" -ForegroundColor Cyan
Write-Host "1. Pare a probe que esta rodando (Ctrl+C no terminal dela)" -ForegroundColor White
Write-Host "2. Execute: .\iniciar_probe.bat" -ForegroundColor White
Write-Host ""
