# Documento de Requisitos — Coruja Monitor v3.0

## Introdução

Este documento descreve os requisitos para a evolução do **Coruja Monitor v2.0** para a versão **v3.0**, transformando-o em uma plataforma de observabilidade inteligente e escalável comparável a Datadog e Dynatrace.

O sistema atual (v2.0) opera com: FastAPI no Linux (api/), React no frontend (frontend/), Celery worker (worker/), PostgreSQL, Docker Compose, e uma sonda Windows (probe/) instalada como serviço NSSM no SRVSONDA001. Já existem componentes como `wmi_pool.py`, `smart_collector.py`, `global_rate_limiter.py`, `event_queue.py`, `metrics_pipeline/`, `protocol_engines/` e `ai-agent/` (anomaly_detector, event_correlator, failure_predictor, root_cause_engine).

A v3.0 introduz: contratos globais Pydantic (spec central), dependency engine entre sensores, topology engine, separação métrica/evento, arquitetura multi-agente de IA, feedback loop de IA, análise de causa raiz avançada, sistema de alertas inteligentes, portal de observabilidade, DSL declarativa para sensores, probes distribuídas, arquitetura de streaming e suite completa de testes — tudo mantendo compatibilidade com a arquitetura existente.

---

## Glossário

- **Coruja_Monitor**: A plataforma de observabilidade inteligente como um todo (v3.0).
- **Spec_Central**: Módulo `core/spec/` com contratos globais Pydantic — fonte única da verdade para todos os módulos.
- **Host**: Entidade monitorada (servidor, switch, appliance) com atributos: `id`, `hostname`, `ip_address`, `type`, `tags`, `metadata`.
- **Sensor**: Unidade atômica de monitoramento com atributos: `id`, `host_id`, `type`, `protocol`, `interval`, `timeout`, `retries`, `query`, `thresholds`.
- **Metric**: Dado contínuo e quantitativo coletado periodicamente (CPU %, RAM %, latência ms). Possui `sensor_id`, `host_id`, `value`, `unit`, `timestamp`.
- **Event**: Mudança de estado discreta e significativa gerada a partir de uma Metric ou de uma fonte externa. Possui `id`, `host_id`, `type`, `severity`, `timestamp`, `source_metric_id`.
- **Alert**: Notificação gerada pelo Alert_Engine a partir de um ou mais Events, com supressão de duplicados e agrupamento.
- **TopologyNode**: Nó no grafo de topologia com atributos: `id`, `type` (switch/server/service/application), `parent_id`, `children_ids`, `metadata`.
- **ProbeNode**: Agente de coleta distribuído com atributos: `id`, `name`, `location`, `status`, `capacity`, `assigned_hosts`.
- **Dependency_Engine**: Componente que gerencia o grafo de dependências entre sensores e controla execução condicional.
- **Topology_Engine**: Componente que modela e mantém as relações hierárquicas entre recursos de infraestrutura.
- **Event_Processor**: Componente que converte Metrics em Events com base em thresholds configurados.
- **SmartSchedulerAgent**: Agente de IA que ajusta dinamicamente os intervalos de coleta por host e sensor.
- **AnomalyDetectionAgent**: Agente de IA que detecta anomalias usando baseline estatístico.
- **CorrelationAgent**: Agente de IA que correlaciona eventos relacionados em janelas de tempo.
- **RootCauseAgent**: Agente de IA que usa topologia e eventos para identificar causa raiz.
- **DecisionAgent**: Agente de IA que decide se um conjunto de eventos deve gerar um Alert.
- **AutoRemediationAgent**: Agente de IA que executa ações automáticas de remediação.
- **Feedback_Loop**: Ciclo de aprendizado: monitoramento → evento → decisão → ação → resultado → aprendizado.
- **Alert_Engine**: Sistema de alertas com supressão de duplicados, agrupamento e priorização automática.
- **Sensor_DSL**: Linguagem declarativa para definição de sensores com parser e pretty-printer.
- **Stream_Pipeline**: Pipeline de ingestão massiva: probe → stream (Redis/Kafka) → processor → TimescaleDB.
- **WMI**: Windows Management Instrumentation — protocolo de coleta em hosts Windows.
- **SNMP**: Simple Network Management Protocol — protocolo de coleta em dispositivos de rede e Linux.
- **TimescaleDB**: Extensão PostgreSQL para séries temporais com compressão e retention policies.

