# ========================================
# Corrigir Dependencias Faltantes
# ========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Corrigindo Dependencias Faltantes" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

cd api

Write-Host "Instalando pydantic-settings e outras dependencias..." -ForegroundColor Yellow
Write-Host ""

# Instalar pydantic-settings especificamente
python -m pip install pydantic-settings

# Instalar todas as dependencias do requirements.txt
python -m pip install -r requirements.txt

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Dependencias Corrigidas!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

cd ..

Write-Host "Agora execute a migracao:" -ForegroundColor Cyan
Write-Host "   cd api" -ForegroundColor White
Write-Host "   python migrate_standalone_sensors.py" -ForegroundColor White
Write-Host ""

pause
