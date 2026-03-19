# Coruja Monitor v3.0 — Arquitetura Completa

## Visão Geral

O Coruja Monitor v3.0 evolui a plataforma de monitoramento v2.0 para uma solução de **observabilidade inteligente** comparável ao Datadog e Dynatrace. A arquitetura mantém compatibilidade total com todos os módulos v2.0 e adiciona 13 fases de novas capacidades.

**Stack**: Python 3 / FastAPI / React / Celery / PostgreSQL + TimescaleDB / Redis Streams / Docker Compose (Linux)  
**Sonda**: Windows Server (SRVSONDA001) via NSSM, diretório `C:\Program Files\CorujaMonitor\Probe`

---

## Diagrama de Arquitetura

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CORUJA MONITOR v3.0                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────┐    ┌──────────────────┐                      │
│  │  SRVSONDA001     │    │  Sonda Edge/Cloud │                      │
│  │  (Windows/NSSM)  │    │  (futuro)         │                      │
│  │  WMI/SNMP/ICMP   │    │                  │                      │
│  └────────┬─────────┘    └────────┬─────────┘                      │
│           │ XADD metrics_stream   │                                 │
│           └──────────┬────────────┘                                 │
│                      ▼                                              │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                  Redis Streams                                │  │
│  │   metrics_stream (maxlen=100k)  events_stream (maxlen=50k)   │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                      │ XREADGROUP (batch 500)                       │
│                      ▼                                              │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                  Core Server (Linux Docker)                 │    │
│  │                                                             │    │
│  │  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  │    │
│  │  │ FastAPI      │  │ Celery Worker│  │  AI Agent        │  │    │
│  │  │ api/         │  │ worker/      │  │  ai-agent/       │  │    │
│  │  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘  │    │
│  │         │                 │                    │            │    │
│  │  ┌──────▼─────────────────▼────────────────────▼─────────┐ │    │
│  │  │              Módulos v3 (novos)                        │ │    │
│  │  │  core/spec/          — Spec Central (fonte da verdade) │ │    │
│  │  │  engine/             — DependencyEngine (DAG)          │ │    │
│  │  │  topology_engine/    — TopologyGraph + ImpactCalc      │ │    │
│  │  │  event_processor/    — ThresholdEvaluator + Processor  │ │    │
│  │  │  ai_agents/          — Pipeline 5 agentes + Feedback   │ │    │
│  │  │  alert_engine/       — Suppressor+Grouper+Prioritizer  │ │    │
│  │  │  sensor_dsl/         — Lexer+Parser+Compiler+Printer   │ │    │
│  │  └────────────────────────────────────────────────────────┘ │    │
│  │                                                             │    │
│  │  ┌──────────────────────┐  ┌──────────────────────────┐   │    │
│  │  │ PostgreSQL+TimescaleDB│  │ Redis                    │   │    │
│  │  │ metrics_ts (hypertable│  │ Streams + Cache          │   │    │
│  │  │ ai_feedback_actions   │  │ TTL 5min (suppressor)    │   │    │
│  │  │ topology_nodes        │  │ Buffer 10k métricas      │   │    │
│  │  │ intelligent_alerts    │  └──────────────────────────┘   │    │
│  │  └──────────────────────┘                                  │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                      │ REST + WebSocket                             │
│                      ▼                                              │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                  Frontend React (porta 3000)                │    │
│  │  Dashboard  │  ObservabilityDashboard  │  TopologyView      │    │
│  │  IntelligentAlerts  │  AIOpsV3  │  AdvancedMetrics          │    │
│  │  EventsTimeline  │  NOCMode  │  KnowledgeBase  │  ...       │    │
│  └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Módulos v3 — Descrição

### core/spec/ — Spec Central
Fonte única da verdade para todos os tipos de dados. Todos os módulos importam daqui.
- `enums.py`: HostType, Protocol, SensorStatus, EventSeverity, AlertStatus, NodeType, ProbeStatus
- `models.py`: Host, Sensor, Metric, Event, Alert, TopologyNode, ProbeNode (Pydantic)

### engine/dependency_engine.py — DAG de Dependências
Controla execução condicional de sensores. Se Ping falha, TCP e WMI são suspensos automaticamente.
- DAG via `networkx.DiGraph`; detecção de ciclo antes de cada `add_edge`
- Cache de estado por host com TTL 30 segundos

### topology_engine/ — Topologia e Impacto
Modela hierarquia switch→servidor→serviço e calcula blast radius de falhas.
- `TopologyGraph`: add_node, add_edge, get_ancestors, get_descendants
- `ImpactCalculator`: blast_radius retorna hosts/serviços/aplicações afetados
- `SNMPTopologyDiscovery` e `WMITopologyDiscovery`: descoberta automática

### event_processor/ — Processador de Eventos
Converte Metrics em Events apenas em transições de estado (idempotente).
- `ThresholdEvaluator`: avalia thresholds dinâmicos por host
- `EventProcessor`: cache `_last_status` por sensor; publica em `events_stream` via XADD

### ai_agents/ — Pipeline de Agentes IA
Pipeline sequencial com circuit breaker (>50% falhas → open 5min).
1. `AnomalyDetectionAgent` — Z-score, janela 7 dias, desvio >3σ
2. `CorrelationAgent` — janela 5 minutos, agrupa por host/grupo topológico
3. `RootCauseAgent` — usa TopologyGraph para identificar nó raiz
4. `DecisionAgent` — avalia severidade, manutenção, histórico de falsos positivos
5. `AutoRemediationAgent` — executa apenas com confiança ≥ 85%
6. `FeedbackLoop` — registra ações em `ai_feedback_actions`, retreina a cada 24h

### alert_engine/ — Motor de Alertas
Orquestra: DuplicateSuppressor → EventGrouper → AlertPrioritizer → AlertNotifier
- Supressão: cache Redis TTL 5min, chave hash(host+type+severity)
- Agrupamento: janela 5 minutos por host
- Prioridade: severidade×0.40 + hosts×0.30 + impacto×0.20 + horário×0.10
- Notificação: email/webhook/Teams, SLA ≤30s, retry 3x backoff exponencial
- Flood protection: >100 eventos/min → 1 alerta de alta prioridade

### sensor_dsl/ — DSL de Sensores
Linguagem de domínio para definição declarativa de sensores.
```
sensor "cpu_monitor" extends "cpu_template" {
  protocol = "wmi"
  interval = 60
  warning  = 80
  critical = 95
}
```
- Lexer → Parser (recursivo descendente) → Compiler → Sensor (Pydantic)
- Suporta herança de templates, comentários `#` e `/* */`

### probe/metrics_pipeline/ — Streaming Architecture
- `stream_producer.py`: batch publish XADD, buffer local 10k métricas quando Redis indisponível
- `stream_consumer.py`: consumer groups XREADGROUP, múltiplos consumidores paralelos
- `metrics_processor.py`: batch insert TimescaleDB ≤500 métricas/operação

### api/routers/observability.py — Endpoints v3
- `GET /api/v1/observability/health-score` — score 0-100 da infraestrutura
- `GET /api/v1/observability/impact-map` — servidores com alertas ativos
- `GET /api/v1/alerts/intelligent` — alertas inteligentes com filtros
- `GET /api/v1/alerts/intelligent/{id}/root-cause` — análise de causa raiz
- `WS /api/v1/ws/observability` — atualizações em tempo real (≤5s)

---

## Banco de Dados — Tabelas v3

| Tabela | Descrição |
|--------|-----------|
| `metrics_ts` | Hypertable TimescaleDB, retention 90 dias, compressão 7 dias |
| `ai_feedback_actions` | Ações dos agentes IA com resultado e tempo de resolução |
| `topology_nodes` | Nós do grafo de topologia com hierarquia self-referencial |
| `intelligent_alerts` | Alertas consolidados com causa raiz e hosts afetados |

---

## Fluxo de Dados Completo

```
ProbeNode (SRVSONDA001)
  → DependencyEngine.should_execute()
  → Protocol Engine (WMI/SNMP/ICMP/TCP)
  → Metric → Redis Stream "metrics_stream" (XADD)
  → StreamConsumer (XREADGROUP, batch 500)
  → EventProcessor
      → ThresholdEvaluator → SensorStatus
      → StateTransition (mudança?) → Event
      → Redis Stream "events_stream" (XADD, maxlen=50k)
      → TimescaleDB metrics_ts
  → AgentPipeline
      → AnomalyDetection (Z-score >3σ)
      → Correlation (janela 5min)
      → RootCause (TopologyGraph)
      → Decision (severidade + contexto)
      → AutoRemediation (confiança ≥85%)
  → AlertEngine
      → DuplicateSuppressor (TTL 5min)
      → EventGrouper (janela 5min)
      → AlertPrioritizer (score ponderado)
      → AlertNotifier (email/webhook/Teams, SLA ≤30s)
  → FeedbackLoop → ai_feedback_actions
  → Frontend (WebSocket ≤5s)
```
