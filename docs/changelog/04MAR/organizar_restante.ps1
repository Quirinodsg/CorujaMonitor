# Script para organizar arquivos restantes
# Data: 04 de Março de 2026

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ORGANIZANDO ARQUIVOS RESTANTES" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Criar pasta de tutoriais
$folders = @(
    "docs/tutorials",
    "docs/implementation",
    "docs/reference"
)

foreach ($folder in $folders) {
    if (-not (Test-Path $folder)) {
        New-Item -ItemType Directory -Path $folder -Force | Out-Null
        Write-Host "[CRIADO]" -ForegroundColor Green -NoNewline
        Write-Host " $folder"
    }
}

Write-Host ""

# Função para mover arquivo
function Move-GitFile {
    param([string]$Source, [string]$Destination)
    
    if (Test-Path $Source) {
        $destDir = Split-Path $Destination -Parent
        if (-not (Test-Path $destDir)) {
            New-Item -ItemType Directory -Path $destDir -Force | Out-Null
        }
        
        git mv $Source $Destination 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK]" -ForegroundColor Green -NoNewline
            Write-Host " $Source"
            return $true
        }
    }
    return $false
}

Write-Host "Movendo TUTORIAIS..." -ForegroundColor Yellow
Write-Host ""

# Tutoriais e guias práticos
$tutoriais = @(
    @{src="COMO_INSTALAR_NOVA_PROBE.md"; dest="docs/tutorials/COMO_INSTALAR_NOVA_PROBE.md"},
    @{src="GUIA_VISUAL_LOGO_CORUJA.md"; dest="docs/tutorials/GUIA_VISUAL_LOGO_CORUJA.md"},
    @{src="GUIA_VISUAL_RECONHECIMENTO.md"; dest="docs/tutorials/GUIA_VISUAL_RECONHECIMENTO.md"},
    @{src="GUIA_URL_PROBE.md"; dest="docs/tutorials/GUIA_URL_PROBE.md"},
    @{src="GUIA_ATUALIZACAO_SONDA.md"; dest="docs/tutorials/GUIA_ATUALIZACAO_SONDA.md"},
    @{src="GUIA_DESINSTALACAO.md"; dest="docs/tutorials/GUIA_DESINSTALACAO.md"},
    @{src="GUIA_REINSTALACAO_LIMPA.md"; dest="docs/tutorials/GUIA_REINSTALACAO_LIMPA.md"},
    @{src="GUIA_RAPIDO_AUTO_START.md"; dest="docs/tutorials/GUIA_RAPIDO_AUTO_START.md"},
    @{src="GUIA_RAPIDO_GRUPOS.md"; dest="docs/tutorials/GUIA_RAPIDO_GRUPOS.md"},
    @{src="GUIA_MODERNIZACAO_COMPLETO.md"; dest="docs/tutorials/GUIA_MODERNIZACAO_COMPLETO.md"},
    @{src="INSTALAR_OLLAMA_WINDOWS.md"; dest="docs/tutorials/INSTALAR_OLLAMA_WINDOWS.md"},
    @{src="CONFIGURAR_LOGO_CORUJA.md"; dest="docs/tutorials/CONFIGURAR_LOGO_CORUJA.md"},
    @{src="LEIA_ISTO_PRIMEIRO.md"; dest="docs/tutorials/LEIA_ISTO_PRIMEIRO.md"},
    @{src="LEIA_ISTO_TOPDESK.md"; dest="docs/tutorials/LEIA_ISTO_TOPDESK.md"},
    @{src="EXEMPLOS_PRATICOS_AIOPS.md"; dest="docs/tutorials/EXEMPLOS_PRATICOS_AIOPS.md"},
    @{src="WMI_COMPARACAO_VISUAL.md"; dest="docs/tutorials/WMI_COMPARACAO_VISUAL.md"},
    @{src="WMI_REMOTO_RESUMO.md"; dest="docs/tutorials/WMI_REMOTO_RESUMO.md"},
    @{src="COMANDOS_RAPIDOS.md"; dest="docs/tutorials/COMANDOS_RAPIDOS.md"},
    @{src="COMANDOS_DOCKER_CORRETOS.md"; dest="docs/tutorials/COMANDOS_DOCKER_CORRETOS.md"},
    @{src="COMANDOS_TOPDESK.md"; dest="docs/tutorials/COMANDOS_TOPDESK.md"}
)

