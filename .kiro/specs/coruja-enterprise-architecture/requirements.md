# Documento de Requisitos

## Introdução

Este documento descreve os requisitos para a refatoração arquitetural enterprise do **Coruja Monitor**, transformando-o na plataforma de monitoramento agentless mais eficiente, escalável e moderna possível.

O sistema atual coleta métricas via WMI, SNMP e ICMP a partir de um probe Windows (SRVSONDA001), com API FastAPI no Linux, frontend React, worker Celery, AI Agent Python e PostgreSQL. Os problemas identificados incluem: coleta imprecisa de memória (88% reportado vs 38% real), ausência de connection pooling, scheduler sem controle de concorrência, e falta de camadas de abstração para suportar milhares de hosts.

A refatoração visa introduzir: protocol engines especializados, connection pooling, scheduler inteligente, worker pool controlado, sensor engine unificado, pré-check de conectividade, otimização de queries WMI/SNMP, cache de métricas, monitoramento adaptativo, auto-discovery aprimorado, event-driven monitoring, TimescaleDB, AIOps expandido, monitoramento interno do probe, segurança de credenciais, arquitetura multi-probe e observabilidade com Prometheus/Grafana.

---

## Glossário

- **Probe**: Agente de coleta instalado em um datacenter/rede, responsável por coletar métricas de hosts remotos via protocolos agentless (WMI, SNMP, ICMP, TCP).
- **Sensor**: Unidade atômica de monitoramento com atributos: `id`, `type`, `target`, `interval`, `timeout`, `retries`, `query`, `protocol`.
- **Protocol_Engine**: Módulo especializado para execução de um protocolo específico (ICMP, WMI, SNMP, TCP, Registry, Docker, Kubernetes).
- **Connection_Pool**: Gerenciador de conexões reutilizáveis por protocolo e host, com limite configurável e idle timeout.
- **Scheduler**: Componente responsável por distribuir a execução de sensores ao longo do tempo, evitando picos de carga.
- **Worker_Pool**: Conjunto de threads/coroutines gerenciadas para execução paralela controlada de sensores.
- **Sensor_Engine**: Camada de abstração que recebe definições de sensores e despacha para o Protocol_Engine correto.
- **Pre_Check**: Verificação de conectividade em cascata (Ping → TCP Port → Protocolo específico) antes de executar sensores pesados.
- **Adaptive_Monitor**: Mecanismo que ajusta a frequência de coleta com base no estado do host (estável vs. problema detectado).
- **Event_Engine**: Componente que processa eventos assíncronos de fontes como WMI subscriptions, Windows Event Log, container events e Kubernetes events.
- **AIOps_Engine**: Motor de inteligência artificial para detecção de anomalias, correlação de eventos, análise de causa raiz e predição de falhas.
- **TimescaleDB**: Extensão PostgreSQL para dados de séries temporais com compressão, retention policy e downsampling.
- **Vault**: Sistema de gerenciamento seguro de credenciais (HashiCorp Vault ou Azure Key Vault).
- **Core_Server**: Servidor central que coordena múltiplos probes distribuídos.
- **WQL**: WMI Query Language — linguagem de consulta para o Windows Management Instrumentation.
- **SNMP_Bulk**: Operação SNMP GetBulk que recupera múltiplos OIDs em uma única requisição de rede.
- **Metric_Cache**: Cache local ou Redis com TTL configurável para evitar queries duplicadas ao mesmo host.
- **Internal_Metrics**: Métricas de saúde do próprio probe (CPU, memória, latência de conexões, tamanho da fila de workers).

---

## Requisitos

### Requisito 1: Protocol Engines Especializados

**User Story:** Como engenheiro de monitoramento, quero protocol engines especializados por protocolo, para que cada tipo de coleta seja otimizado, isolado e extensível independentemente.

#### Critérios de Aceitação

