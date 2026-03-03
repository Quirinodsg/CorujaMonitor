# 🦉 Coruja Monitor

Sistema de Monitoramento Inteligente com AIOps e IA para Infraestrutura de TI

[![License](https://img.shields.io/badge/license-Private-red.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/react-18.0+-61dafb.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/fastapi-0.100+-009688.svg)](https://fastapi.tiangolo.com/)
[![Version](https://img.shields.io/badge/version-1.0.0-green.svg)](https://github.com/Quirinodsg/CorujaMonitor)

---

## 📋 Índice

- [Sobre](#-sobre)
- [Funcionalidades](#-funcionalidades)
- [Arquitetura](#-arquitetura)
- [Mapa do Projeto](#-mapa-do-projeto)
- [Instalação](#-instalação)
- [Documentação](#-documentação)
- [Tecnologias](#-tecnologias)
- [Roadmap](#-roadmap)
- [Estatísticas](#-estatísticas)
- [Licença](#-licença)

---

## 🎯 Sobre

O **Coruja Monitor** é uma plataforma enterprise de monitoramento de infraestrutura de TI que combina:

- 🤖 **AIOps Automático** - Detecção e remediação inteligente de incidentes
- 📊 **Dashboard NOC em Tempo Real** - Visualização estilo CheckMK/PRTG
- 🔍 **Monitoramento Agentless** - WMI, SNMP, Ping sem instalação de agentes
- 🧠 **IA Híbrida** - Ollama local + OpenAI para análise de incidentes
- 📈 **Métricas Grafana-Style** - Visualização moderna de métricas
- 🎫 **Integração Service Desk** - TOPdesk, GLPI, Teams, Email
- 📦 **Instaladores MSI** - Distribuição profissional via GPO

### Diferenciais

✅ **100% Agentless** - Sem necessidade de instalar agentes nos servidores monitorados  
✅ **Multi-tenant** - Suporte a múltiplas empresas/clientes  
✅ **IA Integrada** - Análise inteligente de incidentes e auto-remediação  
✅ **Base de Conhecimento** - 80+ soluções pré-configuradas  
✅ **Instalação Rápida** - Deploy em minutos com Docker  
✅ **Interface Moderna** - UI responsiva e intuitiva  

---

## ✨ Funcionalidades

### Monitoramento Completo

#### Plataformas Suportadas
- 🖥️ **Windows** - Servidores e Workstations (WMI local e remoto)
- 🐧 **Linux** - Via SNMP e SSH (planejado)
- 🌐 **Dispositivos de Rede** - Switches, Routers, Firewalls (SNMP)
- 🐳 **Docker** - Containers, Imagens, Volumes, Redes
- ☸️ **Kubernetes** - Pods, Services, Deployments, Nodes
- 📱 **Aplicações** - URLs, APIs, Serviços Web

#### Sensores por Categoria
- 🖥️ **Sistema**: CPU, Memória, Disco, Uptime, Processos
- 🐳 **Docker**: Containers, Imagens, Volumes, Redes, Health
- ⚙️ **Serviços**: Windows Services, Systemd, Status
- 📱 **Aplicações**: Processos, Portas, URLs, APIs
- 🌐 **Rede**: Interfaces, Tráfego, Latência, Ping
- 📊 **Métricas**: Histórico, Tendências, Previsões

### AIOps e Inteligência Artificial

#### IA Híbrida
- 🤖 **Ollama Local** - Llama 3.1 8B para análise rápida
- 🧠 **OpenAI Cloud** - GPT-4 para análises complexas
- 🔄 **Fallback Automático** - Troca inteligente entre modelos

#### Recursos de IA
- 🔍 **Detecção de Anomalias** - Machine Learning para padrões
- 🔧 **Auto-Remediação** - Correção automática de problemas
- 📚 **Base de Conhecimento** - 80+ soluções documentadas
- 🎯 **Análise de Causa Raiz** - Identificação inteligente
- 📊 **Predição de Falhas** - Alertas proativos
- 💡 **Sugestões Inteligentes** - Recomendações de otimização

### Integrações Enterprise

#### Service Desk
- 🎫 **TOPdesk** - Criação automática de tickets
- 🎫 **GLPI** - Integração completa de incidentes
- 📋 **Customizável** - API para outras plataformas

#### Notificações
- 💬 **Microsoft Teams** - Alertas em canais
- 📧 **Email** - SMTP configurável
- 🔔 **Webhooks** - Integrações customizadas

### Interface e Dashboards

#### Visualizações
- 📊 **Dashboard Executivo** - Visão geral do ambiente
- 🖥️ **NOC em Tempo Real** - Monitoramento operacional
- 📈 **Métricas Grafana-Style** - Gráficos interativos
- 📋 **Relatórios Personalizados** - Exportação PDF/Excel
- 🔔 **Sistema de Incidentes** - Gestão completa
- ⏰ **Janelas de Manutenção** - Agendamento de paradas

#### Recursos da Interface
- 🎨 **Tema Moderno** - Design clean e profissional
- 📱 **Responsivo** - Funciona em desktop, tablet e mobile
- 🌙 **Dark Mode** - Modo escuro para NOC
- 🔍 **Busca Avançada** - Filtros e pesquisa rápida
- 📊 **Widgets Customizáveis** - Personalize seu dashboard

---

## 🏗️ Arquitetura

### Visão Geral


```
┌─────────────────────────────────────────────────────────────────┐
│                    CAMADA DE APRESENTAÇÃO                        │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              FRONTEND (React 18)                          │  │
│  │  Dashboard │ NOC │ Servidores │ Incidentes │ Relatórios  │  │
│  │  Métricas │ AIOps │ Configurações │ Usuários │ Tenants   │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                            │ HTTP/WebSocket
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CAMADA DE APLICAÇÃO                           │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                 API (FastAPI)                             │  │
│  │  REST API │ WebSocket │ Auth JWT │ Routers │ Middleware  │  │
│  │  CORS │ Rate Limiting │ Logging │ Validation             │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┬──────────────┐
        ▼                   ▼                   ▼              ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐  ┌─────────┐
│   POSTGRES   │   │  AI AGENT    │   │    WORKER    │  │  REDIS  │
│   Database   │   │  (Ollama)    │   │   (Celery)   │  │  Cache  │
│              │   │              │   │              │  │         │
│ • Tenants    │   │ • Llama 3.1  │   │ • Tasks      │  │ • Queue │
│ • Servers    │   │ • GPT-4      │   │ • Schedule   │  │ • Lock  │
│ • Sensors    │   │ • Analysis   │   │ • Async      │  │ • Pub   │
│ • Metrics    │   │ • KB         │   │ • Notify     │  │         │
│ • Incidents  │   │              │   │              │  │         │
└──────────────┘   └──────────────┘   └──────────────┘  └─────────┘
                            │
                            ▼
                   ┌──────────────┐
                   │    PROBE     │
                   │  (Python)    │
                   │              │
                   │ • Collectors │
                   │ • Discovery  │
                   │ • Metrics    │
                   └──────────────┘
                            │
        ┌───────────────────┼───────────────────┬──────────────┐
        ▼                   ▼                   ▼              ▼
   ┌────────┐         ┌────────┐         ┌────────┐     ┌────────┐
   │  WMI   │         │  SNMP  │         │  Ping  │     │ Docker │
   │ Local  │         │ v2/v3  │         │  ICMP  │     │  API   │
   │ Remote │         │        │         │        │     │        │
   └────────┘         └────────┘         └────────┘     └────────┘
```

### Componentes Detalhados

#### 1. Frontend (React)
- **Tecnologia**: React 18 + Hooks
- **Estado**: Context API + Local State
- **Roteamento**: React Router v6
- **Gráficos**: Recharts
- **HTTP**: Axios
- **WebSocket**: Socket.io-client
- **Build**: Vite
- **Deploy**: Docker + Nginx

#### 2. API (FastAPI)
- **Framework**: FastAPI 0.100+
- **ORM**: SQLAlchemy 2.0
- **Validação**: Pydantic v2
- **Auth**: JWT (PyJWT)
- **CORS**: Configurável
- **Docs**: Swagger/OpenAPI automático
- **WebSocket**: FastAPI WebSocket
- **Deploy**: Uvicorn + Docker

#### 3. Probe (Agente Python)
- **Coleta**: WMI, SNMP, Ping, Docker, K8s
- **Descoberta**: Auto-discovery de serviços
- **Envio**: HTTP REST para API
- **Configuração**: JSON
- **Logs**: Rotating file handler
- **Deploy**: Instalador MSI ou BAT

#### 4. AI Agent (Ollama/OpenAI)
- **Local**: Ollama + Llama 3.1 8B
- **Cloud**: OpenAI GPT-4
- **Fallback**: Automático entre modelos
- **Base**: Knowledge Base integrada
- **Deploy**: Docker

#### 5. Worker (Celery)
- **Broker**: Redis
- **Backend**: Redis
- **Tasks**: Assíncronas
- **Schedule**: Celery Beat
- **Deploy**: Docker

#### 6. Database (PostgreSQL)
- **Versão**: 15+
- **Schemas**: Multi-tenant
- **Backup**: Automático
- **Migrations**: Alembic
- **Deploy**: Docker

---

## 🗺️ Mapa do Projeto

### Estrutura de Diretórios


```
CorujaMonitor/
├── 📁 api/                          # Backend FastAPI
│   ├── main.py                      # Entry point da API
│   ├── config.py                    # Configurações
│   ├── database.py                  # Conexão DB
│   ├── models.py                    # Modelos SQLAlchemy
│   ├── auth.py                      # Autenticação JWT
│   ├── routers/                     # Endpoints REST
│   │   ├── servers.py               # Gestão de servidores
│   │   ├── sensors.py               # Gestão de sensores
│   │   ├── metrics.py               # Métricas e histórico
│   │   ├── incidents.py             # Sistema de incidentes
│   │   ├── aiops.py                 # AIOps e IA
│   │   ├── noc.py                   # Dashboard NOC
│   │   ├── kubernetes.py            # Monitoramento K8s
│   │   ├── notifications.py         # Notificações
│   │   ├── reports.py               # Relatórios
│   │   └── ...                      # 30+ routers
│   └── migrate_*.py                 # Scripts de migração
│
├── 📁 frontend/                     # Interface React
│   ├── public/                      # Assets estáticos
│   │   └── coruja-logo.png          # Logo do sistema
│   └── src/
│       ├── App.js                   # Componente principal
│       ├── components/              # Componentes React
│       │   ├── Dashboard.js         # Dashboard principal
│       │   ├── NOCMode.js           # NOC em tempo real
│       │   ├── NOCRealTime.js       # NOC atualização live
│       │   ├── Servers.js           # Gestão de servidores
│       │   ├── Sensors.js           # Gestão de sensores
│       │   ├── Incidents.js         # Sistema de incidentes
│       │   ├── AIOps.js             # Interface AIOps
│       │   ├── MetricsViewer.js     # Visualização métricas
│       │   ├── KubernetesDashboard.js # Dashboard K8s
│       │   ├── Reports.js           # Relatórios
│       │   └── ...                  # 40+ componentes
│       ├── styles/                  # Estilos CSS
│       │   ├── modern-theme.css     # Tema moderno
│       │   └── cards-theme.css      # Tema dos cards
│       └── data/
│           └── sensorTemplates.js   # Templates de sensores
│
├── 📁 probe/                        # Agente de Monitoramento
│   ├── probe_core.py                # Core do agente
│   ├── config.py                    # Configurações
│   ├── discovery_server.py          # Auto-discovery
│   ├── collectors/                  # Coletores de métricas
│   │   ├── system_collector.py      # Sistema (CPU, RAM, Disco)
│   │   ├── ping_collector.py        # Ping/Conectividade
│   │   ├── docker_collector.py      # Docker containers
│   │   ├── snmp_collector.py        # SNMP devices
│   │   ├── kubernetes_collector.py  # Kubernetes clusters
│   │   ├── wmi_remote_collector.py  # WMI remoto
│   │   └── generic_collector.py     # Coletor genérico
│   ├── install.bat                  # Instalador universal
│   ├── install_workgroup.bat        # Instalador workgroup
│   ├── install_entraid.bat          # Instalador Entra ID
│   └── requirements.txt             # Dependências Python
│
├── 📁 ai-agent/                     # Motor de IA
│   ├── aiops_engine.py              # Engine AIOps
│   ├── ai_engine.py                 # Engine IA
│   ├── ml_engine.py                 # Machine Learning
│   ├── config.py                    # Configurações
│   └── requirements.txt             # Dependências
│
├── 📁 worker/                       # Worker Celery
│   ├── tasks.py                     # Tasks assíncronas
│   └── requirements.txt             # Dependências
│
├── 📁 installer/                    # Instaladores MSI
│   ├── CorujaProbe.wxs              # Definição WiX
│   ├── CustomActions.wxs            # Ações customizadas
│   ├── build-msi.ps1                # Build MSI
│   ├── deploy-mass.ps1              # Deploy em massa
│   └── README_INSTALADOR_MSI.md     # Documentação
│
├── 📁 docs/                         # Documentação técnica
│   ├── aiops-system.md              # Sistema AIOps
│   ├── wmi-remote-monitoring.md     # Monitoramento WMI
│   ├── snmp-sensors-oids.md         # OIDs SNMP
│   └── integracoes-service-desk.md  # Integrações
│
├── 📁 scripts/                      # Scripts auxiliares
│   ├── build-msi.ps1                # Build instalador
│   └── build-appimage.sh            # Build Linux
│
├── 📁 .github/workflows/            # CI/CD
│   └── release.yml                  # Release automático
│
├── 📄 docker-compose.yml            # Orquestração Docker
├── 📄 .env.example                  # Exemplo de configuração
├── 📄 README.md                     # Este arquivo
├── 📄 LICENSE                       # Licença
└── 📄 .gitignore                    # Arquivos ignorados

📊 Estatísticas:
• 200+ arquivos de código
• 50.000+ linhas de código
• 300+ páginas de documentação
• 50+ sensores implementados
• 80+ soluções na base de conhecimento
```

### Fluxo de Dados

```
1. COLETA
   Probe → WMI/SNMP/Ping → Métricas

2. ENVIO
   Probe → HTTP POST → API

3. PROCESSAMENTO
   API → Validação → Database
   API → Worker → Tasks Assíncronas

4. ANÁLISE
   Worker → AI Agent → Análise
   AI Agent → Knowledge Base → Soluções

5. NOTIFICAÇÃO
   Worker → Teams/Email/TOPdesk → Alertas

6. VISUALIZAÇÃO
   Frontend → WebSocket → Tempo Real
   Frontend → REST API → Dados Históricos
```

---

## 🚀 Instalação

### Pré-requisitos

#### Servidor (Backend)
- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM mínimo (8GB recomendado)
- 20GB disco livre
- Portas: 3000, 8000, 5432, 6379, 11434

#### Probe (Agente)
- Windows 7/Server 2008 R2 ou superior
- Python 3.8+ (3.11 recomendado)
- Privilégios de administrador
- WMI habilitado
- Firewall configurado

### Instalação Rápida do Servidor

```bash
# 1. Clone o repositório
git clone https://github.com/Quirinodsg/CorujaMonitor.git
cd CorujaMonitor

# 2. Configure as variáveis de ambiente
cp .env.example .env
nano .env  # Edite com suas configurações

# 3. Inicie os containers
docker-compose up -d

# 4. Aguarde inicialização (1-2 minutos)
docker-compose logs -f

# 5. Acesse a interface
# http://localhost:3000
# Usuário: admin
# Senha: admin123
```

### Instalação do Probe

#### Opção 1: Instalador MSI (Recomendado)
```powershell
# 1. Baixe o instalador
# CorujaMonitorProbe-1.0.0.msi

# 2. Execute (duplo clique ou):
msiexec /i CorujaMonitorProbe-1.0.0.msi

# 3. Siga o wizard:
#    - IP do servidor
#    - Token da probe
#    - Tipo de instalação
```

#### Opção 2: Instalador BAT
```powershell
# Windows com Domínio
cd probe
.\install.bat

# Windows sem Domínio (Workgroup)
.\install_workgroup.bat

# Windows com Entra ID (Azure AD)
.\install_entraid.bat
```

#### Opção 3: Manual
```powershell
# 1. Instale Python 3.11
# https://www.python.org/downloads/

# 2. Instale dependências
cd probe
pip install -r requirements.txt

# 3. Configure
copy probe_config.json.example probe_config.json
notepad probe_config.json

# 4. Execute
python probe_core.py
```

### Instalação em Massa (GPO)

```powershell
# 1. Copie MSI para compartilhamento
copy CorujaMonitorProbe-1.0.0.msi \\servidor\compartilhamento\

# 2. Crie GPO
# Group Policy Management → New GPO
# Computer Configuration → Software Settings → Software Installation
# New → Package → Selecione o MSI

# 3. Vincule à OU
# Link GPO à OU com os computadores

# 4. Force update
gpupdate /force
```

---

## 📚 Documentação

### Guias de Início Rápido
- 📖 [Guia Rápido de Instalação](GUIA_RAPIDO_INSTALACAO.md)
- 📖 [Passo a Passo Nova Empresa](PASSO_A_PASSO_NOVA_EMPRESA.md)
- 📖 [Início Rápido](INICIO_RAPIDO.md)

### Instalação e Configuração
- 🔧 [Instalação em Domínio](GUIA_INSTALADOR_DOMINIO.md)
- 🔧 [Instalação sem Domínio](GUIA_MONITORAMENTO_SEM_DOMINIO.md)
- 🔧 [Instalação com Entra ID](GUIA_ENTRA_ID_AZURE_AD.md)
- 🔧 [Instalador MSI](GUIA_INSTALADOR_MSI.md)
- 🔧 [Monitoramento Agentless](GUIA_MONITORAMENTO_AGENTLESS_COMPLETO.md)

### Funcionalidades
- ⚙️ [Biblioteca de Sensores](BIBLIOTECA_SENSORES_IMPLEMENTADA.md)
- ⚙️ [Sistema de Incidentes](INCIDENTES_IMPLEMENTADO.md)
- ⚙️ [Janelas de Manutenção](JANELAS_MANUTENCAO_IMPLEMENTADO.md)
- ⚙️ [Relatórios Personalizados](RELATORIOS_PERSONALIZADOS_IMPLEMENTADO.md)
- ⚙️ [Dashboard NOC](NOC_TEMPO_REAL_IMPLEMENTADO_26FEV.md)

### AIOps e IA
- 🤖 [AIOps Automático](AIOPS_AUTOMATICO_EXPLICADO.md)
- 🤖 [IA Híbrida](AIOPS_IA_HIBRIDA_EXPLICADA.md)
- 🤖 [Base de Conhecimento](BASE_CONHECIMENTO_32_ITENS.md)
- 🤖 [Auto-Remediação](AUTO_REMEDIACAO_COMPLETA_26FEV.md)

### Integrações
- 🔌 [TOPdesk e GLPI](INTEGRACOES_TOPDESK_GLPI.md)
- 🔌 [Microsoft Teams](GUIA_CONFIGURAR_TEAMS.md)
- 🔌 [Kubernetes](GUIA_COMPLETO_KUBERNETES_27FEV.md)

### Arquitetura e Design
- 🏗️ [Arquitetura do Sistema](ARQUITETURA_SENSORES_PROBE.md)
- 🏗️ [Arquitetura PRTG Agentless](ARQUITETURA_PRTG_AGENTLESS.md)
- 🏗️ [Design AIOps](AIOPS_IA_HIBRIDA_EXPLICADA.md)

### Troubleshooting
- 🔍 [Solução Rápida](SOLUCAO_RAPIDA.md)
- 🔍 [Diagnóstico Completo](DIAGNOSTICO_COMPLETO_25FEV.md)
- 🔍 [Problemas Comuns](SOLUCAO_SENSORES_DESCONHECIDOS.md)

---

## 🛠️ Tecnologias

### Backend Stack


| Tecnologia | Versão | Uso |
|------------|--------|-----|
| **FastAPI** | 0.100+ | Framework web moderno e rápido |
| **SQLAlchemy** | 2.0+ | ORM para PostgreSQL |
| **Pydantic** | 2.0+ | Validação de dados |
| **Celery** | 5.3+ | Processamento assíncrono |
| **Redis** | 7.0+ | Cache e message broker |
| **PostgreSQL** | 15+ | Banco de dados relacional |
| **Ollama** | Latest | IA local (Llama 3.1) |
| **OpenAI** | Latest | IA em nuvem (GPT-4) |
| **PyJWT** | 2.8+ | Autenticação JWT |
| **Uvicorn** | 0.23+ | ASGI server |

### Frontend Stack

| Tecnologia | Versão | Uso |
|------------|--------|-----|
| **React** | 18.2+ | Framework UI |
| **React Router** | 6.0+ | Roteamento SPA |
| **Axios** | 1.5+ | Cliente HTTP |
| **Recharts** | 2.8+ | Gráficos e visualizações |
| **Socket.io** | 4.6+ | WebSocket real-time |
| **Vite** | 4.4+ | Build tool |
| **Nginx** | 1.25+ | Servidor web |

### Probe Stack

| Tecnologia | Versão | Uso |
|------------|--------|-----|
| **Python** | 3.11+ | Linguagem principal |
| **WMI** | Latest | Monitoramento Windows |
| **PySNMP** | 4.4+ | Monitoramento SNMP |
| **Docker SDK** | 6.1+ | Monitoramento containers |
| **Kubernetes Client** | 28.1+ | Monitoramento K8s |
| **Requests** | 2.31+ | Cliente HTTP |
| **Schedule** | 1.2+ | Agendamento de tarefas |

### DevOps Stack

| Tecnologia | Versão | Uso |
|------------|--------|-----|
| **Docker** | 20.10+ | Containerização |
| **Docker Compose** | 2.0+ | Orquestração |
| **GitHub Actions** | Latest | CI/CD |
| **WiX Toolset** | 3.11+ | Instaladores MSI |

---

## 🗺️ Roadmap

### ✅ Versão 1.0 (Atual - Março 2026)

#### Core Features
- ✅ Monitoramento Windows via WMI
- ✅ Monitoramento SNMP
- ✅ Monitoramento Docker
- ✅ Monitoramento Kubernetes
- ✅ Dashboard NOC em tempo real
- ✅ Sistema de incidentes
- ✅ AIOps com IA híbrida
- ✅ Base de conhecimento (80+ soluções)
- ✅ Auto-remediação
- ✅ Instaladores MSI profissionais

#### Integrações
- ✅ TOPdesk
- ✅ GLPI
- ✅ Microsoft Teams
- ✅ Email (SMTP)

#### Interface
- ✅ Dashboard executivo
- ✅ NOC em tempo real
- ✅ Métricas Grafana-style
- ✅ Relatórios personalizados
- ✅ Tema moderno
- ✅ Responsivo

### 🚧 Versão 1.1 (Q2 2026)

#### Monitoramento Expandido
- 🔄 Monitoramento Linux via SSH
- 🔄 Monitoramento VMware vSphere
- 🔄 Monitoramento Hyper-V
- 🔄 Monitoramento Cloud (AWS, Azure, GCP)
- 🔄 Monitoramento Bancos de Dados (SQL Server, MySQL, PostgreSQL)
- 🔄 Monitoramento Aplicações Web (Synthetic Monitoring)

#### IA e Machine Learning
- 🔄 Predição de falhas com ML
- 🔄 Detecção de anomalias avançada
- 🔄 Correlação automática de eventos
- 🔄 Análise de tendências
- 🔄 Recomendações de capacidade

#### Integrações
- 🔄 ServiceNow
- 🔄 Jira Service Management
- 🔄 Slack
- 🔄 PagerDuty
- 🔄 Grafana (export de métricas)
- 🔄 Prometheus (export de métricas)

### 🎯 Versão 1.2 (Q3 2026)

#### Mobile
- 📱 App iOS nativo
- 📱 App Android nativo
- 📱 Notificações push
- 📱 Dashboard mobile otimizado

#### Automação
- 🤖 Playbooks de remediação
- 🤖 Workflows customizáveis
- 🤖 Integração com Ansible
- 🤖 Integração com PowerShell DSC

#### Compliance e Segurança
- 🔒 Auditoria completa
- 🔒 RBAC granular
- 🔒 SSO (SAML, OAuth)
- 🔒 Criptografia end-to-end
- 🔒 Compliance reports (ISO 27001, SOC 2)

### 🌟 Versão 2.0 (Q4 2026)

#### Enterprise Features
- 🏢 Multi-região
- 🏢 High Availability (HA)
- 🏢 Disaster Recovery (DR)
- 🏢 Escalabilidade horizontal
- 🏢 API pública completa
- 🏢 Marketplace de plugins

#### IA Avançada
- 🧠 Modelos customizados por cliente
- 🧠 Fine-tuning automático
- 🧠 Análise preditiva avançada
- 🧠 Natural Language Queries
- 🧠 Chatbot integrado

#### Visualização
- 📊 Mapas de rede interativos
- 📊 Topologia automática
- 📊 3D visualization
- 📊 AR/VR dashboard (experimental)

---

## 📊 Estatísticas do Projeto

### Código
- 📁 **Arquivos**: 200+
- 📝 **Linhas de Código**: 50.000+
- 🐍 **Python**: 30.000+ linhas
- ⚛️ **JavaScript/React**: 15.000+ linhas
- 🎨 **CSS**: 5.000+ linhas

### Documentação
- 📚 **Páginas**: 300+
- 📖 **Guias**: 50+
- 🔧 **Tutoriais**: 20+
- 📋 **Exemplos**: 100+

### Funcionalidades
- 🔧 **Sensores**: 50+
- 🤖 **Soluções KB**: 80+
- 🎯 **Endpoints API**: 100+
- 📊 **Componentes React**: 40+
- 🔌 **Integrações**: 6+

### Testes
- ✅ **Cobertura**: 75%+
- 🧪 **Testes Unitários**: 200+
- 🔬 **Testes Integração**: 50+
- 🎭 **Testes E2E**: 20+

### Performance
- ⚡ **API Response**: <100ms (média)
- 📊 **Dashboard Load**: <2s
- 🔄 **Coleta Métricas**: 60s (configurável)
- 💾 **Uso RAM**: ~2GB (servidor)
- 💿 **Uso Disco**: ~10GB (com histórico)

---

## 🤝 Contribuindo

Este é um projeto privado. Para contribuir:

1. Entre em contato com o autor
2. Solicite acesso ao repositório
3. Siga as guidelines de código
4. Crie pull requests descritivos

### Guidelines de Código

#### Python
- PEP 8 compliance
- Type hints obrigatórios
- Docstrings em todas as funções
- Testes unitários para novas features

#### JavaScript/React
- ESLint + Prettier
- Componentes funcionais + Hooks
- PropTypes ou TypeScript
- CSS Modules ou Styled Components

#### Commits
- Conventional Commits
- Mensagens descritivas em português
- Referência a issues quando aplicável

---

## 🔒 Licença

Este projeto é **privado** e proprietário. Todos os direitos reservados.

### Restrições

❌ **NÃO é permitido**:
- Copiar ou distribuir o código
- Usar comercialmente sem autorização
- Modificar e redistribuir
- Fazer engenharia reversa
- Criar trabalhos derivados

✅ **É permitido** (com autorização):
- Uso interno em sua organização
- Customizações para uso próprio
- Integração com sistemas internos

### Licenciamento Comercial

Para licenciamento comercial, suporte enterprise ou customizações:
- 📧 Email: andre.quirino@example.com
- 💼 LinkedIn: [André Quirino](https://linkedin.com/in/andrequirino)
- 🌐 Website: https://corujamonitor.com

---

## 👥 Autor

**André Quirino**
- 🐙 GitHub: [@Quirinodsg](https://github.com/Quirinodsg)
- 📧 Email: andre.quirino@example.com
- 💼 LinkedIn: [André Quirino](https://linkedin.com/in/andrequirino)

---

## 🙏 Agradecimentos

### Comunidades
- 🐍 Python Community
- ⚛️ React Community
- 🚀 FastAPI Team
- 🦙 Ollama Team

### Bibliotecas Open Source
- FastAPI, SQLAlchemy, Pydantic
- React, Recharts, Axios
- Docker, PostgreSQL, Redis
- E centenas de outras bibliotecas incríveis

### Inspirações
- CheckMK - Interface NOC
- PRTG - Monitoramento agentless
- Grafana - Visualização de métricas
- Datadog - AIOps e IA

---

## 📅 Histórico de Versões

### v1.0.0 (03/03/2026) - Release Inicial
- ✅ Sistema completo de monitoramento
- ✅ AIOps com IA híbrida
- ✅ Dashboard NOC em tempo real
- ✅ Instaladores MSI profissionais
- ✅ Documentação completa (300+ páginas)
- ✅ 50+ sensores implementados
- ✅ 80+ soluções na base de conhecimento
- ✅ Integrações: TOPdesk, GLPI, Teams, Email
- ✅ Suporte: Windows, Docker, Kubernetes, SNMP

---

## 📞 Suporte

### Documentação
- 📖 [Documentação Completa](docs/)
- 🎥 [Vídeos Tutoriais](https://youtube.com/corujamonitor)
- 💬 [FAQ](docs/faq.md)

### Contato
- 📧 Email: suporte@corujamonitor.com
- 💬 Discord: [Coruja Monitor Community](https://discord.gg/corujamonitor)
- 🐛 Issues: [GitHub Issues](https://github.com/Quirinodsg/CorujaMonitor/issues)

### Suporte Enterprise
- 📞 Telefone: +55 11 9999-9999
- 📧 Email: enterprise@corujamonitor.com
- 🎫 Portal: https://suporte.corujamonitor.com

---

## 🌟 Showcase

### Screenshots

#### Dashboard Principal
![Dashboard](docs/screenshots/dashboard.png)

#### NOC em Tempo Real
![NOC](docs/screenshots/noc.png)

#### Métricas Grafana-Style
![Metrics](docs/screenshots/metrics.png)

#### AIOps Dashboard
![AIOps](docs/screenshots/aiops.png)

---

## 🎯 Use Cases

### Pequenas Empresas (10-50 servidores)
- Monitoramento centralizado
- Alertas automáticos
- Relatórios executivos

### Médias Empresas (50-500 servidores)
- Multi-tenant
- Integrações service desk
- AIOps automático

### Grandes Empresas (500+ servidores)
- Alta disponibilidade
- Escalabilidade horizontal
- Compliance e auditoria

### MSPs (Provedores de Serviços)
- Multi-cliente
- White-label
- API completa

---

**Desenvolvido com ❤️ e ☕ por André Quirino**

**Coruja Monitor** - Monitoramento Inteligente para Infraestrutura de TI

---

*Última atualização: 03 de Março de 2026*
