# Tasks de Implementacao - Coruja Enterprise Architecture

- [ ] 1. Fundacao - Protocol Engine Base e Engines ICMP/TCP
  - [ ] 1.1 Criar `probe/protocol_engines/__init__.py` com exports dos engines
  - [ ] 1.2 Criar `probe/protocol_engines/base_engine.py` com classe abstrata `BaseProtocolEngine` e interface `execute(sensor) -> SensorResult`
  - [ ] 1.3 Criar `probe/protocol_engines/icmp_engine.py` usando `icmplib` ou `ping3`, com suporte a timeout e retries
  - [ ] 1.4 Criar `probe/protocol_engines/tcp_engine.py` com verificacao de porta TCP e timeout configuravel
  - [ ] 1.5 Criar `probe/protocol_engines/registry_engine.py` para leitura de chaves do Windows Registry via `winreg`
  - [ ] 1.6 Criar `probe/protocol_engines/docker_engine.py` para coleta de metricas de containers via Docker SDK (`docker` lib)
  - [ ] 1.7 Criar `probe/protocol_engines/kubernetes_engine.py` para coleta de pods, nodes e deployments via `kubernetes` client
  - [ ] 1.8 Garantir que cada engine retorne `status=unknown` com `error="engine_unavailable"` quando a dependencia nao estiver instalada

- [ ] 2. SNMP Engine com Bulk e Connection Pool SNMP/TCP
  - [ ] 2.1 Criar `probe/protocol_engines/snmp_engine.py` com suporte a SNMP v1/v2c/v3 usando `pysnmp`
  - [ ] 2.2 Implementar `GetBulk` com `max-repetitions=25` para SNMP v2c/v3 no `snmp_engine.py`
  - [ ] 2.3 Implementar fallback para `GetNext` individual quando o dispositivo suportar apenas SNMP v1 ou quando `GetBulk` falhar
  - [ ] 2.4 Implementar SNMP walk na OID `1.3.6.1.2.1.2.2` (ifTable) usando GetBulk no `snmp_engine.py`
  - [ ] 2.5 Criar `probe/connection_pool/__init__.py`
  - [ ] 2.6 Criar `probe/connection_pool/snmp_pool.py` com pool de ate 5 conexoes por host, idle timeout de 300s e limpeza a cada 60s
  - [ ] 2.7 Criar `probe/connection_pool/tcp_pool.py` com pool de ate 10 conexoes por host, idle timeout de 300s e limpeza a cada 60s
  - [ ] 2.8 Integrar `snmp_pool.py` no `snmp_engine.py` para reutilizacao de sessoes SNMP

- [ ] 3. Pre-Check de Conectividade
  - [ ] 3.1 Criar `probe/engine/pre_check.py` com classe `PreCheck`
  - [ ] 3.2 Implementar verificacao em cascata para WMI: ICMP Ping -> TCP porta 135 -> WMI namespace `root/cimv2`
  - [ ] 3.3 Implementar verificacao em cascata para SNMP: ICMP Ping -> UDP porta 161
  - [ ] 3.4 Implementar cache de resultado do pre-check com TTL de 30 segundos por host
  - [ ] 3.5 Garantir que o pre-check complete todas as verificacoes em no maximo 5 segundos por host
  - [ ] 3.6 Retornar `status=critical` com `error="host_unreachable"` quando ICMP falhar, sem executar verificacoes subsequentes

- [ ] 4. Metric Cache (Redis + local)
  - [ ] 4.1 Criar `probe/engine/metric_cache.py` com classe `MetricCache`
  - [ ] 4.2 Implementar backend Redis usando `redis-py` com conexao configuravel via env var
  - [ ] 4.3 Implementar backend de cache em memoria local como fallback automatico quando Redis nao estiver disponivel
  - [ ] 4.4 Aplicar TTL de 5 segundos para metricas de CPU e memoria
  - [ ] 4.5 Aplicar TTL de 10 segundos para metricas de disco e servicos
  - [ ] 4.6 Usar chave de cache no formato `{host}:{sensor_type}:{query_hash}`
  - [ ] 4.7 Expor metodos `get_stats()` retornando `cache_hits`, `cache_misses`, `cache_hit_ratio`

