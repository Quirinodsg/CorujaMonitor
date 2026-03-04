# Script para organizar o repositório Git
# Data: 04 de Março de 2026

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ORGANIZANDO REPOSITÓRIO GIT" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Criar estrutura de pastas
Write-Host "Criando estrutura de pastas..." -ForegroundColor Yellow

$folders = @(
    "docs/guides",           # Guias de instalação e uso
    "docs/architecture",     # Arquitetura e design
    "docs/troubleshooting",  # Solução de problemas
    "docs/changelog",        # Histórico de mudanças por data
    "scripts/maintenance",   # Scripts de manutenção
    "scripts/deployment",    # Scripts de deploy
    "scripts/testing"        # Scripts de teste
)

foreach ($folder in $folders) {
    if (-not (Test-Path $folder)) {
        New-Item -ItemType Directory -Path $folder -Force | Out-Null
        Write-Host "[CRIADO]" -ForegroundColor Green -NoNewline
        Write-Host " $folder"
    } else {
        Write-Host "[EXISTE]" -ForegroundColor Gray -NoNewline
        Write-Host " $folder"
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  MOVENDO ARQUIVOS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Função para mover arquivo com Git
function Move-GitFile {
    param(
        [string]$Source,
        [string]$Destination
    )
    
    if (Test-Path $Source) {
        $destDir = Split-Path $Destination -Parent
        if (-not (Test-Path $destDir)) {
            New-Item -ItemType Directory -Path $destDir -Force | Out-Null
        }
        
        git mv $Source $Destination 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK]" -ForegroundColor Green -NoNewline
            Write-Host " $Source → $Destination"
            return $true
        } else {
            Write-Host "[ERRO]" -ForegroundColor Red -NoNewline
            Write-Host " $Source"
            return $false
        }
    }
    return $false
}

Write-Host "1. Movendo GUIAS..." -ForegroundColor Yellow
Write-Host ""

# Guias de Instalação
$guias = @(
    @{src="GUIA_RAPIDO_INSTALACAO.md"; dest="docs/guides/GUIA_RAPIDO_INSTALACAO.md"},
    @{src="GUIA_INSTALADOR_UNIVERSAL.md"; dest="docs/guides/GUIA_INSTALADOR_UNIVERSAL.md"},
    @{src="GUIA_INSTALADOR_DOMINIO.md"; dest="docs/guides/GUIA_INSTALADOR_DOMINIO.md"},
    @{src="GUIA_ENTRA_ID_AZURE_AD.md"; dest="docs/guides/GUIA_ENTRA_ID_AZURE_AD.md"},
    @{src="GUIA_MONITORAMENTO_SEM_DOMINIO.md"; dest="docs/guides/GUIA_MONITORAMENTO_SEM_DOMINIO.md"},
    @{src="GUIA_MONITORAMENTO_AGENTLESS_COMPLETO.md"; dest="docs/guides/GUIA_MONITORAMENTO_AGENTLESS_COMPLETO.md"},
    @{src="GUIA_INSTALADOR_MSI.md"; dest="docs/guides/GUIA_INSTALADOR_MSI.md"},
    @{src="GUIA_CONFIGURAR_TEAMS.md"; dest="docs/guides/GUIA_CONFIGURAR_TEAMS.md"},
    @{src="GUIA_COMPLETO_KUBERNETES_27FEV.md"; dest="docs/guides/GUIA_COMPLETO_KUBERNETES.md"},
    @{src="GUIA_RAPIDO_KUBERNETES.md"; dest="docs/guides/GUIA_RAPIDO_KUBERNETES.md"},
    @{src="GUIA_RAPIDO_AIOPS.md"; dest="docs/guides/GUIA_RAPIDO_AIOPS.md"},
    @{src="GUIA_COMMIT_GITHUB.md"; dest="docs/guides/GUIA_COMMIT_GITHUB.md"},
    @{src="PASSO_A_PASSO_NOVA_EMPRESA.md"; dest="docs/guides/PASSO_A_PASSO_NOVA_EMPRESA.md"},
    @{src="INICIO_RAPIDO.md"; dest="docs/guides/INICIO_RAPIDO.md"},
    @{src="LEIA_PRIMEIRO.md"; dest="docs/guides/LEIA_PRIMEIRO.md"}
)

foreach ($item in $guias) {
    Move-GitFile -Source $item.src -Destination $item.dest | Out-Null
}

Write-Host ""
Write-Host "2. Movendo ARQUITETURA..." -ForegroundColor Yellow
Write-Host ""

