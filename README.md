# 🦉 Coruja Monitor

Sistema de Monitoramento Inteligente com AIOps e Observabilidade para Infraestrutura de TI

[![License](https://img.shields.io/badge/license-Private-red.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/react-18.0+-61dafb.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/fastapi-0.100+-009688.svg)](https://fastapi.tiangolo.com/)
[![Version](https://img.shields.io/badge/version-3.0.0-brightgreen.svg)](https://github.com/Quirinodsg/CorujaMonitor)
[![Tests](https://img.shields.io/badge/tests-349%20passed-success.svg)](tests/)
[![TimescaleDB](https://img.shields.io/badge/timescaledb-2.14-orange.svg)](https://www.timescale.com/)

---

## O que é o Coruja Monitor

O **Coruja Monitor** é uma plataforma enterprise de monitoramento de infraestrutura de TI que combina coleta agentless (WMI, SNMP, ICMP, TCP, Docker, Kubernetes), observabilidade inteligente com pipeline de IA, e interface NOC em tempo real.

Inspirado em PRTG, Zabbix, CheckMK e Datadog — mas desenvolvido do zero para ambientes Windows/Linux com foco em facilidade de deploy e operação.

---

## Índice

- [Novidades v3.0](#novidades-v30)
- [Arquitetura](#arquitetura-geral)
- [Fluxo de Dados](#fluxo-de-dados)
- [Módulos v3](#módulos-v3)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Instalação](#instalação)
- [Testes](#testes)
- [API](#api)
- [Tecnologias](#tecnologias)
- [Histórico de Versões](#histórico-de-versões)
- [Documentação](#documentação)

---

## Novidades v3.0

A versão 3.0 transforma o Coruja Monitor de um sistema de monitoramento em uma plataforma de **observabilidade inteligente**, comparável ao Datadog e Dynatrace. Todos os módulos v2.0 continuam funcionando sem modificação.

| Capacidade | v2.0 | v3.0 |
|---|---|---|
| Spec Central (fonte única da verdade) | ❌ tipos duplicados | ✅ `core/spec/` |
| DAG de dependências entre sensores | ❌ | ✅ networkx, TTL 30s |
| Topologia de rede (switch→servidor→serviço) | ❌ | ✅ grafo + blast radius |
| Detecção de transição de estado | ❌ toda métrica = evento | ✅ só mudanças de estado |
| Pipeline IA orquestrado | ❌ agentes isolados | ✅ 5 agentes + circuit breaker |
| Feedback loop de IA | ❌ | ✅ retreino 24h, histórico 90 dias |
| Supressão de alertas duplicados | ❌ | ✅ Redis TTL 5min |
| Priorização ponderada de alertas | ❌ | ✅ score 4 fatores |
| DSL declarativa de sensores | ❌ | ✅ Lexer+Parser+Compiler |
| Consumer groups Redis Streams | ❌ | ✅ XREADGROUP paralelo |
| Buffer offline de métricas | ❌ | ✅ deque 10k métricas |
| TimescaleDB otimizado | básico | ✅ hypertable + retention 90d |
| Health score unificado | ❌ | ✅ `/observability/health-score` |
| WebSocket de observabilidade | ❌ | ✅ `/ws/observability` ≤5s |
| Testes property-based (Hypothesis) | ❌ | ✅ 23 invariantes |
| Cobertura de testes | ~30% | ✅ ≥80% módulos críticos |
| Total de testes | 120 | **349** |


---

## Arquitetura Geral

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                         CORUJA MONITOR v3.0                                ║
║                    Plataforma de Observabilidade Inteligente                ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  ┌─────────────────────────────────────────────────────────────────────┐    ║
║  │                    CAMADA DE COLETA (Sonda)                         │    ║
║  │                                                                     │    ║
║  │  SRVSONDA001 (Windows Server — NSSM)                                │    ║
║  │  C:\Program Files\CorujaMonitor\Probe                               │    ║
║  │                                                                     │    ║
║  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │    ║
║  │  │ WMI Engine   │  │ SNMP Engine  │  │ ICMP Engine  │             │    ║
║  │  │ (Windows)    │  │ (v1/v2c/v3)  │  │ (Ping)       │             │    ║
║  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘             │    ║
║  │         │                 │                  │                     │    ║
║  │  ┌──────▼─────────────────▼──────────────────▼───────────────┐    │    ║
║  │  │  DependencyEngine (DAG networkx)                           │    │    ║
║  │  │  Se Ping falha → TCP e WMI suspensos automaticamente       │    │    ║
║  │  └──────────────────────────────┬────────────────────────────┘    │    ║
║  │                                 │ XADD batch 500                  │    ║
║  └─────────────────────────────────┼─────────────────────────────────┘    ║
║                                    │                                        ║
║  ┌─────────────────────────────────▼─────────────────────────────────┐    ║
║  │                    CAMADA DE STREAMING (Redis)                     │    ║
║  │                                                                    │    ║
║  │   metrics_stream ──── maxlen 100.000 entradas                      │    ║
║  │   events_stream  ──── maxlen  50.000 entradas                      │    ║
║  │   Consumer Group: coruja-consumers (XREADGROUP, at-least-once)     │    ║
║  │   Buffer local: deque 10.000 métricas (resiliência offline)        │    ║
║  └─────────────────────────────────┬──────────────────────────────────┘    ║
║                                    │ XREADGROUP batch 500                   ║
║  ┌─────────────────────────────────▼──────────────────────────────────┐    ║
║  │                    CAMADA DE PROCESSAMENTO (Linux Docker)           │    ║
║  │                                                                     │    ║
║  │  core/spec/ ◄─── FONTE ÚNICA DA VERDADE                            │    ║
║  │  ├── enums.py   (HostType, Protocol, SensorStatus, EventSeverity)  │    ║
║  │  └── models.py  (Host, Sensor, Metric, Event, Alert, TopologyNode) │    ║
║  │                                                                     │    ║
║  │  ┌─────────────────────────────────────────────────────────────┐   │    ║
║  │  │  event_processor/                                           │   │    ║
║  │  │  ThresholdEvaluator → só transições de estado geram eventos │   │    ║
║  │  └──────────────────────────────┬──────────────────────────────┘   │    ║
║  │                                 │                                   │    ║
║  │  ┌──────────────────────────────▼──────────────────────────────┐   │    ║
║  │  │  ai_agents/ (Pipeline Orquestrado)                          │   │    ║
║  │  │                                                             │   │    ║
║  │  │  [1] AnomalyDetection  ──── Z-score >3σ, janela 7 dias     │   │    ║
║  │  │       │                                                     │   │    ║
║  │  │  [2] Correlation       ──── janela 5min, por host/grupo     │   │    ║
║  │  │       │                                                     │   │    ║
║  │  │  [3] RootCause         ──── TopologyGraph, nó raiz          │   │    ║
║  │  │       │                                                     │   │    ║
║  │  │  [4] Decision          ──── severidade + manutenção         │   │    ║
║  │  │       │                                                     │   │    ║
║  │  │  [5] AutoRemediation   ──── só com confiança ≥85%           │   │    ║
║  │  │                                                             │   │    ║
║  │  │  Circuit Breaker: >50% falhas → open 5min                   │   │    ║
║  │  │  FeedbackLoop: retreino 24h, histórico 90 dias              │   │    ║
║  │  └──────────────────────────────┬──────────────────────────────┘   │    ║
║  │                                 │                                   │    ║
║  │  ┌──────────────────────────────▼──────────────────────────────┐   │    ║
║  │  │  alert_engine/ (Orquestração de Alertas)                    │   │    ║
║  │  │                                                             │   │    ║
║  │  │  DuplicateSuppressor ── Redis TTL 5min                      │   │    ║
║  │  │       │                                                     │   │    ║
║  │  │  EventGrouper        ── janela 5min por host                │   │    ║
║  │  │       │                                                     │   │    ║
║  │  │  AlertPrioritizer    ── sev×0.40 + hosts×0.30 +             │   │    ║
║  │  │       │                  impacto×0.20 + horário×0.10        │   │    ║
║  │  │  AlertNotifier       ── email/webhook/Teams, SLA ≤30s       │   │    ║
║  │  │                         retry 3x backoff exponencial        │   │    ║
║  │  └──────────────────────────────┬──────────────────────────────┘   │    ║
║  │                                 │                                   │    ║
║  │  ┌──────────────────────────────▼──────────────────────────────┐   │    ║
║  │  │  PostgreSQL + TimescaleDB                                   │   │    ║
║  │  │  metrics_ts (hypertable, retention 90d, compressão 7d)      │   │    ║
║  │  │  ai_feedback_actions │ topology_nodes │ intelligent_alerts  │   │    ║
║  │  └─────────────────────────────────────────────────────────────┘   │    ║
║  └─────────────────────────────────┬───────────────────────────────────┘    ║
║                                    │ REST + WebSocket                        ║
║  ┌─────────────────────────────────▼───────────────────────────────────┐    ║
║  │                    CAMADA DE APRESENTAÇÃO (React)                    │    ║
║  │                                                                      │    ║
║  │  ── v2 (mantidos) ────────────────────────────────────────────────  │    ║
║  │  Dashboard │ AIOps │ NOCMode │ EventTimeline │ MetricsViewer        │    ║
║  │  KnowledgeBase │ Incidents │ Reports │ Settings │ ...               │    ║
║  │                                                                      │    ║
║  │  ── v3 (novos) ────────────────────────────────────────────────────  │    ║
║  │  ObservabilityDashboard  ── health score + mapa de impacto          │    ║
║  │  TopologyView            ── grafo interativo SVG                    │    ║
║  │  IntelligentAlerts       ── causa raiz + timeline                   │    ║
║  │  AIOpsV3                 ── pipeline + feedback metrics             │    ║
║  │  AdvancedMetrics         ── sparklines + export CSV                 │    ║
║  │  EventsTimeline          ── agrupado por data + filtros             │    ║
║  └──────────────────────────────────────────────────────────────────────┘    ║
╚══════════════════════════════════════════════════════════════════════════════╝
```


---

## Fluxo de Dados

```
  SRVSONDA001 (Windows)
       │
       │  1. DependencyEngine verifica se sensor deve executar
       │     (Ping falhou? → WMI suspenso em cascata)
       │
       ▼
  Protocol Engine (WMI / SNMP / ICMP / TCP)
       │
       │  2. Coleta a métrica
       │
       ▼
  Redis Stream "metrics_stream"  ←── XADD batch 500
       │                              (buffer local 10k se Redis offline)
       │  3. Consumer Group XREADGROUP (at-least-once delivery)
       │
       ▼
  EventProcessor
       │  4. ThresholdEvaluator avalia limites dinâmicos
       │  5. Só gera Event se houve TRANSIÇÃO de estado
       │     (ok→warning, warning→critical, etc.)
       │
       ├──► TimescaleDB metrics_ts  (batch insert ≤500)
       │
       └──► Redis Stream "events_stream"  ←── XADD maxlen 50k
                 │
                 │  6. AgentPipeline processa o evento
                 │
                 ▼
           AnomalyDetection  (Z-score >3σ do baseline 7 dias)
                 │
                 ▼
           Correlation       (agrupa eventos da janela 5min)
                 │
                 ▼
           RootCause         (TopologyGraph → identifica nó raiz)
                 │
                 ▼
           Decision          (avalia severidade, manutenção, histórico)
                 │
                 ▼
           AutoRemediation   (executa se confiança ≥85%)
                 │
                 ▼
           AlertEngine
           ├── DuplicateSuppressor  (Redis TTL 5min — sem spam)
           ├── EventGrouper         (janela 5min por host)
           ├── AlertPrioritizer     (score ponderado 4 fatores)
           └── AlertNotifier        (email / webhook / Teams, SLA ≤30s)
                 │
                 ▼
           FeedbackLoop  ──► ai_feedback_actions (PostgreSQL)
                 │            retreino automático a cada 24h
                 │
                 ▼
           Frontend WebSocket  (atualização ≤5 segundos)
```

---

## Módulos v3

### core/spec/ — Spec Central

Fonte única da verdade. Todos os módulos importam tipos daqui — elimina duplicação e inconsistências.

```
core/spec/
├── enums.py    HostType, Protocol, SensorStatus, EventSeverity,
│               AlertStatus, NodeType, ProbeStatus
└── models.py   Host, Sensor, Metric, Event, Alert,
                TopologyNode, ProbeNode  (Pydantic v2)
```

### engine/dependency_engine.py — DAG de Dependências

```
  Ping ──► TCP Port 443
       └─► WMI CPU
           └─► WMI Disk

  Se Ping → CRITICAL:
    TCP Port 443 → SUSPENDED (não executa)
    WMI CPU      → SUSPENDED
    WMI Disk     → SUSPENDED
```

- DAG via `networkx.DiGraph`
- Detecção de ciclo antes de cada `add_edge`
- Cache de estado por host com TTL 30 segundos

### topology_engine/ — Topologia e Impacto

```
  SW-CORE-01 (switch)
  ├── SRVCRMPRD001 (server)
  │   ├── CRM-API (service)
  │   └── CRM-DB (service)
  └── SRVCRMPRD002 (server)
      └── CRM-WEB (service)

  blast_radius("SW-CORE-01"):
    hosts afetados:    [SRVCRMPRD001, SRVCRMPRD002]
    serviços afetados: [CRM-API, CRM-DB, CRM-WEB]
    total_impact: 5
```

### ai_agents/ — Pipeline de Agentes IA

```
  Evento entra no pipeline
       │
  ┌────▼────────────────────────────────────────────────────┐
  │  Circuit Breaker                                        │
  │  Estado: CLOSED (normal) / OPEN (>50% falhas → 5min)   │
  └────┬────────────────────────────────────────────────────┘
       │
  [1] AnomalyDetectionAgent
       Baseline: média + desvio padrão dos últimos 7 dias
       Trigger:  |valor - média| > 3σ
       │
  [2] CorrelationAgent
       Janela: 5 minutos
       Agrupa: por host e por grupo topológico
       │
  [3] RootCauseAgent
       Usa TopologyGraph para subir na hierarquia
       Identifica o nó ancestral comum das falhas
       │
  [4] DecisionAgent
       Avalia: severidade, janela de manutenção,
               histórico de falsos positivos
       │
  [5] AutoRemediationAgent
       Executa apenas se confiança ≥ 85%
       Registra ação em ai_feedback_actions
       │
  FeedbackLoop
       Classifica outcome: resolved_fast / resolved_slow / false_positive
       Retreina baseline a cada 24h com histórico de 90 dias
```

### alert_engine/ — Motor de Alertas

```
  Fórmula de prioridade:
  score = (severidade × 0.40)
        + (hosts_afetados × 0.30)
        + (impacto_topológico × 0.20)
        + (horário_crítico × 0.10)

  Flood protection:
  >100 eventos/min → colapsa em 1 alerta de alta prioridade

  SLA de notificação: ≤30 segundos
  Retry: 3 tentativas com backoff exponencial
```

### sensor_dsl/ — DSL de Sensores

```
# Definição declarativa de sensor
sensor "cpu_monitor" extends "cpu_template" {
  protocol = "wmi"
  interval = 60
  warning  = 80
  critical = 95
}

# Pipeline: Lexer → Parser → AST → Compiler → Sensor (Pydantic)
# Suporta: herança de templates, comentários # e /* */
```


---

## Estrutura do Projeto

```
CorujaMonitor/
│
├── core/                         # v3 — Spec Central
│   └── spec/
│       ├── enums.py              # 7 enums (fonte única da verdade)
│       └── models.py             # 7 modelos Pydantic
│
├── engine/                       # v3 — Engines
│   └── dependency_engine.py      # DAG networkx, cache TTL 30s
│
├── topology_engine/              # v3 — Topologia
│   ├── graph.py                  # TopologyGraph (add/get/ancestors)
│   ├── impact.py                 # ImpactCalculator (blast radius)
│   └── discovery.py              # SNMP/WMI auto-discovery
│
├── event_processor/              # v3 — Processador de Eventos
│   ├── processor.py              # Idempotente, só transições
│   └── threshold_evaluator.py    # Thresholds dinâmicos por host
│
├── ai_agents/                    # v3 — Pipeline IA Orquestrado
│   ├── pipeline.py               # Orquestrador + circuit breaker
│   ├── anomaly_detection.py      # Z-score, janela 7 dias
│   ├── correlation.py            # Janela 5min, por host/grupo
│   ├── root_cause.py             # TopologyGraph → nó raiz
│   ├── decision.py               # Severidade + contexto
│   ├── auto_remediation.py       # Confiança ≥85%
│   ├── smart_scheduler.py        # Agendamento inteligente
│   ├── base_agent.py             # Interface base
│   └── feedback_loop.py          # Retreino 24h, histórico 90d
│
├── alert_engine/                 # v3 — Motor de Alertas
│   ├── engine.py                 # Orquestrador principal
│   ├── suppressor.py             # Redis TTL 5min
│   ├── grouper.py                # Janela 5min por host
│   ├── prioritizer.py            # Score ponderado 4 fatores
│   └── notifier.py               # email/webhook/Teams, SLA ≤30s
│
├── sensor_dsl/                   # v3 — DSL de Sensores
│   ├── lexer.py
│   ├── parser.py
│   ├── ast_nodes.py
│   ├── compiler.py
│   └── printer.py
│
├── api/                          # Backend FastAPI
│   ├── main.py
│   ├── models.py
│   ├── database.py
│   ├── auth.py
│   ├── migrate_v3.py             # v3 — DDL (metrics_ts, topology_nodes, ...)
│   ├── middleware/
│   │   └── waf.py                # Web Application Firewall
│   └── routers/
│       ├── observability.py      # v3 — health-score, impact-map, WS
│       ├── probe_manager.py      # v3 — ProbeManager distribuído
│       ├── servers.py
│       ├── sensors.py
│       ├── metrics.py
│       ├── aiops.py
│       ├── noc.py
│       └── ...                   # 40+ routers v2 mantidos
│
├── probe/                        # Sonda Windows (SRVSONDA001)
│   ├── probe_core.py             # Núcleo da sonda
│   ├── protocol_engines/         # v2 — Motores por protocolo
│   │   ├── icmp_engine.py
│   │   ├── tcp_engine.py
│   │   ├── snmp_engine.py        # pysnmp 7.x, GetBulk
│   │   ├── wmi_engine.py
│   │   ├── docker_engine.py
│   │   └── kubernetes_engine.py
│   ├── engine/                   # v2 — Engine Core
│   │   ├── wmi_pool.py           # Pool WMI + backoff anti-lockout AD
│   │   ├── smart_collector.py
│   │   ├── adaptive_monitor.py   # Intervalos 30s/60s/300s
│   │   ├── metric_cache.py       # Redis + local, TTL por tipo
│   │   ├── pre_check.py          # Conectividade antes de sensores pesados
│   │   ├── scheduler.py
│   │   ├── thread_pool.py
│   │   ├── global_rate_limiter.py
│   │   ├── internal_metrics.py
│   │   └── prometheus_exporter.py # :9090
│   ├── metrics_pipeline/         # v2/v3 — Streaming
│   │   ├── stream_producer.py    # XADD batch + buffer 10k
│   │   ├── stream_consumer.py    # XREADGROUP consumer groups
│   │   └── metrics_processor.py  # Batch insert TimescaleDB ≤500
│   ├── connection_pool/
│   │   ├── snmp_pool.py
│   │   └── tcp_pool.py
│   ├── event_engine/
│   │   ├── event_queue.py
│   │   ├── wmi_event_listener.py
│   │   └── kubernetes_event_listener.py
│   └── security/
│       ├── credential_manager.py # Fernet encryption
│       └── vault_client.py       # HashiCorp + Azure KV
│
├── frontend/                     # Interface React 18
│   └── src/components/
│       ├── ObservabilityDashboard.js  # v3
│       ├── TopologyView.js            # v3
│       ├── IntelligentAlerts.js       # v3
│       ├── AIOpsV3.js                 # v3
│       ├── AdvancedMetrics.js         # v3
│       ├── EventsTimeline.js          # v3
│       ├── Dashboard.js               # v2
│       ├── AIOps.js                   # v2
│       ├── NOCMode.js                 # v2
│       └── ...                        # 40+ componentes v2 mantidos
│
├── ai-agent/                     # Motor AIOps standalone (porta 8001)
│   ├── anomaly_detector.py       # Isolation Forest
│   ├── failure_predictor.py      # Regressão linear
│   ├── event_correlator.py       # Correlação temporal
│   └── root_cause_engine.py      # RCA com detecção de cascata
│
├── tests/                        # 349 testes, 0 falhas
│   ├── test_spec_central.py      # 25 testes
│   ├── test_dependency_engine.py # 19 testes
│   ├── test_topology_engine.py   # 16 testes
│   ├── test_event_processor.py   # 25 testes
│   ├── test_ai_agents.py         # 29 testes
│   ├── test_alert_engine.py      # 25 testes
│   ├── test_sensor_dsl.py        # 35 testes
│   ├── test_pbt_properties.py    # 4 testes property-based
│   ├── test_load_simulation.py   # 3 testes de carga
│   ├── test_regression_v2.py     # 5 testes de regressão
│   └── test_audit_enterprise.py  # 120 testes enterprise
│
├── docs/                         # Documentação completa
│   ├── v3/                       # Documentação v3.0
│   ├── architecture/             # Arquiteturas e roadmaps
│   ├── guides/                   # Guias de instalação
│   ├── reference/                # Referências técnicas
│   ├── changelog/                # Histórico detalhado por data
│   └── README.md                 # Índice da documentação
│
├── installer/                    # Instaladores MSI (WiX)
├── worker/                       # Celery tasks
├── security/                     # Scripts de segurança
├── docker-compose.yml
├── .env.example
├── CHANGELOG.md
└── version.txt
```


---

## Instalação

### Pré-requisitos

**Servidor Linux:**
- Docker 20.10+ e docker-compose instalados
- 4GB RAM mínimo (8GB recomendado)
- Portas abertas: 3000 (frontend), 8000 (API), 8001 (AI agent), 5432 (PostgreSQL), 6379 (Redis)

**Sonda Windows:**
- Windows Server 2012 R2+
- Python 3.11+
- Conta de serviço com permissões WMI (`TECHBIZ\coruja.monitor`)
- NSSM para gerenciamento do serviço

### Deploy no Servidor (Linux)

```bash
# 1. Clonar repositório
git clone https://github.com/Quirinodsg/CorujaMonitor.git
cd /home/administrador/CorujaMonitor

# 2. Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas credenciais

# 3. Subir todos os serviços
docker-compose up -d

# 4. Executar migração v3 (cria tabelas novas)
docker exec coruja-api python3 migrate_v3.py

# 5. Verificar saúde
docker-compose ps
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/observability/health-score
```

### Instalar Sonda (Windows — SRVSONDA001)

```powershell
# Instalar como serviço Windows (domínio AD)
cd "C:\Program Files\CorujaMonitor\Probe"
.\install.bat

# Verificar serviço
Get-Service CorujaProbe
Get-Content ".\logs\probe.log" -Tail 50
```

### Atualizar (Kiro → Linux)

```bash
# No Kiro (Windows — desenvolvimento):
git add -A
git commit -m "feat: descrição"
git push origin master

# No Linux:
cd /home/administrador/CorujaMonitor
git pull
docker-compose up -d --build api worker frontend
```

---

## Testes

```bash
# Todos os 349 testes
pytest tests/ -v

# Com cobertura (≥80% módulos críticos)
pytest tests/ --cov=core --cov=engine --cov=topology_engine \
  --cov=event_processor --cov=ai_agents --cov=alert_engine \
  --cov-report=term-missing --cov-fail-under=80

# Apenas regressão v2 (garante que nada quebrou)
pytest tests/test_regression_v2.py -v

# Property-based (Hypothesis — 23 invariantes)
pytest tests/test_pbt_properties.py -v
```

| Arquivo | Testes | Tipo |
|---|---|---|
| `test_spec_central.py` | 25 | Unitário |
| `test_dependency_engine.py` | 19 | Unitário + Property |
| `test_topology_engine.py` | 16 | Unitário + Property |
| `test_event_processor.py` | 25 | Unitário + Property |
| `test_ai_agents.py` | 29 | Unitário + Property |
| `test_alert_engine.py` | 25 | Unitário + Property |
| `test_sensor_dsl.py` | 35 | Unitário + Property |
| `test_pbt_properties.py` | 4 | Property-based (Hypothesis) |
| `test_load_simulation.py` | 3 | Carga (1.000 hosts × 50 sensores) |
| `test_regression_v2.py` | 5 | Regressão v2.0 |
| `test_audit_enterprise.py` | 120 | Auditoria Enterprise |
| **Total** | **349** | **0 falhas** |

---

## API

### Endpoints v3 (novos)

| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/api/v1/observability/health-score` | Score 0-100 da infraestrutura |
| GET | `/api/v1/observability/impact-map` | Servidores com alertas ativos |
| GET | `/api/v1/alerts/intelligent` | Alertas inteligentes com filtros |
| GET | `/api/v1/alerts/intelligent/{id}/root-cause` | Análise de causa raiz |
| GET | `/api/v1/topology/graph` | Grafo completo `{nodes, edges}` |
| GET | `/api/v1/topology/impact/{node_id}` | Blast radius de um nó |
| WS  | `/api/v1/ws/observability` | Atualizações em tempo real (≤5s) |

### Endpoints v2 (mantidos)

| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/api/v1/dashboard/summary` | Resumo do dashboard |
| GET | `/api/v1/servers` | Lista servidores |
| GET | `/api/v1/sensors` | Lista sensores |
| GET | `/api/v1/metrics` | Métricas com filtros |
| GET | `/api/v1/incidents` | Incidentes |
| GET | `/api/v1/aiops/analysis` | Análise AIOps v2 |
| GET | `/api/v1/noc/status` | Status NOC |
| WS  | `/api/v1/ws/dashboard` | WebSocket dashboard v2 |

Documentação interativa: `http://localhost:8000/docs`

---

## Tecnologias

| Camada | Tecnologia | Versão | Uso |
|---|---|---|---|
| Backend | FastAPI | 0.100+ | Framework web + WebSocket |
| Backend | SQLAlchemy | 2.0+ | ORM |
| Backend | Pydantic | 2.0+ | Validação e modelos |
| Backend | Celery | 5.3+ | Tasks assíncronas |
| Backend | Redis | 7.0+ | Streams + cache |
| Backend | PostgreSQL | 15+ | Banco de dados |
| Backend | TimescaleDB | 2.14 | Séries temporais (hypertable) |
| Backend | networkx | 3.x | DAG de dependências |
| Backend | Hypothesis | 6.x | Property-based testing |
| AI | Ollama | Latest | IA local (llama2) |
| AI | scikit-learn | 1.x | Isolation Forest |
| Sonda | Python | 3.11–3.13 | Linguagem principal |
| Sonda | pysnmp | 7.1.22 | SNMP v1/v2c/v3 + GetBulk |
| Sonda | psutil | 5.x | Métricas internas |
| Sonda | cryptography | 41+ | Fernet (credenciais) |
| Frontend | React | 18.2+ | UI |
| Frontend | Recharts | 2.8+ | Gráficos |
| Infra | Docker Compose | 2.x | Orquestração |
| Infra | NSSM | 2.24 | Serviço Windows |

---

## Histórico de Versões

| Versão | Data | Destaques |
|---|---|---|
| **3.0.0** | Mar 2026 | Observabilidade inteligente, pipeline IA, topologia, DSL, 349 testes |
| 2.1.0 | Mar 2026 | WAF reativado, WMI pool, streaming, 120 testes |
| 2.0.0 | Mar 2026 | Protocol engines, connection pools, adaptive monitoring, AIOps |
| 1.0.0 | Mar 2026 | Sistema completo de monitoramento agentless |

Veja [CHANGELOG.md](CHANGELOG.md) para o histórico completo.

---

## Documentação

| Documento | Descrição |
|---|---|
| [docs/v3/ARCHITECTURE.md](docs/v3/ARCHITECTURE.md) | Arquitetura completa v3.0 com diagramas |
| [docs/v3/ARCHITECTURE_BEFORE_AFTER.md](docs/v3/ARCHITECTURE_BEFORE_AFTER.md) | Comparativo v2 vs v3 |
| [docs/v3/API_REFERENCE.md](docs/v3/API_REFERENCE.md) | Referência completa da API v3 |
| [docs/v3/DEPLOYMENT.md](docs/v3/DEPLOYMENT.md) | Guia de deploy e atualização |
| [docs/v3/TEST_SUITE.md](docs/v3/TEST_SUITE.md) | Suite de testes e invariantes |
| [docs/README.md](docs/README.md) | Índice completo da documentação |

---

## Licença

Este projeto é **privado** e proprietário. Todos os direitos reservados.

---

**Coruja Monitor** — Monitoramento Inteligente para Infraestrutura de TI

*Versão 3.0.0 — Março 2026*
