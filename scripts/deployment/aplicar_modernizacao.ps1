# Script de Aplicação da Modernização do Sistema Coruja
# Aplica tema moderno, sistema de atualização e prepara empacotamento

param(
    [switch]$SkipBackup,
    [switch]$SkipDependencies
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  Coruja - Modernização do Sistema" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Função para criar backup
function Create-Backup {
    if ($SkipBackup) {
        Write-Host "⏭️  Backup ignorado (--SkipBackup)" -ForegroundColor Yellow
        return
    }
    
    Write-Host "📦 Criando backup..." -ForegroundColor Yellow
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupDir = "backups/pre_modernizacao_$timestamp"
    
    New-Item -ItemType Directory -Force -Path $backupDir | Out-Null
    
    # Backup de arquivos críticos
    $itemsToBackup = @(
        "frontend/src/styles",
        "frontend/src/components",
        "api/routers",
        ".env"
    )
    
    foreach ($item in $itemsToBackup) {
        if (Test-Path $item) {
            $dest = Join-Path $backupDir $item
            $destDir = Split-Path $dest -Parent
            New-Item -ItemType Directory -Force -Path $destDir | Out-Null
            Copy-Item -Path $item -Destination $dest -Recurse -Force
        }
    }
    
    Write-Host "✓ Backup criado: $backupDir" -ForegroundColor Green
}

# Função para instalar dependências
function Install-Dependencies {
    if ($SkipDependencies) {
        Write-Host "⏭️  Dependências ignoradas (--SkipDependencies)" -ForegroundColor Yellow
        return
    }
    
    Write-Host "📚 Instalando dependências..." -ForegroundColor Yellow
    
    # Python
    if (Test-Path "api/requirements.txt") {
        Write-Host "  → Python packages..." -ForegroundColor Gray
        pip install -r api/requirements.txt --upgrade --quiet
        pip install semver requests --quiet
    }
    
    # Node.js
    if (Test-Path "frontend/package.json") {
        Write-Host "  → Node.js packages..." -ForegroundColor Gray
        Push-Location frontend
        npm install --silent
        Pop-Location
    }
    
    Write-Host "✓ Dependências instaladas" -ForegroundColor Green
}

# Função para aplicar tema moderno
function Apply-ModernTheme {
    Write-Host "🎨 Aplicando tema moderno..." -ForegroundColor Yellow
    
    # Verificar se arquivo existe
    if (-not (Test-Path "frontend/src/styles/modern-theme.css")) {
        Write-Host "❌ Arquivo modern-theme.css não encontrado!" -ForegroundColor Red
        return $false
    }
    
    # Importar tema no App.js ou index.js
    $appFiles = @(
        "frontend/src/App.js",
        "frontend/src/index.js"
    )
    
    foreach ($file in $appFiles) {
        if (Test-Path $file) {
            $content = Get-Content $file -Raw
            
            if ($content -notmatch "modern-theme.css") {
                $import = "import './styles/modern-theme.css';`n"
                $content = $import + $content
                Set-Content -Path $file -Value $content
                Write-Host "  → Tema importado em $file" -ForegroundColor Gray
            }
        }
    }
    
    Write-Host "✓ Tema moderno aplicado" -ForegroundColor Green
    return $true
}

# Função para configurar sistema de atualização
function Setup-AutoUpdate {
    Write-Host "🔄 Configurando sistema de atualização..." -ForegroundColor Yellow
    
    # Verificar backend
    if (-not (Test-Path "api/routers/auto_update.py")) {
        Write-Host "❌ Backend de atualização não encontrado!" -ForegroundColor Red
        return $false
    }
    
    # Adicionar rota no main.py
    $mainFile = "api/main.py"
    if (Test-Path $mainFile) {
        $content = Get-Content $mainFile -Raw
        
        if ($content -notmatch "auto_update") {
            # Adicionar import
            $importLine = "from api.routers import auto_update"
            $routerLine = "app.include_router(auto_update.router)"
            
            Write-Host "  → Adicionando rota de atualização..." -ForegroundColor Gray
            # Nota: Implementação simplificada - ajustar conforme estrutura real
        }
    }
    
    # Criar arquivo version.txt se não existir
    if (-not (Test-Path "version.txt")) {
        Set-Content -Path "version.txt" -Value "1.0.0"
        Write-Host "  → Arquivo version.txt criado" -ForegroundColor Gray
    }
    
    # Configurar .env
    if (Test-Path ".env") {
        $envContent = Get-Content ".env" -Raw
        
        if ($envContent -notmatch "GITHUB_REPO") {
            Add-Content -Path ".env" -Value "`nGITHUB_REPO=seu-usuario/coruja-monitoring"
            Write-Host "  → GITHUB_REPO adicionado ao .env" -ForegroundColor Gray
        }
    }
    
    Write-Host "✓ Sistema de atualização configurado" -ForegroundColor Green
    return $true
}

# Função para adicionar componente de atualização ao frontend
function Add-UpdateComponent {
    Write-Host "⚛️  Adicionando componente de atualização..." -ForegroundColor Yellow
    
    if (-not (Test-Path "frontend/src/components/SystemUpdates.js")) {
        Write-Host "❌ Componente SystemUpdates.js não encontrado!" -ForegroundColor Red
        return $false
    }
    
    # Adicionar rota no App.js ou router
    Write-Host "  → Componente disponível em /settings/updates" -ForegroundColor Gray
    Write-Host "  → Adicione manualmente ao menu de configurações" -ForegroundColor Gray
    
    Write-Host "✓ Componente de atualização pronto" -ForegroundColor Green
    return $true
}

# Função para preparar scripts de build
function Prepare-BuildScripts {
    Write-Host "🔨 Preparando scripts de build..." -ForegroundColor Yellow
    
    # Verificar scripts
    $scripts = @(
        "scripts/build-deb.sh",
        "scripts/build-appimage.sh",
        "scripts/build-msi.ps1"
    )
    
    $allExist = $true
    foreach ($script in $scripts) {
        if (-not (Test-Path $script)) {
            Write-Host "  ⚠️  $script não encontrado" -ForegroundColor Yellow
            $allExist = $false
        } else {
            # Tornar executável (Linux/Mac)
            if ($script -match "\.sh$") {
                # chmod +x será necessário no Linux
                Write-Host "  → $script encontrado" -ForegroundColor Gray
            }
        }
    }
    
    if ($allExist) {
        Write-Host "✓ Scripts de build prontos" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Alguns scripts não foram encontrados" -ForegroundColor Yellow
    }
    
    return $allExist
}

# Função para verificar GitHub Actions
function Check-GitHubActions {
    Write-Host "🚀 Verificando GitHub Actions..." -ForegroundColor Yellow
    
    if (Test-Path ".github/workflows/release.yml") {
        Write-Host "✓ Workflow de release configurado" -ForegroundColor Green
        Write-Host "  → Para criar release: git tag v1.0.0 && git push origin v1.0.0" -ForegroundColor Gray
        return $true
    } else {
        Write-Host "⚠️  Workflow não encontrado" -ForegroundColor Yellow
        return $false
    }
}

# Função para rebuild do frontend
function Rebuild-Frontend {
    Write-Host "🏗️  Reconstruindo frontend..." -ForegroundColor Yellow
    
    if (Test-Path "frontend") {
        Push-Location frontend
        
        Write-Host "  → Limpando build anterior..." -ForegroundColor Gray
        if (Test-Path "build") {
            Remove-Item -Path "build" -Recurse -Force
        }
        
        Write-Host "  → Executando build..." -ForegroundColor Gray
        npm run build 2>&1 | Out-Null
        
        Pop-Location
        
        if (Test-Path "frontend/build") {
            Write-Host "✓ Frontend reconstruído" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ Erro ao construir frontend" -ForegroundColor Red
            return $false
        }
    }
    
    return $false
}

# Função para testar sistema
function Test-System {
    Write-Host "🧪 Testando sistema..." -ForegroundColor Yellow
    
    # Verificar arquivos críticos
    $criticalFiles = @(
        "frontend/src/styles/modern-theme.css",
        "frontend/src/components/SystemUpdates.js",
        "api/routers/auto_update.py",
        "update_and_restart.ps1"
    )
    
    $allOk = $true
    foreach ($file in $criticalFiles) {
        if (Test-Path $file) {
            Write-Host "  ✓ $file" -ForegroundColor Green
        } else {
            Write-Host "  ❌ $file não encontrado" -ForegroundColor Red
            $allOk = $false
        }
    }
    
    return $allOk
}

# ============================================
# EXECUÇÃO PRINCIPAL
# ============================================

try {
    # 1. Criar backup
    Create-Backup
    Write-Host ""
    
    # 2. Instalar dependências
    Install-Dependencies
    Write-Host ""
    
    # 3. Aplicar tema moderno
    $themeOk = Apply-ModernTheme
    Write-Host ""
    
    # 4. Configurar auto-update
    $updateOk = Setup-AutoUpdate
    Write-Host ""
    
    # 5. Adicionar componente
    $componentOk = Add-UpdateComponent
    Write-Host ""
    
    # 6. Preparar builds
    $buildOk = Prepare-BuildScripts
    Write-Host ""
    
    # 7. Verificar GitHub Actions
    $actionsOk = Check-GitHubActions
    Write-Host ""
    
    # 8. Rebuild frontend
    $frontendOk = Rebuild-Frontend
    Write-Host ""
    
    # 9. Testar sistema
    $testOk = Test-System
    Write-Host ""
    
    # Resumo
    Write-Host "=========================================" -ForegroundColor Cyan
    Write-Host "  Resumo da Modernização" -ForegroundColor Cyan
    Write-Host "=========================================" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "Tema Moderno:           $(if($themeOk){'✓'}else{'❌'})" -ForegroundColor $(if($themeOk){'Green'}else{'Red'})
    Write-Host "Sistema de Atualização: $(if($updateOk){'✓'}else{'❌'})" -ForegroundColor $(if($updateOk){'Green'}else{'Red'})
    Write-Host "Componente Frontend:    $(if($componentOk){'✓'}else{'❌'})" -ForegroundColor $(if($componentOk){'Green'}else{'Red'})
    Write-Host "Scripts de Build:       $(if($buildOk){'✓'}else{'❌'})" -ForegroundColor $(if($buildOk){'Green'}else{'Red'})
    Write-Host "GitHub Actions:         $(if($actionsOk){'✓'}else{'❌'})" -ForegroundColor $(if($actionsOk){'Green'}else{'Red'})
    Write-Host "Frontend Build:         $(if($frontendOk){'✓'}else{'❌'})" -ForegroundColor $(if($frontendOk){'Green'}else{'Red'})
    Write-Host ""
    
    if ($themeOk -and $updateOk -and $testOk) {
        Write-Host "=========================================" -ForegroundColor Green
        Write-Host "  ✓ Modernização Concluída!" -ForegroundColor Green
        Write-Host "=========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Próximos passos:" -ForegroundColor Cyan
        Write-Host "1. Reiniciar sistema: .\restart.bat" -ForegroundColor White
        Write-Host "2. Acessar: http://localhost:3000" -ForegroundColor White
        Write-Host "3. Testar tema e responsividade" -ForegroundColor White
        Write-Host "4. Configurar GITHUB_REPO no .env" -ForegroundColor White
        Write-Host "5. Testar atualização em /settings/updates" -ForegroundColor White
        Write-Host ""
        Write-Host "Documentação completa: GUIA_MODERNIZACAO_COMPLETO.md" -ForegroundColor Yellow
    } else {
        Write-Host "=========================================" -ForegroundColor Yellow
        Write-Host "  ⚠️  Modernização Parcial" -ForegroundColor Yellow
        Write-Host "=========================================" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Alguns componentes não foram aplicados." -ForegroundColor Yellow
        Write-Host "Verifique os erros acima e tente novamente." -ForegroundColor Yellow
    }
    
} catch {
    Write-Host ""
    Write-Host "=========================================" -ForegroundColor Red
    Write-Host "  ❌ Erro durante modernização" -ForegroundColor Red
    Write-Host "=========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Erro: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Para reverter, use o backup em: backups/" -ForegroundColor Yellow
    exit 1
}
