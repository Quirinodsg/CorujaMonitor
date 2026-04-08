# Plano de Implementação: Suite de Testes Completa Coruja Monitor v3.0

## Visão Geral

Implementação incremental da suite de testes abrangente para o Coruja Monitor v3.0. Cada tarefa constrói sobre as anteriores, começando pela infraestrutura compartilhada (utilitários, fixtures, configuração), seguida pelos testes unitários e PBT por módulo, integração, E2E, e finalizando com relatório automatizado. Linguagem: Python 3.11+ com pytest, Hypothesis, fakeredis.

## Tarefas

- [x] 1. Configurar infraestrutura da suite de testes
  - [x] 1.1 Criar estrutura de diretórios e arquivos `__init__.py`
    - Criar diretórios: `tests/unit/`, `tests/integration/`, `tests/e2e/`, `tests/load/`, `tests/chaos/`, `tests/ai/`, `tests/api/`, `tests/security/`, `tests/frontend/`, `tests/probe/`, `tests/database/`, `tests/pbt/`, `tests/utils/`, `tests/report/`
    - Criar `__init__.py` em cada diretório
    - _Requisitos: 1.1_

  - [x] 1.2 Criar `pytest.ini` com markers e configuração
    - Definir markers: unit, integration, e2e, load, chaos, ai, security, pbt, slow
    - Configurar `addopts = -v --tb=short --strict-markers` e `testpaths = tests`
    - _Requisitos: 1.1, 1.3_

  - [x] 1.3 Criar `.coveragerc` com cobertura ≥85%
    - Source: core, engine, topology_engine, event_processor, ai_agents, alert_engine, sensor_dsl
    - `fail_under = 85`, `show_missing = true`
    - _Requisitos: 1.5_

  - [x] 1.4 Criar `tests/conftest.py` com fixtures globais
    - Fixture `mock_redis`: fakeredis ou mock manual com suporte a XADD/XREADGROUP/XACK
    - Fixture `mock_db`: SQLAlchemy session com SQLite in-memory
    - Fixtures `event_simulator`, `topology_simulator`, `chaos_engine`
    - _Requisitos: 1.2, 1.4_

  - [x] 1.5 Criar `tests/utils/hypothesis_strategies.py` com strategies reutilizáveis
    - Strategies para Host, Sensor, Metric, Event, Alert, TopologyNode
    - Strategy `dag_st` para DAGs válidos (nós + arestas sem ciclo)
    - Strategy `dsl_source_st` para source DSL válido
    - Strategy `threshold_st` para thresholds
    - _Requisitos: 1.2_

- [x] 2. Criar utilitários compartilhados (`tests/utils/`)
  - [x] 2.1 Implementar `tests/utils/event_simulator.py`
    - Classe `EventSimulator` com métodos: `generate_metric`, `generate_event`, `generate_metric_stream`, `generate_state_transitions`, `generate_flood`
    - _Requisitos: 1.2, 5.1, 7.4, 14.6_

  - [x] 2.2 Implementar `tests/utils/topology_simulator.py`
    - Classe `TopologySimulator` com métodos: `create_simple_topology`, `create_datacenter_topology`, `inject_failure`, `create_cascade_scenario`
    - _Requisitos: 1.2, 8.2, 12.3_

  - [x] 2.3 Implementar `tests/utils/load_generator.py`
    - Classe `LoadGenerator` com métodos: `generate_hosts`, `generate_sensors`, `generate_metrics_batch`, `simulate_collection_cycle`
    - Suportar 1000 hosts × 50 sensores (50.000 métricas/ciclo)
    - _Requisitos: 1.2, 13.1_

  - [x] 2.4 Implementar `tests/utils/chaos_engine.py`
    - Classe `ChaosEngine` com context managers: `simulate_redis_offline`, `simulate_api_offline`, `simulate_network_latency`, `simulate_packet_loss`, `simulate_redis_reconnect`
    - _Requisitos: 1.2, 14.1, 14.2, 14.3, 14.4_

