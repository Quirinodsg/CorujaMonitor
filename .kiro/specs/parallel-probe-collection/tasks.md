# Tarefas de Implementação — Coleta Paralela de Probes

## Tarefas

- [x] 1. Configuração e Feature Flag (Requisitos 1, 9)
  - [x] 1.1 Adicionar seção `probe` ao `config.yaml` com valores padrão: `parallel_enabled: false`, `max_workers: 8`, `timeout_seconds: 30`, `dispatch_mode: bulk`, `canary_hosts: []`
  - [x] 1.2 Implementar `_load_parallel_config()` no `ProbeCore` para carregar a seção `probe` do `config.yaml` com fallback para valores padrão seguros
  - [x] 1.3 Implementar lógica de feature flag no `ProbeCore._collect_metrics()`: se `parallel_enabled=true` delegar ao `ProbeOrchestrator`, senão executar `_collect_metrics_sequential()`
  - [x] 1.4 Adicionar log na inicialização: "Parallel engine ENABLED" ou "Sequential mode"
  - [x] 1.5 Garantir que `_collect_metrics_sequential()` permanece inalterado e funcional

- [x] 2. ProbeTelemetry — Observabilidade (Requisitos 5, 8, 11)
  - [x] 2.1 Implementar classe `ProbeTelemetry` em `probe/parallel_engine.py` com `threading.Lock` para thread safety
  - [x] 2.2 Implementar `start_cycle()` e `end_cycle()` para marcar início/fim do ciclo e calcular duração em ms
  - [x] 2.3 Implementar `record_host(host, duration_ms, metrics_count, error)` thread-safe para registrar resultado por host
  - [x] 2.4 Implementar `summary()` retornando dict com: `cycle_duration_ms`, `total_hosts`, `total_metrics`, `total_errors`, `slowest_host`, `slowest_ms`, `errors`
  - [x] 2.5 Escrever teste de propriedade: `test_telemetry_thread_safety` — registros concorrentes de N threads não perdem dados (total_hosts == N)

- [x] 3. MetricsDispatcher — Despacho de Métricas (Requisitos 4, 8, 10, 11)
  - [x] 3.1 Implementar classe `MetricsDispatcher` em `probe/parallel_engine.py` com buffer thread-safe (`threading.Lock`)
  - [x] 3.2 Implementar `enqueue(metrics)`: adiciona ao buffer, dispara `_flush()` se `len(buffer) >= batch_size`
  - [x] 3.3 Implementar `_flush()`: envia métricas via POST ao `/api/v1/metrics/probe/bulk` com `probe_token`, formato JSON preservado
  - [x] 3.4 Implementar `flush()`: força envio de todas as métricas restantes no buffer
  - [x] 3.5 Implementar `stats` property retornando contadores: `sent`, `errors`, `buffered`
  - [x] 3.6 Adicionar logging: log de sucesso com quantidade enviada, warning em caso de falha com código HTTP
  - [x] 3.7 Escrever teste de propriedade: `test_dispatcher_no_metric_loss` — todas as métricas enfileiradas são enviadas após flush (sem perda)

- [x] 4. SensorExecutor — Execução Isolada de Sensores (Requisitos 3, 10)
  - [x] 4.1 Implementar classe `SensorExecutor` em `probe/parallel_engine.py` com referência ao `ProbeCore`
  - [x] 4.2 Implementar `collect_server(server)`: roteia para WMI ou SNMP baseado em `monitoring_protocol`, retorna lista de métricas
  - [x] 4.3 Implementar `collect_standalone(sensor, timestamp)`: preserva lógica de roteamento HTTP → ICMP → Engetron → Conflex → Printer → EqualLogic → SNMP → fallback
  - [x] 4.4 Garantir isolamento de falhas: exceção em um coletor não propaga para outros servidores
  - [x] 4.5 Preservar formato de métricas: `hostname`, `sensor_type`, `sensor_name`, `value`, `unit`, `status`, `timestamp`, `metadata`

