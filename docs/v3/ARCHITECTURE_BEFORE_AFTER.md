# Coruja Monitor — Arquitetura: Antes (v2) vs Depois (v3)

## v2.0 — Arquitetura Original

```
┌─────────────────────────────────────────────────────────┐
│                  CORUJA MONITOR v2.0                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  SRVSONDA001 (Windows)                                  │
│  ┌─────────────────────────────────────────────────┐   │
│  │  probe_core.py                                  │   │
│  │  ├── wmi_pool.py (pool de conexões WMI)         │   │
│  │  ├── smart_collector.py (coleta adaptativa)     │   │
│  │  ├── global_rate_limiter.py (throttling)        │   │
│  │  ├── event_queue.py (fila de eventos local)     │   │
│  │  └── metrics_pipeline/                          │   │
│  │      ├── stream_producer.py (XADD básico)       │   │
│  │      ├── stream_consumer.py (XREAD simples)     │   │
│  │      └── metrics_processor.py (insert unitário) │   │
│  └─────────────────────────────────────────────────┘   │
│                    │ HTTP POST /api/v1/metrics           │
│                    ▼                                    │
│  ┌─────────────────────────────────────────────────┐   │
│  │  FastAPI (api/)                                 │   │
│  │  ├── 40+ routers (auth, servers, sensors, ...)  │   │
│  │  └── Sem observabilidade unificada              │   │
│  └─────────────────────────────────────────────────┘   │
│                    │                                    │
│  ┌─────────────────────────────────────────────────┐   │
│  │  PostgreSQL (sem TimescaleDB otimizado)         │   │
│  │  Redis (cache simples)                          │   │
│  └─────────────────────────────────────────────────┘   │
│                    │                                    │
│  ┌─────────────────────────────────────────────────┐   │
│  │  React Frontend                                 │   │
│  │  Dashboard, AIOps, NOCMode, EventTimeline, ...  │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ai-agent/ (serviço separado, porta 8001)               │
│  ├── anomaly_detector.py (standalone)                   │
│  ├── event_correlator.py (standalone)                   │
│  └── root_cause_engine.py (standalone)                  │
└─────────────────────────────────────────────────────────┘
```

### Limitações do v2.0
- Sem Spec Central: tipos duplicados em múltiplos módulos
- Sem DAG de dependências: sensores filhos executam mesmo quando pai falha
- Sem topologia: não há modelagem de hierarquia switch→servidor→serviço
- EventProcessor ausente: toda métrica gera evento (sem detecção de transição)
- Agentes IA isolados: sem pipeline orquestrado, sem feedback loop
- Alert engine básico: sem supressão de duplicados, sem priorização ponderada
- Sem DSL: sensores configurados apenas via UI/API
- Streaming básico: sem consumer groups, sem buffer de resiliência
- TimescaleDB não otimizado: sem hypertable, sem retention policy

---