- [x] 3. Checkpoint — Verificar infraestrutura base
  - Garantir que todos os imports funcionam, fixtures são carregadas, e `pytest --collect-only tests/` lista os diretórios corretamente. Perguntar ao usuário se há dúvidas.

- [x] 4. Testes unitários e PBT do Dependency Engine (DAG)
  - [x] 4.1 Criar `tests/unit/test_dependency_engine.py`
    - Testar add_sensor, add_dependency, rejeição de ciclos, suspensão em cascata, reativação, isolamento entre hosts, cache TTL
    - _Requisitos: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

  - [ ]* 4.2 Criar `tests/pbt/test_pbt_dag.py` — Property 1: DAG invariante
    - **Property 1: DAG invariante — grafo nunca contém ciclos**
    - **Valida: Requisitos 3.1, 3.2**

  - [ ]* 4.3 Criar `tests/pbt/test_pbt_dag.py` — Property 2: Suspensão/reativação round-trip
    - **Property 2: Suspensão em cascata e reativação round-trip**
    - **Valida: Requisitos 3.3, 3.4**

  - [ ]* 4.4 Criar `tests/pbt/test_pbt_dag.py` — Property 3: Isolamento entre hosts
    - **Property 3: Isolamento de estado entre hosts**
    - **Valida: Requisitos 3.5**

- [x] 5. Testes unitários e PBT do Event Processor
  - [x] 5.1 Criar `tests/unit/test_event_processor.py`
    - Testar idempotência, transições de estado (ok→warning→critical→ok), thresholds dinâmicos, modo "lower is worse", independência entre sensores, persistência batch ≤500
    - _Requisitos: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_

  - [ ]* 5.2 Criar `tests/pbt/test_pbt_event_processor.py` — Property 4: Idempotência
    - **Property 4: Idempotência do EventProcessor — transições de estado**
    - **Valida: Requisitos 5.1, 5.2**

  - [ ]* 5.3 Criar `tests/pbt/test_pbt_event_processor.py` — Property 5: Thresholds
    - **Property 5: Avaliação de thresholds — corretude e modo invertido**
    - **Valida: Requisitos 5.3, 5.4**

  - [ ]* 5.4 Criar `tests/pbt/test_pbt_event_processor.py` — Property 6: Independência de sensores
    - **Property 6: Independência de estado entre sensores**
    - **Valida: Requisitos 5.5**

- [x] 6. Testes unitários e PBT do Streaming Redis
  - [x] 6.1 Criar `tests/unit/test_streaming_redis.py`
    - Testar XADD batch 500, XREADGROUP consumer groups, at-least-once delivery, buffer offline (deque 10k), reconexão e drenagem do buffer
    - _Requisitos: 4.1, 4.2, 4.3, 4.4, 4.5_

  - [ ]* 6.2 Criar `tests/pbt/test_pbt_streaming.py` — Property 7: Buffer round-trip
    - **Property 7: Buffer offline round-trip — armazenamento e drenagem sem perda**
    - **Valida: Requisitos 4.4, 4.5, 14.5**

  - [ ]* 6.3 Criar `tests/pbt/test_pbt_streaming.py` — Property 8: Buffer FIFO
    - **Property 8: Buffer FIFO — descarte de métricas mais antigas**
    - **Valida: Requisitos 2.6**

  - [ ]* 6.4 Criar `tests/pbt/test_pbt_streaming.py` — Property 9: Batch ≤500
    - **Property 9: Batch persistence — lotes ≤500**
    - **Valida: Requisitos 4.1, 5.6, 17.1**

- [x] 7. Checkpoint — Verificar testes unitários e PBT dos módulos core
  - Garantir que todos os testes passam com `pytest tests/unit/ tests/pbt/ -v`. Perguntar ao usuário se há dúvidas.

