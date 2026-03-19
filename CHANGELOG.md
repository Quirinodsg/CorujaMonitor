# Changelog

Todas as mudanças notáveis do projeto Coruja Monitor são documentadas aqui.

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/).

---

## [3.0.0] — 2026-03-19

### Resumo

Versão 3.0 transforma o Coruja Monitor de um sistema de monitoramento em uma plataforma de **observabilidade inteligente**, comparável ao Datadog e Dynatrace. Introduz 13 novos módulos com pipeline de IA orquestrado, topologia de rede com cálculo de blast radius, DAG de dependências entre sensores, DSL declarativa, streaming com consumer groups e 349 testes automatizados (0 falhas). Todos os módulos v2.0 continuam funcionando sem modificação.

---

### Adicionado

#### Spec Central (`core/spec/`)
- `enums.py` — 7 enums: `HostType`, `Protocol`, `SensorStatus`, `EventSeverity`, `AlertStatus`, `NodeType`, `ProbeStatus`
- `models.py` — 7 modelos Pydantic v2: `Host`, `Sensor`, `Metric`, `Event`, `Alert`, `TopologyNode`, `ProbeNode`
- Fonte única da verdade: todos os módulos importam tipos daqui, eliminando duplicação

#### DAG de Dependências (`engine/dependency_engine.py`)
- `DependencyEngine` com grafo `networkx.DiGraph`
- Suspensão em cascata: se Ping falha, TCP e WMI são suspensos automaticamente
- Detecção de ciclo antes de cada `add_edge` (previne deadlock)
- Cache de estado por host com TTL 30 segundos

#### Topologia de Rede (`topology_engine/`)
- `graph.py` — `TopologyGraph`: `add_node`, `add_edge`, `get_ancestors`, `get_descendants`
- `impact.py` — `ImpactCalculator`: `blast_radius` retorna hosts/serviços/aplicações afetados
- `discovery.py` — `SNMPTopologyDiscovery` e `WMITopologyDiscovery`: descoberta automática de topologia

#### Processador de Eventos (`event_processor/`)
- `threshold_evaluator.py` — avalia thresholds dinâmicos por host
- `processor.py` — idempotente: só gera `Event` em transições de estado (ok→warning, warning→critical, etc.)
- Cache `_last_status` por sensor; publica em `events_stream` via XADD

#### Pipeline de Agentes IA (`ai_agents/`)
- `pipeline.py` — orquestrador com circuit breaker (>50% falhas → open 5min)
- `anomaly_detection.py` — Z-score, janela 7 dias, desvio >3σ
- `correlation.py` — janela 5 minutos, agrupa por host/grupo topológico
- `root_cause.py` — usa `TopologyGraph` para identificar nó raiz
- `decision.py` — avalia severidade, manutenção, histórico de falsos positivos
- `auto_remediation.py` — executa apenas com confiança ≥ 85%
- `feedback_loop.py` — registra ações em `ai_feedback_actions`, retreina a cada 24h com histórico 90 dias
- `base_agent.py` — interface base para todos os agentes
- `smart_scheduler.py` — agendamento inteligente de execução

#### Motor de Alertas (`alert_engine/`)
- `engine.py` — orquestrador: Suppressor → Grouper → Prioritizer → Notifier
- `suppressor.py` — cache Redis TTL 5min, chave `hash(host+type+severity)`
- `grouper.py` — janela 5 minutos por host
- `prioritizer.py` — score ponderado: `severidade×0.40 + hosts×0.30 + impacto×0.20 + horário×0.10`
- `notifier.py` — email/webhook/Teams, SLA ≤30s, retry 3x backoff exponencial
- Flood protection: >100 eventos/min → 1 alerta de alta prioridade

#### DSL de Sensores (`sensor_dsl/`)
- `lexer.py` — tokenizador com suporte a comentários `#` e `/* */`
- `parser.py` — parser recursivo descendente
- `ast_nodes.py` — nós da AST
- `compiler.py` — compila AST para `Sensor` (Pydantic)
- `printer.py` — serializa `Sensor` de volta para DSL
- Suporta herança de templates (`extends`)