foreach ($item in $tutoriais) {
    Move-GitFile -Source $item.src -Destination $item.dest | Out-Null
}

Write-Host ""
Write-Host "Movendo IMPLEMENTAÇÕES..." -ForegroundColor Yellow
Write-Host ""

# Documentos de implementação
$implementacoes = @(
    @{src="AIOPS_IMPLEMENTADO.md"; dest="docs/implementation/AIOPS_IMPLEMENTADO.md"},
    @{src="AUTO_REMEDIACAO_IMPLEMENTADA.md"; dest="docs/implementation/AUTO_REMEDIACAO_IMPLEMENTADA.md"},
    @{src="BIBLIOTECA_SENSORES_IMPLEMENTADA.md"; dest="docs/implementation/BIBLIOTECA_SENSORES_IMPLEMENTADA.md"},
    @{src="CONFIGURACOES_IMPLEMENTADAS.md"; dest="docs/implementation/CONFIGURACOES_IMPLEMENTADAS.md"},
    @{src="CORRECOES_FINAIS_IMPLEMENTADAS.md"; dest="docs/implementation/CORRECOES_FINAIS_IMPLEMENTADAS.md"},
    @{src="DESCOBERTA_SERVICOS_TEMPO_REAL.md"; dest="docs/implementation/DESCOBERTA_SERVICOS_TEMPO_REAL.md"},
    @{src="FERRAMENTAS_ADMIN_IMPLEMENTADAS.md"; dest="docs/implementation/FERRAMENTAS_ADMIN_IMPLEMENTADAS.md"},
    @{src="IMPLEMENTACAO_AGRUPAMENTO_SENSORES.md"; dest="docs/implementation/IMPLEMENTACAO_AGRUPAMENTO_SENSORES.md"},
    @{src="IMPLEMENTACAO_COMPLETA_GRUPOS_AZURE.md"; dest="docs/implementation/IMPLEMENTACAO_COMPLETA_GRUPOS_AZURE.md"},
    @{src="IMPLEMENTACAO_COMPLETA.md"; dest="docs/implementation/IMPLEMENTACAO_COMPLETA.md"},
    @{src="IMPLEMENTACAO_DASHBOARD_NOC_AIOPS.md"; dest="docs/implementation/IMPLEMENTACAO_DASHBOARD_NOC_AIOPS.md"},
    @{src="IMPLEMENTACAO_NOC_SNMP_COMPLETA.md"; dest="docs/implementation/IMPLEMENTACAO_NOC_SNMP_COMPLETA.md"},
    @{src="INCIDENTES_IMPLEMENTADO.md"; dest="docs/implementation/INCIDENTES_IMPLEMENTADO.md"},
    @{src="INTERFACE_AIOPS_IMPLEMENTADA.md"; dest="docs/implementation/INTERFACE_AIOPS_IMPLEMENTADA.md"},
    @{src="JANELAS_MANUTENCAO_IMPLEMENTADO.md"; dest="docs/implementation/JANELAS_MANUTENCAO_IMPLEMENTADO.md"},
    @{src="KNOWLEDGE_BASE_IMPLEMENTADO_COMPLETO.md"; dest="docs/implementation/KNOWLEDGE_BASE_IMPLEMENTADO_COMPLETO.md"},
    @{src="LOGO_E_TIMEZONE_IMPLEMENTADOS.md"; dest="docs/implementation/LOGO_E_TIMEZONE_IMPLEMENTADOS.md"},
    @{src="MODERNIZACAO_APLICADA_SUCESSO.md"; dest="docs/implementation/MODERNIZACAO_APLICADA_SUCESSO.md"},
    @{src="MODERNIZACAO_IMPLEMENTADA.md"; dest="docs/implementation/MODERNIZACAO_IMPLEMENTADA.md"},
    @{src="MONITORAMENTO_ATIVOS_REDE_IMPLEMENTADO.md"; dest="docs/implementation/MONITORAMENTO_ATIVOS_REDE_IMPLEMENTADO.md"},
    @{src="NAVEGACAO_SENSOR_IMPLEMENTADA.md"; dest="docs/implementation/NAVEGACAO_SENSOR_IMPLEMENTADA.md"},
    @{src="NOTIFICACAO_EMAIL_IMPLEMENTADA.md"; dest="docs/implementation/NOTIFICACAO_EMAIL_IMPLEMENTADA.md"},
    @{src="NOTIFICACOES_AUTOMATICAS_IMPLEMENTADAS.md"; dest="docs/implementation/NOTIFICACOES_AUTOMATICAS_IMPLEMENTADAS.md"},
    @{src="OLLAMA_DOCKER_INSTALADO.md"; dest="docs/implementation/OLLAMA_DOCKER_INSTALADO.md"},
    @{src="PROBE_AUTO_START_IMPLEMENTADO.md"; dest="docs/implementation/PROBE_AUTO_START_IMPLEMENTADO.md"},
    @{src="RELATORIOS_PERSONALIZADOS_IMPLEMENTADO.md"; dest="docs/implementation/RELATORIOS_PERSONALIZADOS_IMPLEMENTADO.md"},
    @{src="SENSOR_DOCKER_IMPLEMENTADO.md"; dest="docs/implementation/SENSOR_DOCKER_IMPLEMENTADO.md"},
    @{src="SISTEMA_GRUPOS_HIERARQUICOS_IMPLEMENTADO.md"; dest="docs/implementation/SISTEMA_GRUPOS_HIERARQUICOS_IMPLEMENTADO.md"},
    @{src="SISTEMA_KNOWLEDGE_BASE_IMPLEMENTADO.md"; dest="docs/implementation/SISTEMA_KNOWLEDGE_BASE_IMPLEMENTADO.md"},
    @{src="SISTEMA_RECONHECIMENTO_IMPLEMENTADO.md"; dest="docs/implementation/SISTEMA_RECONHECIMENTO_IMPLEMENTADO.md"},
    @{src="TEMA_MODERNO_IMPLEMENTADO.md"; dest="docs/implementation/TEMA_MODERNO_IMPLEMENTADO.md"},
    @{src="TESTE_CONEXAO_IMPLEMENTADO.md"; dest="docs/implementation/TESTE_CONEXAO_IMPLEMENTADO.md"},
    @{src="THRESHOLDS_TEMPORAIS_IMPLEMENTADO.md"; dest="docs/implementation/THRESHOLDS_TEMPORAIS_IMPLEMENTADO.md"},
    @{src="INSTALADORES_MSI_CRIADOS.md"; dest="docs/implementation/INSTALADORES_MSI_CRIADOS.md"}
)

