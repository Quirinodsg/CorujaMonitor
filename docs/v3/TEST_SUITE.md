# Coruja Monitor v3.0 — Suite de Testes

## Resumo

| Arquivo | Testes | Tipo | Cobertura |
|---------|--------|------|-----------|
| `tests/test_spec_central.py` | 25 | Unitário | core/spec/ |
| `tests/test_dependency_engine.py` | 19 | Unitário + Property | engine/ |
| `tests/test_topology_engine.py` | 16 | Unitário + Property | topology_engine/ |
| `tests/test_event_processor.py` | 25 | Unitário + Property | event_processor/ |
| `tests/test_ai_agents.py` | 29 | Unitário + Property | ai_agents/ |
| `tests/test_alert_engine.py` | 25 | Unitário + Property | alert_engine/ |
| `tests/test_sensor_dsl.py` | 35 | Unitário + Property | sensor_dsl/ |
| `tests/test_pbt_properties.py` | 4 | Property-based (Hypothesis) | core/ + streaming |
| `tests/test_load_simulation.py` | 3 | Carga + Benchmark | ProbeManager |
| `tests/test_regression_v2.py` | 5 | Regressão | módulos v2.0 |
| `tests/test_audit_enterprise.py` | 120 | Auditoria Enterprise | sistema completo |
| **TOTAL** | **349** | | **≥80% módulos críticos** |

---

## Como Executar

```bash
# Todos os testes
pytest tests/ -v

# Com cobertura
pytest tests/ --cov=core --cov=engine --cov=topology_engine \
  --cov=event_processor --cov=ai_agents --cov=alert_engine \
  --cov-report=term-missing --cov-fail-under=80

# Apenas property-based (Hypothesis)
pytest tests/test_pbt_properties.py -v

# Apenas regressão v2
pytest tests/test_regression_v2.py -v

# Benchmark de carga (1000 hosts × 50 sensores)
pytest tests/test_load_simulation.py -v --benchmark-only
```

---

## Properties (Hypothesis) — 23 Invariantes

### Spec Central (Properties 1-2)
| Property | Descrição | Arquivo |
|----------|-----------|---------|
| 1 | Round-trip de serialização Pydantic: `model → JSON → model` produz objeto equivalente | test_pbt_properties.py |
| 2 | Campos obrigatórios ausentes lançam `ValidationError` | test_pbt_properties.py |

### Dependency Engine (Properties 3-4)
| Property | Descrição | Arquivo |
|----------|-----------|---------|
| 3 | DAG nunca contém ciclos após operações de adição | test_dependency_engine.py |
| 4 | Suspensão/reativação round-trip: pai critical → filhos suspensos; pai ok → filhos reativados | test_dependency_engine.py |

### Topology Engine (Properties 5-6)
| Property | Descrição | Arquivo |
|----------|-----------|---------|
| 5 | `blast_radius.total_impact == len(nx.descendants(graph, node_id))` | test_topology_engine.py |
| 6 | Round-trip de persistência: salvar e recarregar grafo preserva nós, arestas e hierarquia | test_topology_engine.py |

### Event Processor (Property 7)
| Property | Descrição | Arquivo |
|----------|-----------|---------|
| 7 | Idempotência: dois `critical` consecutivos do mesmo sensor geram apenas 1 Event | test_event_processor.py |

### AI Agents (Properties 8-12)
| Property | Descrição | Arquivo |
|----------|-----------|---------|
| 8 | Anomalia detectada quando `|v - μ| > 3σ` do baseline | test_ai_agents.py |
| 9 | Pipeline continua após falha de agente individual (circuit breaker) | test_ai_agents.py |
| 10 | AutoRemediation só executa com confiança ≥ 85% | test_ai_agents.py |
| 11 | FeedbackLoop classifica outcome por tempo de resolução | test_ai_agents.py |
| 12 | RootCause identifica nó pai com confiança ≥ 0.8 quando múltiplos filhos falham | test_ai_agents.py |

### Alert Engine (Properties 13-17)
| Property | Descrição | Arquivo |
|----------|-----------|---------|
| 13 | RootCause gera exatamente 1 Alert consolidado por grupo correlacionado | test_alert_engine.py |
| 14 | DuplicateSuppressor impede alertas duplicados (idempotência) | test_alert_engine.py |
| 15 | Score de prioridade respeita fórmula: sev×0.40 + hosts×0.30 + impacto×0.20 + horário×0.10 | test_alert_engine.py |
| 16 | Flood protection: >100 eventos/min → 1 alerta de alta prioridade | test_alert_engine.py |
| 17 | Alertas suprimidos durante janela de manutenção | test_alert_engine.py |

### Sensor DSL (Properties 18-19)
| Property | Descrição | Arquivo |
|----------|-----------|---------|
| 18 | DSL round-trip: `parse → print → parse` produz sensor equivalente | test_sensor_dsl.py |
| 19 | DSL rejeita protocolos inválidos com `DSLSyntaxError` descritivo | test_sensor_dsl.py |

### Distributed Probes (Properties 20-21)
| Property | Descrição | Arquivo |
|----------|-----------|---------|
| 20 | Cada host é monitorado por exatamente 1 ProbeNode ativa | test_load_simulation.py |
| 21 | Balanceamento respeita capacidade máxima de 80% por probe | test_load_simulation.py |

### Streaming (Properties 22-23)
| Property | Descrição | Arquivo |
|----------|-----------|---------|
| 22 | Stream consumer processa em batches de no máximo 500 métricas | test_pbt_properties.py |
| 23 | At-least-once delivery: métricas não-ACKed são reprocessadas | test_pbt_properties.py |

---

## Pontos Fortes da Suite

### 1. Property-Based Testing com Hypothesis
Usa geração automática de casos de teste para encontrar edge cases que testes manuais não cobrem. Configurado com `max_examples=100` (CI) e `max_examples=500` (thorough).

### 2. Testes de Regressão v2.0
Garante que nenhum módulo existente foi quebrado pela migração v3. Cobre `wmi_pool`, `smart_collector`, `global_rate_limiter`, `event_queue`, `stream_producer`.

### 3. Benchmark de Carga
`test_load_simulation.py` simula 1.000 hosts × 50 sensores = 50.000 sensores simultâneos. Valida latência média < 2 segundos e zero perda de dados.

### 4. Testes de Idempotência
Property 7 (EventProcessor) e Property 14 (DuplicateSuppressor) garantem que o sistema não gera eventos/alertas duplicados mesmo sob condições de retry.

### 5. Testes de Circuit Breaker
Property 9 valida que o pipeline de agentes continua funcionando mesmo quando um agente individual falha repetidamente (>50% nas últimas 10 execuções).

### 6. Cobertura ≥80%
Configurado em `pytest.ini` com `--cov-fail-under=80` para os módulos críticos: `core/`, `engine/`, `topology_engine/`, `event_processor/`, `ai_agents/`, `alert_engine/`.

---

## Configuração (pytest.ini)

```ini
[pytest]
testpaths = tests
addopts = --tb=short -q
          --cov=core --cov=engine --cov=topology_engine
          --cov=event_processor --cov=ai_agents --cov=alert_engine
          --cov-report=term-missing
```