#### Streaming Aprimorado (`probe/metrics_pipeline/`)
- `stream_producer.py` — batch publish XADD, buffer local deque 10k métricas (resiliência offline)
- `stream_consumer.py` — consumer groups XREADGROUP, múltiplos consumidores paralelos, at-least-once delivery
- `metrics_processor.py` — batch insert TimescaleDB ≤500 métricas/operação

#### ProbeManager (`engine/probe_manager.py`, `api/routers/probe_manager.py`)
- Gestão de probes distribuídas com weighted round-robin
- Failover automático quando probe fica offline
- Router FastAPI com endpoints de status e atribuição

#### Endpoints de Observabilidade (`api/routers/observability.py`)
- `GET /api/v1/observability/health-score` — score 0-100 com breakdown por status
- `GET /api/v1/observability/impact-map` — servidores com alertas ativos
- `GET /api/v1/alerts/intelligent` — alertas inteligentes com filtros (status, severidade)
- `GET /api/v1/alerts/intelligent/{id}/root-cause` — análise detalhada de causa raiz
- `WS /api/v1/ws/observability` — atualizações em tempo real (≤5 segundos)

#### Migração de Banco de Dados (`api/migrate_v3.py`)
- `metrics_ts` — hypertable TimescaleDB, retention 90 dias, compressão automática 7 dias
- `ai_feedback_actions` — ações dos agentes IA com resultado e tempo de resolução
- `topology_nodes` — nós do grafo com hierarquia self-referencial
- `intelligent_alerts` — alertas consolidados com causa raiz e hosts afetados

#### Componentes React v3 (`frontend/src/components/`)
- `ObservabilityDashboard.js` + CSS — health score + mapa de impacto
- `TopologyView.js` — grafo interativo SVG
- `IntelligentAlerts.js` + CSS — causa raiz + timeline
- `AIOpsV3.js` — pipeline + feedback metrics
- `AdvancedMetrics.js` — sparklines + export CSV
- `EventsTimeline.js` + CSS — agrupado por data + filtros
- `Sidebar.js` — rotas v3 com divisor visual
- `MainLayout.js` — roteamento para todos os componentes v3

#### Suite de Testes v3 (`tests/`)
- `test_spec_central.py` — 25 testes (core/spec/)
- `test_dependency_engine.py` — 19 testes (DAG + property-based)
- `test_topology_engine.py` — 16 testes (grafo + blast radius)
- `test_event_processor.py` — 25 testes (idempotência + thresholds)
- `test_ai_agents.py` — 29 testes (pipeline + circuit breaker)
- `test_alert_engine.py` — 25 testes (suppressor + prioritizer)
- `test_sensor_dsl.py` — 35 testes (lexer + parser + round-trip)
- `test_pbt_properties.py` — 4 testes property-based (Hypothesis)
- `test_load_simulation.py` — 3 testes de carga (1.000 hosts × 50 sensores)
- `test_regression_v2.py` — 5 testes de regressão (garante compatibilidade v2)
- **Total: 349 testes, 0 falhas, cobertura ≥80% módulos críticos**

#### Documentação (`docs/v3/`)
- `ARCHITECTURE.md` — arquitetura completa com diagramas ASCII
- `ARCHITECTURE_BEFORE_AFTER.md` — comparativo v2 vs v3 com tabela de capacidades
- `API_REFERENCE.md` — referência completa dos endpoints v3
- `DEPLOYMENT.md` — guia de deploy, migração e rollback
- `TEST_SUITE.md` — suite de testes e 23 invariantes property-based

---

### Alterado

- `docker-compose.yml` — volumes v3 + variáveis de ambiente para streaming
- `frontend/src/components/Sidebar.js` — rotas v3 com divisor visual
- `frontend/src/components/MainLayout.js` — roteamento para componentes v3
- `probe/engine/wmi_pool.py` — backoff anti-lockout AD (corrige bloqueio de conta `coruja.monitor`)