foreach ($item in $implementacoes) {
    Move-GitFile -Source $item.src -Destination $item.dest | Out-Null
}

Write-Host ""
Write-Host "Movendo REFERÊNCIAS..." -ForegroundColor Yellow
Write-Host ""

# Documentos de referência
$referencias = @(
    @{src="INDICE_INSTALADORES.md"; dest="docs/reference/INDICE_INSTALADORES.md"},
    @{src="INDICE_INSTALADORES_ATUALIZADO.md"; dest="docs/reference/INDICE_INSTALADORES_ATUALIZADO.md"},
    @{src="INDICE_BIBLIOTECA_SENSORES.md"; dest="docs/reference/INDICE_BIBLIOTECA_SENSORES.md"},
    @{src="INDICE_DOCUMENTACAO_AIOPS.md"; dest="docs/reference/INDICE_DOCUMENTACAO_AIOPS.md"},
    @{src="BASE_CONHECIMENTO_32_ITENS.md"; dest="docs/reference/BASE_CONHECIMENTO_32_ITENS.md"},
    @{src="BASE_CONHECIMENTO_80_ITENS_COMPLETA.md"; dest="docs/reference/BASE_CONHECIMENTO_80_ITENS_COMPLETA.md"},
    @{src="INTEGRACOES_TOPDESK_GLPI.md"; dest="docs/reference/INTEGRACOES_TOPDESK_GLPI.md"},
    @{src="NOVAS_FUNCIONALIDADES.md"; dest="docs/reference/NOVAS_FUNCIONALIDADES.md"},
    @{src="RELATORIOS_EXECUTIVOS.md"; dest="docs/reference/RELATORIOS_EXECUTIVOS.md"},
    @{src="RELATORIOS_PERSONALIZADOS_DESIGN.md"; dest="docs/reference/RELATORIOS_PERSONALIZADOS_DESIGN.md"},
    @{src="AGRUPAMENTO_SENSORES_DESIGN.md"; dest="docs/reference/AGRUPAMENTO_SENSORES_DESIGN.md"},
    @{src="PLANO_MODERNIZACAO_SISTEMA.md"; dest="docs/reference/PLANO_MODERNIZACAO_SISTEMA.md"},
    @{src="PROJECT_SUMMARY.md"; dest="docs/reference/PROJECT_SUMMARY.md"},
    @{src="TEMPLATES_EXPANDIDOS.md"; dest="docs/reference/TEMPLATES_EXPANDIDOS.md"}
)

