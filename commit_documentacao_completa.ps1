# Script para commit completo da documentação e código
# Data: 03/03/2026

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "COMMIT COMPLETO - DOCUMENTAÇÃO E CÓDIGO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se está em um repositório Git
if (-not (Test-Path ".git")) {
    Write-Host "Inicializando repositório Git..." -ForegroundColor Yellow
    git init
    Write-Host "Repositório Git inicializado!" -ForegroundColor Green
}

Write-Host "[1/5] Adicionando todos os arquivos ao Git..." -ForegroundColor Yellow
git add .

Write-Host "[2/5] Verificando status..." -ForegroundColor Yellow
$status = git status --short
$fileCount = ($status | Measure-Object).Count
Write-Host "Arquivos a serem commitados: $fileCount" -ForegroundColor Cyan

Write-Host "[3/5] Criando commit..." -ForegroundColor Yellow
$commitMessage = @"
📚 Documentação Completa do Sistema Coruja Monitor

## Arquitetura e Código
- ✅ Backend (API FastAPI)
- ✅ Frontend (React)
- ✅ Probe (Agente de Monitoramento)
- ✅ AI Agent (Motor de IA/AIOps)
- ✅ Worker (Celery para tarefas assíncronas)

## Funcionalidades Implementadas
- ✅ Monitoramento de Servidores (WMI, SNMP, Ping)
- ✅ Sensores por Categoria (Sistema, Docker, Serviços, Aplicações, Rede)
- ✅ Dashboard NOC em Tempo Real
- ✅ Sistema de Incidentes com IA
- ✅ AIOps Automático (Detecção e Remediação)
- ✅ Base de Conhecimento
- ✅ Relatórios Personalizados
- ✅ Integrações (TOPdesk, GLPI, Teams, Email)
- ✅ Kubernetes Monitoring
- ✅ Janelas de Manutenção
- ✅ Thresholds Temporais
- ✅ Notificações Automáticas

## Documentação Incluída
- 📖 Guias de Instalação (Domínio, Workgroup, Entra ID)
- 📖 Arquitetura do Sistema
- 📖 Guias de Configuração
- 📖 Troubleshooting
- 📖 Histórico de Correções
- 📖 Scripts de Automação

## Correções Recentes (03/03/2026)
- 🔧 Cores de incidentes por status
- 🔧 Navegação de cards de incidentes
- 🔧 API de métricas (404 corrigido)
- 🔧 NOC zerado com incidentes abertos
- 🔧 Barras de métricas e layout de cards
- 🔧 Cards de categorias sobrepostos (Flexbox)

Data: $(Get-Date -Format 'dd/MM/yyyy HH:mm:ss')
"@

git commit -m $commitMessage

Write-Host "[4/5] Verificando branches..." -ForegroundColor Yellow
$currentBranch = git branch --show-current
if ([string]::IsNullOrEmpty($currentBranch)) {
    Write-Host "Criando branch main..." -ForegroundColor Yellow
    git branch -M main
    $currentBranch = "main"
}
Write-Host "Branch atual: $currentBranch" -ForegroundColor Cyan

Write-Host "[5/5] Criando tags..." -ForegroundColor Yellow
$tag = "v1.0.0-$(Get-Date -Format 'yyyyMMdd')"
git tag -a $tag -m "Release completo com documentação - $(Get-Date -Format 'dd/MM/yyyy')"
Write-Host "Tag criada: $tag" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "COMMIT REALIZADO COM SUCESSO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "📊 ESTATÍSTICAS:" -ForegroundColor Cyan
Write-Host "  Branch: $currentBranch" -ForegroundColor White
Write-Host "  Tag: $tag" -ForegroundColor White
Write-Host "  Arquivos commitados: $fileCount" -ForegroundColor White
Write-Host ""
Write-Host "🔗 CONFIGURANDO REPOSITÓRIO REMOTO:" -ForegroundColor Cyan

# Verificar se remote já existe
$remoteExists = git remote get-url origin 2>$null
if ([string]::IsNullOrEmpty($remoteExists)) {
    Write-Host "Adicionando remote origin..." -ForegroundColor Yellow
    git remote add origin https://github.com/Quirinodsg/CorujaMonitor.git
    Write-Host "Remote adicionado!" -ForegroundColor Green
} else {
    Write-Host "Remote já configurado: $remoteExists" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "📤 FAZENDO PUSH PARA GITHUB:" -ForegroundColor Cyan
Write-Host "Enviando código para: https://github.com/Quirinodsg/CorujaMonitor" -ForegroundColor White
Write-Host ""

try {
    Write-Host "Enviando branch $currentBranch..." -ForegroundColor Yellow
    git push -u origin $currentBranch 2>&1 | Out-String | Write-Host
    
    Write-Host "Enviando tag $tag..." -ForegroundColor Yellow
    git push origin $tag 2>&1 | Out-String | Write-Host
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "✅ PUSH REALIZADO COM SUCESSO!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "🌐 Acesse seu repositório:" -ForegroundColor Cyan
    Write-Host "   https://github.com/Quirinodsg/CorujaMonitor" -ForegroundColor White
    Write-Host ""
} catch {
    Write-Host ""
    Write-Host "⚠️ ERRO NO PUSH:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    Write-Host "POSSÍVEIS SOLUÇÕES:" -ForegroundColor Yellow
    Write-Host "1. Configure suas credenciais do GitHub:" -ForegroundColor White
    Write-Host "   git config --global user.name 'Seu Nome'" -ForegroundColor Gray
    Write-Host "   git config --global user.email 'seu@email.com'" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Use Personal Access Token para autenticação:" -ForegroundColor White
    Write-Host "   https://github.com/settings/tokens" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. Ou faça push manualmente:" -ForegroundColor White
    Write-Host "   git push -u origin $currentBranch" -ForegroundColor Gray
    Write-Host "   git push origin $tag" -ForegroundColor Gray
    Write-Host ""
}