- [x] 5. ProbeOrchestrator — Orquestração Paralela (Requisitos 2, 7, 8, 11)
  - [x] 5.1 Implementar classe `ProbeOrchestrator` em `probe/parallel_engine.py` com `ThreadPoolExecutor(max_workers, thread_name_prefix="probe")`
  - [x] 5.2 Implementar `collect_all()`: executa fases LOCAL → REMOTO (paralelo) → STANDALONE (paralelo) → HYPER-V
  - [x] 5.3 Implementar `_collect_local(timestamp)`: coleta síncrona de CPU, RAM, Disco, Rede via métodos existentes do ProbeCore
  - [x] 5.4 Implementar `_fetch_servers()`: busca servidores da API, filtra servidor local para evitar duplicação
  - [x] 5.5 Implementar `_collect_servers_parallel(servers, timestamp)`: submete cada servidor ao pool, trata timeout e exceções por servidor
  - [x] 5.6 Implementar filtro de `canary_hosts`: se configurado, aplicar paralelo apenas aos hosts listados
  - [x] 5.7 Implementar `_collect_standalone_parallel(timestamp)`: coleta sensores standalone via SensorExecutor
  - [x] 5.8 Adicionar logging estruturado: duração do ciclo, hosts, métricas, erros, warnings de timeout
  - [x] 5.9 Escrever teste de propriedade: `test_orchestrator_timeout_resilience` — timeout em um servidor não impede coleta dos demais

- [x] 6. MetricsComparator — Validação MCT Shadow Mode (Requisitos 6)
  - [x] 6.1 Implementar classe `MetricsComparator` em `probe/parallel_engine.py` com tolerância de 5%
  - [x] 6.2 Implementar `compare(host, metric, old_val, new_val)`: retorna dict com `diff_pct` e `status` ("OK" ou "DRIFT")
  - [x] 6.3 Tratar caso especial: ambos zero → "OK" com diff 0%; sequencial zero e paralelo != 0 → diff 100%
  - [x] 6.4 Implementar `summary` property: `total`, `ok`, `drifts`, `pass` (bool)
  - [x] 6.5 Escrever teste de propriedade: `test_comparator_tolerance` — métricas com diferença ≤5% sempre classificadas como "OK"

- [x] 7. Integração Shadow Mode no ProbeCore (Requisitos 6, 9)
  - [x] 7.1 Adicionar config `shadow_mode: false` ao `config.yaml` na seção `probe`
  - [x] 7.2 Implementar lógica no `ProbeCore._collect_metrics()`: quando shadow mode ativo, executar sequencial E paralelo no mesmo ciclo
  - [x] 7.3 Comparar resultados via `MetricsComparator` e logar sumário de comparação
  - [x] 7.4 Garantir que apenas os resultados do modo sequencial são enviados à API durante shadow mode

- [x] 8. Canary Release (Requisito 7)
  - [x] 8.1 Implementar releitura de `canary_hosts` do `config.yaml` a cada ciclo no `ProbeOrchestrator`
  - [x] 8.2 Implementar filtro: se `canary_hosts` não vazio, aplicar paralelo apenas aos hosts listados; restante em sequencial
  - [x] 8.3 Quando `canary_hosts` vazio, aplicar paralelo a todos os servidores remotos

- [x] 9. Controle de Concorrência e Thread Safety (Requisito 8)
  - [x] 9.1 Garantir acesso thread-safe ao `ProbeCore.buffer` durante coleta paralela via `threading.Lock`
  - [x] 9.2 Validar que `MetricsDispatcher`, `ProbeTelemetry` e `ProbeOrchestrator` usam locks corretamente
  - [x] 9.3 Escrever teste de propriedade: `test_buffer_thread_safety` — escritas concorrentes de N threads no buffer resultam em exatamente N * metrics_per_thread métricas

- [x] 10. Testes de Integração e Compatibilidade (Requisitos 10, 12)
  - [x] 10.1 Escrever teste verificando que métricas enviadas pelo modo paralelo têm o mesmo formato JSON do modo sequencial
  - [x] 10.2 Escrever teste verificando que `probe_token` está presente em todas as requisições
  - [x] 10.3 Escrever teste verificando que campos obrigatórios (`hostname`, `sensor_type`, `sensor_name`, `value`, `status`, `timestamp`) estão presentes
  - [x] 10.4 Escrever teste verificando que `metadata` preserva `ip_address`, `public_ip` e `sensor_id` quando aplicável

- [x] 11. Logging e Documentação Final (Requisito 11)
  - [x] 11.1 Revisar todos os logs do ProbeOrchestrator: ciclo concluído, timeout, falha, modo ativo
  - [x] 11.2 Revisar todos os logs do MetricsDispatcher: batch enviado, falha de envio
  - [x] 11.3 Documentar configuração no README ou config.yaml com comentários explicativos