foreach ($item in $referencias) {
    Move-GitFile -Source $item.src -Destination $item.dest | Out-Null
}

Write-Host ""
Write-Host "Movendo SOLUÇÕES para troubleshooting..." -ForegroundColor Yellow
Write-Host ""

# Mais soluções para troubleshooting
$solucoes = @(
    @{src="SOLUCAO_COLETA_REMOTA.md"; dest="docs/troubleshooting/SOLUCAO_COLETA_REMOTA.md"},
    @{src="SOLUCAO_COMPLETA_DOCKER.md"; dest="docs/troubleshooting/SOLUCAO_COMPLETA_DOCKER.md"},
    @{src="SOLUCAO_DASHBOARD_ZERADO.md"; dest="docs/troubleshooting/SOLUCAO_DASHBOARD_ZERADO.md"},
    @{src="SOLUCAO_DEFINITIVA_SENSORES_DUPLICADOS.md"; dest="docs/troubleshooting/SOLUCAO_DEFINITIVA_SENSORES_DUPLICADOS.md"},
    @{src="SOLUCAO_ERRO_400_CATEGORIA.md"; dest="docs/troubleshooting/SOLUCAO_ERRO_400_CATEGORIA.md"},
    @{src="SOLUCAO_ERRO_401_TOPDESK.md"; dest="docs/troubleshooting/SOLUCAO_ERRO_401_TOPDESK.md"},
    @{src="SOLUCAO_FINAL_BIBLIOTECA.md"; dest="docs/troubleshooting/SOLUCAO_FINAL_BIBLIOTECA.md"},
    @{src="SOLUCAO_FINAL_COMPLETA.md"; dest="docs/troubleshooting/SOLUCAO_FINAL_COMPLETA.md"},
    @{src="SOLUCAO_FINAL_NOTIFICACOES.md"; dest="docs/troubleshooting/SOLUCAO_FINAL_NOTIFICACOES.md"},
    @{src="SOLUCAO_FINAL_PROBE_INCIDENTES.md"; dest="docs/troubleshooting/SOLUCAO_FINAL_PROBE_INCIDENTES.md"},
    @{src="SOLUCAO_FINAL_SERVICOS.md"; dest="docs/troubleshooting/SOLUCAO_FINAL_SERVICOS.md"},
    @{src="SOLUCAO_FRONTEND_ATUALIZADO.md"; dest="docs/troubleshooting/SOLUCAO_FRONTEND_ATUALIZADO.md"},
    @{src="SOLUCAO_INTERFACE_RESETADA.md"; dest="docs/troubleshooting/SOLUCAO_INTERFACE_RESETADA.md"},
    @{src="SOLUCAO_NOC_ZERADO_FINAL.md"; dest="docs/troubleshooting/SOLUCAO_NOC_ZERADO_FINAL.md"},
    @{src="SOLUCAO_PROBE_401_UNAUTHORIZED.md"; dest="docs/troubleshooting/SOLUCAO_PROBE_401_UNAUTHORIZED.md"},
    @{src="SOLUCAO_PSYCOPG2.md"; dest="docs/troubleshooting/SOLUCAO_PSYCOPG2.md"},
    @{src="SOLUCAO_SENSORES_SNMP_REMOTO.md"; dest="docs/troubleshooting/SOLUCAO_SENSORES_SNMP_REMOTO.md"},
    @{src="SOLUCAO_TENANT_ERRADO.md"; dest="docs/troubleshooting/SOLUCAO_TENANT_ERRADO.md"},
    @{src="SOLUCAO_URGENTE_INSTALADOR.md"; dest="docs/troubleshooting/SOLUCAO_URGENTE_INSTALADOR.md"},
    @{src="DIAGNOSTICO_REMOTO.md"; dest="docs/troubleshooting/DIAGNOSTICO_REMOTO.md"},
    @{src="DIAGNOSTICO_SENSOR_DOCKER.md"; dest="docs/troubleshooting/DIAGNOSTICO_SENSOR_DOCKER.md"},
    @{src="INSTALADOR_FECHA_MESMO_ADMIN.md"; dest="docs/troubleshooting/INSTALADOR_FECHA_MESMO_ADMIN.md"},
    @{src="INSTALADOR_FECHOU_JANELA.md"; dest="docs/troubleshooting/INSTALADOR_FECHOU_JANELA.md"},
    @{src="RESOLVER_BANCO_DADOS.md"; dest="docs/troubleshooting/RESOLVER_BANCO_DADOS.md"},
    @{src="RESTAURAR_INTERFACE.md"; dest="docs/troubleshooting/RESTAURAR_INTERFACE.md"}
)