---

## Requisitos

### Requisito 1: Spec Central — Contratos Globais Pydantic

**User Story:** Como desenvolvedor, quero contratos globais definidos com Pydantic em `core/spec/`, para que todos os módulos do sistema compartilhem a mesma fonte de verdade sobre tipos de dados, evitando inconsistências entre probe, API, worker e agentes de IA.

#### Critérios de Aceitação

1. THE Spec_Central SHALL definir os seguintes modelos Pydantic: `Host`, `Sensor`, `Metric`, `Event`, `Alert`, `TopologyNode`, `ProbeNode`.
2. THE Spec_Central SHALL validar automaticamente todos os campos obrigatórios e tipos de dados ao instanciar qualquer modelo.
3. WHEN um módulo importar um modelo do Spec_Central, THE Spec_Central SHALL garantir que o modelo seja idêntico em todos os módulos sem duplicação de definição.
4. THE `Host` model SHALL conter os campos: `id` (UUID), `hostname` (str), `ip_address` (str), `type` (enum: server/switch/appliance/container), `tags` (list[str]), `metadata` (dict), `created_at` (datetime).
5. THE `Sensor` model SHALL conter os campos: `id` (UUID), `host_id` (UUID), `type` (str), `protocol` (enum: wmi/snmp/icmp/tcp/http), `interval` (int, segundos), `timeout` (int, segundos), `retries` (int), `thresholds` (dict com warning e critical).
6. THE `Metric` model SHALL conter os campos: `sensor_id` (UUID), `host_id` (UUID), `value` (float), `unit` (str), `timestamp` (datetime), `status` (enum: ok/warning/critical/unknown).
7. THE `Event` model SHALL conter os campos: `id` (UUID), `host_id` (UUID), `type` (str), `severity` (enum: info/warning/critical), `timestamp` (datetime), `source_metric_id` (UUID, opcional), `description` (str).
8. THE `Alert` model SHALL conter os campos: `id` (UUID), `event_ids` (list[UUID]), `title` (str), `severity` (enum), `status` (enum: open/acknowledged/resolved), `root_cause` (str, opcional), `affected_hosts` (list[UUID]), `created_at` (datetime).
9. THE `TopologyNode` model SHALL conter os campos: `id` (UUID), `type` (enum: switch/server/service/application), `parent_id` (UUID, opcional), `children_ids` (list[UUID]), `metadata` (dict).
10. THE `ProbeNode` model SHALL conter os campos: `id` (UUID), `name` (str), `location` (str), `status` (enum: online/degraded/offline), `capacity` (int), `assigned_hosts` (list[UUID]).
11. FOR ALL modelos do Spec_Central, serializar para JSON e desserializar de volta SHALL produzir um objeto equivalente ao original (propriedade round-trip).

---

### Requisito 2: Sensor Dependency Engine

**User Story:** Como engenheiro de monitoramento, quero um grafo de dependências entre sensores, para que sensores pesados (WMI) só sejam executados quando sensores de pré-requisito (Ping) confirmarem que o host está acessível, evitando tentativas desnecessárias e lockout de contas AD.

#### Critérios de Aceitação

1. THE Dependency_Engine SHALL representar as dependências entre sensores como um grafo dirigido acíclico (DAG).
2. WHEN um sensor pai (ex.: Ping) retornar `status=critical`, THE Dependency_Engine SHALL suspender a execução de todos os sensores filhos (ex.: WMI, SNMP) daquele host.
3. WHEN um sensor pai retornar ao `status=ok`, THE Dependency_Engine SHALL reativar a execução dos sensores filhos suspensos.
4. THE Dependency_Engine SHALL manter cache de estado por host com TTL de 30 segundos para evitar verificações redundantes.
5. THE Dependency_Engine SHALL suportar dependências em cascata: Ping → TCP_Port_135 → WMI_Namespace → WMI_Sensors.
6. IF um ciclo de dependência for detectado na configuração do grafo, THEN THE Dependency_Engine SHALL rejeitar a configuração e retornar erro descritivo.
7. THE Dependency_Engine SHALL expor o estado atual do grafo via endpoint de status com: total de nós, arestas, sensores suspensos por host.
8. WHEN o estado de dependência de um host mudar, THE Dependency_Engine SHALL registrar a mudança nos logs com timestamp, host, sensor pai e ação tomada.

