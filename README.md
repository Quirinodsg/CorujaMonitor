# 🦉 Coruja Monitor

Sistema de Monitoramento Inteligente com AIOps e IA para Infraestrutura de TI

[![License](https://img.shields.io/badge/license-Private-red.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/react-18.0+-61dafb.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/fastapi-0.100+-009688.svg)](https://fastapi.tiangolo.com/)

---

## 📋 Índice

- [Sobre](#sobre)
- [Funcionalidades](#funcionalidades)
- [Arquitetura](#arquitetura)
- [Instalação](#instalação)
- [Documentação](#documentação)
- [Tecnologias](#tecnologias)
- [Licença](#licença)

---

## 🎯 Sobre

O **Coruja Monitor** é uma plataforma completa de monitoramento de infraestrutura de TI que combina:

- 🤖 **AIOps Automático** - Detecção e remediação inteligente de incidentes
- 📊 **Dashboard NOC em Tempo Real** - Visualização estilo CheckMK/PRTG
- 🔍 **Monitoramento Agentless** - WMI, SNMP, Ping sem instalação de agentes
- 🧠 **IA Híbrida** - Ollama local + OpenAI para análise de incidentes
- 📈 **Métricas Grafana-Style** - Visualização moderna de métricas
- 🎫 **Integração Service Desk** - TOPdesk, GLPI, Teams, Email

---

## ✨ Funcionalidades

### Monitoramento
- ✅ Servidores Windows (WMI local e remoto)
- ✅ Dispositivos de Rede (SNMP)
- ✅ Containers Docker
- ✅ Clusters Kubernetes
- ✅ Serviços e Aplicações
- ✅ Ping/Conectividade

### Sensores por Categoria
- 🖥️ **Sistema**: CPU, Memória, Disco, Uptime
- 🐳 **Docker**: Containers, Imagens, Volumes, Redes
- ⚙️ **Serviços**: Windows Services, Systemd
- 📱 **Aplicações**: Processos, Portas, URLs
- 🌐 **Rede**: Interfaces, Tráfego, Latência

### AIOps e IA
- 🤖 Detecção automática de anomalias
- 🔧 Remediação automática de incidentes
- 📚 Base de conhecimento com 80+ soluções
- 🧠 Análise de causa raiz com IA
- 📊 Predição de falhas

### Integrações
- 🎫 TOPdesk (criação automática de tickets)
- 🎫 GLPI (integração completa)
- 💬 Microsoft Teams (notificações)
- 📧 Email (alertas e relatórios)

### Interface
- 📊 Dashboard executivo
- 🖥️ NOC em tempo real
- 📈 Métricas estilo Grafana
- 📋 Relatórios personalizados
- 🔔 Sistema de incidentes
- ⏰ Janelas de manutenção

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                      │
│  Dashboard │ NOC │ Servidores │ Incidentes │ Relatórios │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                   API (FastAPI)                          │
│  REST API │ WebSocket │ Auth │ Routers │ Models         │
└─────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│   POSTGRES   │   │  AI AGENT    │   │    WORKER    │
│   Database   │   │  (Ollama)    │   │   (Celery)   │
└──────────────┘   └──────────────┘   └──────────────┘
                            │
                            ▼
                   ┌──────────────┐
                   │    PROBE     │
                   │  (Agente)    │
                   └──────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
   ┌────────┐         ┌────────┐         ┌────────┐
   │  WMI   │         │  SNMP  │         │  Ping  │
   └────────┘         └────────┘         └────────┘
```

### Componentes

1. **Frontend** - Interface React moderna e responsiva
2. **API** - Backend FastAPI com REST e WebSocket
3. **Probe** - Agente Python para coleta de métricas
4. **AI Agent** - Motor de IA com Ollama/OpenAI
5. **Worker** - Processamento assíncrono com Celery
6. **Database** - PostgreSQL para persistência

---

## 🚀 Instalação

### Pré-requisitos

- Docker e Docker Compose
- Python 3.11+ (para o Probe)
- Node.js 18+ (para desenvolvimento)

### Instalação Rápida

```bash
# 1. Clone o repositório
git clone https://github.com/Quirinodsg/CorujaMonitor.git
cd CorujaMonitor

# 2. Configure as variáveis de ambiente
cp .env.example .env
# Edite o .env com suas configurações

# 3. Inicie os containers
docker-compose up -d

# 4. Acesse a interface
# http://localhost:3000
# Usuário: admin
# Senha: admin123
```

### Instalação do Probe

#### Windows (Domínio)
```powershell
cd probe
.\install.bat
```

#### Windows (Workgroup)
```powershell
cd probe
.\install_workgroup.bat
```

#### Windows (Entra ID / Azure AD)
```powershell
cd probe
.\install_entraid.bat
```

---

## 📚 Documentação

### Guias de Instalação
- [Guia Rápido de Instalação](GUIA_RAPIDO_INSTALACAO.md)
- [Instalação em Domínio](GUIA_INSTALADOR_DOMINIO.md)
- [Instalação sem Domínio](GUIA_MONITORAMENTO_SEM_DOMINIO.md)
- [Instalação com Entra ID](GUIA_ENTRA_ID_AZURE_AD.md)

### Guias de Configuração
- [Configuração de Sensores](BIBLIOTECA_SENSORES_IMPLEMENTADA.md)
- [Configuração de Integrações](INTEGRACOES_TOPDESK_GLPI.md)
- [Configuração do AIOps](AIOPS_AUTOMATICO_EXPLICADO.md)
- [Configuração de Kubernetes](GUIA_COMPLETO_KUBERNETES_27FEV.md)

### Arquitetura e Design
- [Arquitetura do Sistema](ARQUITETURA_SENSORES_PROBE.md)
- [Design do AIOps](AIOPS_IA_HIBRIDA_EXPLICADA.md)
- [Monitoramento Agentless](GUIA_MONITORAMENTO_AGENTLESS_COMPLETO.md)

### Troubleshooting
- [Solução de Problemas](SOLUCAO_RAPIDA.md)
- [Diagnóstico Completo](DIAGNOSTICO_COMPLETO_25FEV.md)

---

## 🛠️ Tecnologias

### Backend
- **FastAPI** - Framework web moderno e rápido
- **SQLAlchemy** - ORM para PostgreSQL
- **Celery** - Processamento assíncrono
- **Redis** - Cache e message broker
- **Ollama** - IA local (Llama 3.1)
- **OpenAI** - IA em nuvem (GPT-4)

### Frontend
- **React 18** - Interface moderna
- **Recharts** - Gráficos e visualizações
- **Axios** - Cliente HTTP
- **React Router** - Navegação

### Probe
- **Python 3.11** - Linguagem principal
- **WMI** - Monitoramento Windows
- **PySNMP** - Monitoramento SNMP
- **Docker SDK** - Monitoramento containers
- **Kubernetes Client** - Monitoramento K8s

### Infraestrutura
- **Docker** - Containerização
- **Docker Compose** - Orquestração
- **PostgreSQL** - Banco de dados
- **Nginx** - Proxy reverso

---

## 📊 Estatísticas do Projeto

- 📁 **Arquivos de Código**: 200+
- 📝 **Linhas de Código**: 50.000+
- 📚 **Documentação**: 300+ páginas
- 🔧 **Sensores Implementados**: 50+
- 🤖 **Base de Conhecimento**: 80+ soluções
- 🎯 **Funcionalidades**: 30+

---

## 🔒 Licença

Este projeto é **privado** e proprietário. Todos os direitos reservados.

Não é permitido:
- ❌ Copiar ou distribuir o código
- ❌ Usar comercialmente sem autorização
- ❌ Modificar e redistribuir

Para licenciamento comercial, entre em contato.

---

## 👥 Autor

**André Quirino**
- GitHub: [@Quirinodsg](https://github.com/Quirinodsg)
- Email: andre.quirino@example.com

---

## 🙏 Agradecimentos

- Comunidade Python
- Comunidade React
- FastAPI Team
- Ollama Team
- Todos os contribuidores de bibliotecas open source utilizadas

---

## 📅 Histórico de Versões

### v1.0.0 (03/03/2026)
- ✅ Release inicial completo
- ✅ Todas as funcionalidades implementadas
- ✅ Documentação completa
- ✅ Testes realizados

---

**Desenvolvido com ❤️ e ☕ por André Quirino**