- [x] 8. Testes unitários e PBT do AI Pipeline
  - [x] 8.1 Criar `tests/unit/test_ai_pipeline.py`
    - Testar AnomalyDetection (baseline, >3σ), pipeline resiliente (agente falha), AutoRemediation (confiança ≥85%), FeedbackLoop (outcome, pesos), RootCause (nó pai), CircuitBreaker, correlação janela 5min
    - _Requisitos: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8_

  - [ ]* 8.2 Criar `tests/pbt/test_pbt_ai_pipeline.py` — Property 10: Anomalia >3σ
    - **Property 10: Detecção de anomalia >3σ**
    - **Valida: Requisitos 6.1**

  - [ ]* 8.3 Criar `tests/pbt/test_pbt_ai_pipeline.py` — Property 11: Pipeline resiliente
    - **Property 11: Resiliência do pipeline — falha isolada por agente**
    - **Valida: Requisitos 6.2**

  - [ ]* 8.4 Criar `tests/pbt/test_pbt_ai_pipeline.py` — Property 12: Auto-remediação
    - **Property 12: Auto-remediação condicionada à confiança**
    - **Valida: Requisitos 6.3**

  - [ ]* 8.5 Criar `tests/pbt/test_pbt_ai_pipeline.py` — Property 13: FeedbackLoop outcome
    - **Property 13: Classificação de outcome do FeedbackLoop**
    - **Valida: Requisitos 6.4, 6.7**

  - [ ]* 8.6 Criar `tests/pbt/test_pbt_ai_pipeline.py` — Property 14: Root cause
    - **Property 14: Root cause — identificação do nó pai**
    - **Valida: Requisitos 6.5**

  - [ ]* 8.7 Criar `tests/pbt/test_pbt_ai_pipeline.py` — Property 15: Circuit breaker
    - **Property 15: Circuit breaker — abertura e fechamento**
    - **Valida: Requisitos 6.6, 15.4**

- [x] 9. Testes unitários e PBT do Alert Engine
  - [x] 9.1 Criar `tests/unit/test_alert_engine.py`
    - Testar supressão de duplicados (TTL 5min), agrupamento por host/janela, priorização (score 4 fatores), flood protection (>100 ev/min), notificador retry 3x backoff, supressão topológica, janelas de manutenção
    - _Requisitos: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7_

  - [ ]* 9.2 Criar `tests/pbt/test_pbt_alert_engine.py` — Property 16: Correlação temporal
    - **Property 16: Correlação de eventos em janela temporal**
    - **Valida: Requisitos 6.8, 7.2**

  - [ ]* 9.3 Criar `tests/pbt/test_pbt_alert_engine.py` — Property 17: Supressão de duplicados
    - **Property 17: Supressão de duplicados — idempotência de alertas**
    - **Valida: Requisitos 7.1**

  - [ ]* 9.4 Criar `tests/pbt/test_pbt_alert_engine.py` — Property 18: Score [0,1]
    - **Property 18: Score de priorização no intervalo [0, 1]**
    - **Valida: Requisitos 7.3**

  - [ ]* 9.5 Criar `tests/pbt/test_pbt_alert_engine.py` — Property 19: Flood protection
    - **Property 19: Flood protection — consolidação de alertas**
    - **Valida: Requisitos 7.4**

  - [ ]* 9.6 Criar `tests/pbt/test_pbt_alert_engine.py` — Property 20: Supressão topológica
    - **Property 20: Supressão topológica — pai em falha suprime filhos**
    - **Valida: Requisitos 7.6**

  - [ ]* 9.7 Criar `tests/pbt/test_pbt_alert_engine.py` — Property 21: Janelas de manutenção
    - **Property 21: Janelas de manutenção — filtragem de eventos**
    - **Valida: Requisitos 7.7**

- [x] 10. Testes unitários e PBT do Topology Engine
  - [x] 10.1 Criar `tests/unit/test_topology_engine.py`
    - Testar serialização round-trip (to_dict/from_dict), blast radius BFS, 4 camadas hierárquicas, ancestors/descendants, geração de edges
    - _Requisitos: 8.1, 8.2, 8.3, 8.4, 8.5_

  - [ ]* 10.2 Criar `tests/pbt/test_pbt_topology.py` — Property 22: Round-trip
    - **Property 22: Serialização round-trip do TopologyGraph**
    - **Valida: Requisitos 8.1**

  - [ ]* 10.3 Criar `tests/pbt/test_pbt_topology.py` — Property 23: Blast radius
    - **Property 23: Blast radius = descendentes no grafo**
    - **Valida: Requisitos 8.2, 8.4**