---

### Requisito 3: Topology Engine

**User Story:** Como operador de NOC, quero um modelo de topologia que represente as relações entre switches, servidores, serviços e aplicações, para que o impacto de falhas seja visualizado e a análise de causa raiz use o contexto de infraestrutura real.

#### Critérios de Aceitação

1. THE Topology_Engine SHALL modelar a hierarquia: Switch → Servidor → Serviço → Aplicação usando `TopologyNode`.
2. THE Topology_Engine SHALL suportar descoberta automática de topologia via SNMP (ARP table, LLDP/CDP) para switches e roteadores.
3. THE Topology_Engine SHALL suportar descoberta automática de topologia via WMI para servidores Windows (serviços instalados, processos em execução).
4. WHEN um `TopologyNode` do tipo `switch` ficar offline, THE Topology_Engine SHALL identificar automaticamente todos os `TopologyNode` filhos afetados e propagar o status `impacted`.
5. THE Topology_Engine SHALL calcular o `blast_radius` (raio de impacto) de qualquer nó: número de hosts, serviços e aplicações afetados se aquele nó falhar.
6. THE Topology_Engine SHALL persistir o grafo de topologia no banco de dados e recarregá-lo na inicialização.
7. WHEN a topologia for atualizada por descoberta automática, THE Topology_Engine SHALL preservar customizações manuais feitas pelo operador.
8. THE Topology_Engine SHALL expor o grafo completo via API REST em formato compatível com visualização de grafos (nodes + edges).

---

### Requisito 4: Separação Métrica vs. Evento

**User Story:** Como arquiteto de dados, quero separação clara entre Metrics (dados contínuos) e Events (mudanças de estado), para que o pipeline de dados seja otimizado para cada tipo e alertas sejam gerados apenas em transições de estado relevantes, não em cada coleta.

#### Critérios de Aceitação

1. THE Event_Processor SHALL diferenciar `Metric` (dado contínuo quantitativo) de `Event` (mudança de estado discreta).
2. WHEN uma `Metric` cruzar um threshold configurado no `Sensor`, THE Event_Processor SHALL gerar um `Event` com `type` correspondente (ex.: `high_cpu`, `low_memory`, `disk_full`).
3. THE Event_Processor SHALL gerar `Event` apenas na transição de estado (ok→warning, warning→critical, critical→ok), não em cada coleta com o mesmo status.
4. THE Event_Processor SHALL suportar os seguintes tipos de evento gerados por threshold: `high_cpu` (CPU > threshold), `low_memory` (RAM livre < threshold), `disk_full` (disco > threshold), `host_unreachable` (ping falhou), `service_down` (serviço parado).
5. THE Event_Processor SHALL armazenar `Metrics` em tabela otimizada para séries temporais (TimescaleDB hypertable).
6. THE Event_Processor SHALL armazenar `Events` em tabela relacional separada com índices em `host_id`, `type`, `severity` e `timestamp`.
7. WHEN um `Event` for gerado, THE Event_Processor SHALL publicá-lo na fila de eventos para consumo pelos agentes de IA e Alert_Engine em no máximo 1 segundo.
8. THE Event_Processor SHALL suportar thresholds dinâmicos por host, sobrescrevendo os thresholds padrão do sensor.

---

### Requisito 5: Arquitetura Multi-Agente de IA

**User Story:** Como analista de operações, quero uma arquitetura com múltiplos agentes de IA especializados e coordenados, para que cada aspecto da inteligência operacional (scheduling, anomalia, correlação, causa raiz, decisão, remediação) seja tratado por um agente dedicado e extensível.

#### Critérios de Aceitação