# Arquitetura e Design
$arquitetura = @(
    @{src="ARQUITETURA_COMPLETA.md"; dest="docs/architecture/ARQUITETURA_COMPLETA.md"},
    @{src="ARQUITETURA_SENSORES_PROBE.md"; dest="docs/architecture/ARQUITETURA_SENSORES_PROBE.md"},
    @{src="ARQUITETURA_PRTG_AGENTLESS.md"; dest="docs/architecture/ARQUITETURA_PRTG_AGENTLESS.md"},
    @{src="AIOPS_IA_HIBRIDA_EXPLICADA.md"; dest="docs/architecture/AIOPS_IA_HIBRIDA_EXPLICADA.md"},
    @{src="AIOPS_AUTOMATICO_EXPLICADO.md"; dest="docs/architecture/AIOPS_AUTOMATICO_EXPLICADO.md"},
    @{src="DESIGN_GRAFANA_STYLE_DASHBOARD_27FEV.md"; dest="docs/architecture/DESIGN_GRAFANA_STYLE_DASHBOARD.md"},
    @{src="DESIGN_GRUPOS_AZURE_COMPLETO.md"; dest="docs/architecture/DESIGN_GRUPOS_AZURE_COMPLETO.md"},
    @{src="ROADMAP_ENTERPRISE.md"; dest="docs/architecture/ROADMAP_ENTERPRISE.md"},
    @{src="ROADMAP_ENTERPRISE_DETALHADO.md"; dest="docs/architecture/ROADMAP_ENTERPRISE_DETALHADO.md"}
)

foreach ($item in $arquitetura) {
    Move-GitFile -Source $item.src -Destination $item.dest | Out-Null
}

Write-Host ""
Write-Host "3. Movendo TROUBLESHOOTING..." -ForegroundColor Yellow
Write-Host ""

# Troubleshooting
$troubleshooting = @(
    @{src="SOLUCAO_RAPIDA.md"; dest="docs/troubleshooting/SOLUCAO_RAPIDA.md"},
    @{src="SOLUCAO_SENSORES_DESCONHECIDOS.md"; dest="docs/troubleshooting/SOLUCAO_SENSORES_DESCONHECIDOS.md"},
    @{src="SOLUCAO_ERRO_INSTALACAO.md"; dest="docs/troubleshooting/SOLUCAO_ERRO_INSTALACAO.md"},
    @{src="DIAGNOSTICO_COMPLETO_25FEV.md"; dest="docs/troubleshooting/DIAGNOSTICO_COMPLETO.md"},
    @{src="PROBLEMA_URL_PROBE.md"; dest="docs/troubleshooting/PROBLEMA_URL_PROBE.md"}
)

foreach ($item in $troubleshooting) {
    Move-GitFile -Source $item.src -Destination $item.dest | Out-Null
}

Write-Host ""
Write-Host "4. Movendo SCRIPTS..." -ForegroundColor Yellow
Write-Host ""

# Scripts PowerShell
$scripts_ps1 = Get-ChildItem -Path . -Filter "*.ps1" -File | Where-Object { 
    $_.Name -ne "organizar_repositorio.ps1" -and 
    $_.Name -ne "verificar_screenshots.ps1"
}

foreach ($script in $scripts_ps1) {
    $destPath = "scripts/maintenance/$($script.Name)"
    
    # Categorizar scripts
    if ($script.Name -like "*testar*" -or $script.Name -like "*verificar*") {
        $destPath = "scripts/testing/$($script.Name)"
    }
    elseif ($script.Name -like "*aplicar*" -or $script.Name -like "*rebuild*" -or $script.Name -like "*deploy*") {
        $destPath = "scripts/deployment/$($script.Name)"
    }
    
    Move-GitFile -Source $script.Name -Destination $destPath | Out-Null
}

# Scripts BAT
$scripts_bat = Get-ChildItem -Path . -Filter "*.bat" -File

foreach ($script in $scripts_bat) {
    $destPath = "scripts/maintenance/$($script.Name)"
    Move-GitFile -Source $script.Name -Destination $destPath | Out-Null
}

Write-Host ""
Write-Host "5. Movendo CHANGELOG (por data)..." -ForegroundColor Yellow
Write-Host ""

# Arquivos de changelog por data
$changelog_patterns = @("*_20FEV.md", "*_24FEV.md", "*_25FEV.md", "*_26FEV.md", "*_27FEV.md", "*_28FEV.md", "*_02MAR.md", "*_03MAR.md", "*_04MAR.md")

foreach ($pattern in $changelog_patterns) {
    $files = Get-ChildItem -Path . -Filter $pattern -File
    foreach ($file in $files) {
        # Extrair data do nome do arquivo
        if ($file.Name -match "(\d{2}[A-Z]{3})\.md$") {
            $date = $matches[1]
            $destPath = "docs/changelog/$date/$($file.Name)"
            Move-GitFile -Source $file.Name -Destination $destPath | Out-Null
        }
    }
}