- [ ] 5. Adaptive Monitor
  - [ ] 5.1 Criar `probe/engine/adaptive_monitor.py` com classe `AdaptiveMonitor`
  - [ ] 5.2 Implementar logica de reducao de intervalo para 60s quando qualquer sensor do host retornar `status=warning`
  - [ ] 5.3 Implementar logica de reducao de intervalo para 30s quando qualquer sensor do host retornar `status=critical`
  - [ ] 5.4 Implementar restauracao do intervalo padrao de 300s apos 5 ciclos consecutivos de `status=ok`
  - [ ] 5.5 Registrar cada mudanca de intervalo nos logs com motivo da alteracao

- [ ] 6. Expansao do Sensor Engine
  - [ ] 6.1 Expandir `probe/engine/sensor_engine.py` para importar e registrar todos os protocol engines criados nas tasks 1 e 2
  - [ ] 6.2 Implementar metodo `register_engine(type, handler)` para registro dinamico de novos tipos de sensor
  - [ ] 6.3 Integrar `PreCheck` (task 3) no fluxo de execucao do `sensor_engine.py` antes de despachar para o protocol engine
  - [ ] 6.4 Integrar `MetricCache` (task 4) no `sensor_engine.py` para cache de resultados
  - [ ] 6.5 Integrar `AdaptiveMonitor` (task 5) no `sensor_engine.py` para ajuste dinamico de intervalos
  - [ ] 6.6 Garantir que `SensorResult` inclua campo `execution_ms` com tempo de execucao em milissegundos
  - [ ] 6.7 Implementar auto-discovery no `sensor_engine.py` com execucao automatica a cada 3600 segundos
  - [ ] 6.8 Marcar sensor como `status=unknown` quando recurso descoberto anteriormente nao for mais encontrado

- [ ] 7. Expansao do Scheduler
  - [ ] 7.1 Expandir `probe/engine/scheduler.py` para suportar intervalos de 30s, 60s e 300s
  - [ ] 7.2 Implementar delay escalonado de 3 segundos entre grupos de 10 sensores ao adicionar multiplos sensores simultaneamente
  - [ ] 7.3 Implementar limite de 10 sensores ativos simultaneamente por host
  - [ ] 7.4 Implementar limite de 5 queries WMI simultaneas por host
  - [ ] 7.5 Implementar backoff exponencial para sensores com falhas consecutivas: 30s, 60s, 120s, max 300s
  - [ ] 7.6 Expor endpoint de status com total de sensores, sensores ativos por host, queries WMI por host e proxima execucao

- [ ] 8. Worker Pool - Expansao para 20 Workers
  - [ ] 8.1 Expandir `probe/engine/thread_pool.py` para suportar ate 20 workers paralelos
  - [ ] 8.2 Implementar metodo `resize(n)` para ajuste dinamico do numero de workers em runtime
  - [ ] 8.3 Implementar alerta de nivel WARNING nos logs quando a fila atingir 80% da capacidade
  - [ ] 8.4 Expor metricas internas: `worker_queue_size`, `active_workers`, `completed_tasks`, `failed_tasks`
  - [ ] 8.5 Garantir cancelamento de tarefas que excedam o timeout configurado no sensor, registrando `status=timeout`

- [ ] 9. Internal Metrics (psutil)
  - [ ] 9.1 Criar `probe/engine/internal_metrics.py` com classe `InternalMetricsCollector`
  - [ ] 9.2 Coletar a cada 60 segundos: `probe_cpu_percent`, `probe_memory_mb` usando `psutil`
  - [ ] 9.3 Coletar: `rpc_connections_active`, `wmi_query_latency_ms_avg`, `sensor_execution_time_ms_avg`, `worker_queue_size`, `cache_hit_ratio`
  - [ ] 9.4 Enviar metricas para a API com `sensor_type=probe_internal`
  - [ ] 9.5 Registrar alerta WARNING quando `worker_queue_size` exceder 80% da capacidade maxima
  - [ ] 9.6 Registrar alerta WARNING e reduzir workers para 10 quando `probe_memory_mb` exceder 512 MB
  - [ ] 9.7 Manter log de saude rotativo com as ultimas 1000 entradas de internal metrics