---

### Compatibilidade v2 → v3

Todos os módulos v2.0 continuam funcionando sem modificação. A v3.0 é 100% aditiva.

---

### Performance (Benchmarks v3.0)

| Métrica | Resultado |
|---|---|
| Testes automatizados | 349 passed, 0 failed |
| Cobertura módulos críticos | ≥80% |
| Carga: 1.000 hosts × 50 sensores | latência média <2s, zero perda |
| Streaming batch | ≤500 métricas/operação |
| WebSocket observabilidade | atualização ≤5s |
| Supressão de duplicados | Redis TTL 5min |
| SLA de notificação | ≤30s |
| AutoRemediation threshold | confiança ≥85% |

---

## [2.1.0] — 2026-03-16

### Resumo

Versão 2.1 consolida as melhorias enterprise da v2.0 com correções de segurança críticas (WAF reativado),
novos componentes de infraestrutura distribuída e melhorias de UX no portal web. Suite de testes expandida
para 120 testes automatizados com 0 falhas.

---

### Adicionado

#### WAF — Web Application Firewall (`api/middleware/waf.py`)
- Reativado em produção após correções de compatibilidade
- Whitelist de ranges Docker completos: `172.16.0.0/12`, `192.168.0.0/16`, `10.0.0.0/8`
- Bypass automático para WebSocket upgrades (`/ws/dashboard`)
- `validate_content_type` expandido: aceita `application/octet-stream`, `application/xml`, content-type vazio
- Remoção automática de IPs da blacklist após `blacklist_duration` (1h) — TODO implementado

#### WMI Connection Pool (`probe/connection_pool/wmi_pool.py`, `probe/engine/wmi_pool.py`)
- `WMIConnectionPool` com `max_connections_per_host = 3`, `idle_timeout = 300s`
- Funções: `acquire()`, `release()`, `invalidate()`, `cleanup_idle_connections()`, `stats()`
- `PooledConnection` dataclass com tracking de `last_used` e `in_use`
- `_init_thread_com()` para CoInitializeSecurity (gracioso sem pythoncom)
- Singleton `get_pool()` thread-safe

#### Global Rate Limiter (`probe/engine/global_rate_limiter.py`)
- `MAX_GLOBAL_SENSORS_RUNNING = 200`, `QUEUE_LIMIT = 1000`
- Context manager `acquire_slot()` com semáforo
- Métricas: `global_active_sensors`, `global_queue_depth`, `utilization_pct`
- Singleton `get_limiter()`

#### TimescaleDB (`docker-compose.yml`)
- Imagem `timescale/timescaledb:latest-pg15`
- SQL de migration montado em `initdb` com hypertable `sensor_metrics`
- Compressão automática e retention policy (30 dias raw, 1 ano agregado)

#### Streaming de Métricas (`probe/metrics_pipeline/`)
- `stream_producer.py` — `StreamProducer` com Redis Streams + fallback em memória; `MetricEvent` dataclass
- `stream_consumer.py` — consumidor assíncrono com `drain_fallback()`
- `metrics_processor.py` — deduplicação por bucket de 5s, batch persist

#### Probe Nodes Distribuídos (`api/routers/probe_nodes.py`)
- Entidade `ProbeNode` com campos: id, name, location, status, last_heartbeat, version, capacity
- Endpoints: `POST /probes/register`, `POST /probes/heartbeat`, `GET /probes`

#### WMI Batch Collector (`probe/engine/wmi_batch_collector.py`)
- Coleta CPU + RAM + Disco em paralelo com cache TTL 5s
- Reduz queries WMI de N para 1 por host por ciclo

#### SNMP Engine Otimizado (`probe/protocol_engines/snmp_engine.py`)
- GetBulk com `BULK_MAX_REPETITIONS = 25`
- Fallback automático para GetNext

#### Event Queue (`probe/event_engine/event_queue.py`)
- `EventQueue` com deduplicação por janela configurável
- Rate limiting por host
- `MonitoringEvent` dataclass; `flush()` e `stats()`

