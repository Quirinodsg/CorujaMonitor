# Documento de Requisitos — Coleta Paralela de Probes

## Introdução

O sistema Coruja Monitor atualmente coleta métricas de servidores remotos de forma sequencial no `probe_core.py`, resultando em ciclos de coleta de aproximadamente 3 minutos. Este documento especifica os requisitos para refatorar o sistema de coleta para execução paralela utilizando `ThreadPoolExecutor`, com despacho incremental de métricas, validação MCT (Monitoring Confidence Testing) via shadow mode, e rollout seguro com feature flag. O objetivo é reduzir o tempo de ciclo para menos de 30 segundos sem perda de métricas e sem impacto no sistema existente.

## Glossário

- **ProbeCore**: Classe principal da sonda (`probe/probe_core.py`) que orquestra a coleta sequencial de métricas locais, remotas, standalone e Hyper-V.
- **ProbeOrchestrator**: Componente SDD responsável por gerenciar o ciclo de coleta paralela, substituindo o loop sequencial do `ProbeCore._collect_metrics_sequential()`.
- **SensorExecutor**: Componente SDD que executa a coleta por tipo de sensor (WMI, SNMP, Local, Standalone, Hyper-V) dentro do pool de threads.
- **MetricsDispatcher**: Componente SDD responsável pelo envio incremental de métricas via HTTP, com controle de micro-batch, retry e fallback.
- **ProbeTelemetry**: Componente SDD de observabilidade que registra tempo de execução por host, tempo total do ciclo, taxa de erros e contagem de métricas enviadas.
- **MetricsComparator**: Módulo MCT que compara resultados do modo sequencial com o modo paralelo durante o shadow mode.
- **Shadow_Mode**: Fase MCT onde ambos os modos (sequencial e paralelo) executam simultaneamente para comparação de resultados.
- **Feature_Flag**: Configuração `parallel_enabled` no `config.yaml` que controla qual modo de coleta está ativo.
- **Ciclo_de_Coleta**: Uma execução completa de coleta de métricas de todas as fontes (local, remota, standalone, Hyper-V).
- **Despacho_Incremental**: Envio de métricas à API imediatamente após a coleta de cada servidor, sem aguardar o ciclo completo.
- **Despacho_Bulk**: Modo atual onde todas as métricas são acumuladas no buffer e enviadas em uma única requisição ao final do ciclo.
- **Canary_Release**: Estratégia de rollout gradual onde o modo paralelo é ativado em um subconjunto de servidores antes da ativação total.
- **ThreadPoolExecutor**: Executor de pool de threads do Python (`concurrent.futures`) utilizado para paralelizar a coleta de servidores remotos.
- **Buffer**: Lista em memória (`ProbeCore.buffer`) onde métricas são acumuladas antes do envio à API.
- **API_Metrics_Endpoint**: Endpoint `/api/v1/metrics/probe/bulk` que recebe métricas da sonda.

## Requisitos

### Requisito 1: Feature Flag para Coleta Paralela

**User Story:** Como administrador do sistema, eu quero controlar a ativação do modo paralelo via configuração, para que eu possa ativar/desativar sem alterar código.

#### Critérios de Aceitação

1. THE ProbeCore SHALL carregar a configuração `parallel_enabled` do arquivo `config.yaml` na seção `probe`.
2. WHEN `parallel_enabled` é `false`, THE ProbeCore SHALL executar a coleta no modo sequencial original (`_collect_metrics_sequential`).
3. WHEN `parallel_enabled` é `true`, THE ProbeCore SHALL delegar a coleta ao ProbeOrchestrator.
4. THE ProbeCore SHALL carregar os parâmetros `max_workers`, `timeout_seconds`, `dispatch_mode` e `canary_hosts` do `config.yaml`.
5. WHEN o arquivo `config.yaml` não contém a seção `probe`, THE ProbeCore SHALL utilizar valores padrão seguros (`parallel_enabled=false`, `max_workers=8`, `timeout_seconds=30`, `dispatch_mode=bulk`).
6. IF a leitura do `config.yaml` falhar, THEN THE ProbeCore SHALL registrar o erro no log e operar no modo sequencial.


### Requisito 2: Orquestração de Coleta Paralela (ProbeOrchestrator)

