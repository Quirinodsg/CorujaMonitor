# Script para aplicar a Biblioteca de Sensores Independentes
# Execute este script para ativar a nova funcionalidade

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  BIBLIOTECA DE SENSORES INDEPENDENTES" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Detectar ambiente virtual
$venvPaths = @(
    "venv\Scripts\Activate.ps1",
    ".venv\Scripts\Activate.ps1",
    "env\Scripts\Activate.ps1"
)

$venvFound = $false
foreach ($venvPath in $venvPaths) {
    if (Test-Path $venvPath) {
        Write-Host "Ativando ambiente virtual: $venvPath" -ForegroundColor Yellow
        & $venvPath
        $venvFound = $true
        break
    }
}

if (-not $venvFound) {
    Write-Host "⚠️ Aviso: Ambiente virtual não encontrado." -ForegroundColor Yellow
    Write-Host "Continuando com Python global..." -ForegroundColor Yellow
    Write-Host ""
}

# 0. Instalar dependências Python
Write-Host "0. Instalando dependências Python..." -ForegroundColor Yellow
Write-Host ""

cd api

# Instalar todas as dependências do requirements.txt
pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "⚠️ Aviso: Algumas dependências podem não ter sido instaladas." -ForegroundColor Yellow
    Write-Host "Tentando instalar individualmente..." -ForegroundColor Yellow
    
    # Tentar instalar as novas dependências individualmente
    pip install azure-identity
    pip install azure-mgmt-resource
    pip install azure-mgmt-compute
    pip install azure-mgmt-monitor
    pip install pysnmp
    pip install requests
}

Write-Host ""
Write-Host "✅ Dependências instaladas!" -ForegroundColor Green
Write-Host ""

# 1. Executar migração do banco de dados
Write-Host "1. Executando migração do banco de dados..." -ForegroundColor Yellow
Write-Host ""

python migrate_standalone_sensors.py

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Erro na migração do banco de dados!" -ForegroundColor Red
    Write-Host "Verifique os logs acima e tente novamente." -ForegroundColor Red
    Write-Host ""
    Write-Host "Dica: Certifique-se que:" -ForegroundColor Yellow
    Write-Host "1. O ambiente virtual está ativado" -ForegroundColor White
    Write-Host "2. As dependências foram instaladas: pip install -r requirements.txt" -ForegroundColor White
    Write-Host "3. O banco de dados está acessível" -ForegroundColor White
    cd ..
    exit 1
}

cd ..

Write-Host ""
Write-Host "✅ Migração concluída com sucesso!" -ForegroundColor Green
Write-Host ""

# 2. Informações sobre reiniciar serviços
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  PRÓXIMOS PASSOS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "2. Reinicie os serviços:" -ForegroundColor Yellow
Write-Host "   - API Backend (FastAPI)" -ForegroundColor White
Write-Host "   - Frontend (React)" -ForegroundColor White
Write-Host ""

Write-Host "3. Acesse a nova funcionalidade:" -ForegroundColor Yellow
Write-Host "   - Faça login no sistema" -ForegroundColor White
Write-Host "   - Clique em '📚 Biblioteca de Sensores' no menu lateral" -ForegroundColor White
Write-Host "   - Clique em '+ Adicionar Sensor'" -ForegroundColor White
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TIPOS DE SENSORES DISPONÍVEIS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "📡 SNMP:" -ForegroundColor Green
Write-Host "   - Access Points (WiFi)" -ForegroundColor White
Write-Host "   - Ar-Condicionado (Temperatura)" -ForegroundColor White
Write-Host "   - Nobreaks (UPS)" -ForegroundColor White
Write-Host "   - Impressoras" -ForegroundColor White
Write-Host "   - Switches" -ForegroundColor White
Write-Host "   - Roteadores" -ForegroundColor White
Write-Host ""

Write-Host "☁️ Microsoft Azure:" -ForegroundColor Green
Write-Host "   - Virtual Machines" -ForegroundColor White
Write-Host "   - Web Apps" -ForegroundColor White
Write-Host "   - SQL Database" -ForegroundColor White
Write-Host "   - Storage Account" -ForegroundColor White
Write-Host "   - AKS (Kubernetes)" -ForegroundColor White
Write-Host "   - Functions" -ForegroundColor White
Write-Host "   - Backup Vault" -ForegroundColor White
Write-Host "   - Load Balancer" -ForegroundColor White
Write-Host "   - Application Gateway" -ForegroundColor White
Write-Host "   - Cosmos DB" -ForegroundColor White
Write-Host "   - Redis Cache" -ForegroundColor White
Write-Host "   - Service Bus" -ForegroundColor White
Write-Host "   - Event Hub" -ForegroundColor White
Write-Host "   - Key Vault" -ForegroundColor White
Write-Host ""

Write-Host "💿 Storage:" -ForegroundColor Green
Write-Host "   - Dell EqualLogic" -ForegroundColor White
Write-Host "   - NetApp Filer" -ForegroundColor White
Write-Host "   - EMC VNX" -ForegroundColor White
Write-Host "   - HP 3PAR" -ForegroundColor White
Write-Host "   - Synology NAS" -ForegroundColor White
Write-Host "   - QNAP NAS" -ForegroundColor White
Write-Host ""

Write-Host "🌐 Network:" -ForegroundColor Green
Write-Host "   - HTTP/HTTPS" -ForegroundColor White
Write-Host "   - SSL Certificates" -ForegroundColor White
Write-Host "   - DNS Query" -ForegroundColor White
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  EXEMPLO DE USO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Adicionar Access Point:" -ForegroundColor Yellow
Write-Host "1. Selecione a Probe responsável" -ForegroundColor White
Write-Host "2. Escolha categoria 'SNMP'" -ForegroundColor White
Write-Host "3. Clique no template 'Access Point'" -ForegroundColor White
Write-Host "4. Preencha:" -ForegroundColor White
Write-Host "   - Nome: AP-Sala-01" -ForegroundColor Gray
Write-Host "   - IP: 192.168.1.100" -ForegroundColor Gray
Write-Host "   - Community: public" -ForegroundColor Gray
Write-Host "5. Clique em 'Adicionar Sensor'" -ForegroundColor White
Write-Host ""

Write-Host "Adicionar Serviço Azure:" -ForegroundColor Yellow
Write-Host "1. Selecione a Probe responsável" -ForegroundColor White
Write-Host "2. Escolha categoria 'Microsoft Azure'" -ForegroundColor White
Write-Host "3. Clique no template 'Azure Web App'" -ForegroundColor White
Write-Host "4. Preencha as credenciais Azure" -ForegroundColor White
Write-Host "5. Clique em 'Adicionar Sensor'" -ForegroundColor White
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  DOCUMENTAÇÃO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Leia o arquivo:" -ForegroundColor Yellow
Write-Host "BIBLIOTECA_SENSORES_IMPLEMENTADA.md" -ForegroundColor White
Write-Host ""

Write-Host "✅ Configuração concluída!" -ForegroundColor Green
Write-Host ""
Write-Host "Pressione qualquer tecla para sair..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