#### AIOps Expandido (`ai-agent/`)
- `anomaly_detector.py` — baseline automático, `detect_trend()` (regressão linear pura), `predict_capacity()`
- `root_cause_engine.py` — RCA com detecção de cascata (switch → hosts dependentes), top 5 hipóteses por confiança

#### Portal Web — Novos Componentes (`frontend/src/components/`)
- `Dashboard.js` — WebSocket tempo real (`/ws/dashboard`) + polling fallback 30s + indicador "Tempo real"
- `ProbeNodes.js` — cards com status, heartbeat, capacidade, add/remove probe
- `MetricsViewer.js` — gráficos históricos, zoom temporal (1h/6h/24h/7d/30d), comparação por servidor
- `EventTimeline.js` — timeline com filtros por severidade/tipo/host/intervalo + paginação
- `AIOps.js` — anomalias, correlações, RCA, planos de ação
- `Discovery.js` + `Discovery.css` — scan de rede, SNMP discovery, WMI discovery
- `SystemHealth.js` + `SystemHealth.css` — monitoramento interno: CPU probe, fila, latência WMI, ingestão

#### Portal Web — UX (`frontend/src/`)
- Toggle dark/light mode (`Sidebar.js` + `App.js`)
- Carregamento assíncrono em todos os componentes
- `Sensors.js` — busca por texto (nome/tipo) + paginação de 50 itens por página
- `EventTimeline.js` — paginação de 20 itens + filtros por severidade, tipo, host, intervalo

#### API — Novos Routers
- `api/routers/metrics_batch.py` — `POST /metrics/batch` para ingestão em lote
- `api/routers/ws_dashboard.py` — WebSocket `/ws/dashboard` tempo real
- `api/routers/discovery.py` — endpoints `/network-scan`, `/snmp`, `/wmi`, `/add-sensor`

#### Testes (`tests/test_audit_enterprise.py`)
- Expandido de 77 para **120 testes** cobrindo todos os novos componentes
- Seção 13: WMI Connection Pool (12 testes)
- Seção 14: Global Rate Limiter (6 testes)
- Seção 15: Metrics Pipeline (5 testes)
- Seção 16: Event Queue (5 testes)
- Seção 17: Root Cause Engine (4 testes)
- Seção 18: AnomalyDetector expandido (7 testes)
- Seção 19: Discovery Files (4 testes)

---

### Alterado

- `api/main.py` — WAF reativado; todos os novos routers registrados
- `api/middleware/waf.py` — whitelist expandida, WebSocket bypass, blacklist com expiração automática
- `frontend/src/components/Sensors.js` — busca por texto + paginação adicionadas
- `frontend/src/components/Sidebar.js` — toggle dark/light mode

---

### Corrigido

- WAF bloqueava requisições de containers Docker (range `172.17.x.x` não estava na whitelist)
- WAF bloqueava WebSocket upgrades para `/ws/dashboard`
- WAF retornava 415 para requisições sem Content-Type (GET requests com body vazio)
- Blacklist de IPs nunca expirava (TODO implementado com `_blacklist_expiry`)

---

### Performance (Benchmarks v2.1)

| Métrica | Resultado |
|---------|-----------|
| Testes automatizados | 120 passed, 0 failed |
| Registro de 10.000 sensores | < 10s |
| Cache throughput | > 10.000 ops/s |
| WMI Pool — 50 hosts simultâneos | 50/50 sem conflito |
| Rate Limiter — context manager | thread-safe |
| EventQueue dedup | janela configurável |

---



### Resumo

Versão 2.0 representa uma reescrita completa da camada de coleta (probe) com arquitetura enterprise,
inspirada em PRTG, Zabbix, CheckMK e Datadog. Introduz protocol engines dedicados, connection pooling,
adaptive monitoring, metric cache, AIOps engine com ML, segurança com Vault e uma suite de 77 testes
automatizados com 0 falhas.