**User Story:** Como operador de NOC, eu quero que a coleta de métricas de servidores remotos ocorra em paralelo, para que o ciclo de coleta seja concluído em menos de 30 segundos.

#### Critérios de Aceitação

1. THE ProbeOrchestrator SHALL utilizar `ThreadPoolExecutor` com número de workers configurável via `max_workers`.
2. WHEN um ciclo de coleta é iniciado, THE ProbeOrchestrator SHALL coletar métricas locais (CPU, RAM, Disco, Rede) de forma síncrona antes de iniciar a coleta remota.
3. WHEN servidores remotos estão configurados, THE ProbeOrchestrator SHALL submeter a coleta de cada servidor remoto como uma tarefa independente no pool de threads.
4. THE ProbeOrchestrator SHALL agrupar a coleta em fases: LOCAL → REMOTO (WMI/SNMP em paralelo) → STANDALONE → HYPER-V.
5. WHEN a coleta de um servidor remoto exceder `timeout_seconds`, THE ProbeOrchestrator SHALL cancelar a tarefa, registrar timeout no log e prosseguir com os demais servidores.
6. IF a coleta de um servidor remoto falhar com exceção, THEN THE ProbeOrchestrator SHALL registrar o erro no log e continuar a coleta dos demais servidores.
7. THE ProbeOrchestrator SHALL filtrar o servidor local da lista de servidores remotos para evitar coleta duplicada.
8. THE ProbeOrchestrator SHALL completar o ciclo de coleta de todos os servidores dentro do tempo máximo de `timeout_seconds * 2`.

### Requisito 3: Execução de Sensores por Tipo (SensorExecutor)

**User Story:** Como desenvolvedor, eu quero que cada tipo de sensor (WMI, SNMP, Standalone) seja executado de forma isolada, para que falhas em um tipo não afetem os demais.

#### Critérios de Aceitação

1. THE SensorExecutor SHALL executar coletores WMI para servidores com `monitoring_protocol=wmi` ou `wmi_enabled=true`.
2. THE SensorExecutor SHALL executar coletores SNMP para servidores com `monitoring_protocol=snmp`.
3. WHEN um coletor WMI falha para um servidor, THE SensorExecutor SHALL registrar o erro e não afetar a coleta de outros servidores.
4. WHEN um coletor SNMP falha para um servidor, THE SensorExecutor SHALL registrar o erro e não afetar a coleta de outros servidores.
5. THE SensorExecutor SHALL executar coletores standalone (Engetron, Conflex, Printer, EqualLogic, ICMP) utilizando a lógica de roteamento existente em `_collect_standalone_sensors`.
6. THE SensorExecutor SHALL preservar a lógica de roteamento de sensores standalone: HTTP → ICMP (por tipo/categoria) → Engetron (por nome) → Conflex (por nome) → SNMP → fallback.

### Requisito 4: Despacho Incremental de Métricas (MetricsDispatcher)

**User Story:** Como operador de NOC, eu quero que as métricas sejam enviadas à API assim que coletadas de cada servidor, para que eu veja dados atualizados sem esperar o ciclo completo.

#### Critérios de Aceitação

1. WHEN `dispatch_mode` é `incremental`, THE MetricsDispatcher SHALL enviar métricas à API após a coleta de cada servidor remoto.
2. WHEN `dispatch_mode` é `bulk`, THE MetricsDispatcher SHALL acumular métricas no buffer e enviar ao final do ciclo.
3. THE MetricsDispatcher SHALL agrupar métricas em micro-batches de tamanho configurável (`batch_size`, padrão 50) antes do envio.
4. THE MetricsDispatcher SHALL enviar métricas para o endpoint existente `/api/v1/metrics/probe/bulk` sem alteração na estrutura da requisição.
5. IF o envio de um micro-batch falhar, THEN THE MetricsDispatcher SHALL registrar o erro no log e incrementar o contador de erros.
6. THE MetricsDispatcher SHALL forçar o envio de todas as métricas restantes no buffer ao final do ciclo via `flush()`.
7. THE MetricsDispatcher SHALL utilizar acesso thread-safe ao buffer interno via `threading.Lock`.
8. THE MetricsDispatcher SHALL formatar métricas no mesmo formato utilizado pelo `ProbeCore._send_metrics()` (hostname, sensor_type, sensor_name, value, unit, status, timestamp, metadata).

