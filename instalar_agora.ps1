# ========================================
# Instalacao Rapida - Biblioteca Sensores
# ========================================

Write-Host ""
Write-Host "Instalando dependencias..." -ForegroundColor Yellow

cd api

# Instalar TODAS as dependencias
python -m pip install -r requirements.txt

Write-Host ""
Write-Host "Executando migracao..." -ForegroundColor Yellow

# Executar migracao
python migrate_standalone_sensors.py

cd ..

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  CONCLUIDO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Reinicie API e Frontend:" -ForegroundColor Cyan
Write-Host "  cd api && uvicorn main:app --reload" -ForegroundColor White
Write-Host "  cd frontend && npm start" -ForegroundColor White
Write-Host ""

pause