1. THE Sensor_Engine SHALL suportar os seguintes tipos de Protocol_Engine: `icmp_engine`, `wmi_engine`, `snmp_engine`, `tcp_engine`, `registry_engine`, `docker_engine`, `kubernetes_engine`.
2. WHEN um Sensor é despachado pelo Sensor_Engine, THE Sensor_Engine SHALL selecionar o Protocol_Engine correspondente ao atributo `protocol` do Sensor.
3. THE Sensor_Engine SHALL expor uma interface uniforme `execute(sensor: SensorDefinition) -> SensorResult` independentemente do Protocol_Engine utilizado.
4. IF um Protocol_Engine não estiver disponível no ambiente (ex.: biblioteca não instalada), THEN THE Sensor_Engine SHALL retornar `SensorResult` com `status=unknown` e `error="engine_unavailable"` sem interromper os demais sensores.
5. WHERE o ambiente suportar Docker, THE docker_engine SHALL coletar métricas de containers (CPU, memória, status, restart count) via Docker API.
6. WHERE o ambiente suportar Kubernetes, THE kubernetes_engine SHALL coletar métricas de pods, nodes e deployments via Kubernetes API.

---

### Requisito 2: Connection Pooling por Protocolo

**User Story:** Como operador de infraestrutura, quero que o probe reutilize conexões existentes por host e protocolo, para que o overhead de autenticação e handshake seja minimizado e o `wmiprvse.exe` não seja sobrecarregado.

#### Critérios de Aceitação

1. THE Connection_Pool SHALL manter no máximo 3 conexões simultâneas por host para o protocolo WMI.
2. THE Connection_Pool SHALL manter no máximo 5 conexões simultâneas por host para o protocolo SNMP.
3. THE Connection_Pool SHALL manter no máximo 10 conexões simultâneas por host para o protocolo TCP.
4. WHEN uma conexão permanecer ociosa por mais de 300 segundos, THE Connection_Pool SHALL fechar a conexão e removê-la do pool.
5. WHEN todas as conexões de um host estiverem em uso, THE Connection_Pool SHALL aguardar até 10 segundos antes de retornar erro de `pool_exhausted`.
6. THE Connection_Pool SHALL executar limpeza de conexões ociosas a cada 60 segundos.
7. WHEN uma conexão do pool falhar durante uso, THE Connection_Pool SHALL removê-la do pool e criar uma nova conexão de substituição.

---

### Requisito 3: Scheduler Inteligente

**User Story:** Como administrador do sistema, quero um scheduler que distribua a execução de sensores ao longo do tempo, para que picos de carga sejam evitados e o probe opere de forma estável com milhares de sensores.

#### Critérios de Aceitação

1. THE Scheduler SHALL suportar os intervalos de execução: 30 segundos, 60 segundos e 300 segundos.
2. WHEN múltiplos sensores forem adicionados simultaneamente, THE Scheduler SHALL distribuir os primeiros ciclos de execução com delay escalonado de 3 segundos entre grupos de 10 sensores.
3. THE Scheduler SHALL limitar a no máximo 10 sensores ativos simultaneamente por host.
4. THE Scheduler SHALL limitar a no máximo 5 queries WMI simultâneas por host.
5. THE Scheduler SHALL limitar a no máximo 20 sensores em execução paralela no total.
6. WHEN um sensor falhar consecutivamente, THE Scheduler SHALL aplicar backoff exponencial: 30s, 60s, 120s, com máximo de 300s entre tentativas.
7. THE Scheduler SHALL expor um endpoint de status com: total de sensores, sensores ativos por host, queries WMI por host, e próxima execução de cada sensor.

---

### Requisito 4: Worker Pool Controlado

**User Story:** Como engenheiro de performance, quero um worker pool com concorrência controlada, para que o probe execute sensores em paralelo sem consumir recursos excessivos do sistema operacional.

#### Critérios de Aceitação

