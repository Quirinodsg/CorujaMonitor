# Documento de Requisitos — Suite de Testes Completa Coruja Monitor v3.0

## Introdução

Este documento define os requisitos para a criação de uma suite de testes abrangente e mission-critical para o sistema Coruja Monitor v3.0. A suite deve cobrir todos os 11 módulos do sistema (Probe, Dependency Engine, Streaming, Event Processor, AI Pipeline, Alert Engine, Topology Engine, Sensor DSL, API, Frontend, Database) com 9 tipos de teste (unitário, integração, E2E, carga, chaos engineering, resiliência, performance, segurança, IA). O sistema já possui 349 testes existentes; esta suite expande a cobertura para ≥85% com cenários críticos obrigatórios, utilitários de simulação e relatório automatizado de métricas.

## Glossário

- **Suite_de_Testes**: Conjunto completo de testes automatizados organizados por tipo e módulo
- **Probe**: Sonda de coleta de métricas (Windows) com coletores WMI, SNMP, ICMP, TCP, Docker, Kubernetes
- **Dependency_Engine**: Motor de dependências baseado em DAG (networkx) que controla execução condicional de sensores
- **Streaming_Redis**: Camada de streaming via Redis Streams (XADD/XREADGROUP) com consumer groups e buffer offline
- **Event_Processor**: Processador de eventos baseado em transição de estado com avaliação de thresholds dinâmicos
- **AI_Pipeline**: Pipeline orquestrado de 5 agentes IA (AnomalyDetection, Correlation, RootCause, Decision, AutoRemediation)
- **Alert_Engine**: Motor de alertas com supressão de duplicados, agrupamento, priorização ponderada e notificação SLA ≤30s
- **Topology_Engine**: Motor de topologia baseado em grafo networkx com 4 camadas hierárquicas e blast radius BFS
- **Sensor_DSL**: Linguagem declarativa de sensores com pipeline Lexer → Parser → AST → Compiler e herança de templates
- **API_FastAPI**: Backend REST/WebSocket com 50+ routers, endpoints v2/v3, autenticação e MFA
- **Frontend_React**: Interface React 18 com 40+ componentes, dashboards v3, modo NOC e WebSocket real-time
- **TimescaleDB**: PostgreSQL com extensão TimescaleDB para hypertable metrics_ts (retenção 90 dias, compressão 7 dias)
- **Circuit_Breaker**: Mecanismo de proteção que abre após >50% de falhas nas últimas 10 execuções (5 min de pausa)
- **Feedback_Loop**: Sistema de retroalimentação da IA com retreino a cada 24h e histórico de 90 dias
- **Chaos_Engine**: Utilitário de teste que simula falhas de infraestrutura (Redis offline, latência de rede, perda de pacotes)
- **Event_Simulator**: Utilitário que gera eventos sintéticos para testes de carga e integração
- **Topology_Simulator**: Utilitário que cria topologias de infraestrutura simuladas para testes
- **Load_Generator**: Utilitário que simula carga de 1000 hosts com 50 sensores cada
- **SDD**: Specification-Driven Development — metodologia de desenvolvimento orientada por especificação
- **MCT**: Monitored Canary Testing — metodologia de teste canário monitorado
- **PBT**: Property-Based Testing — testes baseados em propriedades usando Hypothesis

## Requisitos

### Requisito 1: Estrutura e Organização da Suite de Testes

**User Story:** Como desenvolvedor, eu quero uma suite de testes organizada por tipo e módulo com utilitários compartilhados, para que eu possa executar testes de forma isolada ou completa com cobertura ≥85%.

#### Critérios de Aceitação