## v3.0 — Arquitetura Nova

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CORUJA MONITOR v3.0                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  SRVSONDA001 (Windows/NSSM)          Sondas Futuras                │
│  ┌──────────────────────────────┐    ┌──────────────────────────┐  │
│  │  probe_core.py (v2 mantido)  │    │  ProbeNode Edge/Cloud    │  │
│  │  + DependencyEngine          │    │  (weighted round-robin)  │  │
│  │  + stream_producer (batch)   │    └──────────────────────────┘  │
│  └──────────────┬───────────────┘                │                 │
│                 │ XADD metrics_stream (batch 500) │                 │
│                 └──────────────┬──────────────────┘                 │
│                                ▼                                    │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Redis Streams                                              │   │
│  │  metrics_stream (maxlen=100k) + events_stream (maxlen=50k)  │   │
│  │  Consumer Groups: coruja-consumers                          │   │
│  │  Buffer local 10k métricas (resiliência offline)            │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                │ XREADGROUP (at-least-once)         │
│                                ▼                                    │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Core Server (Linux Docker)                                 │   │
│  │                                                             │   │
│  │  core/spec/ ←── FONTE ÚNICA DA VERDADE ───────────────────  │   │
│  │  ├── enums.py (7 enums)                                     │   │
│  │  └── models.py (7 modelos Pydantic)                         │   │
│  │                                                             │   │
│  │  engine/dependency_engine.py                                │   │
│  │  └── DAG networkx, cache TTL 30s, suspensão em cascata      │   │
│  │                                                             │   │
│  │  topology_engine/                                           │   │
│  │  ├── graph.py (TopologyGraph)                               │   │
│  │  ├── impact.py (BlastRadius)                                │   │
│  │  └── discovery.py (SNMP/WMI auto-discovery)                 │   │
│  │                                                             │   │
│  │  event_processor/                                           │   │
│  │  ├── threshold_evaluator.py (thresholds dinâmicos)          │   │
│  │  └── processor.py (idempotente, só transições de estado)    │   │
│  │                                                             │   │
│  │  ai_agents/ (pipeline orquestrado)                          │   │
│  │  ├── AnomalyDetection → Correlation → RootCause             │   │
│  │  ├── Decision → AutoRemediation (confiança ≥85%)            │   │
│  │  ├── pipeline.py (circuit breaker >50% falhas)              │   │
│  │  └── feedback_loop.py (retreino 24h, histórico 90 dias)     │   │
│  │                                                             │   │
│  │  alert_engine/                                              │   │
│  │  ├── suppressor.py (Redis TTL 5min)                         │   │
│  │  ├── grouper.py (janela 5min)                               │   │
│  │  ├── prioritizer.py (score ponderado 4 fatores)             │   │
│  │  └── notifier.py (email/webhook/Teams, SLA ≤30s)            │   │
│  │                                                             │   │
│  │  sensor_dsl/                                                │   │
│  │  └── Lexer→Parser→Compiler→Printer (DSL declarativa)        │   │
│  │                                                             │   │
│  │  api/routers/observability.py (NOVO)                        │   │
│  │  ├── GET /health-score                                      │   │
│  │  ├── GET /impact-map                                        │   │
│  │  ├── GET /alerts/intelligent                                │   │
│  │  └── WS /ws/observability (≤5s)                             │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                │ REST + WebSocket                   │
│                                ▼                                    │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Frontend React (v3 + v2 coexistindo)                       │   │
│  │  ── v2 mantidos ──────────────────────────────────────────  │   │
│  │  Dashboard, AIOps, NOCMode, EventTimeline, MetricsViewer    │   │
│  │  ── v3 novos ─────────────────────────────────────────────  │   │
│  │  ObservabilityDashboard (health score + mapa de impacto)    │   │
│  │  TopologyView (grafo interativo SVG)                        │   │
│  │  IntelligentAlerts (causa raiz + timeline)                  │   │
│  │  AIOpsV3 (pipeline + feedback metrics)                      │   │
│  │  AdvancedMetrics (sparklines + export CSV)                  │   │
│  │  EventsTimeline (agrupado por data + filtros)               │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Comparativo Direto

| Capacidade | v2.0 | v3.0 |
|-----------|------|------|
| Spec Central | ❌ tipos duplicados | ✅ core/spec/ único |
| DAG de dependências | ❌ | ✅ networkx, TTL 30s |
| Topologia de rede | ❌ | ✅ grafo + blast radius |
| Detecção de transição | ❌ toda métrica = evento | ✅ só mudanças de estado |
| Pipeline IA orquestrado | ❌ agentes isolados | ✅ 5 agentes + circuit breaker |
| Feedback loop | ❌ | ✅ retreino 24h, 90 dias |
| Supressão de duplicados | ❌ | ✅ Redis TTL 5min |
| Priorização de alertas | ❌ | ✅ score ponderado 4 fatores |
| DSL de sensores | ❌ | ✅ Lexer+Parser+Compiler |
| Consumer groups Redis | ❌ | ✅ XREADGROUP paralelo |
| Buffer offline | ❌ | ✅ deque 10k métricas |
| TimescaleDB otimizado | ❌ | ✅ hypertable + retention 90d |
| Health score unificado | ❌ | ✅ /observability/health-score |
| WebSocket observabilidade | ❌ | ✅ /ws/observability ≤5s |
| Probes distribuídas | básico | ✅ weighted round-robin + failover |
| Testes property-based | ❌ | ✅ 23 properties com Hypothesis |
| Cobertura de testes | ~30% | ✅ ≥80% módulos críticos |

---

## Compatibilidade v2 → v3

Todos os módulos v2.0 continuam funcionando sem modificação:

| Módulo v2.0 | Status v3.0 |
|-------------|-------------|
| `probe/engine/wmi_pool.py` | ✅ Mantido (backoff anti-lockout adicionado) |
| `probe/engine/smart_collector.py` | ✅ Mantido |
| `probe/engine/global_rate_limiter.py` | ✅ Mantido |
| `probe/event_engine/event_queue.py` | ✅ Mantido (coexiste com events_stream) |
| `probe/metrics_pipeline/stream_producer.py` | ✅ Estendido (batch + buffer) |
| `probe/metrics_pipeline/stream_consumer.py` | ✅ Estendido (consumer groups) |
| `probe/metrics_pipeline/metrics_processor.py` | ✅ Estendido (batch 500) |
| `ai-agent/anomaly_detector.py` | ✅ Mantido (encapsulado em AnomalyDetectionAgent) |
| `ai-agent/event_correlator.py` | ✅ Mantido (encapsulado em CorrelationAgent) |
| `ai-agent/root_cause_engine.py` | ✅ Mantido (encapsulado em RootCauseAgent) |
| Todos os 40+ routers FastAPI | ✅ Mantidos |
| Todos os componentes React v2 | ✅ Mantidos |