- [x] 11. Testes unitários e PBT do Sensor DSL
  - [x] 11.1 Criar `tests/unit/test_sensor_dsl.py`
    - Testar Lexer (tokenização), Parser (SensorNode), herança de templates, erros de sintaxe (DSLSyntaxError), protocolo inválido, remoção de comentários
    - _Requisitos: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7_

  - [ ]* 11.2 Criar `tests/pbt/test_pbt_sensor_dsl.py` — Property 24: DSL round-trip
    - **Property 24: DSL round-trip — parse(print(parse(source))) ≡ parse(source)**
    - **Valida: Requisitos 9.1**

  - [ ]* 11.3 Criar `tests/pbt/test_pbt_sensor_dsl.py` — Property 25: Herança de templates
    - **Property 25: Herança de templates — campos herdados e sobrescritos**
    - **Valida: Requisitos 9.4**

  - [ ]* 11.4 Criar `tests/pbt/test_pbt_sensor_dsl.py` — Property 26: Protocolo inválido
    - **Property 26: DSL rejeita protocolos inválidos**
    - **Valida: Requisitos 9.5, 9.6**

  - [ ]* 11.5 Criar `tests/pbt/test_pbt_sensor_dsl.py` — Property 27: Comentários
    - **Property 27: Comentários não afetam resultado da compilação**
    - **Valida: Requisitos 9.7**

- [x] 12. Checkpoint — Verificar todos os testes unitários e PBT
  - Garantir que todos os testes passam com `pytest tests/unit/ tests/pbt/ -v`. Perguntar ao usuário se há dúvidas.

- [x] 13. Testes do Probe (Sonda)
  - [x] 13.1 Criar `tests/probe/test_collectors.py`
    - Testar coletores WMI, SNMP, ICMP, TCP, Docker, Kubernetes com mocks de rede
    - _Requisitos: 2.1, 2.2, 2.3_

  - [x] 13.2 Criar `tests/probe/test_connection_pools.py` e `test_rate_limiter.py`
    - Testar pool de conexões (aquisição, liberação, timeout) e rate limiter global
    - _Requisitos: 2.4, 2.5_

  - [x] 13.3 Criar `tests/probe/test_buffer_offline.py` e `test_orchestrator.py`
    - Testar buffer offline (deque 10k, FIFO), ProbeOrchestrator (coleta paralela, isolamento de falhas)
    - _Requisitos: 2.6, 2.7_

  - [ ]* 13.4 Criar `tests/pbt/test_pbt_probe.py` — Property 33: Isolamento de falhas
    - **Property 33: Isolamento de falhas entre coletores do Probe**
    - **Valida: Requisitos 2.7, 15.5**

  - [ ]* 13.5 Criar `tests/pbt/test_pbt_probe.py` — Property 34: Retry backoff
    - **Property 34: Retry com backoff exponencial no AlertNotifier**
    - **Valida: Requisitos 7.5, 15.2**

