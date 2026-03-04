# Script para push automático para GitHub
# Data: 03/03/2026

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PUSH AUTOMÁTICO PARA GITHUB" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Adicionar Git ao PATH
$env:Path += ";C:\Program Files\Git\cmd"

Write-Host "[1/8] Verificando Git..." -ForegroundColor Yellow
$gitVersion = git --version
Write-Host "Git encontrado: $gitVersion" -ForegroundColor Green

Write-Host "[2/8] Inicializando repositório (se necessário)..." -ForegroundColor Yellow
if (-not (Test-Path ".git")) {
    git init
    Write-Host "Repositório inicializado!" -ForegroundColor Green
} else {
    Write-Host "Repositório já existe!" -ForegroundColor Cyan
}

Write-Host "[3/8] Adicionando todos os arquivos..." -ForegroundColor Yellow
git add .

Write-Host "[4/8] Verificando arquivos..." -ForegroundColor Yellow
$status = git status --short
$fileCount = ($status | Measure-Object).Count
Write-Host "Arquivos a serem commitados: $fileCount" -ForegroundColor Cyan

if ($fileCount -eq 0) {
    Write-Host ""
    Write-Host "⚠️ Nenhum arquivo novo para commitar!" -ForegroundColor Yellow
    Write-Host "Verificando se há commits..." -ForegroundColor Yellow
    
    $hasCommits = git log --oneline 2>$null
    if ([string]::IsNullOrEmpty($hasCommits)) {
        Write-Host "Nenhum commit encontrado. Criando commit inicial..." -ForegroundColor Yellow
        git add .
        $fileCount = 1
    } else {
        Write-Host "Repositório já tem commits. Fazendo push..." -ForegroundColor Cyan
    }
}

if ($fileCount -gt 0) {
    Write-Host "[5/8] Criando commit..." -ForegroundColor Yellow
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
    Write-Host "Commit criado!" -ForegroundColor Green
}

Write-Host "[6/8] Configurando branch main..." -ForegroundColor Yellow
$currentBranch = git branch --show-current
if ([string]::IsNullOrEmpty($currentBranch)) {
    git branch -M main
    $currentBranch = "main"
    Write-Host "Branch main criada!" -ForegroundColor Green
} else {
    Write-Host "Branch atual: $currentBranch" -ForegroundColor Cyan
}

Write-Host "[7/8] Configurando remote..." -ForegroundColor Yellow
$remoteExists = git remote get-url origin 2>$null
if ([string]::IsNullOrEmpty($remoteExists)) {
    git remote add origin https://github.com/Quirinodsg/CorujaMonitor.git
    Write-Host "Remote adicionado!" -ForegroundColor Green
} else {
    Write-Host "Remote já configurado: $remoteExists" -ForegroundColor Cyan
}

Write-Host "[8/8] Fazendo push para GitHub..." -ForegroundColor Yellow
Write-Host ""
Write-Host "🔐 ATENÇÃO: Você precisará autenticar!" -ForegroundColor Yellow
Write-Host "   Username: Quirinodsg" -ForegroundColor White
Write-Host "   Password: Use seu Personal Access Token" -ForegroundColor White
Write-Host ""
Write-Host "Enviando para: https://github.com/Quirinodsg/CorujaMonitor" -ForegroundColor Cyan
Write-Host ""

try {
    git push -u origin $currentBranch
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "✅ PUSH REALIZADO COM SUCESSO!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "🌐 Acesse seu repositório:" -ForegroundColor Cyan
    Write-Host "   https://github.com/Quirinodsg/CorujaMonitor" -ForegroundColor White
    Write-Host ""
    
    # Criar e enviar tag
    Write-Host "Criando tag de release..." -ForegroundColor Yellow
    $tag = "v1.0.0-$(Get-Date -Format 'yyyyMMdd')"
    git tag -a $tag -m "Release completo com documentação - $(Get-Date -Format 'dd/MM/yyyy')"
    git push origin $tag
    Write-Host "Tag $tag enviada!" -ForegroundColor Green
    
} catch {
    Write-Host ""
    Write-Host "⚠️ ERRO NO PUSH:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    Write-Host "POSSÍVEIS CAUSAS:" -ForegroundColor Yellow
    Write-Host "1. Credenciais incorretas" -ForegroundColor White
    Write-Host "2. Repositório não existe ou é privado" -ForegroundColor White
    Write-Host "3. Sem permissão de escrita" -ForegroundColor White
    Write-Host ""
    Write-Host "SOLUÇÃO:" -ForegroundColor Yellow
    Write-Host "1. Crie um Personal Access Token:" -ForegroundColor White
    Write-Host "   https://github.com/settings/tokens" -ForegroundColor Gray
    Write-Host "2. Use o token como senha ao fazer push" -ForegroundColor White
    Write-Host ""
}