1. THE Worker_Pool SHALL manter no máximo 20 workers paralelos (threads ou coroutines).
2. THE Worker_Pool SHALL suportar tanto `ThreadPoolExecutor` quanto `AsyncIO` como backend de execução.
3. WHEN a fila de tarefas do Worker_Pool atingir 80% da capacidade máxima, THE Worker_Pool SHALL registrar um alerta de nível WARNING nos logs.
4. THE Worker_Pool SHALL expor métricas internas: `worker_queue_size`, `active_workers`, `completed_tasks`, `failed_tasks`.
5. WHEN uma tarefa exceder o timeout configurado no Sensor, THE Worker_Pool SHALL cancelar a tarefa e registrar `status=timeout` no SensorResult.

---

### Requisito 5: Sensor Engine Unificado

**User Story:** Como desenvolvedor, quero uma camada de abstração unificada para definição e execução de sensores, para que novos tipos de sensores possam ser adicionados sem modificar o código de coleta existente.

#### Critérios de Aceitação

1. THE Sensor_Engine SHALL aceitar definições de sensores com os atributos obrigatórios: `id`, `type`, `target`, `interval`, `timeout`, `retries`, `protocol`.
2. THE Sensor_Engine SHALL aceitar os atributos opcionais: `query` (WQL customizada), `port` (para TCP), `service_name` (para WMI service), `credentials`, `tags`.
3. WHEN um sensor for executado com `retries > 0` e falhar, THE Sensor_Engine SHALL re-executar o sensor até o número máximo de tentativas antes de retornar `status=unknown`.
4. THE Sensor_Engine SHALL registrar o tempo de execução em milissegundos no campo `execution_ms` de cada SensorResult.
5. THE Sensor_Engine SHALL suportar registro dinâmico de novos tipos de sensor via `register_engine(type, handler)` sem reinicialização do probe.

---

### Requisito 6: Pré-Check de Conectividade

**User Story:** Como operador de NOC, quero que o probe verifique a conectividade antes de executar sensores pesados, para que tentativas de coleta em hosts inacessíveis não desperdicem recursos e gerem alertas precisos.

#### Critérios de Aceitação

1. WHEN um sensor WMI for agendado para execução, THE Pre_Check SHALL verificar em sequência: (1) ICMP Ping, (2) TCP porta 135, (3) WMI namespace `root/cimv2` antes de executar a coleta.
2. WHEN um sensor SNMP for agendado para execução, THE Pre_Check SHALL verificar em sequência: (1) ICMP Ping, (2) UDP porta 161 antes de executar a coleta.
3. IF o ICMP Ping falhar no Pre_Check, THEN THE Pre_Check SHALL retornar `status=critical` com `error="host_unreachable"` e não executar as verificações subsequentes.
4. IF o TCP Port check falhar no Pre_Check, THEN THE Pre_Check SHALL retornar `status=critical` com `error="port_unreachable"` e não executar o sensor.
5. THE Pre_Check SHALL armazenar o resultado em cache por 30 segundos para evitar verificações redundantes no mesmo host.
6. THE Pre_Check SHALL completar todas as verificações em no máximo 5 segundos por host.

---

### Requisito 7: Otimização de Queries WMI (WQL)

**User Story:** Como engenheiro de performance, quero que as queries WMI utilizem WQL específico em vez de `SELECT *`, para que o tempo de coleta seja reduzido e o impacto no host monitorado seja minimizado.

#### Critérios de Aceitação

