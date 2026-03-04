# ========================================
# Instalador Biblioteca de Sensores
# ========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Biblioteca de Sensores - Instalacao" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Instalar dependencias no Python global
Write-Host "1. Instalando dependencias Python..." -ForegroundColor Yellow
Write-Host ""

cd api

# Verificar se Python esta instalado
Write-Host "   Verificando Python..." -ForegroundColor Gray
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "   ERRO: Python nao encontrado!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Instale Python 3.8+ e adicione ao PATH" -ForegroundColor Yellow
    pause
    exit 1
}
Write-Host "   OK $pythonVersion" -ForegroundColor Green

# Instalar TODAS as dependencias do requirements.txt
Write-Host "   Atualizando pip..." -ForegroundColor Gray
python -m pip install --upgrade pip --quiet

Write-Host "   Instalando TODAS as dependencias do requirements.txt..." -ForegroundColor Gray
Write-Host "   (Isso pode levar alguns minutos...)" -ForegroundColor Gray
python -m pip install -r requirements.txt --quiet

if ($LASTEXITCODE -eq 0) {
    Write-Host "   OK Todas as dependencias instaladas!" -ForegroundColor Green
} else {
    Write-Host "   AVISO: Algumas dependencias podem ter falhado" -ForegroundColor Yellow
    Write-Host "   Tentando instalar as essenciais individualmente..." -ForegroundColor Gray
    
    # Instalar as mais importantes individualmente
    python -m pip install sqlalchemy psycopg2-binary pydantic pydantic-settings --quiet
    python -m pip install azure-identity azure-mgmt-resource pysnmp requests --quiet
    
    Write-Host "   OK Dependencias essenciais instaladas!" -ForegroundColor Green
}

Write-Host ""

# 2. Executar migracao do banco de dados
Write-Host "2. Executando migracao do banco de dados..." -ForegroundColor Yellow
Write-Host ""

python migrate_standalone_sensors.py

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "   OK Migracao concluida!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "   ERRO: Falha na migracao!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Verifique:" -ForegroundColor Yellow
    Write-Host "   1. Banco de dados esta rodando?" -ForegroundColor White
    Write-Host "   2. Credenciais no .env estao corretas?" -ForegroundColor White
    Write-Host "   3. Tabela 'sensors' existe?" -ForegroundColor White
    pause
    exit 1
}

cd ..

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  INSTALACAO CONCLUIDA COM SUCESSO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Proximos passos:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Reinicie a API:" -ForegroundColor White
Write-Host "   - Pare o processo atual (Ctrl+C)" -ForegroundColor Gray
Write-Host "   - cd api" -ForegroundColor Gray
Write-Host "   - uvicorn main:app --reload" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Reinicie o Frontend:" -ForegroundColor White
Write-Host "   - Pare o processo atual (Ctrl+C)" -ForegroundColor Gray
Write-Host "   - cd frontend" -ForegroundColor Gray
Write-Host "   - npm start" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Acesse o sistema:" -ForegroundColor White
Write-Host "   - Login: admin@coruja.com / admin123" -ForegroundColor Gray
Write-Host "   - Clique em '📚 Biblioteca de Sensores'" -ForegroundColor Gray
Write-Host "   - Adicione seu primeiro sensor!" -ForegroundColor Gray
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

pause