foreach ($item in $solucoes) {
    Move-GitFile -Source $item.src -Destination $item.dest | Out-Null
}

Write-Host ""
Write-Host "Movendo arquivos TEMPORÁRIOS para changelog/04MAR..." -ForegroundColor Yellow
Write-Host ""

# Arquivos temporários e de organização
$temporarios = @(
    @{src="NOVA_ESTRUTURA_REPOSITORIO.md"; dest="docs/changelog/04MAR/NOVA_ESTRUTURA_REPOSITORIO.md"},
    @{src="ORGANIZACAO_CONCLUIDA_04MAR.md"; dest="docs/changelog/04MAR/ORGANIZACAO_CONCLUIDA_04MAR.md"},
    @{src="EXECUTAR_ORGANIZACAO_AGORA.md"; dest="docs/changelog/04MAR/EXECUTAR_ORGANIZACAO_AGORA.md"},
    @{src="ATUALIZACAO_GIT_LAYOUT_COMPACTO_04MAR.md"; dest="docs/changelog/04MAR/ATUALIZACAO_GIT_LAYOUT_COMPACTO_04MAR.md"},
    @{src="INSTRUCOES_TESTE_CARDS_04MAR.md"; dest="docs/changelog/04MAR/INSTRUCOES_TESTE_CARDS_04MAR.md"},
    @{src="SOLUCAO_DEFINITIVA_CARDS_04MAR.md"; dest="docs/changelog/04MAR/SOLUCAO_DEFINITIVA_CARDS_04MAR.md"},
    @{src="RESUMO_SCREENSHOTS_04MAR.md"; dest="docs/changelog/04MAR/RESUMO_SCREENSHOTS_04MAR.md"}
)

foreach ($item in $temporarios) {
    Move-GitFile -Source $item.src -Destination $item.dest | Out-Null
}

Write-Host ""
Write-Host "Criando README.md nas novas pastas..." -ForegroundColor Yellow
Write-Host ""