---

### Adicionado

#### Protocol Engines (`probe/protocol_engines/`)
- `base_engine.py` — interface abstrata `BaseProtocolEngine` com `EngineResult` padronizado
- `icmp_engine.py` — ICMP ping com count, timeout, retries, jitter e packet loss
- `tcp_engine.py` — TCP port check com medição de latência de conexão
- `snmp_engine.py` — SNMP v1/v2c/v3 com GetBulk, GetNext e fallback automático; compatível com pysnmp 7.x
- `registry_engine.py` — leitura remota de Windows Registry
- `docker_engine.py` — Docker API (containers, stats, health)
- `kubernetes_engine.py` — Kubernetes API (pods, nodes, deployments)
- `__init__.py` — exports centralizados

#### Connection Pools (`probe/connection_pool/`)
- `snmp_pool.py` — pool de sessões SNMP com limite por host, reuso e stats em tempo real
- `tcp_pool.py` — pool de sockets TCP com keep-alive
- `__init__.py`

#### Engine Core (`probe/engine/`)
- `pre_check.py` — `ConnectivityPreCheck` com cache TTL 30s; valida ICMP, TCP e SNMP antes de sensores pesados
- `metric_cache.py` — cache Redis + fallback local; TTL 5s para CPU/RAM, 10s para disco/serviços; hit ratio tracking
- `adaptive_monitor.py` — intervalos dinâmicos 30s (critical) / 60s (warning) / 300s (normal); restaura após 5 ciclos OK
- `internal_metrics.py` — coleta métricas internas via psutil; alerta em 512MB RAM e 80% de fila
- `prometheus_exporter.py` — exporta métricas na porta 9090, atualiza a cada 15s

#### Event Engine (`probe/event_engine/`)
- `wmi_event_listener.py` — captura eventos WMI do Windows
- `docker_event_listener.py` — captura eventos Docker (start, stop, die, health_status)
- `kubernetes_event_listener.py` — captura eventos Kubernetes (Warning, Normal)

#### Segurança (`probe/security/`)
- `credential_manager.py` — Fernet encryption, HMAC integrity check, redação automática de senhas em logs
- `vault_client.py` — suporte a HashiCorp Vault e Azure Key Vault com fallback gracioso

#### AIOps (`ai-agent/`)
- `anomaly_detector.py` — Isolation Forest (scikit-learn); janela 7 dias, retreino 24h, mínimo 50 amostras
- `failure_predictor.py` — regressão linear para predição de breach; horizonte 24h, intervalo de confiança ±1σ
- `event_correlator.py` — correlação temporal em janela de 5 min; causa raiz por severidade e ordem temporal

#### API (`api/routers/`)
- `multi_probe.py` — gestão de múltiplas probes com tipos (datacenter, cloud, edge) e threshold offline 120s
- `timescale_migration.py` — migração para TimescaleDB com hypertables e retention policy

#### Testes (`tests/`)
- `test_audit_enterprise.py` — 77 testes cobrindo todos os 17 componentes da arquitetura enterprise
  - Seção 1: Arquitetura Geral (6 testes)
  - Seção 2: Protocol Engines (14 testes)
  - Seção 3: Connection Pools (6 testes)
  - Seção 4: Scheduler (6 testes)
  - Seção 5: Worker Pool (5 testes)
  - Seção 6: Metric Cache (8 testes)
  - Seção 7: Pre-Check Conectividade (6 testes)
  - Seção 8: Adaptive Monitor (7 testes)
  - Seção 9: Segurança (5 testes)
  - Seção 10: AIOps (8 testes)
  - Seção 11: Escalabilidade/Benchmarks (4 testes)
  - Seção 12: Multi-Probe API (2 testes)

#### Documentação
- `docs/ENTERPRISE_MONITORING_ARCHITECTURE.md` — arquitetura completa v2.0
- `CHANGELOG.md` — este arquivo
- `README.md` atualizado para v2.0 com badges, tabelas e estrutura revisada

---

### Alterado