1. THE SmartSchedulerAgent SHALL ajustar dinamicamente os intervalos de coleta por sensor com base no histórico de anomalias: reduzir para 30s quando anomalia detectada, restaurar para padrão após 5 ciclos normais.
2. THE AnomalyDetectionAgent SHALL manter um baseline estatístico (média + desvio padrão) por sensor com janela deslizante de 7 dias.
3. WHEN o valor de uma `Metric` desviar mais de 3 desvios padrão do baseline, THE AnomalyDetectionAgent SHALL gerar um `Event` com `type=anomaly` e `confidence_score`.
4. THE CorrelationAgent SHALL agrupar `Events` relacionados dentro de uma janela de 5 minutos no mesmo host ou hosts do mesmo grupo topológico.
5. THE RootCauseAgent SHALL usar o grafo de topologia para identificar o nó raiz de um grupo de eventos correlacionados, priorizando nós com maior `blast_radius`.
6. THE DecisionAgent SHALL avaliar eventos correlacionados e decidir se geram um `Alert`, considerando: severidade, número de hosts afetados, horário (janela de manutenção) e histórico de falsos positivos.
7. THE AutoRemediationAgent SHALL executar ações de remediação pré-configuradas (reiniciar serviço, limpar cache, escalar recurso) quando o DecisionAgent aprovar e a confiança for superior a 85%.
8. WHEN o AutoRemediationAgent executar uma ação, THE AutoRemediationAgent SHALL registrar: ação executada, host alvo, timestamp, resultado (sucesso/falha) e duração.
9. THE Multi_Agent_System SHALL coordenar os agentes em pipeline sequencial: AnomalyDetectionAgent → CorrelationAgent → RootCauseAgent → DecisionAgent → AutoRemediationAgent.
10. IF qualquer agente falhar durante o processamento, THEN THE Multi_Agent_System SHALL continuar o pipeline com os demais agentes e registrar o erro do agente falho.

---

### Requisito 6: AI Feedback Loop

**User Story:** Como engenheiro de IA, quero um ciclo de feedback que registre ações tomadas e seus resultados, para que os agentes de IA aprendam com o histórico operacional e melhorem a precisão das decisões ao longo do tempo.

#### Critérios de Aceitação

1. THE Feedback_Loop SHALL registrar cada ciclo completo: `monitoring_event` → `ai_decision` → `action_taken` → `action_result` → `learning_update`.
2. THE Feedback_Loop SHALL armazenar o histórico de ações com os campos: `action_id`, `agent_name`, `action_type`, `target_host`, `timestamp`, `result` (success/failure/partial), `resolution_time_seconds`.
3. WHEN uma ação de remediação for executada e o problema for resolvido em menos de 300 segundos, THE Feedback_Loop SHALL registrar como `positive_outcome` e aumentar o peso daquela ação no modelo de decisão.
4. WHEN uma ação de remediação for executada e o problema persistir após 300 segundos, THE Feedback_Loop SHALL registrar como `negative_outcome` e reduzir o peso daquela ação.
5. THE Feedback_Loop SHALL calcular e expor métricas de eficácia: `actions_total`, `actions_successful`, `mean_resolution_time_seconds`, `false_positive_rate`.
6. THE Feedback_Loop SHALL retreinar os modelos dos agentes com os dados de feedback a cada 24 horas.
7. THE Feedback_Loop SHALL manter histórico de no mínimo 90 dias de ações e resultados para análise de tendências.

---

### Requisito 7: Root Cause Analysis Engine

**User Story:** Como operador de NOC, quero um motor de análise de causa raiz que use topologia e eventos correlacionados, para que em cenários como "switch down → hosts offline" a causa raiz seja identificada automaticamente e não sejam gerados alertas individuais para cada host afetado.

#### Critérios de Aceitação