Write-Host ""
Write-Host "6. Movendo SCREENSHOTS..." -ForegroundColor Yellow
Write-Host ""

# Documentação de screenshots
$screenshots_docs = @(
    @{src="ADICIONAR_SCREENSHOTS_GIT.md"; dest="docs/screenshots/ADICIONAR_SCREENSHOTS_GIT.md"},
    @{src="STATUS_SCREENSHOTS_04MAR.md"; dest="docs/screenshots/STATUS_SCREENSHOTS.md"},
    @{src="RESUMO_SCREENSHOTS_04MAR.md"; dest="docs/screenshots/RESUMO_SCREENSHOTS.md"},
    @{src="RESUMO_FINAL_SCREENSHOTS_04MAR.md"; dest="docs/screenshots/RESUMO_FINAL_SCREENSHOTS.md"},
    @{src="CAPTURAR_SCREENSHOTS_AGORA.md"; dest="docs/screenshots/CAPTURAR_SCREENSHOTS_AGORA.md"}
)

foreach ($item in $screenshots_docs) {
    Move-GitFile -Source $item.src -Destination $item.dest | Out-Null
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CRIANDO ÍNDICES" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Criar README.md em cada pasta
$readmes = @{
    "docs/guides/README.md" = @"
# 📚 Guias de Instalação e Uso

Esta pasta contém todos os guias de instalação, configuração e uso do Coruja Monitor.

## 🚀 Início Rápido

- [LEIA_PRIMEIRO.md](LEIA_PRIMEIRO.md) - Comece aqui!
- [INICIO_RAPIDO.md](INICIO_RAPIDO.md) - Guia rápido de instalação
- [GUIA_RAPIDO_INSTALACAO.md](GUIA_RAPIDO_INSTALACAO.md) - Instalação completa

## 📦 Instalação

- [GUIA_INSTALADOR_UNIVERSAL.md](GUIA_INSTALADOR_UNIVERSAL.md) - Instalador universal
- [GUIA_INSTALADOR_DOMINIO.md](GUIA_INSTALADOR_DOMINIO.md) - Instalação em domínio AD
- [GUIA_ENTRA_ID_AZURE_AD.md](GUIA_ENTRA_ID_AZURE_AD.md) - Instalação com Entra ID
- [GUIA_MONITORAMENTO_SEM_DOMINIO.md](GUIA_MONITORAMENTO_SEM_DOMINIO.md) - Sem domínio
- [GUIA_INSTALADOR_MSI.md](GUIA_INSTALADOR_MSI.md) - Instalador MSI

## 🔧 Configuração

- [GUIA_CONFIGURAR_TEAMS.md](GUIA_CONFIGURAR_TEAMS.md) - Integração Teams
- [GUIA_MONITORAMENTO_AGENTLESS_COMPLETO.md](GUIA_MONITORAMENTO_AGENTLESS_COMPLETO.md) - Monitoramento agentless

## ☸️ Kubernetes

- [GUIA_COMPLETO_KUBERNETES.md](GUIA_COMPLETO_KUBERNETES.md) - Guia completo
- [GUIA_RAPIDO_KUBERNETES.md](GUIA_RAPIDO_KUBERNETES.md) - Guia rápido

## 🤖 AIOps

- [GUIA_RAPIDO_AIOPS.md](GUIA_RAPIDO_AIOPS.md) - Guia rápido AIOps

## 🏢 Empresas

- [PASSO_A_PASSO_NOVA_EMPRESA.md](PASSO_A_PASSO_NOVA_EMPRESA.md) - Adicionar nova empresa

## 🔄 Git

- [GUIA_COMMIT_GITHUB.md](GUIA_COMMIT_GITHUB.md) - Como fazer commits
"@

    "docs/architecture/README.md" = @"
# 🏗️ Arquitetura e Design

Esta pasta contém documentação sobre a arquitetura e design do sistema.

## 📐 Arquitetura

- [ARQUITETURA_COMPLETA.md](ARQUITETURA_COMPLETA.md) - Arquitetura completa do sistema
- [ARQUITETURA_SENSORES_PROBE.md](ARQUITETURA_SENSORES_PROBE.md) - Arquitetura de sensores
- [ARQUITETURA_PRTG_AGENTLESS.md](ARQUITETURA_PRTG_AGENTLESS.md) - Monitoramento agentless

## 🤖 AIOps

- [AIOPS_IA_HIBRIDA_EXPLICADA.md](AIOPS_IA_HIBRIDA_EXPLICADA.md) - IA Híbrida
- [AIOPS_AUTOMATICO_EXPLICADO.md](AIOPS_AUTOMATICO_EXPLICADO.md) - AIOps automático

## 🎨 Design

- [DESIGN_GRAFANA_STYLE_DASHBOARD.md](DESIGN_GRAFANA_STYLE_DASHBOARD.md) - Dashboard Grafana-style
- [DESIGN_GRUPOS_AZURE_COMPLETO.md](DESIGN_GRUPOS_AZURE_COMPLETO.md) - Grupos Azure

## 🗺️ Roadmap

- [ROADMAP_ENTERPRISE.md](ROADMAP_ENTERPRISE.md) - Roadmap resumido
- [ROADMAP_ENTERPRISE_DETALHADO.md](ROADMAP_ENTERPRISE_DETALHADO.md) - Roadmap detalhado
"@

    "docs/troubleshooting/README.md" = @"
# 🔧 Solução de Problemas

Esta pasta contém guias de troubleshooting e solução de problemas comuns.

## 🚀 Início Rápido

- [SOLUCAO_RAPIDA.md](SOLUCAO_RAPIDA.md) - Soluções rápidas para problemas comuns

## 🔍 Diagnóstico

- [DIAGNOSTICO_COMPLETO.md](DIAGNOSTICO_COMPLETO.md) - Diagnóstico completo do sistema

## 🐛 Problemas Comuns

- [SOLUCAO_SENSORES_DESCONHECIDOS.md](SOLUCAO_SENSORES_DESCONHECIDOS.md) - Sensores "Desconhecido"
- [SOLUCAO_ERRO_INSTALACAO.md](SOLUCAO_ERRO_INSTALACAO.md) - Erros de instalação
- [PROBLEMA_URL_PROBE.md](PROBLEMA_URL_PROBE.md) - Problemas com URL da probe
"@

    "scripts/README.md" = @"
# 🔧 Scripts

Esta pasta contém scripts PowerShell e Batch para manutenção, deploy e testes.

## 📁 Estrutura

- **maintenance/** - Scripts de manutenção e utilitários
- **deployment/** - Scripts de deploy e aplicação de mudanças
- **testing/** - Scripts de teste e verificação

## 🚀 Scripts Principais

### Manutenção
- Limpeza de cache
- Reinicialização de serviços
- Backup e restore

### Deploy
- Aplicar correções
- Rebuild de containers
- Atualização de componentes

### Testes
- Verificação de status
- Testes de funcionalidades
- Validação de configurações

## ⚠️ Importante

Sempre execute scripts com privilégios de administrador quando necessário.
"@

    "docs/changelog/README.md" = @"
# 📅 Histórico de Mudanças

Esta pasta contém o histórico de mudanças organizadas por data.

## 📂 Estrutura

Cada subpasta representa uma data específica (formato: DDMMM):
- 20FEV - 20 de Fevereiro de 2026
- 24FEV - 24 de Fevereiro de 2026
- 25FEV - 25 de Fevereiro de 2026
- 26FEV - 26 de Fevereiro de 2026
- 27FEV - 27 de Fevereiro de 2026
- 28FEV - 28 de Fevereiro de 2026
- 02MAR - 02 de Março de 2026
- 03MAR - 03 de Março de 2026
- 04MAR - 04 de Março de 2026

## 📝 Conteúdo

Cada pasta contém:
- Correções aplicadas
- Implementações realizadas
- Resumos de sessão
- Status de funcionalidades
- Instruções específicas

## 🔍 Como Usar

Para encontrar mudanças de uma data específica, navegue até a pasta correspondente.
"@
}

foreach ($path in $readmes.Keys) {
    $content = $readmes[$path]
    $dir = Split-Path $path -Parent
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
    Set-Content -Path $path -Value $content -Encoding UTF8
    Write-Host "[CRIADO]" -ForegroundColor Green -NoNewline
    Write-Host " $path"
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  RESUMO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Estrutura criada:" -ForegroundColor Yellow
Write-Host "  docs/guides/           - Guias de instalação e uso"
Write-Host "  docs/architecture/     - Arquitetura e design"
Write-Host "  docs/troubleshooting/  - Solução de problemas"
Write-Host "  docs/changelog/        - Histórico por data"
Write-Host "  scripts/maintenance/   - Scripts de manutenção"
Write-Host "  scripts/deployment/    - Scripts de deploy"
Write-Host "  scripts/testing/       - Scripts de teste"
Write-Host ""

Write-Host "Próximos passos:" -ForegroundColor Yellow
Write-Host "1. Revise as mudanças: git status"
Write-Host "2. Commit: git commit -m 'docs: Reorganiza estrutura do repositório'"
Write-Host "3. Push: git push origin master"
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CONCLUÍDO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