1. THE wmi_engine SHALL coletar CPU usando a query: `SELECT PercentProcessorTime FROM Win32_PerfFormattedData_PerfOS_Processor WHERE Name='_Total'` como método primário.
2. IF a query `Win32_PerfFormattedData_PerfOS_Processor` falhar, THEN THE wmi_engine SHALL usar como fallback: `SELECT Name,LoadPercentage,NumberOfLogicalProcessors FROM Win32_Processor`.
3. THE wmi_engine SHALL coletar memória usando: `SELECT FreePhysicalMemory,TotalVisibleMemorySize FROM Win32_OperatingSystem`.
4. THE wmi_engine SHALL coletar discos usando: `SELECT DeviceID,FreeSpace,Size,VolumeName FROM Win32_LogicalDisk WHERE DriveType=3`.
5. THE wmi_engine SHALL coletar serviços usando: `SELECT Name,State,StartMode,DisplayName FROM Win32_Service WHERE StartMode='Auto'`.
6. THE wmi_engine SHALL coletar processos usando: `SELECT Name,ProcessId,WorkingSetSize FROM Win32_Process` ordenado por `WorkingSetSize` decrescente, limitado aos top 10.
7. THE wmi_engine SHALL registrar o tempo de execução de cada WQL query em milissegundos nos logs de nível DEBUG.
8. WHEN a query WMI de memória retornar `TotalVisibleMemorySize`, THE wmi_engine SHALL calcular o percentual de uso como `((TotalVisibleMemorySize - FreePhysicalMemory) / TotalVisibleMemorySize) * 100`, corrigindo o problema de imprecisão atual.

---

### Requisito 8: Cache de Métricas

**User Story:** Como arquiteto de sistemas, quero um cache de métricas com TTL configurável, para que queries duplicadas ao mesmo host dentro do mesmo intervalo sejam evitadas e a carga nos hosts monitorados seja reduzida.

#### Critérios de Aceitação

1. THE Metric_Cache SHALL suportar dois backends: Redis (quando disponível) e cache em memória local (fallback).
2. THE Metric_Cache SHALL aplicar TTL padrão de 5 segundos para métricas de CPU e memória.
3. THE Metric_Cache SHALL aplicar TTL padrão de 10 segundos para métricas de disco e serviços.
4. WHEN uma métrica for solicitada e existir no cache dentro do TTL, THE Metric_Cache SHALL retornar o valor em cache sem executar nova query.
5. THE Metric_Cache SHALL usar como chave de cache a combinação: `{host}:{sensor_type}:{query_hash}`.
6. THE Metric_Cache SHALL expor métricas de eficiência: `cache_hits`, `cache_misses`, `cache_hit_ratio`.
7. WHEN o backend Redis não estiver disponível, THE Metric_Cache SHALL fazer fallback automático para cache em memória sem interromper a coleta.

---

### Requisito 9: Monitoramento Adaptativo

**User Story:** Como operador de NOC, quero que a frequência de coleta se ajuste automaticamente ao estado do host, para que problemas sejam detectados mais rapidamente sem aumentar a carga em hosts saudáveis.

#### Critérios de Aceitação

1. WHILE um host estiver com todos os sensores em `status=ok` por pelo menos 3 ciclos consecutivos, THE Adaptive_Monitor SHALL manter o intervalo de coleta padrão de 300 segundos.
2. WHEN qualquer sensor de um host retornar `status=warning`, THE Adaptive_Monitor SHALL reduzir o intervalo de coleta para 60 segundos.
3. WHEN qualquer sensor de um host retornar `status=critical`, THE Adaptive_Monitor SHALL reduzir o intervalo de coleta para 30 segundos.
4. WHEN um host retornar ao `status=ok` por pelo menos 5 ciclos consecutivos após um período de alerta, THE Adaptive_Monitor SHALL restaurar o intervalo de coleta para 300 segundos.
5. THE Adaptive_Monitor SHALL registrar cada mudança de intervalo nos logs com o motivo da alteração.

---

### Requisito 10: Otimização SNMP com Bulk Requests

**User Story:** Como engenheiro de rede, quero que as coletas SNMP utilizem GetBulk em vez de múltiplos GETs individuais, para que o número de round-trips de rede seja reduzido e a coleta de dispositivos com muitos OIDs seja mais eficiente.

#### Critérios de Aceitação