- [ ] 10. Prometheus Exporter
  - [ ] 10.1 Criar `probe/engine/prometheus_exporter.py` com classe `PrometheusExporter`
  - [ ] 10.2 Expor endpoint `/metrics` na porta 9090 no formato Prometheus text/plain usando `prometheus_client`
  - [ ] 10.3 Implementar metricas: `coruja_probe_sensors_total`, `coruja_probe_sensor_execution_seconds`, `coruja_probe_wmi_queries_total`
  - [ ] 10.4 Implementar metricas: `coruja_probe_cache_hits_total`, `coruja_probe_cache_misses_total`, `coruja_probe_worker_queue_size`, `coruja_probe_errors_total`
  - [ ] 10.5 Adicionar labels: `probe_name`, `sensor_type`, `target_host`, `status` em todas as metricas
  - [ ] 10.6 Atualizar metricas a cada 15 segundos

- [ ] 11. Event Engine (WMI + Docker + Kubernetes)
  - [ ] 11.1 Criar `probe/event_engine/__init__.py`
  - [ ] 11.2 Criar `probe/event_engine/wmi_event_listener.py` com subscriptions WMI para: criacao/parada de servicos, falhas de disco e eventos de seguranca criticos
  - [ ] 11.3 Criar `probe/event_engine/docker_event_listener.py` consumindo stream `/events` da Docker API para eventos `die`, `oom`, `health_status`
  - [ ] 11.4 Criar `probe/event_engine/kubernetes_event_listener.py` consumindo stream `/api/v1/watch/events` para eventos `OOMKilling`, `BackOff`, `Failed`, `Evicted`
  - [ ] 11.5 Implementar conversao de eventos em `SensorResult` e envio para a API em no maximo 5 segundos
  - [ ] 11.6 Implementar reconexao com backoff exponencial (5s, 10s, 30s, 60s) quando a conexao com a fonte de eventos for interrompida

- [ ] 12. Credential Manager (AES-256 + Vault)
  - [ ] 12.1 Criar `probe/security/__init__.py`
  - [ ] 12.2 Criar `probe/security/credential_manager.py` com criptografia AES-256 para credenciais armazenadas localmente usando `cryptography` lib
  - [ ] 12.3 Implementar validacao de integridade das credenciais criptografadas na inicializacao do probe
  - [ ] 12.4 Garantir que senhas, chaves e tokens nunca sejam registrados em logs (substituir por `[REDACTED]`)
  - [ ] 12.5 Implementar deteccao de rotacao de credenciais e atualizacao em no maximo 60 segundos sem reinicializacao
  - [ ] 12.6 Criar `probe/security/vault_client.py` com suporte a HashiCorp Vault via API REST
  - [ ] 12.7 Adicionar suporte a Azure Key Vault via SDK `azure-keyvault-secrets` no `vault_client.py`

- [ ] 13. TimescaleDB Migration
  - [ ] 13.1 Criar `api/routers/timescale_migration.py` com endpoints para gerenciar a migracao
  - [ ] 13.2 Criar script SQL `api/migrations/timescaledb_setup.sql` com: habilitacao da extensao, criacao de hypertables com `chunk_time_interval = 1 day`
  - [ ] 13.3 Adicionar ao script SQL: compressao automatica em chunks com mais de 7 dias
  - [ ] 13.4 Adicionar ao script SQL: retention policy para remover dados com mais de 365 dias
  - [ ] 13.5 Adicionar ao script SQL: continuous aggregates para medias horarias (retencao 90 dias) e medias diarias (retencao 365 dias)
  - [ ] 13.6 Registrar o router `timescale_migration` no `api/main.py`

