# Script para criar pacote instalador completo

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "📦 CRIAR PACOTE INSTALADOR COMPLETO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Set-Location "C:\Users\andre.quirino\Coruja Monitor"

# Criar estrutura de pastas
Write-Host "📁 Criando estrutura de pastas..." -ForegroundColor Yellow
$null = New-Item -ItemType Directory -Force -Path "probe-installer\probe"
$null = New-Item -ItemType Directory -Force -Path "probe-installer\probe\collectors"

# Copiar arquivos Python
Write-Host "📄 Copiando arquivos Python..." -ForegroundColor Yellow
Copy-Item "probe\*.py" -Destination "probe-installer\probe\" -Force
Copy-Item "probe\collectors\*.py" -Destination "probe-installer\probe\collectors\" -Force -Recurse

# Copiar scripts BAT
Write-Host "📄 Copiando scripts BAT..." -ForegroundColor Yellow
Copy-Item "probe\*.bat" -Destination "probe-installer\probe\" -Force

# Copiar documentação
Write-Host "📄 Copiando documentação..." -ForegroundColor Yellow
Copy-Item "probe\*.md" -Destination "probe-installer\probe\" -Force
Copy-Item "probe\*.txt" -Destination "probe-installer\probe\" -Force

# Copiar requirements
Write-Host "📄 Copiando requirements.txt..." -ForegroundColor Yellow
Copy-Item "probe\requirements.txt" -Destination "probe-installer\probe\" -Force

# Copiar config
Write-Host "📄 Copiando arquivos de configuração..." -ForegroundColor Yellow
Copy-Item "probe\*.json" -Destination "probe-installer\probe\" -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✅ PACOTE CRIADO COM SUCESSO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "📦 Pasta: probe-installer\" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 CONTEÚDO:" -ForegroundColor Yellow
Write-Host "   • INSTALAR_TUDO.bat (instalador principal)" -ForegroundColor White
Write-Host "   • DESINSTALAR.bat (desinstalador)" -ForegroundColor White
Write-Host "   • README.txt (instruções)" -ForegroundColor White
Write-Host "   • probe\ (todos os arquivos da probe)" -ForegroundColor White
Write-Host ""
Write-Host "🎯 PRÓXIMO PASSO:" -ForegroundColor Cyan
Write-Host "   1. Comprima a pasta 'probe-installer' em ZIP" -ForegroundColor White
Write-Host "   2. Distribua o ZIP para os clientes" -ForegroundColor White
Write-Host "   3. Cliente descompacta e executa INSTALAR_TUDO.bat" -ForegroundColor White
Write-Host ""

# Contar arquivos
$pythonFiles = (Get-ChildItem -Path "probe-installer\probe\*.py" -Recurse).Count
$batFiles = (Get-ChildItem -Path "probe-installer\probe\*.bat").Count
$collectorFiles = (Get-ChildItem -Path "probe-installer\probe\collectors\*.py").Count

Write-Host "📊 ESTATÍSTICAS:" -ForegroundColor Yellow
Write-Host "   • Arquivos Python: $pythonFiles" -ForegroundColor White
Write-Host "   • Scripts BAT: $batFiles" -ForegroundColor White
Write-Host "   • Coletores: $collectorFiles" -ForegroundColor White
Write-Host ""

Write-Host "Pressione ENTER para sair..."
Read-Host
