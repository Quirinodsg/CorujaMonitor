# 📁 NOVA ESTRUTURA DO REPOSITÓRIO

**Data:** 04 de Março de 2026  
**Objetivo:** Organizar arquivos para manter o Git limpo e profissional

---

## 🎯 Problema Atual

O repositório tem **300+ arquivos markdown** na raiz, tornando difícil:
- Encontrar documentação específica
- Navegar pelo projeto
- Manter organização
- Apresentar profissionalmente

---

## ✅ Solução: Nova Estrutura

### Estrutura Proposta

```
CorujaMonitor/
├── 📁 docs/
│   ├── 📁 guides/              # Guias de instalação e uso
│   │   ├── README.md
│   │   ├── LEIA_PRIMEIRO.md
│   │   ├── INICIO_RAPIDO.md
│   │   ├── GUIA_RAPIDO_INSTALACAO.md
│   │   ├── GUIA_INSTALADOR_UNIVERSAL.md
│   │   ├── GUIA_INSTALADOR_DOMINIO.md
│   │   ├── GUIA_ENTRA_ID_AZURE_AD.md
│   │   ├── GUIA_MONITORAMENTO_SEM_DOMINIO.md
│   │   ├── GUIA_MONITORAMENTO_AGENTLESS_COMPLETO.md
│   │   ├── GUIA_INSTALADOR_MSI.md
│   │   ├── GUIA_CONFIGURAR_TEAMS.md
│   │   ├── GUIA_COMPLETO_KUBERNETES.md
│   │   ├── GUIA_RAPIDO_KUBERNETES.md
│   │   ├── GUIA_RAPIDO_AIOPS.md
│   │   ├── GUIA_COMMIT_GITHUB.md
│   │   └── PASSO_A_PASSO_NOVA_EMPRESA.md
│   │
│   ├── 📁 architecture/        # Arquitetura e design
│   │   ├── README.md
│   │   ├── ARQUITETURA_COMPLETA.md
│   │   ├── ARQUITETURA_SENSORES_PROBE.md
│   │   ├── ARQUITETURA_PRTG_AGENTLESS.md
│   │   ├── AIOPS_IA_HIBRIDA_EXPLICADA.md
│   │   ├── AIOPS_AUTOMATICO_EXPLICADO.md
│   │   ├── DESIGN_GRAFANA_STYLE_DASHBOARD.md
│   │   ├── DESIGN_GRUPOS_AZURE_COMPLETO.md
│   │   ├── ROADMAP_ENTERPRISE.md
│   │   └── ROADMAP_ENTERPRISE_DETALHADO.md
│   │
│   ├── 📁 troubleshooting/     # Solução de problemas
│   │   ├── README.md
│   │   ├── SOLUCAO_RAPIDA.md
│   │   ├── SOLUCAO_SENSORES_DESCONHECIDOS.md
│   │   ├── SOLUCAO_ERRO_INSTALACAO.md
│   │   ├── DIAGNOSTICO_COMPLETO.md
│   │   └── PROBLEMA_URL_PROBE.md
│   │
│   ├── 📁 changelog/           # Histórico por data
│   │   ├── README.md
│   │   ├── 20FEV/              # 20 de Fevereiro
│   │   ├── 24FEV/              # 24 de Fevereiro
│   │   ├── 25FEV/              # 25 de Fevereiro
│   │   ├── 26FEV/              # 26 de Fevereiro
│   │   ├── 27FEV/              # 27 de Fevereiro
│   │   ├── 28FEV/              # 28 de Fevereiro
│   │   ├── 02MAR/              # 02 de Março
│   │   ├── 03MAR/              # 03 de Março
│   │   └── 04MAR/              # 04 de Março
│   │
│   ├── 📁 screenshots/         # Screenshots do sistema
│   │   ├── README.md
│   │   ├── ADICIONAR_SCREENSHOTS_GIT.md
│   │   ├── STATUS_SCREENSHOTS.md
│   │   ├── CAPTURAR_SCREENSHOTS_AGORA.md
│   │   ├── dashboard.png       # (a adicionar)
│   │   ├── noc.png             # (a adicionar)
│   │   ├── metrics.png         # (a adicionar)
│   │   └── aiops.png           # (a adicionar)
│   │
│   ├── LGPD_COMPLIANCE.md
│   ├── ISO27001_COMPLIANCE.md
│   ├── aiops-system.md
│   ├── integracoes-service-desk.md
│   ├── wmi-remote-monitoring.md
│   └── snmp-sensors-oids.md
│
├── 📁 scripts/
│   ├── README.md
│   ├── 📁 maintenance/         # Scripts de manutenção
│   │   ├── limpar_cache_completo.ps1
│   │   ├── reiniciar_probe.ps1
│   │   ├── popular_base_conhecimento.ps1
│   │   └── ...
│   │
│   ├── 📁 deployment/          # Scripts de deploy
│   │   ├── aplicar_layout_compacto.ps1
│   │   ├── aplicar_correcoes_finais.ps1
│   │   ├── rebuild_frontend_completo.ps1
│   │   └── ...
│   │
│   └── 📁 testing/             # Scripts de teste
│       ├── verificar_screenshots.ps1
│       ├── testar_aiops_completo.ps1
│       ├── verificar_status_completo.ps1
│       └── ...
│
├── 📁 api/                     # Backend (já organizado)
├── 📁 frontend/                # Frontend (já organizado)
├── 📁 probe/                   # Probe (já organizado)
├── 📁 ai-agent/                # AI Agent (já organizado)
├── 📁 worker/                  # Worker (já organizado)
├── 📁 installer/               # Instaladores (já organizado)
│
├── README.md                   # README principal
├── CONTRIBUTING.md             # Guia de contribuição
├── LICENSE                     # Licença
├── .gitignore                  # Git ignore
├── docker-compose.yml          # Docker compose
└── .env.example                # Exemplo de configuração
```