- [ ] 14. AIOps Expandido (Isolation Forest + Prophet/ARIMA + Correlacao)
  - [ ] 14.1 Criar `ai-agent/anomaly_detector.py` com Isolation Forest para metricas de CPU, memoria e disco usando `scikit-learn`
  - [ ] 14.2 Implementar janela de treinamento de 7 dias e retreinamento automatico a cada 24 horas no `anomaly_detector.py`
  - [ ] 14.3 Gerar alerta com `anomaly_score`, `affected_metric`, `expected_range`, `observed_value` e `confidence_level` ao detectar anomalia
  - [ ] 14.4 Criar `ai-agent/failure_predictor.py` com Prophet ou ARIMA para predicao de tendencias (disco crescendo, memoria aumentando)
  - [ ] 14.5 Implementar horizonte de predicao de 24 horas e gerar alerta preditivo com `predicted_breach_time` e `confidence_interval`
  - [ ] 14.6 Criar `ai-agent/event_correlator.py` para correlacao de alertas dentro de janela de 5 minutos no mesmo host ou grupo
  - [ ] 14.7 Implementar analise de causa raiz no `event_correlator.py` baseada em ordem temporal, severidade e dependencias entre hosts

- [ ] 15. Multi-Probe API Endpoints
  - [ ] 15.1 Criar `api/routers/multi_probe.py` com endpoints para registro e gerenciamento de probes
  - [ ] 15.2 Implementar endpoint `POST /probes/register` para registro de novos probes com tipo (`probe_datacenter`, `probe_cloud`, `probe_edge`)
  - [ ] 15.3 Implementar endpoint `POST /probes/{probe_id}/heartbeat` para recebimento de heartbeat a cada 60 segundos
  - [ ] 15.4 Implementar logica de redistribuicao de servidores quando probe ficar offline por mais de 120 segundos
  - [ ] 15.5 Implementar endpoint `GET /probes/status` com dashboard de todos os probes: `probe_name`, `type`, `status`, `servers_monitored`, `sensors_active`, `last_heartbeat`
  - [ ] 15.6 Implementar distribuicao automatica de servidores entre probes com base em localizacao, carga e capacidade
  - [ ] 15.7 Registrar o router `multi_probe` no `api/main.py`

- [ ] 16. Refatorar probe_core.py para Novo Pipeline
  - [ ] 16.1 Refatorar `probe/probe_core.py` para instanciar e inicializar todos os novos componentes: `SensorEngine`, `Scheduler`, `ThreadPool`, `PreCheck`, `MetricCache`, `AdaptiveMonitor`, `InternalMetricsCollector`, `PrometheusExporter`
  - [ ] 16.2 Substituir chamadas diretas aos collectors antigos pelo novo `SensorEngine` com despacho via protocol engines
  - [ ] 16.3 Inicializar o `EventEngine` (WMI/Docker/K8s) em threads separadas no startup do probe
  - [ ] 16.4 Inicializar o `CredentialManager` no startup e injetar nas dependencias que precisam de credenciais
  - [ ] 16.5 Garantir graceful shutdown: aguardar workers ativos terminarem, fechar connection pools e salvar estado do scheduler

- [ ] 17. Atualizar probe/requirements.txt com Novas Dependencias
  - [ ] 17.1 Adicionar `redis` para o MetricCache com backend Redis
  - [ ] 17.2 Adicionar `prometheus_client` para o PrometheusExporter
  - [ ] 17.3 Adicionar `cryptography` para o CredentialManager (AES-256)
  - [ ] 17.4 Adicionar `hvac` para integracao com HashiCorp Vault
  - [ ] 17.5 Adicionar `azure-keyvault-secrets` e `azure-identity` para Azure Key Vault
  - [ ] 17.6 Adicionar `scikit-learn` para Isolation Forest no AIOps
  - [ ] 17.7 Adicionar `prophet` ou `statsmodels` (ARIMA) para predicao de falhas
  - [ ] 17.8 Adicionar `docker` SDK para o docker_engine e docker_event_listener
  - [ ] 17.9 Adicionar `kubernetes` client para o kubernetes_engine e kubernetes_event_listener
  - [ ] 17.10 Adicionar `psutil` para coleta de internal metrics (se ainda nao presente)