1. THE RootCauseAgent SHALL analisar grupos de eventos correlacionados e identificar o `TopologyNode` com maior probabilidade de ser a causa raiz.
2. WHEN múltiplos hosts ficarem offline simultaneamente e compartilharem um `TopologyNode` pai comum (ex.: switch), THE RootCauseAgent SHALL identificar o nó pai como causa raiz com `confidence >= 0.8`.
3. THE RootCauseAgent SHALL usar a ordem temporal dos eventos: o evento mais antigo no nó de maior hierarquia tem prioridade como causa raiz.
4. THE RootCauseAgent SHALL gerar um único `Alert` consolidado para a causa raiz, listando todos os hosts afetados como `affected_hosts`, em vez de alertas individuais.
5. THE RootCauseAgent SHALL calcular e incluir no Alert: `root_cause_node`, `affected_nodes_count`, `estimated_impact` (serviços e aplicações afetados), `confidence_score`.
6. WHEN a causa raiz for resolvida (nó pai voltar ao status ok), THE RootCauseAgent SHALL automaticamente marcar o Alert consolidado como `resolved` e notificar os hosts afetados.
7. THE RootCauseAgent SHALL suportar análise de causa raiz para os cenários: falha de switch, falha de servidor pai, falha de serviço compartilhado, e saturação de recurso em cascata.

---

### Requisito 8: Intelligent Alert System

**User Story:** Como operador de NOC, quero um sistema de alertas inteligente que suprima duplicados, agrupe eventos relacionados e priorize automaticamente, para que o volume de alertas seja gerenciável e cada alerta recebido seja acionável.

#### Critérios de Aceitação

1. THE Alert_Engine SHALL suprimir alertas duplicados: se um Alert com o mesmo `host_id`, `type` e `severity` já estiver `open`, THE Alert_Engine SHALL não criar um novo Alert.
2. THE Alert_Engine SHALL agrupar Events relacionados em um único Alert quando: mesmo host, mesma janela de 5 minutos, e tipos de evento relacionados (ex.: `high_cpu` + `high_memory` no mesmo host).
3. THE Alert_Engine SHALL calcular prioridade automática de cada Alert com base em: severidade (40%), número de hosts afetados (30%), impacto em serviços críticos (20%), e horário de negócio (10%).
4. WHEN um Alert for criado, THE Alert_Engine SHALL notificar os canais configurados (email, webhook, Teams/Slack) em no máximo 30 segundos.
5. THE Alert_Engine SHALL suportar janelas de manutenção: WHILE um host estiver em janela de manutenção, THE Alert_Engine SHALL suprimir todos os Alerts para aquele host.
6. THE Alert_Engine SHALL implementar escalação automática: se um Alert crítico não for reconhecido em 15 minutos, THE Alert_Engine SHALL escalar para o próximo nível de notificação.
7. THE Alert_Engine SHALL expor métricas de qualidade: `alerts_total`, `alerts_suppressed`, `alerts_grouped`, `mean_time_to_acknowledge`, `mean_time_to_resolve`.
8. IF o Alert_Engine receber mais de 100 Events por minuto do mesmo host, THEN THE Alert_Engine SHALL ativar modo de flood protection e agrupar todos os eventos em um único Alert de alta prioridade.

---

### Requisito 9: Observability Portal (Frontend v3)

**User Story:** Como operador de NOC e engenheiro de infraestrutura, quero um portal de observabilidade completo com dashboards especializados, para que o estado da infraestrutura, anomalias, topologia e alertas sejam visualizados de forma clara e acionável em tempo real.

#### Critérios de Aceitação

1. THE Observability_Portal SHALL incluir um Dashboard de Observabilidade com: health score geral da infraestrutura, mapa de impacto, alertas críticos ativos, e tendências de métricas nas últimas 24 horas.
2. THE Observability_Portal SHALL incluir uma Topology View com grafo interativo de infraestrutura (estilo Datadog Service Map): nós coloridos por status, arestas representando dependências, e drill-down por nó.
3. THE Observability_Portal SHALL incluir uma Página de Alertas Inteligentes com: causa raiz identificada, lista de hosts afetados, timeline de eventos, e ações de remediação sugeridas.
4. THE Observability_Portal SHALL incluir uma Página de AIOps com: anomalias detectadas, previsões de falha (próximas 24h), ações automáticas executadas, e métricas de eficácia dos agentes.
5. THE Observability_Portal SHALL incluir uma Página de Métricas Avançadas com: zoom temporal, comparação entre hosts, correlação visual entre métricas, e exportação de dados.
6. THE Observability_Portal SHALL incluir uma Página de Eventos com: timeline interativa, filtros por host/tipo/severidade/período, e agrupamento por causa raiz.
7. WHEN o status de qualquer host mudar, THE Observability_Portal SHALL atualizar o dashboard em tempo real via WebSocket em no máximo 5 segundos.
8. THE Observability_Portal SHALL ser responsivo e funcionar em resoluções de 1280x720 até 4K.
9. THE Observability_Portal SHALL manter compatibilidade com os componentes React existentes (Dashboard.js, AIOps.js, NOCMode.js, EventTimeline.js) via refatoração incremental.