1. THE snmp_engine SHALL usar `GetBulk` com `max-repetitions=25` para coletar múltiplos OIDs em uma única requisição quando o dispositivo suportar SNMP v2c ou v3.
2. THE snmp_engine SHALL usar `GetNext` individual apenas para dispositivos que suportam exclusivamente SNMP v1.
3. WHEN uma operação `GetBulk` falhar, THE snmp_engine SHALL fazer fallback para `GetNext` individual por OID.
4. THE snmp_engine SHALL coletar interfaces de rede via SNMP walk na OID `1.3.6.1.2.1.2.2` (ifTable) usando GetBulk.
5. THE snmp_engine SHALL registrar o número de OIDs coletados por requisição e o tempo total nos logs de nível DEBUG.

---

### Requisito 11: Auto-Discovery Aprimorado

**User Story:** Como administrador de infraestrutura, quero que o probe descubra automaticamente recursos monitoráveis nos hosts, para que discos, interfaces, serviços, processos, containers e pods sejam adicionados como sensores sem configuração manual.

#### Critérios de Aceitação

1. WHEN o auto-discovery for executado em um host Windows com WMI disponível, THE Sensor_Engine SHALL descobrir e registrar sensores para: todos os discos locais (`DriveType=3`), todos os serviços com `StartMode=Auto`, e os top 5 processos por uso de memória.
2. WHEN o auto-discovery for executado em um host com SNMP disponível, THE snmp_engine SHALL executar SNMP walk nas OIDs de interface (`ifTable`), disco (`dskTable`) e processos (`hrSWRunTable`) para descobrir recursos.
3. WHEN o auto-discovery for executado em um host com Docker disponível, THE docker_engine SHALL descobrir todos os containers em execução e registrar sensores de CPU, memória e status para cada um.
4. WHEN o auto-discovery for executado em um cluster Kubernetes, THE kubernetes_engine SHALL descobrir todos os namespaces, deployments e pods e registrar sensores correspondentes.
5. THE Sensor_Engine SHALL executar auto-discovery automaticamente a cada 3600 segundos para detectar novos recursos.
6. WHEN um recurso descoberto anteriormente não for mais encontrado (ex.: disco removido, container parado), THE Sensor_Engine SHALL marcar o sensor correspondente como `status=unknown` e notificar a API.

---

### Requisito 12: Event-Driven Monitoring

**User Story:** Como engenheiro de operações, quero que o probe processe eventos assíncronos de fontes como WMI subscriptions e Kubernetes events, para que alertas sejam gerados em tempo real sem depender exclusivamente de polling.

#### Critérios de Aceitação

1. WHERE o ambiente for Windows com WMI disponível, THE Event_Engine SHALL criar subscriptions WMI para eventos de: criação/parada de serviços, falhas de disco, e eventos de segurança críticos.
2. WHERE o ambiente suportar Kubernetes, THE Event_Engine SHALL consumir o stream de eventos da Kubernetes API (`/api/v1/watch/events`) e processar eventos de tipo `Warning` e `Normal` com `reason` em: `OOMKilling`, `BackOff`, `Failed`, `Evicted`.
3. WHERE o ambiente suportar Docker, THE Event_Engine SHALL consumir o stream de eventos Docker (`/events`) e processar eventos de tipo: `die`, `oom`, `health_status`.
4. WHEN o Event_Engine receber um evento, THE Event_Engine SHALL converter o evento em um SensorResult e enviá-lo à API em no máximo 5 segundos.
5. IF a conexão com a fonte de eventos for interrompida, THEN THE Event_Engine SHALL tentar reconectar com backoff exponencial: 5s, 10s, 30s, 60s.

---

### Requisito 13: Migração para TimescaleDB

**User Story:** Como arquiteto de dados, quero migrar o armazenamento de métricas para TimescaleDB, para que queries de séries temporais sejam executadas com alta performance e o armazenamento seja otimizado com compressão e retention policies.