# Criar READMEs
$readmes = @{
    "docs/tutorials/README.md" = @"
# 📚 Tutoriais

Tutoriais práticos e guias visuais para usar o Coruja Monitor.

## 🚀 Início Rápido

- [LEIA_ISTO_PRIMEIRO.md](LEIA_ISTO_PRIMEIRO.md) - Comece aqui!
- [COMO_INSTALAR_NOVA_PROBE.md](COMO_INSTALAR_NOVA_PROBE.md) - Instalação passo a passo

## 🎨 Guias Visuais

- [GUIA_VISUAL_LOGO_CORUJA.md](GUIA_VISUAL_LOGO_CORUJA.md) - Configurar logo
- [GUIA_VISUAL_RECONHECIMENTO.md](GUIA_VISUAL_RECONHECIMENTO.md) - Sistema de reconhecimento
- [WMI_COMPARACAO_VISUAL.md](WMI_COMPARACAO_VISUAL.md) - WMI local vs remoto

## 🔧 Configuração

- [CONFIGURAR_LOGO_CORUJA.md](CONFIGURAR_LOGO_CORUJA.md) - Personalizar logo
- [GUIA_URL_PROBE.md](GUIA_URL_PROBE.md) - Configurar URL da probe
- [GUIA_RAPIDO_AUTO_START.md](GUIA_RAPIDO_AUTO_START.md) - Auto-start da probe
- [GUIA_RAPIDO_GRUPOS.md](GUIA_RAPIDO_GRUPOS.md) - Grupos de sensores

## 🔄 Manutenção

- [GUIA_ATUALIZACAO_SONDA.md](GUIA_ATUALIZACAO_SONDA.md) - Atualizar probe
- [GUIA_DESINSTALACAO.md](GUIA_DESINSTALACAO.md) - Desinstalar probe
- [GUIA_REINSTALACAO_LIMPA.md](GUIA_REINSTALACAO_LIMPA.md) - Reinstalação limpa

## 🤖 AIOps

- [EXEMPLOS_PRATICOS_AIOPS.md](EXEMPLOS_PRATICOS_AIOPS.md) - Exemplos práticos
- [INSTALAR_OLLAMA_WINDOWS.md](INSTALAR_OLLAMA_WINDOWS.md) - Instalar Ollama

## 📋 Comandos Rápidos

- [COMANDOS_RAPIDOS.md](COMANDOS_RAPIDOS.md) - Comandos úteis
- [COMANDOS_DOCKER_CORRETOS.md](COMANDOS_DOCKER_CORRETOS.md) - Comandos Docker
- [COMANDOS_TOPDESK.md](COMANDOS_TOPDESK.md) - Comandos TOPdesk
"@

    "docs/implementation/README.md" = @"
# 🔨 Implementações

Documentação de funcionalidades implementadas no sistema.

## 🤖 AIOps e IA

- [AIOPS_IMPLEMENTADO.md](AIOPS_IMPLEMENTADO.md)
- [AUTO_REMEDIACAO_IMPLEMENTADA.md](AUTO_REMEDIACAO_IMPLEMENTADA.md)
- [KNOWLEDGE_BASE_IMPLEMENTADO_COMPLETO.md](KNOWLEDGE_BASE_IMPLEMENTADO_COMPLETO.md)
- [INTERFACE_AIOPS_IMPLEMENTADA.md](INTERFACE_AIOPS_IMPLEMENTADA.md)

## 📊 Dashboard e Interface

- [IMPLEMENTACAO_DASHBOARD_NOC_AIOPS.md](IMPLEMENTACAO_DASHBOARD_NOC_AIOPS.md)
- [TEMA_MODERNO_IMPLEMENTADO.md](TEMA_MODERNO_IMPLEMENTADO.md)
- [MODERNIZACAO_IMPLEMENTADA.md](MODERNIZACAO_IMPLEMENTADA.md)
- [NAVEGACAO_SENSOR_IMPLEMENTADA.md](NAVEGACAO_SENSOR_IMPLEMENTADA.md)

## 🔍 Monitoramento

- [IMPLEMENTACAO_NOC_SNMP_COMPLETA.md](IMPLEMENTACAO_NOC_SNMP_COMPLETA.md)
- [DESCOBERTA_SERVICOS_TEMPO_REAL.md](DESCOBERTA_SERVICOS_TEMPO_REAL.md)
- [SENSOR_DOCKER_IMPLEMENTADO.md](SENSOR_DOCKER_IMPLEMENTADO.md)
- [MONITORAMENTO_ATIVOS_REDE_IMPLEMENTADO.md](MONITORAMENTO_ATIVOS_REDE_IMPLEMENTADO.md)

## 📚 Biblioteca e Sensores

- [BIBLIOTECA_SENSORES_IMPLEMENTADA.md](BIBLIOTECA_SENSORES_IMPLEMENTADA.md)
- [IMPLEMENTACAO_AGRUPAMENTO_SENSORES.md](IMPLEMENTACAO_AGRUPAMENTO_SENSORES.md)
- [SISTEMA_GRUPOS_HIERARQUICOS_IMPLEMENTADO.md](SISTEMA_GRUPOS_HIERARQUICOS_IMPLEMENTADO.md)

## 🎫 Incidentes e Notificações

- [INCIDENTES_IMPLEMENTADO.md](INCIDENTES_IMPLEMENTADO.md)
- [NOTIFICACOES_AUTOMATICAS_IMPLEMENTADAS.md](NOTIFICACOES_AUTOMATICAS_IMPLEMENTADAS.md)
- [NOTIFICACAO_EMAIL_IMPLEMENTADA.md](NOTIFICACAO_EMAIL_IMPLEMENTADA.md)
- [JANELAS_MANUTENCAO_IMPLEMENTADO.md](JANELAS_MANUTENCAO_IMPLEMENTADO.md)

## 📊 Relatórios

- [RELATORIOS_PERSONALIZADOS_IMPLEMENTADO.md](RELATORIOS_PERSONALIZADOS_IMPLEMENTADO.md)

## ⚙️ Configurações

- [CONFIGURACOES_IMPLEMENTADAS.md](CONFIGURACOES_IMPLEMENTADAS.md)
- [THRESHOLDS_TEMPORAIS_IMPLEMENTADO.md](THRESHOLDS_TEMPORAIS_IMPLEMENTADO.md)
- [SISTEMA_RECONHECIMENTO_IMPLEMENTADO.md](SISTEMA_RECONHECIMENTO_IMPLEMENTADO.md)

## 🔧 Ferramentas

- [FERRAMENTAS_ADMIN_IMPLEMENTADAS.md](FERRAMENTAS_ADMIN_IMPLEMENTADAS.md)
- [TESTE_CONEXAO_IMPLEMENTADO.md](TESTE_CONEXAO_IMPLEMENTADO.md)

## 📦 Instaladores

- [INSTALADORES_MSI_CRIADOS.md](INSTALADORES_MSI_CRIADOS.md)
- [PROBE_AUTO_START_IMPLEMENTADO.md](PROBE_AUTO_START_IMPLEMENTADO.md)

## 🎨 Visual

- [LOGO_E_TIMEZONE_IMPLEMENTADOS.md](LOGO_E_TIMEZONE_IMPLEMENTADOS.md)
"@

    "docs/reference/README.md" = @"
# 📖 Referências

Documentação de referência, índices e bases de conhecimento.

## 📑 Índices

- [INDICE_INSTALADORES.md](INDICE_INSTALADORES.md) - Todos os instaladores
- [INDICE_INSTALADORES_ATUALIZADO.md](INDICE_INSTALADORES_ATUALIZADO.md) - Versão atualizada
- [INDICE_BIBLIOTECA_SENSORES.md](INDICE_BIBLIOTECA_SENSORES.md) - Biblioteca de sensores
- [INDICE_DOCUMENTACAO_AIOPS.md](INDICE_DOCUMENTACAO_AIOPS.md) - Documentação AIOps

## 📚 Base de Conhecimento

- [BASE_CONHECIMENTO_32_ITENS.md](BASE_CONHECIMENTO_32_ITENS.md) - 32 soluções
- [BASE_CONHECIMENTO_80_ITENS_COMPLETA.md](BASE_CONHECIMENTO_80_ITENS_COMPLETA.md) - 80 soluções

## 🔌 Integrações

- [INTEGRACOES_TOPDESK_GLPI.md](INTEGRACOES_TOPDESK_GLPI.md) - TOPdesk e GLPI

## 📊 Funcionalidades

- [NOVAS_FUNCIONALIDADES.md](NOVAS_FUNCIONALIDADES.md) - Novas features
- [RELATORIOS_EXECUTIVOS.md](RELATORIOS_EXECUTIVOS.md) - Relatórios
- [RELATORIOS_PERSONALIZADOS_DESIGN.md](RELATORIOS_PERSONALIZADOS_DESIGN.md) - Design de relatórios

## 🎨 Design

- [AGRUPAMENTO_SENSORES_DESIGN.md](AGRUPAMENTO_SENSORES_DESIGN.md) - Design de agrupamento
- [TEMPLATES_EXPANDIDOS.md](TEMPLATES_EXPANDIDOS.md) - Templates de sensores

## 📋 Planejamento

- [PLANO_MODERNIZACAO_SISTEMA.md](PLANO_MODERNIZACAO_SISTEMA.md) - Plano de modernização
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Resumo do projeto
"@
}

foreach ($path in $readmes.Keys) {
    $content = $readmes[$path]
    Set-Content -Path $path -Value $content -Encoding UTF8
    Write-Host "[CRIADO]" -ForegroundColor Green -NoNewline
    Write-Host " $path"
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CONCLUÍDO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Próximos passos:" -ForegroundColor Yellow
Write-Host "1. git status"
Write-Host "2. git commit -m 'docs: Adiciona pasta tutorials e organiza arquivos restantes'"
Write-Host "3. git push origin master"
Write-Host ""
