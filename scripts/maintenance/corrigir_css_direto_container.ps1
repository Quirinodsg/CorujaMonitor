# Script para corrigir CSS diretamente no container
# Data: 03/03/2026

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CORREÇÃO DIRETA NO CONTAINER" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/4] Criando arquivo CSS corrigido..." -ForegroundColor Yellow

$cssContent = @'
/* Sensors Summary - Melhorado e alinhado */
.sensors-summary {
  display: flex !important;
  flex-wrap: wrap !important;
  gap: 20px !important;
  margin-bottom: 30px !important;
}

.sensors-summary .summary-card {
  flex: 1 1 calc(33.333% - 14px) !important;
  min-width: 220px !important;
  max-width: calc(33.333% - 14px) !important;
  box-sizing: border-box !important;
}

@media (max-width: 1200px) {
  .sensors-summary .summary-card {
    flex: 1 1 calc(50% - 10px) !important;
    max-width: calc(50% - 10px) !important;
  }
}

@media (max-width: 768px) {
  .sensors-summary .summary-card {
    flex: 1 1 100% !important;
    max-width: 100% !important;
  }
}
'@

$cssContent | Out-File -FilePath "sensors-summary-fix.css" -Encoding UTF8 -NoNewline

Write-Host "[2/4] Copiando para o container..." -ForegroundColor Yellow
docker cp sensors-summary-fix.css coruja-frontend-1:/tmp/sensors-summary-fix.css

Write-Host "[3/4] Aplicando correção no arquivo CSS..." -ForegroundColor Yellow
docker exec coruja-frontend-1 bash -c @"
# Fazer backup
cp /app/src/components/Management.css /app/src/components/Management.css.bak

# Remover seção antiga
sed -i '/\/\* Sensors Summary - Melhorado e alinhado \*\//,/@media (max-width: 768px) {/{
  /\/\* Sensors Summary - Melhorado e alinhado \*\//!{
    /@media (max-width: 768px) {/!d
  }
}' /app/src/components/Management.css

# Adicionar nova seção na linha 1862
sed -i '1862r /tmp/sensors-summary-fix.css' /app/src/components/Management.css
"@

Write-Host "[4/4] Limpando arquivo temporário..." -ForegroundColor Yellow
Remove-Item -Path "sensors-summary-fix.css" -Force

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "CORREÇÃO APLICADA DIRETAMENTE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "IMPORTANTE:" -ForegroundColor Yellow
Write-Host "1. Pressione Ctrl+Shift+R no navegador" -ForegroundColor White
Write-Host "2. Se não funcionar, reinicie o frontend:" -ForegroundColor White
Write-Host "   docker-compose restart frontend" -ForegroundColor Cyan
Write-Host ""