#### Critérios de Aceitação

1. THE TimescaleDB SHALL ser configurado como extensão do PostgreSQL existente, sem substituição do banco de dados.
2. THE TimescaleDB SHALL criar hypertables para as tabelas de métricas com particionamento por tempo (`chunk_time_interval = 1 day`).
3. THE TimescaleDB SHALL aplicar compressão automática em chunks com mais de 7 dias de idade.
4. THE TimescaleDB SHALL aplicar retention policy para remover dados com mais de 365 dias automaticamente.
5. THE TimescaleDB SHALL criar continuous aggregates (downsampling) para: médias horárias (retenção 90 dias) e médias diárias (retenção 365 dias).
6. WHEN uma query de dashboard solicitar dados de um período superior a 24 horas, THE TimescaleDB SHALL usar os continuous aggregates em vez dos dados brutos.
7. THE TimescaleDB SHALL expor métricas de compressão: `total_chunks`, `compressed_chunks`, `compression_ratio`, `disk_size_before`, `disk_size_after`.

---

### Requisito 14: AIOps Expandido

**User Story:** Como analista de operações, quero capacidades avançadas de AIOps incluindo detecção de anomalias, correlação de eventos e predição de falhas, para que problemas sejam identificados proativamente antes de impactar os usuários.

#### Critérios de Aceitação

1. THE AIOps_Engine SHALL implementar detecção de anomalias usando Isolation Forest para métricas de CPU, memória e disco, com janela de treinamento de 7 dias.
2. WHEN o AIOps_Engine detectar uma anomalia, THE AIOps_Engine SHALL gerar um alerta com: `anomaly_score`, `affected_metric`, `expected_range`, `observed_value`, e `confidence_level`.
3. THE AIOps_Engine SHALL implementar correlação de eventos para identificar grupos de alertas relacionados dentro de uma janela de 5 minutos no mesmo host ou hosts do mesmo grupo.
4. THE AIOps_Engine SHALL implementar análise de causa raiz que, dado um conjunto de alertas correlacionados, identifique o alerta mais provável de ser a causa raiz com base em: ordem temporal, severidade e dependências entre hosts.
5. THE AIOps_Engine SHALL implementar predição de falhas usando Prophet ou ARIMA para métricas de tendência (disco crescendo, memória aumentando), com horizonte de predição de 24 horas.
6. WHEN o AIOps_Engine predizer que uma métrica atingirá threshold crítico em menos de 24 horas, THE AIOps_Engine SHALL gerar um alerta preditivo com `predicted_breach_time` e `confidence_interval`.
7. THE AIOps_Engine SHALL retreinar os modelos de detecção de anomalias automaticamente a cada 24 horas com os dados mais recentes.

---

### Requisito 15: Monitoramento Interno do Probe

**User Story:** Como engenheiro de confiabilidade, quero que o probe monitore sua própria saúde e performance, para que degradações no próprio agente de coleta sejam detectadas e reportadas antes de causarem lacunas no monitoramento.

#### Critérios de Aceitação

1. THE Probe SHALL coletar e reportar as seguintes Internal_Metrics a cada 60 segundos: `probe_cpu_percent`, `probe_memory_mb`, `rpc_connections_active`, `wmi_query_latency_ms_avg`, `sensor_execution_time_ms_avg`, `worker_queue_size`, `cache_hit_ratio`.
2. THE Probe SHALL enviar as Internal_Metrics para a API usando o mesmo endpoint de métricas regulares, com `sensor_type=probe_internal`.
3. WHEN `worker_queue_size` exceder 80% da capacidade máxima do Worker_Pool, THE Probe SHALL registrar um alerta de nível WARNING.
4. WHEN `probe_memory_mb` exceder 512 MB, THE Probe SHALL registrar um alerta de nível WARNING e reduzir o número máximo de workers para 10.
5. THE Probe SHALL manter um log de saúde rotativo com as últimas 1000 entradas de Internal_Metrics para diagnóstico local.