### Requisito 5: Observabilidade da Sonda (ProbeTelemetry)

**User Story:** Como administrador do sistema, eu quero visibilidade completa sobre o desempenho de cada ciclo de coleta, para que eu possa identificar gargalos e falhas rapidamente.

#### Critérios de Aceitação

1. THE ProbeTelemetry SHALL registrar o tempo de execução em milissegundos para cada host coletado.
2. THE ProbeTelemetry SHALL registrar o tempo total do ciclo de coleta em milissegundos.
3. THE ProbeTelemetry SHALL registrar a contagem total de métricas coletadas por ciclo.
4. THE ProbeTelemetry SHALL registrar a contagem total de erros por ciclo.
5. THE ProbeTelemetry SHALL identificar o host mais lento de cada ciclo.
6. THE ProbeTelemetry SHALL registrar mensagens de erro específicas por host quando ocorrerem falhas.
7. THE ProbeTelemetry SHALL utilizar acesso thread-safe via `threading.Lock` para registros concorrentes.
8. WHEN um ciclo é concluído, THE ProbeTelemetry SHALL gerar um sumário estruturado contendo: duração do ciclo, total de hosts, total de métricas, total de erros, host mais lento e lista de erros.


### Requisito 6: Validação MCT — Shadow Mode

**User Story:** Como administrador do sistema, eu quero executar o modo paralelo em shadow (simultâneo ao sequencial) para validar que os resultados são equivalentes antes de migrar.

#### Critérios de Aceitação

1. WHEN shadow mode está ativo, THE ProbeCore SHALL executar tanto a coleta sequencial quanto a coleta paralela no mesmo ciclo.
2. THE MetricsComparator SHALL comparar o valor de cada métrica coletada pelo modo sequencial com o valor coletado pelo modo paralelo para o mesmo host e sensor.
3. WHEN a diferença percentual entre os valores sequencial e paralelo for menor ou igual a 5%, THE MetricsComparator SHALL classificar a comparação como "OK".
4. WHEN a diferença percentual entre os valores sequencial e paralelo for maior que 5%, THE MetricsComparator SHALL classificar a comparação como "DRIFT" e registrar um warning no log.
5. THE MetricsComparator SHALL gerar um sumário contendo: total de comparações, comparações OK, comparações com DRIFT e resultado geral (pass/fail).
6. WHEN ambos os valores (sequencial e paralelo) são zero, THE MetricsComparator SHALL classificar a comparação como "OK" com diferença de 0%.
7. WHEN o valor sequencial é zero e o paralelo é diferente de zero, THE MetricsComparator SHALL classificar a diferença como 100%.

### Requisito 7: Canary Release

**User Story:** Como administrador do sistema, eu quero ativar o modo paralelo gradualmente em subconjuntos de servidores, para que eu possa validar em produção com risco controlado.

#### Critérios de Aceitação

1. THE ProbeOrchestrator SHALL suportar uma lista de `canary_hosts` configurável no `config.yaml`.
2. WHEN `canary_hosts` está configurado e não vazio, THE ProbeOrchestrator SHALL aplicar coleta paralela apenas aos hosts listados em `canary_hosts`.
3. WHEN `canary_hosts` está vazio ou não configurado, THE ProbeOrchestrator SHALL aplicar coleta paralela a todos os servidores remotos.
4. THE ProbeOrchestrator SHALL permitir expansão gradual da lista de `canary_hosts` sem reiniciar a sonda (releitura do config a cada ciclo).

### Requisito 8: Controle de Concorrência e Thread Safety

**User Story:** Como desenvolvedor, eu quero garantir que a coleta paralela não cause condições de corrida no buffer de métricas, para que nenhuma métrica seja perdida ou corrompida.

#### Critérios de Aceitação

1. THE ProbeOrchestrator SHALL garantir que o acesso ao `ProbeCore.buffer` seja thread-safe durante a coleta paralela.
2. THE MetricsDispatcher SHALL utilizar `threading.Lock` para proteger operações de leitura e escrita no buffer interno.
3. THE ProbeTelemetry SHALL utilizar `threading.Lock` para proteger registros concorrentes de telemetria.
4. IF duas threads tentarem escrever no buffer simultaneamente, THEN THE ProbeOrchestrator SHALL serializar os acessos via lock sem perda de dados.
5. THE ProbeOrchestrator SHALL utilizar `thread_name_prefix="probe"` no ThreadPoolExecutor para facilitar diagnóstico em logs.

