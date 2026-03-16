# 🦉 Coruja Monitor

Sistema de Monitoramento Inteligente com AIOps e IA para Infraestrutura de TI

[![License](https://img.shields.io/badge/license-Private-red.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/react-18.0+-61dafb.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/fastapi-0.100+-009688.svg)](https://fastapi.tiangolo.com/)
[![Version](https://img.shields.io/badge/version-2.0.0-brightgreen.svg)](https://github.com/Quirinodsg/CorujaMonitor)
[![Tests](https://img.shields.io/badge/tests-77%20passed-success.svg)](tests/)
[![pysnmp](https://img.shields.io/badge/pysnmp-7.1.22-blue.svg)](https://pysnmp.com/)

---

## O que há de novo na v2.0

A versão 2.0 representa uma reescrita completa da camada de coleta (probe), introduzindo uma arquitetura enterprise inspirada em PRTG, Zabbix e Datadog. Os principais pilares são:

- **Protocol Engines** — motores dedicados por protocolo (ICMP, TCP, SNMP, WMI, Docker, Kubernetes, Registry)
- **Connection Pooling** — reuso de conexões SNMP e TCP, reduzindo overhead de rede em até 80%
- **Adaptive Monitoring** — intervalos dinâmicos (30s/60s/300s) baseados no estado do host
- **Metric Cache** — cache Redis/local com TTL por tipo de métrica, eliminando queries duplicadas
- **Connectivity Pre-Check** — validação de conectividade antes de sensores pesados, com cache de 30s
- **AIOps Engine** — detecção de anomalias (Isolation Forest), predição de falhas (regressão linear) e correlação de eventos
- **Prometheus Exporter** — métricas internas expostas na porta 9090
- **Vault/Credential Manager** — credenciais criptografadas com Fernet, suporte a HashiCorp Vault e Azure Key Vault
- **Suite de testes** — 77 testes automatizados, 0 falhas

---

## Índice

- [Sobre](#sobre)
- [Novidades v2.0](#arquitetura-enterprise-v20)
- [Arquitetura](#arquitetura)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Instalação](#instalação)
- [Testes](#testes)
- [Tecnologias](#tecnologias)
- [Roadmap](#roadmap)
- [Changelog](#changelog)
- [Licença](#licença)

---

## Sobre

O **Coruja Monitor** é uma plataforma enterprise de monitoramento de infraestrutura de TI que combina:

- **AIOps Automático** — detecção e remediação inteligente de incidentes
- **Dashboard NOC em Tempo Real** — visualização estilo CheckMK/PRTG
- **Monitoramento Agentless** — WMI, SNMP, Ping sem instalação de agentes
- **IA Híbrida** — Ollama local + OpenAI para análise de incidentes
- **Métricas Grafana-Style** — visualização moderna de métricas
- **Integração Service Desk** — TOPdesk, GLPI, Teams, Email
- **Instaladores MSI** — distribuição profissional via GPO

### Diferenciais

- 100% Agentless — sem necessidade de instalar agentes nos servidores monitorados
- Multi-tenant — suporte a múltiplas empresas/clientes
- IA Integrada — análise inteligente de incidentes e auto-remediação
- Base de Conhecimento — 80+ soluções pré-configuradas
- Instalação Rápida — deploy em minutos com Docker
- Interface Moderna — UI responsiva e intuitiva

---

## Arquitetura Enterprise v2.0

### Protocol Engines (`probe/protocol_engines/`)

Cada protocolo tem seu próprio motor isolado, com interface padronizada via `BaseProtocolEngine`:

| Engine | Protocolo | Recursos |
|--------|-----------|----------|
| `ICMPEngine` | Ping | count, timeout, retries, jitter, packet loss |
| `TCPEngine` | TCP Port | timeout, latência de conexão |
| `SNMPEngine` | SNMP v1/v2c/v3 | GetBulk, GetNext, fallback automático |
| `WMIEngine` | WMI/WinRM | queries otimizadas, sem SELECT * |
| `RegistryEngine` | Windows Registry | leitura remota de chaves |
| `DockerEngine` | Docker API | containers, stats, health |
| `KubernetesEngine` | K8s API | pods, nodes, deployments |

### Connection Pools (`probe/connection_pool/`)

- `SNMPConnectionPool` — max por host configurável, reuso de sessões, stats em tempo real
- `TCPConnectionPool` — pool de sockets TCP com keep-alive

### Engine Core (`probe/engine/`)

| Módulo | Função |
|--------|--------|
| `pre_check.py` | Valida conectividade antes de sensores pesados (cache TTL 30s) |
| `metric_cache.py` | Cache Redis + fallback local, TTL 5s (CPU/RAM) / 10s (disco/serviços) |
| `adaptive_monitor.py` | Intervalos 30s/60s/300s, restaura após 5 ciclos OK |
| `sensor_engine.py` | Orquestra execução de sensores |
| `scheduler.py` | Distribui sensores ao longo do tempo, evita picos |
| `thread_pool.py` | WorkerPool com 20 workers padrão |
| `internal_metrics.py` | Métricas internas (CPU, RAM, fila) com alertas |
| `prometheus_exporter.py` | Exporta métricas na porta 9090, atualiza a cada 15s |

### AIOps (`ai-agent/`)

| Módulo | Algoritmo | Detalhes |
|--------|-----------|----------|
| `anomaly_detector.py` | Isolation Forest | janela 7 dias, retreino 24h, mín. 50 amostras |
| `failure_predictor.py` | Regressão Linear | horizonte 24h, intervalo de confiança ±1σ |
| `event_correlator.py` | Correlação temporal | janela 5 min, causa raiz por severidade |

### Segurança (`probe/security/`)

- `CredentialManager` — Fernet encryption, HMAC integrity check, redação de senhas em logs
- `VaultClient` — suporte a HashiCorp Vault e Azure Key Vault com fallback gracioso

---

## Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│                    CAMADA DE APRESENTAÇÃO                        │
│  Frontend (React 18) — Dashboard, NOC, Servidores, AIOps        │
└─────────────────────────────────────────────────────────────────┘
                            │ HTTP/WebSocket
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CAMADA DE APLICAÇÃO                           │
│  API (FastAPI) — REST, WebSocket, Auth JWT, 100+ endpoints      │
└─────────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┬──────────────┐
        ▼                   ▼                   ▼              ▼
   PostgreSQL           AI Agent            Worker          Redis
   (TimescaleDB)     (Ollama/OpenAI)       (Celery)        (Cache)
        │
        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PROBE v2.0 (Enterprise)                       │
│                                                                  │
│  Protocol Engines → Connection Pools → Sensor Engine            │
│  Pre-Check → Metric Cache → Adaptive Monitor → Scheduler        │
│  Internal Metrics → Prometheus Exporter (:9090)                 │
│  Security (Vault + CredentialManager)                           │
│  Event Engine (WMI Events, Docker Events, K8s Events)           │
└─────────────────────────────────────────────────────────────────┘
        │
   ICMP │ TCP │ SNMP v1/v2c/v3 │ WMI │ Docker │ Kubernetes
```

---

## Estrutura do Projeto

```
CorujaMonitor/
├── api/                          # Backend FastAPI
│   ├── main.py
│   ├── models.py
│   ├── database.py
│   ├── auth.py
│   ├── routers/                  # 30+ endpoints REST
│   │   ├── multi_probe.py        # Gestão multi-probe
│   │   ├── timescale_migration.py
│   │   ├── aiops_advanced.py
│   │   └── ...
│   └── middleware/
│       └── waf.py                # Web Application Firewall
│
├── frontend/                     # Interface React 18
│   └── src/
│       ├── components/           # 40+ componentes
│       │   ├── NOCRealTime.js
│       │   ├── AIOps.js
│       │   ├── KubernetesDashboard.js
│       │   └── ...
│       └── styles/
│
├── probe/                        # Agente v2.0 (Enterprise)
│   ├── protocol_engines/         # NOVO v2.0
│   │   ├── base_engine.py
│   │   ├── icmp_engine.py
│   │   ├── tcp_engine.py
│   │   ├── snmp_engine.py        # pysnmp 7.x, GetBulk
│   │   ├── registry_engine.py
│   │   ├── docker_engine.py
│   │   └── kubernetes_engine.py
│   ├── connection_pool/          # NOVO v2.0
│   │   ├── snmp_pool.py
│   │   └── tcp_pool.py
│   ├── engine/                   # NOVO v2.0
│   │   ├── pre_check.py          # Connectivity pre-check
│   │   ├── metric_cache.py       # Redis + local cache
│   │   ├── adaptive_monitor.py   # Intervalos dinâmicos
│   │   ├── sensor_engine.py
│   │   ├── scheduler.py
│   │   ├── thread_pool.py
│   │   ├── internal_metrics.py   # psutil metrics
│   │   └── prometheus_exporter.py # :9090
│   ├── event_engine/             # NOVO v2.0
│   │   ├── wmi_event_listener.py
│   │   ├── docker_event_listener.py
│   │   └── kubernetes_event_listener.py
│   ├── security/                 # NOVO v2.0
│   │   ├── credential_manager.py # Fernet encryption
│   │   └── vault_client.py       # HashiCorp + Azure KV
│   ├── collectors/               # Coletores legados
│   │   ├── ping_collector.py
│   │   ├── snmp_collector.py
│   │   ├── docker_collector.py
│   │   ├── kubernetes_collector.py
│   │   ├── wmi_native_collector.py
│   │   └── ...
│   └── probe_core.py
│
├── ai-agent/                     # Motor AIOps v2.0
│   ├── anomaly_detector.py       # Isolation Forest
│   ├── failure_predictor.py      # Linear regression
│   ├── event_correlator.py       # Event correlation
│   ├── aiops_engine.py
│   ├── ml_engine.py
│   └── ai_engine.py
│
├── tests/                        # Suite de testes v2.0
│   └── test_audit_enterprise.py  # 77 testes, 0 falhas
│
├── docs/
│   ├── ENTERPRISE_MONITORING_ARCHITECTURE.md
│   ├── REQUISITO_HOSTNAME_KERBEROS.md
│   └── ...
│
├── installer/                    # Instaladores MSI
├── worker/                       # Celery tasks
├── security/                     # Scripts de segurança
├── docker-compose.yml
├── .env.example
└── CHANGELOG.md
```

---

## Instalação

### Pré-requisitos

**Servidor:**
- Docker 20.10+ e Docker Compose 2.0+
- 4GB RAM mínimo (8GB recomendado)
- Portas: 3000, 8000, 5432, 6379, 9090

**Probe:**
- Python 3.11+ (testado até 3.13)
- Windows Server 2012 R2+ ou Linux
- Privilégios de administrador

### Servidor (Docker)

```bash
git clone https://github.com/Quirinodsg/CorujaMonitor.git
cd CorujaMonitor
cp .env.example .env
# edite .env com suas configurações
docker-compose up -d
# acesse http://localhost:3000 — admin / admin123
```

### Probe (Windows)

```powershell
# Instalar dependências
cd probe
pip install -r requirements.txt

# Instalar pysnmp 7.x (obrigatório para Python 3.11+)
pip install "pysnmp>=7.0"

# Executar
python probe_core.py
```

### Probe como Serviço Windows

```powershell
# Domínio AD
.\install.bat

# Workgroup
.\install_workgroup.bat

# Entra ID / Azure AD
.\install_entraid.bat
```

### Instalação em Massa (GPO)

```powershell
# Copie o MSI para um compartilhamento de rede
# Crie GPO: Computer Configuration → Software Settings → Software Installation
# Vincule à OU e force: gpupdate /force
```

---

## Testes

A suite de testes cobre todos os 17 componentes da arquitetura enterprise:

```bash
# Executar todos os testes
cd probe
python -m pytest ../tests/test_audit_enterprise.py -v

# Resultado esperado:
# 77 passed, 0 skipped, 0 failed
```

### Cobertura por seção

| Seção | Testes | Status |
|-------|--------|--------|
| Arquitetura Geral (imports) | 6 | ✅ |
| Protocol Engines | 14 | ✅ |
| Connection Pools | 6 | ✅ |
| Scheduler | 6 | ✅ |
| Worker Pool | 5 | ✅ |
| Metric Cache | 8 | ✅ |
| Pre-Check Conectividade | 6 | ✅ |
| Adaptive Monitor | 7 | ✅ |
| Segurança (Credentials/Vault) | 5 | ✅ |
| AIOps (Anomaly/Failure/Correlator) | 8 | ✅ |
| Escalabilidade (Benchmarks) | 4 | ✅ |
| Multi-Probe API | 2 | ✅ |
| **Total** | **77** | **✅ 0 falhas** |

---

## Tecnologias

### Backend

| Tecnologia | Versão | Uso |
|------------|--------|-----|
| FastAPI | 0.100+ | Framework web |
| SQLAlchemy | 2.0+ | ORM |
| Pydantic | 2.0+ | Validação |
| Celery | 5.3+ | Tasks assíncronas |
| Redis | 7.0+ | Cache e broker |
| PostgreSQL | 15+ | Banco de dados |
| TimescaleDB | 2.x | Séries temporais |
| Ollama | Latest | IA local |
| OpenAI | Latest | IA cloud |

### Probe v2.0

| Tecnologia | Versão | Uso |
|------------|--------|-----|
| Python | 3.11–3.13 | Linguagem principal |
| pysnmp | 7.1.22 | SNMP v1/v2c/v3 + GetBulk |
| scikit-learn | 1.x | Isolation Forest (AIOps) |
| psutil | 5.x | Métricas internas |
| cryptography | 41+ | Fernet (credenciais) |
| Docker SDK | 6.1+ | Monitoramento containers |
| kubernetes | 28.1+ | Monitoramento K8s |

### Frontend

| Tecnologia | Versão | Uso |
|------------|--------|-----|
| React | 18.2+ | UI |
| Recharts | 2.8+ | Gráficos |
| Socket.io | 4.6+ | WebSocket real-time |
| Axios | 1.5+ | HTTP client |
| Vite | 4.4+ | Build |

---

## Roadmap

### v2.0 (Março 2026) — atual

- Protocol Engines (ICMP, TCP, SNMP, WMI, Docker, K8s, Registry)
- Connection Pooling (SNMP + TCP)
- Adaptive Monitoring (30s/60s/300s)
- Metric Cache (Redis + local, TTL por tipo)
- Connectivity Pre-Check (cache 30s)
- AIOps Engine (Isolation Forest + regressão linear + correlação)
- Prometheus Exporter (:9090)
- Vault/Credential Manager (Fernet + HashiCorp + Azure KV)
- Event Engine (WMI, Docker, Kubernetes)
- Multi-Probe API
- TimescaleDB migration
- Suite de testes: 77 testes, 0 falhas
- pysnmp 7.x (Python 3.13 compatível)

### v2.1 (Q2 2026)

- Monitoramento Linux via SSH nativo
- VMware vSphere / Hyper-V
- Cloud monitoring (AWS CloudWatch, Azure Monitor, GCP)
- SQL Server / MySQL / PostgreSQL monitoring
- Synthetic monitoring (URLs, APIs)
- ServiceNow / Jira Service Management
- Slack / PagerDuty / Telegram

### v2.2 (Q3 2026)

- App mobile iOS/Android
- Playbooks de remediação (Ansible + PowerShell DSC)
- RBAC granular
- Auditoria completa
- Compliance reports (ISO 27001, SOC 2)

### v3.0 (Q4 2026)

- Multi-região e High Availability
- Disaster Recovery automático
- Escalabilidade horizontal (Kubernetes-native)
- API pública completa + Marketplace de plugins
- Modelos de IA customizados por cliente
- Natural Language Queries
- Mapas de rede interativos com topologia automática

---

## Changelog

Veja [CHANGELOG.md](CHANGELOG.md) para o histórico completo de versões.

---

## Licença

Este projeto é **privado** e proprietário. Todos os direitos reservados.

Para licenciamento comercial ou suporte enterprise:
- Email: suporte@corujamonitor.com
- GitHub: [@Quirinodsg](https://github.com/Quirinodsg)

---

## Autor

**André Quirino**
- GitHub: [@Quirinodsg](https://github.com/Quirinodsg)
- LinkedIn: [André Quirino](https://linkedin.com/in/andrequirino)

---

**Coruja Monitor** — Monitoramento Inteligente para Infraestrutura de TI

*Versão 2.0.0 — Março 2026*