---

### Requisito 16: Segurança de Credenciais

**User Story:** Como responsável pela segurança, quero que as credenciais de acesso aos hosts monitorados sejam armazenadas e transmitidas de forma segura, para que senhas e chaves não fiquem expostas em arquivos de configuração ou logs.

#### Critérios de Aceitação

1. THE Probe SHALL criptografar todas as credenciais armazenadas localmente usando AES-256.
2. WHERE o ambiente disponibilizar HashiCorp Vault, THE Probe SHALL buscar credenciais diretamente do Vault via API, sem armazenamento local.
3. WHERE o ambiente disponibilizar Azure Key Vault, THE Probe SHALL buscar credenciais diretamente do Azure Key Vault via SDK, sem armazenamento local.
4. THE Probe SHALL nunca registrar senhas, chaves ou tokens em arquivos de log, substituindo-os por `[REDACTED]`.
5. WHEN uma credencial for rotacionada no sistema de gerenciamento, THE Probe SHALL detectar a mudança e atualizar a credencial em uso em no máximo 60 segundos sem reinicialização.
6. THE Probe SHALL validar a integridade das credenciais criptografadas na inicialização e recusar credenciais com assinatura inválida.

---

### Requisito 17: Arquitetura Multi-Probe Escalável

**User Story:** Como arquiteto de infraestrutura, quero uma arquitetura que suporte múltiplos probes distribuídos coordenados por um Core Server, para que o monitoramento escale horizontalmente para cobrir datacenters, nuvem e edge sem ponto único de falha.

#### Critérios de Aceitação

1. THE Core_Server SHALL suportar o registro e gerenciamento de múltiplos probes com os tipos: `probe_datacenter`, `probe_cloud`, `probe_edge`.
2. THE Core_Server SHALL distribuir automaticamente servidores para monitoramento entre probes disponíveis com base em: localização de rede, carga atual e capacidade configurada.
3. WHEN um Probe ficar offline por mais de 120 segundos, THE Core_Server SHALL redistribuir os servidores desse probe para outros probes disponíveis do mesmo tipo.
4. THE Core_Server SHALL receber heartbeat de cada Probe a cada 60 segundos e atualizar o status do probe como `online`, `degraded` ou `offline`.
5. WHEN um Probe retornar ao estado `online` após período offline, THE Core_Server SHALL restaurar a distribuição original de servidores para esse probe.
6. THE Core_Server SHALL expor um dashboard de status de todos os probes com: `probe_name`, `type`, `status`, `servers_monitored`, `sensors_active`, `last_heartbeat`.

---

### Requisito 18: Observabilidade com Prometheus e Grafana

**User Story:** Como engenheiro de SRE, quero que o probe exponha métricas no formato Prometheus e que dashboards Grafana pré-configurados estejam disponíveis, para que a saúde do sistema de monitoramento seja observável com as ferramentas padrão da indústria.

#### Critérios de Aceitação

1. THE Probe SHALL expor um endpoint `/metrics` no formato Prometheus (text/plain) na porta 9090.
2. THE Probe SHALL expor as seguintes métricas Prometheus: `coruja_probe_sensors_total`, `coruja_probe_sensor_execution_seconds`, `coruja_probe_wmi_queries_total`, `coruja_probe_cache_hits_total`, `coruja_probe_cache_misses_total`, `coruja_probe_worker_queue_size`, `coruja_probe_errors_total`.
3. THE Probe SHALL incluir labels Prometheus: `probe_name`, `sensor_type`, `target_host`, `status`.
4. WHERE o ambiente disponibilizar Grafana, THE Probe SHALL fornecer dashboards pré-configurados em formato JSON para: visão geral do probe, performance de coleta por protocolo, e saúde do worker pool.
5. THE Probe SHALL atualizar as métricas Prometheus a cada 15 segundos.
