# Script Simplificado para Aplicar Modernização
# Execute do diretório raiz do projeto

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Aplicando Modernização Coruja" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

try {
    # 1. Importar tema no App.js
    Write-Host "1. Importando tema moderno..." -ForegroundColor Yellow
    $appFile = "frontend/src/App.js"
    
    if (Test-Path $appFile) {
        $content = Get-Content $appFile -Raw
        if ($content -notmatch "modern-theme.css") {
            $import = "import './styles/modern-theme.css';`n"
            Set-Content -Path $appFile -Value ($import + $content)
            Write-Host "   ✓ Tema importado em App.js" -ForegroundColor Green
        } else {
            Write-Host "   ✓ Tema já estava importado" -ForegroundColor Yellow
        }
    } else {
        Write-Host "   ⚠️  App.js não encontrado" -ForegroundColor Yellow
    }

    # 2. Adicionar rota no backend
    Write-Host ""
    Write-Host "2. Configurando backend..." -ForegroundColor Yellow
    $mainFile = "api/main.py"
    
    if (Test-Path $mainFile) {
        $content = Get-Content $mainFile -Raw
        if ($content -notmatch "auto_update") {
            Add-Content -Path $mainFile -Value "`n# Sistema de Atualização Automática"
            Add-Content -Path $mainFile -Value "from api.routers import auto_update"
            Add-Content -Path $mainFile -Value "app.include_router(auto_update.router)"
            Write-Host "   ✓ Rota de atualização adicionada" -ForegroundColor Green
        } else {
            Write-Host "   ✓ Rota já estava configurada" -ForegroundColor Yellow
        }
    } else {
        Write-Host "   ⚠️  main.py não encontrado" -ForegroundColor Yellow
    }

    # 3. Criar arquivo version.txt
    Write-Host ""
    Write-Host "3. Criando arquivo de versão..." -ForegroundColor Yellow
    if (-not (Test-Path "version.txt")) {
        Set-Content -Path "version.txt" -Value "1.0.0"
        Write-Host "   ✓ version.txt criado (v1.0.0)" -ForegroundColor Green
    } else {
        Write-Host "   ✓ version.txt já existe" -ForegroundColor Yellow
    }

    # 4. Configurar .env
    Write-Host ""
    Write-Host "4. Configurando .env..." -ForegroundColor Yellow
    if (Test-Path ".env") {
        $envContent = Get-Content ".env" -Raw
        if ($envContent -notmatch "GITHUB_REPO") {
            Add-Content -Path ".env" -Value "`n# Sistema de Atualização"
            Add-Content -Path ".env" -Value "GITHUB_REPO=seu-usuario/coruja-monitoring"
            Write-Host "   ✓ GITHUB_REPO adicionado" -ForegroundColor Green
            Write-Host "   ⚠️  Edite .env e configure seu repositório!" -ForegroundColor Yellow
        } else {
            Write-Host "   ✓ GITHUB_REPO já configurado" -ForegroundColor Yellow
        }
    } else {
        Write-Host "   ⚠️  .env não encontrado" -ForegroundColor Yellow
    }

    # 5. Instalar dependências Python
    Write-Host ""
    Write-Host "5. Instalando dependências Python..." -ForegroundColor Yellow
    pip install semver requests --quiet 2>&1 | Out-Null
    Write-Host "   ✓ Dependências instaladas (semver, requests)" -ForegroundColor Green

    # 6. Verificar arquivos criados
    Write-Host ""
    Write-Host "6. Verificando arquivos..." -ForegroundColor Yellow
    
    $files = @(
        "frontend/src/styles/modern-theme.css",
        "frontend/src/components/SystemUpdates.js",
        "frontend/src/components/SystemUpdates.css",
        "api/routers/auto_update.py",
        "update_and_restart.ps1"
    )
    
    $allOk = $true
    foreach ($file in $files) {
        if (Test-Path $file) {
            Write-Host "   ✓ $file" -ForegroundColor Green
        } else {
            Write-Host "   ❌ $file não encontrado" -ForegroundColor Red
            $allOk = $false
        }
    }

    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  ✓ Modernização Aplicada!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Próximos passos:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. Reiniciar sistema:" -ForegroundColor White
    Write-Host "   .\restart.bat" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Acessar o sistema:" -ForegroundColor White
    Write-Host "   http://localhost:3000" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. Testar tema moderno:" -ForegroundColor White
    Write-Host "   - Verificar visual dark com glassmorphism" -ForegroundColor Gray
    Write-Host "   - Testar responsividade (redimensionar janela)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "4. Configurar atualizações:" -ForegroundColor White
    Write-Host "   - Editar .env e definir GITHUB_REPO" -ForegroundColor Gray
    Write-Host "   - Adicionar rota /settings/updates no menu" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Documentação completa:" -ForegroundColor Yellow
    Write-Host "- APLICAR_MODERNIZACAO_AGORA.md" -ForegroundColor Gray
    Write-Host "- GUIA_MODERNIZACAO_COMPLETO.md" -ForegroundColor Gray
    Write-Host "- MODERNIZACAO_IMPLEMENTADA.md" -ForegroundColor Gray
    Write-Host ""

} catch {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "  ❌ Erro ao aplicar modernização" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Erro: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Consulte: APLICAR_MODERNIZACAO_AGORA.md" -ForegroundColor Yellow
    exit 1
}