- [x] 14. Testes da API FastAPI
  - [x] 14.1 Criar `tests/api/test_endpoints_v3.py` e `test_endpoints_v2.py`
    - Testar endpoints v3: `/observability/health-score`, `/alerts/intelligent`, `/topology/graph`, `/topology/impact/{node_id}`
    - Testar endpoints v2: `/dashboard/summary`, `/servers`, `/sensors`, `/metrics`, `/incidents`
    - _Requisitos: 10.1, 10.2_

  - [x] 14.2 Criar `tests/api/test_auth.py`, `test_websocket.py`, `test_validation.py`
    - Testar autenticação (401 sem token), WebSocket `/ws/observability`, validação de parâmetros (422)
    - _Requisitos: 10.3, 10.4, 10.5, 10.6_

  - [ ]* 14.3 Criar `tests/pbt/test_pbt_api.py` — Property 28: Auth 401
    - **Property 28: Autenticação — endpoints protegidos retornam 401**
    - **Valida: Requisitos 10.3, 16.1**

  - [ ]* 14.4 Criar `tests/pbt/test_pbt_api.py` — Property 29: Validação 422
    - **Property 29: Validação de parâmetros — API retorna 422**
    - **Valida: Requisitos 10.5**

  - [ ]* 14.5 Criar `tests/pbt/test_pbt_api.py` — Property 30: Sem dados sensíveis
    - **Property 30: Respostas da API não expõem dados sensíveis**
    - **Valida: Requisitos 16.2**

- [x] 15. Testes de Segurança
  - [x] 15.1 Criar `tests/security/test_auth_enforcement.py`, `test_credential_encryption.py`, `test_waf.py`, `test_token_expiry.py`
    - Testar endpoints protegidos (401), criptografia Fernet, WAF (SQL injection, XSS), expiração de tokens
    - _Requisitos: 16.1, 16.2, 16.3, 16.4, 16.5_

  - [ ]* 15.2 Criar `tests/pbt/test_pbt_security.py` — Property 31: Fernet round-trip
    - **Property 31: Criptografia Fernet round-trip de credenciais**
    - **Valida: Requisitos 16.3**

  - [ ]* 15.3 Criar `tests/pbt/test_pbt_security.py` — Property 32: WAF
    - **Property 32: WAF bloqueia payloads maliciosos**
    - **Valida: Requisitos 16.4**

- [x] 16. Checkpoint — Verificar testes unitários, PBT, probe, API e segurança
  - Garantir que todos os testes passam. Perguntar ao usuário se há dúvidas.

- [x] 17. Testes de Integração Cross-Module
  - [x] 17.1 Criar `tests/integration/test_metric_to_alert_flow.py`
    - Fluxo completo: Métrica → EventProcessor → AI Pipeline → AlertEngine → Notificação
    - _Requisitos: 12.1, 12.5_

  - [x] 17.2 Criar `tests/integration/test_host_down_scenario.py`
    - Cenário HOST DOWN: ping falha → WMI/TCP suspensos via DependencyEngine → evento único → alerta
    - _Requisitos: 12.2_

  - [x] 17.3 Criar `tests/integration/test_cascade_failure.py`
    - Cenário CASCADE FAILURE: switch falha → TopologyEngine blast radius → alerta consolidado
    - _Requisitos: 12.3_

  - [x] 17.4 Criar `tests/integration/test_ai_decision_flow.py`
    - Cenário AI DECISION: anomalia → correlação → causa raiz → decisão → auto-remediação ≥85%
    - _Requisitos: 12.4_

  - [ ]* 17.5 Criar `tests/pbt/test_pbt_integration.py` — Property 35: Pipeline sem perda
    - **Property 35: Pipeline cross-module sem perda de dados**
    - **Valida: Requisitos 12.5**

- [x] 18. Testes E2E — Cenários Críticos Obrigatórios
  - [x] 18.1 Criar `tests/e2e/test_host_down.py`
    - Cenário HOST DOWN: ping falha → suspensão → evento único → alerta <30s
    - _Requisitos: 19.1_

  - [x] 18.2 Criar `tests/e2e/test_redis_offline.py`
    - Cenário REDIS OFFLINE: buffer local → coleta continua → reconexão → perda = 0%
    - _Requisitos: 19.2_

  - [x] 18.3 Criar `tests/e2e/test_event_flood.py`
    - Cenário EVENT FLOOD: 1000 eventos/min → flood protection → 1 alerta consolidado
    - _Requisitos: 19.3_

  - [x] 18.4 Criar `tests/e2e/test_cascade_failure.py`
    - Cenário CASCADE FAILURE: switch falha → topologia → blast radius → alerta
    - _Requisitos: 19.4_

  - [x] 18.5 Criar `tests/e2e/test_high_load.py`
    - Cenário HIGH LOAD: 1000 hosts → throughput mantido → latência <200ms
    - _Requisitos: 19.5_

  - [x] 18.6 Criar `tests/e2e/test_ai_decision.py`
    - Cenário AI DECISION: anomalia → pipeline completo → remediação ≥85% → feedback
    - _Requisitos: 19.6_

  - [x] 18.7 Criar `tests/e2e/test_websocket_drop.py`
    - Cenário WEBSOCKET DROP: conexão perdida → reconexão automática → dados atualizados
    - _Requisitos: 19.7_