---

## 📊 Benefícios

### Antes (Atual)
```
CorujaMonitor/
├── 300+ arquivos .md na raiz
├── 50+ scripts .ps1 na raiz
├── Difícil de navegar
└── Desorganizado
```

### Depois (Proposto)
```
CorujaMonitor/
├── docs/
│   ├── guides/ (15 arquivos)
│   ├── architecture/ (9 arquivos)
│   ├── troubleshooting/ (5 arquivos)
│   ├── changelog/ (por data)
│   └── screenshots/
├── scripts/
│   ├── maintenance/
│   ├── deployment/
│   └── testing/
├── README.md (limpo e profissional)
└── Fácil de navegar
```

---

## 🚀 Como Aplicar

### Opção 1: Automática (Recomendado)

```powershell
# Execute o script de organização
.\organizar_repositorio.ps1

# Revise as mudanças
git status

# Commit
git commit -m "docs: Reorganiza estrutura do repositório"

# Push
git push origin master
```

### Opção 2: Manual

```powershell
# Criar pastas
mkdir docs\guides
mkdir docs\architecture
mkdir docs\troubleshooting
mkdir docs\changelog
mkdir scripts\maintenance
mkdir scripts\deployment
mkdir scripts\testing

# Mover arquivos (exemplo)
git mv GUIA_RAPIDO_INSTALACAO.md docs/guides/
git mv ARQUITETURA_COMPLETA.md docs/architecture/
git mv SOLUCAO_RAPIDA.md docs/troubleshooting/

# Commit
git commit -m "docs: Reorganiza estrutura do repositório"

# Push
git push origin master
```

---

## 📋 Categorização de Arquivos

### docs/guides/
**Critério:** Guias de instalação, configuração e uso
- Todos os GUIA_*.md
- LEIA_PRIMEIRO.md
- INICIO_RAPIDO.md
- PASSO_A_PASSO_*.md

### docs/architecture/
**Critério:** Arquitetura, design e roadmap
- ARQUITETURA_*.md
- DESIGN_*.md
- ROADMAP_*.md
- AIOPS_*_EXPLICADA.md

### docs/troubleshooting/
**Critério:** Solução de problemas e diagnóstico
- SOLUCAO_*.md
- DIAGNOSTICO_*.md
- PROBLEMA_*.md

### docs/changelog/
**Critério:** Histórico de mudanças por data
- *_20FEV.md → changelog/20FEV/
- *_24FEV.md → changelog/24FEV/
- *_25FEV.md → changelog/25FEV/
- *_26FEV.md → changelog/26FEV/
- *_27FEV.md → changelog/27FEV/
- *_28FEV.md → changelog/28FEV/
- *_02MAR.md → changelog/02MAR/
- *_03MAR.md → changelog/03MAR/
- *_04MAR.md → changelog/04MAR/