---

### Requisito 10: Sensor DSL

**User Story:** Como administrador de monitoramento, quero uma linguagem declarativa para definir sensores, para que novos sensores possam ser criados sem escrever código Python, usando uma sintaxe legível e validada.

#### Critérios de Aceitação

1. THE Sensor_DSL SHALL suportar a seguinte sintaxe de definição de sensor:
   ```
   sensor "cpu_load" {
     protocol = "wmi"
     query    = "Win32_Processor.LoadPercentage"
     interval = 60
     warning  = 80
     critical = 95
   }
   ```
2. THE Sensor_DSL SHALL suportar os campos obrigatórios: `protocol`, `interval`.
3. THE Sensor_DSL SHALL suportar os campos opcionais: `query`, `warning`, `critical`, `timeout`, `retries`, `tags`, `description`.
4. WHEN um arquivo DSL válido for fornecido, THE Sensor_DSL SHALL parsear e retornar uma lista de objetos `Sensor` do Spec_Central.
5. WHEN um arquivo DSL inválido for fornecido, THE Sensor_DSL SHALL retornar uma mensagem de erro descritiva com número de linha e campo inválido.
6. THE Sensor_DSL SHALL incluir um pretty-printer que formate objetos `Sensor` de volta para a sintaxe DSL.
7. FOR ALL definições DSL válidas, parsear então imprimir então parsear novamente SHALL produzir um objeto `Sensor` equivalente ao original (propriedade round-trip).
8. THE Sensor_DSL SHALL suportar comentários de linha com `#` e comentários de bloco com `/* */`.
9. THE Sensor_DSL SHALL validar os valores de `protocol` contra a lista de protocolos suportados: `wmi`, `snmp`, `icmp`, `tcp`, `http`.
10. THE Sensor_DSL SHALL suportar herança de templates: `sensor "disk_c" extends "disk_template" { path = "C:" }`.

---

### Requisito 11: Distributed Probes

**User Story:** Como arquiteto de infraestrutura, quero probes distribuídas com balanceamento de carga, afinidade por localização e failover automático, para que o monitoramento escale horizontalmente e não haja ponto único de falha na coleta.

#### Critérios de Aceitação

1. THE Coruja_Monitor SHALL suportar múltiplas `ProbeNode` registradas no Core_Server com tipos: `datacenter`, `cloud`, `edge`.
2. THE Core_Server SHALL distribuir hosts entre ProbeNodes disponíveis usando balanceamento de carga baseado em: capacidade atual (hosts atribuídos / capacidade máxima) e localização de rede (afinidade por subnet).
3. WHEN uma ProbeNode ficar offline por mais de 120 segundos, THE Core_Server SHALL redistribuir automaticamente os hosts daquela ProbeNode para outras ProbeNodes disponíveis do mesmo tipo ou tipo compatível.
4. WHEN uma ProbeNode retornar ao status `online` após período offline, THE Core_Server SHALL restaurar gradualmente os hosts originais em no máximo 300 segundos para evitar pico de carga.
5. THE Core_Server SHALL receber heartbeat de cada ProbeNode a cada 60 segundos e atualizar o status: `online` (heartbeat < 90s), `degraded` (heartbeat 90-120s), `offline` (heartbeat > 120s).
6. THE Coruja_Monitor SHALL garantir que cada host seja monitorado por exatamente uma ProbeNode ativa em qualquer momento.
7. THE Core_Server SHALL expor dashboard de status de todas as ProbeNodes com: nome, tipo, status, hosts monitorados, sensores ativos, última comunicação.
8. WHERE múltiplas ProbeNodes estiverem disponíveis na mesma localização, THE Core_Server SHALL distribuir a carga de forma que nenhuma ProbeNode exceda 80% de sua capacidade máxima.

---

### Requisito 12: Streaming Architecture