- [x] 19. Testes de Carga, Chaos, Frontend e Database
  - [x] 19.1 Criar `tests/load/test_throughput.py` e `test_api_latency.py`
    - Simular 1000 hosts × 50 sensores, validar throughput ≥1000 métricas/s, latência API <200ms
    - _Requisitos: 13.1, 13.2, 13.3, 13.4_

  - [x] 19.2 Criar `tests/chaos/test_redis_failure.py`, `test_network_latency.py`, `test_packet_loss.py`, `test_event_flood_chaos.py`
    - Usar ChaosEngine para simular Redis offline, latência 100-500ms, perda de pacotes 10-50%, event flood
    - _Requisitos: 14.1, 14.2, 14.3, 14.4, 14.5, 14.6_

  - [x] 19.3 Criar `tests/ai/test_anomaly_detection.py`, `test_correlation.py`, `test_root_cause.py`, `test_feedback_loop.py`, `test_circuit_breaker.py`
    - Testes específicos de IA: baseline, correlação temporal, RCA, feedback, circuit breaker
    - _Requisitos: 6.1, 6.2, 6.5, 6.6, 6.7, 6.8_

  - [x] 19.4 Criar `tests/frontend/test_dashboard_render.py`, `test_noc_mode.py`, `test_websocket_reconnect.py`
    - Testar renderização de componentes v3, modo NOC, reconexão WebSocket
    - _Requisitos: 11.1, 11.2, 11.3, 11.4_

  - [x] 19.5 Criar `tests/database/test_hypertable.py`, `test_retention.py`, `test_compression.py`, `test_query_performance.py`
    - Testar batch insert ≤500, retenção 90 dias, compressão 7 dias, queries <1s
    - _Requisitos: 17.1, 17.2, 17.3, 17.4, 17.5_

- [x] 20. Relatório automatizado e resiliência
  - [x] 20.1 Criar `tests/report/metrics_collector.py` e `report_generator.py`
    - Dataclasses `TestMetrics` e `ChaosScenario`
    - `ReportGenerator` com `collect_metrics`, `validate_thresholds`, `generate_report`
    - Validar: perda >0% → FAIL, atraso >30s → FAIL, IA não resolve → FAIL
    - _Requisitos: 18.1, 18.2, 18.3, 18.4, 18.5_

  - [x] 20.2 Criar testes de resiliência em `tests/chaos/` e `tests/unit/`
    - Auto-reconexão WebSocket com backoff, retry 3x AlertNotifier, fallback DuplicateSuppressor, isolamento de falhas no Probe
    - _Requisitos: 15.1, 15.2, 15.3, 15.4, 15.5_

- [x] 21. Checkpoint final — Validar suite completa
  - Executar `pytest tests/ -v --cov=core --cov=engine --cov=topology_engine --cov=event_processor --cov=ai_agents --cov=alert_engine --cov=sensor_dsl --cov-report=term-missing --cov-fail-under=85`
  - Garantir que todos os testes passam e cobertura ≥85%. Perguntar ao usuário se há dúvidas.

## Notas

- Tarefas marcadas com `*` são opcionais e podem ser puladas para um MVP mais rápido
- Cada tarefa referencia requisitos específicos para rastreabilidade
- Checkpoints garantem validação incremental
- Testes property-based validam propriedades universais de corretude via Hypothesis
- Testes unitários validam exemplos específicos e edge cases