1. THE Suite_de_Testes SHALL organizar os testes na estrutura de diretórios: `tests/unit/`, `tests/integration/`, `tests/e2e/`, `tests/load/`, `tests/chaos/`, `tests/ai/`, `tests/frontend/`, `tests/api/`, `tests/probe/`, `tests/utils/`
2. THE Suite_de_Testes SHALL fornecer os utilitários compartilhados `event_simulator.py`, `topology_simulator.py`, `load_generator.py` e `chaos_engine.py` no diretório `tests/utils/`
3. THE Suite_de_Testes SHALL suportar execução paralela de testes via pytest-xdist
4. THE Suite_de_Testes SHALL utilizar mocks isolados para dependências externas (Redis, PostgreSQL, API HTTP)
5. WHEN todos os testes são executados, THE Suite_de_Testes SHALL atingir cobertura de código ≥85% nos módulos críticos (core, engine, topology_engine, event_processor, ai_agents, alert_engine, sensor_dsl)
6. THE Suite_de_Testes SHALL gerar logs detalhados de execução com timestamps e resultados por módulo

### Requisito 2: Testes Unitários do Probe (Sonda Windows)

**User Story:** Como desenvolvedor, eu quero testes unitários isolados para cada coletor da sonda, para que eu possa validar a lógica de coleta WMI, SNMP, ICMP, TCP, Docker e Kubernetes independentemente.

#### Critérios de Aceitação

1. THE Suite_de_Testes SHALL testar cada coletor do Probe (WMI, SNMP, ICMP, TCP, Docker, Kubernetes) com mocks das dependências de rede
2. WHEN o coletor WMI recebe dados válidos de um servidor Windows, THE Suite_de_Testes SHALL validar que as métricas de CPU, memória e disco são extraídas corretamente
3. WHEN o coletor SNMP recebe uma resposta GetBulk válida, THE Suite_de_Testes SHALL validar que os OIDs são mapeados para métricas com unidades corretas
4. THE Suite_de_Testes SHALL testar o pool de conexões (WMI pool, SNMP pool, TCP pool) validando aquisição, liberação e timeout de conexões
5. THE Suite_de_Testes SHALL testar o rate limiter global validando que requisições acima do limite são enfileiradas
6. WHEN o buffer offline (deque 10k) atinge capacidade máxima, THE Suite_de_Testes SHALL validar que as métricas mais antigas são descartadas (FIFO)
7. THE Suite_de_Testes SHALL testar o ProbeOrchestrator validando coleta paralela via ThreadPoolExecutor com isolamento de falhas entre hosts

### Requisito 3: Testes Unitários do Dependency Engine (DAG)

**User Story:** Como desenvolvedor, eu quero testes que validem todas as invariantes do DAG de dependências, para que eu possa garantir execução condicional correta e detecção de ciclos.

#### Critérios de Aceitação

1. THE Suite_de_Testes SHALL validar que o grafo de dependências mantém a propriedade DAG (sem ciclos) após qualquer operação de adição de aresta
2. WHEN uma aresta que criaria um ciclo é adicionada, THE Dependency_Engine SHALL rejeitar a operação e manter o grafo válido
3. THE Suite_de_Testes SHALL validar a suspensão em cascata: sensor pai CRITICAL suspende todos os descendentes diretos e indiretos
4. THE Suite_de_Testes SHALL validar a reativação round-trip: suspensão seguida de recuperação restaura a execução dos filhos
5. THE Suite_de_Testes SHALL validar o isolamento entre hosts: estado de host_A não afeta execução de sensores em host_B
6. WHEN o cache TTL expira, THE Dependency_Engine SHALL permitir execução do sensor independentemente do estado anterior

### Requisito 4: Testes do Streaming Redis

**User Story:** Como desenvolvedor, eu quero testes que validem a entrega at-least-once via Redis Streams, para que eu possa garantir que métricas não são perdidas durante o transporte.

#### Critérios de Aceitação

1. THE Suite_de_Testes SHALL validar que XADD em batch de 500 métricas persiste todas as entradas no stream com maxlen correto (100k para metrics_stream, 50k para events_stream)
2. THE Suite_de_Testes SHALL validar que XREADGROUP com consumer groups entrega mensagens a pelo menos um consumidor
3. WHEN um consumidor falha antes de enviar XACK, THE Suite_de_Testes SHALL validar que a mensagem é reprocessada por outro consumidor (at-least-once)
4. WHEN o Redis está offline, THE Suite_de_Testes SHALL validar que o buffer local (deque 10k) armazena métricas sem perda de dados
5. WHEN o Redis reconecta após falha, THE Suite_de_Testes SHALL validar que as métricas do buffer local são enviadas ao stream

