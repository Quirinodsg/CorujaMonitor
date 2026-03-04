# ========================================
# Instalar Dependencias (Sem Recompilar psycopg2)
# ========================================

Write-Host "Instalando dependencias essenciais..." -ForegroundColor Yellow
Write-Host ""

cd api

# Instalar dependencias uma por uma, pulando psycopg2-binary
Write-Host "Instalando pydantic-settings..." -ForegroundColor Gray
python -m pip install pydantic-settings

Write-Host "Instalando Azure SDK..." -ForegroundColor Gray
python -m pip install azure-identity azure-mgmt-resource azure-mgmt-compute azure-mgmt-monitor

Write-Host "Instalando SNMP..." -ForegroundColor Gray
python -m pip install pysnmp

Write-Host "Instalando outras dependencias..." -ForegroundColor Gray
python -m pip install requests httpx pytz

Write-Host ""
Write-Host "Dependencias instaladas!" -ForegroundColor Green
Write-Host ""

Write-Host "Executando migracao..." -ForegroundColor Yellow
python migrate_standalone_sensors.py

cd ..

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  CONCLUIDO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

pause