### Requisito 9: Preservação do Modo Sequencial

**User Story:** Como administrador do sistema, eu quero que o modo sequencial original permaneça intacto e funcional, para que eu possa reverter instantaneamente em caso de problemas.

#### Critérios de Aceitação

1. THE ProbeCore SHALL manter o método `_collect_metrics_sequential()` inalterado e funcional.
2. WHEN `parallel_enabled` é alterado de `true` para `false`, THE ProbeCore SHALL reverter imediatamente para o modo sequencial no próximo ciclo.
3. THE ProbeCore SHALL preservar a ordem de coleta sequencial: LOCAL → REMOTO → STANDALONE → HYPER-V → KUBERNETES.
4. THE ProbeCore SHALL preservar a lógica de envio bulk existente em `_send_metrics()` quando operando no modo sequencial.

### Requisito 10: Compatibilidade com Sistema Existente

**User Story:** Como administrador do sistema, eu quero que a coleta paralela não altere a API, o banco de dados, as regras de alerta ou o Celery, para que o restante do sistema continue funcionando normalmente.

#### Critérios de Aceitação

1. THE ProbeOrchestrator SHALL enviar métricas no mesmo formato JSON aceito pelo endpoint `/api/v1/metrics/probe/bulk`.
2. THE ProbeOrchestrator SHALL preservar os campos obrigatórios: `hostname`, `sensor_type`, `sensor_name`, `value`, `unit`, `status`, `timestamp`, `metadata`.
3. THE ProbeOrchestrator SHALL preservar o campo `probe_token` em todas as requisições à API.
4. THE ProbeOrchestrator SHALL preservar a lógica de `ip_address` e `public_ip` no metadata para métricas locais.
5. THE ProbeOrchestrator SHALL preservar a lógica de `sensor_id` no metadata para sensores standalone.
6. IF o endpoint da API retornar erro, THEN THE MetricsDispatcher SHALL manter as métricas no buffer para retry, limitando o tamanho do buffer a `max_buffer_size`.

### Requisito 11: Logging Estruturado

**User Story:** Como administrador do sistema, eu quero logs estruturados e informativos sobre a coleta paralela, para que eu possa diagnosticar problemas rapidamente.

#### Critérios de Aceitação

1. WHEN um ciclo paralelo é concluído, THE ProbeOrchestrator SHALL registrar no log: duração do ciclo, número de hosts, número de métricas e número de erros.
2. WHEN um host excede o timeout, THE ProbeOrchestrator SHALL registrar um warning no log com o hostname e o tempo de timeout.
3. WHEN a coleta de um host falha, THE ProbeOrchestrator SHALL registrar um erro no log com o hostname e a mensagem de exceção.
4. WHEN o MetricsDispatcher envia um batch com sucesso, THE MetricsDispatcher SHALL registrar no log a quantidade de métricas enviadas e o total acumulado.
5. WHEN o MetricsDispatcher falha ao enviar um batch, THE MetricsDispatcher SHALL registrar um warning no log com o código HTTP ou mensagem de erro.
6. THE ProbeCore SHALL registrar no log qual modo está ativo na inicialização: "Parallel engine ENABLED" ou "Sequential mode".

### Requisito 12: Critérios de Sucesso e Performance

**User Story:** Como gerente de operações, eu quero métricas claras de sucesso para validar que a migração para coleta paralela atingiu os objetivos.

#### Critérios de Aceitação

1. WHEN o modo paralelo está ativo, THE ProbeOrchestrator SHALL completar o ciclo de coleta em menos de 30 segundos para ambientes com até 50 servidores remotos.
2. THE MetricsDispatcher SHALL entregar todas as métricas coletadas à API sem perda (zero metric loss em operação normal).
3. WHEN o shadow mode está ativo, THE MetricsComparator SHALL reportar diferença menor que 5% entre os modos sequencial e paralelo para todas as métricas.
4. THE ProbeOrchestrator SHALL manter o consumo de memória proporcional ao número de workers e ao tamanho do buffer, sem vazamento de memória entre ciclos.