### Requisito 5: Testes do Event Processor

**User Story:** Como desenvolvedor, eu quero testes que validem a idempotência do processador de eventos e a avaliação de thresholds dinâmicos, para que eu possa garantir que apenas transições de estado geram eventos.

#### Critérios de Aceitação

1. THE Suite_de_Testes SHALL validar a Property 7 (idempotência): duas métricas consecutivas com mesmo status resultante geram apenas um evento
2. WHEN uma métrica causa transição de estado (ok→warning, warning→critical, critical→ok), THE Event_Processor SHALL gerar exatamente um evento com severidade correspondente
3. THE Suite_de_Testes SHALL validar thresholds dinâmicos: thresholds customizados por host sobrescrevem os padrões do sensor
4. THE Suite_de_Testes SHALL validar o modo "lower is worse" para métricas como memória livre (valor baixo = crítico)
5. THE Suite_de_Testes SHALL validar que sensores diferentes mantêm estados independentes
6. THE Suite_de_Testes SHALL validar a persistência de métricas no TimescaleDB via batch insert ≤500

### Requisito 6: Testes do AI Pipeline (SDD + MCT)

**User Story:** Como desenvolvedor, eu quero testes que validem a inteligência real do pipeline de IA, para que eu possa garantir detecção de anomalias, correlação, causa raiz, decisão e auto-remediação com confiança mensurável.

#### Critérios de Aceitação

1. THE Suite_de_Testes SHALL validar a Property 8: AnomalyDetectionAgent detecta valores que desviam >3σ do baseline com confiança >0
2. THE Suite_de_Testes SHALL validar a Property 9: falha em agente K do pipeline não interrompe execução dos agentes K+1..N
3. THE Suite_de_Testes SHALL validar a Property 10: AutoRemediationAgent executa ações apenas com confiança ≥85%
4. THE Suite_de_Testes SHALL validar a Property 11: FeedbackLoop classifica outcome como "positive" para resolução <300s e "negative" para ≥300s
5. THE Suite_de_Testes SHALL validar a Property 12: RootCauseEngine identifica nó pai com confiança ≥0.8 quando N≥2 filhos estão offline
6. THE Suite_de_Testes SHALL validar o Circuit Breaker: >50% de falhas nas últimas 10 execuções abre o circuito por 5 minutos
7. THE Suite_de_Testes SHALL validar o FeedbackLoop: pesos de ações aumentam em outcomes positivos e diminuem em negativos
8. THE Suite_de_Testes SHALL validar a correlação de eventos em janela de 5 minutos agrupados por host

### Requisito 7: Testes do Alert Engine

**User Story:** Como desenvolvedor, eu quero testes que validem supressão de duplicados, agrupamento, priorização e notificação SLA ≤30s, para que eu possa garantir alertas precisos sem spam.

#### Critérios de Aceitação

1. THE Suite_de_Testes SHALL validar a supressão de duplicados: mesmo (host_id, type, severity) dentro de 5 minutos gera apenas um alerta
2. THE Suite_de_Testes SHALL validar o agrupamento de eventos: eventos do mesmo host dentro de janela de 5 minutos são agrupados em um único alerta
3. THE Suite_de_Testes SHALL validar a fórmula de priorização: score = severidade×0.40 + hosts×0.30 + impacto×0.20 + horário×0.10, com resultado no intervalo [0, 1]
4. THE Suite_de_Testes SHALL validar flood protection: >100 eventos/minuto do mesmo host gera exatamente 1 alerta consolidado de alta prioridade
5. THE Suite_de_Testes SHALL validar o notificador com retry 3x e backoff exponencial para canais email, webhook e Teams
6. THE Suite_de_Testes SHALL validar a supressão topológica: quando switch pai está em falha, alertas dos servidores filhos são suprimidos
7. THE Suite_de_Testes SHALL validar janelas de manutenção: eventos de hosts em manutenção ativa são filtrados

### Requisito 8: Testes do Topology Engine