**User Story:** Como arquiteto de dados, quero uma arquitetura de streaming para ingestão massiva de métricas, para que o sistema suporte milhares de hosts com dezenas de sensores cada sem degradação de performance no banco de dados.

#### Critérios de Aceitação

1. THE Stream_Pipeline SHALL implementar o fluxo: ProbeNode → Stream_Broker (Redis Streams ou Kafka) → Stream_Processor → TimescaleDB.
2. THE Stream_Pipeline SHALL suportar ingestão de no mínimo 10.000 métricas por segundo no Stream_Broker sem perda de dados.
3. THE Stream_Processor SHALL consumir métricas do Stream_Broker em batches de no máximo 500 métricas por operação de escrita no banco.
4. THE Stream_Pipeline SHALL garantir entrega at-least-once: se o Stream_Processor falhar, as métricas não processadas SHALL ser reprocessadas na reinicialização.
5. WHEN o Stream_Broker não estiver disponível, THE ProbeNode SHALL armazenar métricas em buffer local com capacidade de no mínimo 10.000 métricas e reenviar quando a conexão for restaurada.
6. THE Stream_Pipeline SHALL expor métricas de throughput: `messages_per_second`, `processing_latency_ms`, `buffer_size`, `consumer_lag`.
7. THE Stream_Pipeline SHALL suportar múltiplos consumidores paralelos (consumer groups) para escalar o processamento horizontalmente.
8. WHEN a latência de processamento exceder 5 segundos, THE Stream_Pipeline SHALL registrar alerta de nível WARNING e aumentar o número de consumidores automaticamente se possível.

---

### Requisito 13: Testes e Validação

**User Story:** Como engenheiro de qualidade, quero uma suite completa de testes automatizados cobrindo todos os componentes críticos do v3.0, para que regressões sejam detectadas antes de chegar à produção e a confiabilidade do sistema seja garantida.

#### Critérios de Aceitação

1. THE Test_Suite SHALL incluir testes unitários para: Dependency_Engine (grafo DAG, execução condicional, cache de estado), Topology_Engine (hierarquia, blast radius, propagação de status), Event_Processor (geração de eventos por threshold, deduplicação), e Alert_Engine (supressão, agrupamento, priorização).
2. THE Test_Suite SHALL incluir testes para todos os agentes de IA: SmartSchedulerAgent, AnomalyDetectionAgent, CorrelationAgent, RootCauseAgent, DecisionAgent, AutoRemediationAgent.
3. THE Test_Suite SHALL incluir testes para o Sensor_DSL: parsing de sintaxe válida, rejeição de sintaxe inválida, e propriedade round-trip (parse → print → parse).
4. THE Test_Suite SHALL incluir simulação de carga com 1.000 hosts e 50 sensores por host (50.000 sensores totais) para validar performance do Dependency_Engine e Stream_Pipeline.
5. WHEN a simulação de 1.000 hosts for executada, THE Stream_Pipeline SHALL processar todas as métricas com latência média inferior a 2 segundos e sem perda de dados.
6. THE Test_Suite SHALL incluir testes de integração para o ciclo completo: coleta de métrica → geração de evento → correlação → causa raiz → alerta → remediação → feedback.
7. THE Test_Suite SHALL incluir testes de regressão para os componentes existentes do v2.0: `wmi_pool.py`, `smart_collector.py`, `global_rate_limiter.py`, `event_queue.py`, garantindo que a migração para v3.0 não quebre funcionalidades existentes.
8. WHEN qualquer teste de regressão do v2.0 falhar, THE Test_Suite SHALL bloquear o merge e reportar o componente afetado com detalhes do erro.
9. THE Test_Suite SHALL atingir cobertura mínima de 80% de linhas de código nos módulos: `core/spec/`, `engine/dependency_engine.py`, `topology_engine/`, `event_processor/`, `ai_agents/`, `alert_engine/`.
10. THE Test_Suite SHALL incluir testes de propriedade (property-based testing) para: round-trip de serialização dos modelos Pydantic do Spec_Central, idempotência do Event_Processor (processar o mesmo evento duas vezes não gera duplicatas), e invariantes do Dependency_Engine (grafo DAG nunca contém ciclos após operações de adição).