### scripts/maintenance/
**Critério:** Scripts de manutenção e utilitários
- limpar_*.ps1
- reiniciar_*.ps1
- popular_*.ps1
- configurar_*.ps1

### scripts/deployment/
**Critério:** Scripts de deploy e aplicação
- aplicar_*.ps1
- rebuild_*.ps1
- atualizar_*.ps1
- corrigir_*.ps1

### scripts/testing/
**Critério:** Scripts de teste e verificação
- testar_*.ps1
- verificar_*.ps1
- validar_*.ps1

---

## 🔍 Navegação Rápida

### Quero instalar o sistema
```
docs/guides/LEIA_PRIMEIRO.md
docs/guides/GUIA_RAPIDO_INSTALACAO.md
```

### Quero entender a arquitetura
```
docs/architecture/ARQUITETURA_COMPLETA.md
docs/architecture/AIOPS_IA_HIBRIDA_EXPLICADA.md
```

### Tenho um problema
```
docs/troubleshooting/SOLUCAO_RAPIDA.md
docs/troubleshooting/DIAGNOSTICO_COMPLETO.md
```

### Quero ver o histórico
```
docs/changelog/04MAR/
docs/changelog/03MAR/
```

### Quero executar um script
```
scripts/testing/verificar_status_completo.ps1
scripts/deployment/aplicar_correcoes_finais.ps1
```

---

## 📝 Atualização do README.md

O README.md principal será atualizado com links para a nova estrutura:

```markdown
## 📚 Documentação

### Guias
- [Guia Rápido de Instalação](docs/guides/GUIA_RAPIDO_INSTALACAO.md)
- [Passo a Passo Nova Empresa](docs/guides/PASSO_A_PASSO_NOVA_EMPRESA.md)
- [Todos os Guias](docs/guides/)

### Arquitetura
- [Arquitetura Completa](docs/architecture/ARQUITETURA_COMPLETA.md)
- [AIOps IA Híbrida](docs/architecture/AIOPS_IA_HIBRIDA_EXPLICADA.md)
- [Toda a Arquitetura](docs/architecture/)

### Troubleshooting
- [Solução Rápida](docs/troubleshooting/SOLUCAO_RAPIDA.md)
- [Diagnóstico Completo](docs/troubleshooting/DIAGNOSTICO_COMPLETO.md)
- [Todos os Problemas](docs/troubleshooting/)

### Histórico
- [Changelog](docs/changelog/)
```

---

## ⚠️ Importante

### O Que NÃO Será Movido

Arquivos que permanecem na raiz:
- README.md (principal)
- CONTRIBUTING.md
- LICENSE
- .gitignore
- .env.example
- docker-compose.yml
- organizar_repositorio.ps1 (temporário)
- verificar_screenshots.ps1 (útil na raiz)

### Compatibilidade

Links internos nos arquivos markdown serão mantidos funcionais porque:
- Git preserva histórico
- Links relativos continuam funcionando
- GitHub atualiza automaticamente

---

## 🎯 Resultado Final

### Raiz Limpa
```
CorujaMonitor/
├── docs/           # Toda documentação
├── scripts/        # Todos os scripts
├── api/            # Backend
├── frontend/       # Frontend
├── probe/          # Probe
├── ai-agent/       # AI Agent
├── worker/         # Worker
├── installer/      # Instaladores
├── README.md       # README principal
├── CONTRIBUTING.md
├── LICENSE
└── docker-compose.yml
```

### Profissional e Organizado
- ✅ Fácil de navegar
- ✅ Estrutura clara
- ✅ Documentação categorizada
- ✅ Scripts organizados
- ✅ Histórico preservado
- ✅ Links funcionando
- ✅ GitHub bonito

---

## 📞 Próximos Passos

1. **Revisar** este documento
2. **Executar** `organizar_repositorio.ps1`
3. **Verificar** com `git status`
4. **Commit** das mudanças
5. **Push** para GitHub
6. **Verificar** no GitHub se ficou bonito

---

**Tempo estimado:** 5 minutos  
**Impacto:** Alto (organização profissional)  
**Risco:** Baixo (Git preserva histórico)