**User Story:** Como desenvolvedor, eu quero testes que validem o grafo de topologia, blast radius e cálculo de impacto, para que eu possa garantir análise correta de cascata de falhas.

#### Critérios de Aceitação

1. THE Suite_de_Testes SHALL validar a serialização round-trip do TopologyGraph: to_dict() seguido de from_dict() produz grafo equivalente
2. THE Suite_de_Testes SHALL validar o blast radius via BFS: falha em switch retorna todos os servidores e serviços dependentes
3. THE Suite_de_Testes SHALL validar as 4 camadas hierárquicas: network (0), hypervisor (1), server (2), service (3)
4. THE Suite_de_Testes SHALL validar ancestors e descendants: consultas retornam nós corretos na hierarquia
5. THE Suite_de_Testes SHALL validar a geração de edges baseada em sensores TCP e ICMP

### Requisito 9: Testes do Sensor DSL

**User Story:** Como desenvolvedor, eu quero testes que validem o pipeline completo Lexer → Parser → AST → Compiler → Printer com round-trip, para que eu possa garantir que definições de sensores são compiladas e serializadas corretamente.

#### Critérios de Aceitação

1. THE Suite_de_Testes SHALL validar a Property 18 (round-trip): parse(print(parse(source))) produz Sensor equivalente ao parse(source) original
2. THE Suite_de_Testes SHALL validar o Lexer: tokenização correta de keywords (sensor, extends), strings, números, identificadores e símbolos
3. THE Suite_de_Testes SHALL validar o Parser: construção correta de SensorNode com campos obrigatórios (protocol, interval) e opcionais
4. THE Suite_de_Testes SHALL validar herança de templates: sensor que extends template herda campos do template e sobrescreve com campos próprios
5. IF uma definição DSL contém erro de sintaxe, THEN THE Sensor_DSL SHALL lançar DSLSyntaxError com número de linha e campo afetado
6. IF um protocolo inválido é especificado, THEN THE Sensor_DSL SHALL lançar DSLSyntaxError listando protocolos válidos
7. THE Suite_de_Testes SHALL validar remoção de comentários de linha (#) e bloco (/* */) pelo Lexer

### Requisito 10: Testes da API FastAPI

**User Story:** Como desenvolvedor, eu quero testes que validem todos os endpoints v2 e v3 da API, autenticação e WebSocket, para que eu possa garantir respostas corretas e performance adequada.

#### Critérios de Aceitação

1. THE Suite_de_Testes SHALL testar os endpoints v3: `/observability/health-score`, `/alerts/intelligent`, `/topology/graph`, `/topology/impact/{node_id}`
2. THE Suite_de_Testes SHALL testar os endpoints v2: `/dashboard/summary`, `/servers`, `/sensors`, `/metrics`, `/incidents`
3. THE Suite_de_Testes SHALL validar autenticação: requisições sem token válido retornam HTTP 401
4. THE Suite_de_Testes SHALL validar o WebSocket `/ws/observability`: conexão, recebimento de payload com health_score, e desconexão limpa
5. WHEN a API recebe requisição com parâmetros inválidos, THE API_FastAPI SHALL retornar HTTP 422 com detalhes de validação
6. THE Suite_de_Testes SHALL validar que a latência média dos endpoints é <200ms sob carga normal

### Requisito 11: Testes do Frontend React

**User Story:** Como desenvolvedor, eu quero testes que validem os dashboards v3, modo NOC e atualização real-time, para que eu possa garantir renderização correta e performance da interface.

#### Critérios de Aceitação

1. THE Suite_de_Testes SHALL testar renderização dos componentes v3: ObservabilityDashboard, TopologyView, IntelligentAlerts, AIOpsV3
2. THE Suite_de_Testes SHALL testar o modo NOC: layout fullscreen, atualização automática e visibilidade de alertas críticos
3. THE Suite_de_Testes SHALL validar reconexão automática do WebSocket após desconexão
4. THE Suite_de_Testes SHALL validar que o tempo de renderização inicial dos dashboards é <3 segundos

### Requisito 12: Testes de Integração Cross-Module

**User Story:** Como desenvolvedor, eu quero testes de integração que validem fluxos completos entre módulos, para que eu possa garantir que o sistema funciona end-to-end.

#### Critérios de Aceitação

1. THE Suite_de_Testes SHALL validar o fluxo completo: Métrica → EventProcessor → AI Pipeline → AlertEngine → Notificação
2. THE Suite_de_Testes SHALL validar o cenário HOST DOWN: ping falha → WMI/TCP suspensos via DependencyEngine → evento único gerado → alerta criado
3. THE Suite_de_Testes SHALL validar o cenário CASCADE FAILURE: switch falha → servidores dependentes detectados via TopologyEngine → blast radius calculado → alerta consolidado
4. THE Suite_de_Testes SHALL validar o cenário AI DECISION: anomalia detectada → correlação → causa raiz → decisão → auto-remediação executada com confiança ≥85%
5. THE Suite_de_Testes SHALL validar que o EventProcessor alimenta o AI Pipeline que alimenta o AlertEngine sem perda de dados

### Requisito 13: Testes de Carga e Performance

**User Story:** Como desenvolvedor, eu quero testes de carga que simulem 1000 hosts com 50 sensores cada, para que eu possa garantir que o sistema escala sem degradação.

#### Critérios de Aceitação

1. THE Load_Generator SHALL simular 1000 hosts simultâneos com 50 sensores cada (50.000 métricas por ciclo)
2. WHEN 1000 hosts estão sendo monitorados, THE Suite_de_Testes SHALL validar que o throughput de ingestão de métricas é ≥1000 métricas/segundo
3. THE Suite_de_Testes SHALL validar que a latência média da API permanece <200ms sob carga de 1000 hosts
4. THE Suite_de_Testes SHALL validar que o Event Processor processa ≥500 eventos/segundo sem acúmulo no buffer
5. THE Suite_de_Testes SHALL validar que o frontend renderiza atualizações em <5 segundos sob carga

### Requisito 14: Testes de Chaos Engineering

**User Story:** Como desenvolvedor, eu quero testes de chaos engineering que simulem falhas de infraestrutura, para que eu possa garantir resiliência do sistema em cenários adversos.

#### Critérios de Aceitação

1. THE Chaos_Engine SHALL simular Redis offline e validar que o buffer local (deque 10k) armazena métricas sem perda
2. THE Chaos_Engine SHALL simular API offline e validar que a sonda continua coletando e armazenando métricas localmente
3. THE Chaos_Engine SHALL simular latência de rede (100ms-500ms) e validar que timeouts são respeitados sem travamento
4. THE Chaos_Engine SHALL simular perda de pacotes (10%-50%) e validar que retries recuperam dados perdidos
5. WHEN o Redis reconecta após falha, THE Suite_de_Testes SHALL validar que métricas do buffer são reenviadas sem duplicação
6. THE Suite_de_Testes SHALL validar o cenário EVENT FLOOD: 1000 eventos/minuto processados sem colapso do sistema

### Requisito 15: Testes de Resiliência

**User Story:** Como desenvolvedor, eu quero testes de resiliência que validem auto-reconexão, retry e fallback, para que eu possa garantir recuperação automática após falhas.

#### Critérios de Aceitação

1. THE Suite_de_Testes SHALL validar auto-reconexão do WebSocket após desconexão com backoff exponencial
2. THE Suite_de_Testes SHALL validar retry 3x com backoff exponencial no AlertNotifier para canais de notificação
3. THE Suite_de_Testes SHALL validar fallback do DuplicateSuppressor: quando Redis está indisponível, cache em memória assume sem perda de funcionalidade
4. THE Suite_de_Testes SHALL validar que o Circuit Breaker do AI Pipeline abre após >50% de falhas e fecha após 5 minutos
5. THE Suite_de_Testes SHALL validar que falha em um coletor do Probe não afeta coleta de outros coletores (isolamento de falhas)

### Requisito 16: Testes de Segurança

**User Story:** Como desenvolvedor, eu quero testes de segurança que validem autenticação, proteção contra vazamento de dados e criptografia de credenciais, para que eu possa garantir a segurança do sistema.

#### Critérios de Aceitação

1. THE Suite_de_Testes SHALL validar que endpoints protegidos retornam HTTP 401 sem token de autenticação válido
2. THE Suite_de_Testes SHALL validar que respostas da API não expõem credenciais, tokens ou dados sensíveis em mensagens de erro
3. THE Suite_de_Testes SHALL validar que credenciais da sonda são armazenadas com criptografia Fernet
4. THE Suite_de_Testes SHALL validar que o WAF (Web Application Firewall) bloqueia payloads de SQL injection e XSS
5. THE Suite_de_Testes SHALL validar que tokens de autenticação expiram após o tempo configurado

### Requisito 17: Testes de Database (TimescaleDB)

**User Story:** Como desenvolvedor, eu quero testes que validem a hypertable, retenção, compressão e queries pesadas do TimescaleDB, para que eu possa garantir performance e integridade dos dados de séries temporais.

#### Critérios de Aceitação

1. THE Suite_de_Testes SHALL validar que a hypertable metrics_ts aceita batch insert de ≤500 métricas por operação
2. THE Suite_de_Testes SHALL validar que a política de retenção remove dados com mais de 90 dias
3. THE Suite_de_Testes SHALL validar que a compressão automática é aplicada a chunks com mais de 7 dias
4. THE Suite_de_Testes SHALL validar que queries de agregação (média, máximo, mínimo por intervalo) retornam resultados corretos em <1 segundo para 1 milhão de registros
5. THE Suite_de_Testes SHALL validar que índices (idx_metrics_sensor_timestamp) são utilizados nas queries LATERAL do health-score e impact-map

### Requisito 18: Relatório Automatizado de Métricas

**User Story:** Como operador, eu quero um relatório automatizado com métricas de qualidade do sistema após cada execução da suite, para que eu possa monitorar a saúde do sistema continuamente.

#### Critérios de Aceitação

1. WHEN a suite de testes completa a execução, THE Suite_de_Testes SHALL gerar relatório com: Disponibilidade do Sistema (%), Perda de Eventos (%), Precisão de Alertas (%), Precisão da IA (%), MTTR, Throughput (métricas/seg), Latência Média da API, Tempo de Atualização da UI
2. THE Suite_de_Testes SHALL falhar automaticamente se qualquer métrica de perda de dados for >0%
3. THE Suite_de_Testes SHALL falhar automaticamente se a IA não resolver incidentes simulados
4. THE Suite_de_Testes SHALL falhar automaticamente se o atraso de alerta for >30 segundos
5. THE Suite_de_Testes SHALL falhar automaticamente se a UI congelar durante testes de carga

### Requisito 19: Cenários Críticos Obrigatórios

**User Story:** Como desenvolvedor, eu quero testes E2E que simulem os 7 cenários críticos obrigatórios, para que eu possa validar o comportamento do sistema em situações reais de produção.

#### Critérios de Aceitação

1. THE Suite_de_Testes SHALL validar o cenário HOST DOWN: ping falha → WMI/TCP suspensos → evento único gerado → alerta criado em <30s
2. THE Suite_de_Testes SHALL validar o cenário REDIS OFFLINE: buffer local ativado → coleta continua → métricas reenviadas após reconexão → perda de dados = 0%
3. THE Suite_de_Testes SHALL validar o cenário EVENT FLOOD: 1000 eventos/minuto → flood protection ativado → sistema não colapsa → 1 alerta consolidado gerado
4. THE Suite_de_Testes SHALL validar o cenário CASCADE FAILURE: switch falha → servidores detectados via topologia → serviços impactados calculados → alerta com blast radius
5. THE Suite_de_Testes SHALL validar o cenário HIGH LOAD: 1000 hosts simultâneos → throughput mantido → latência API <200ms → sem perda de métricas
6. THE Suite_de_Testes SHALL validar o cenário AI DECISION: anomalia detectada → pipeline completo executado → auto-remediação com confiança ≥85% → feedback registrado
7. THE Suite_de_Testes SHALL validar o cenário WEBSOCKET DROP: conexão perdida → reconexão automática → dados atualizados sem intervenção manual