- `probe/protocol_engines/snmp_engine.py` — import atualizado de `pysnmp.hlapi.v1arch.asyncio.sync` (inexistente) para `pysnmp.hlapi.v3arch.asyncio` (API correta do pysnmp 7.x)
- `README.md` — versão atualizada de 1.0.0 para 2.0.0; seções de arquitetura, tecnologias e roadmap revisadas
- Badge de versão atualizado para `2.0.0`
- Badge de testes adicionado: `77 passed`

---

### Corrigido

- Compatibilidade do pysnmp com Python 3.13: substituído `pysnmp 4.4.12` (incompatível com `pyasn1.compat.octets` removido) por `pysnmp 7.1.22`
- Import path do SNMP engine corrigido para `pysnmp.hlapi.v3arch.asyncio` com aliases snake_case (`get_cmd`, `bulk_cmd`, `next_cmd`)
- Teste `test_17_snmp_engine_host_invalido_retorna_unknown` que estava sendo pulado (skipped) agora passa com pysnmp 7.x instalado

---

### Performance (Benchmarks v2.0)

Medidos na suite de testes em Python 3.13 / Windows:

| Métrica | Resultado |
|---------|-----------|
| Registro de 10.000 sensores (500 hosts × 20) | < 10s |
| Memória para 10.000 sensores | < 200MB |
| Cache throughput (set + get) | > 10.000 ops/s |
| AdaptiveMonitor throughput | > 5.000 updates/s |
| WorkerPool (500 tasks, 20 workers) | < 5s |
| 200 tarefas paralelas (20 workers) | ~0.1s |
| Pre-check cache hit | < 50ms |

---

## [1.0.0] — 2026-03-04

### Adicionado

#### Core
- Sistema completo de monitoramento agentless
- Monitoramento Windows via WMI (local e remoto)
- Monitoramento SNMP v1/v2c
- Monitoramento Docker (containers, imagens, volumes, redes)
- Monitoramento Kubernetes (pods, services, deployments, nodes)
- Ping/ICMP para todos os hosts
- Auto-discovery de serviços e dispositivos

#### AIOps e IA
- Motor AIOps com IA híbrida (Ollama local + OpenAI cloud)
- Fallback automático entre modelos
- Base de conhecimento com 80+ soluções documentadas
- Auto-remediação de incidentes
- Análise de causa raiz
- Sugestões inteligentes de otimização

#### Interface
- Dashboard executivo
- NOC em tempo real (estilo CheckMK)
- Métricas Grafana-style (Servidores, Rede, WebApps, Kubernetes, Personalizado)
- Sistema de incidentes com acknowledgement
- Janelas de manutenção
- Relatórios personalizados (PDF/Excel)
- Tema moderno responsivo com dark mode para NOC

#### Segurança e Autenticação
- JWT com refresh tokens
- LDAP/Active Directory
- SAML 2.0 SSO
- Azure AD/Entra ID
- OAuth 2.0
- MFA (TOTP)
- Políticas de senha avançadas
- WAF (Web Application Firewall)
- Conformidade LGPD e ISO 27001

#### Integrações
- TOPdesk — criação automática de tickets
- GLPI — integração completa
- Zammad — help desk moderno
- Microsoft Dynamics 365
- Microsoft Teams — alertas em canais
- Email (SMTP configurável)
- Twilio SMS
- WhatsApp Business

#### Instaladores
- MSI profissional com WiX Toolset
- Instalador BAT para domínio AD
- Instalador BAT para workgroup
- Instalador BAT para Entra ID
- Deploy em massa via GPO
- Auto-start como serviço Windows

#### Multi-tenant
- Suporte a múltiplas empresas/clientes
- Isolamento de dados por tenant
- Gestão de usuários por tenant

#### API
- 100+ endpoints REST
- WebSocket para tempo real
- Swagger/OpenAPI automático
- Rate limiting
- CORS configurável

---

*Coruja Monitor — Monitoramento Inteligente para Infraestrutura de TI*
