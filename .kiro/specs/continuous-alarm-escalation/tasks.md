# Plano de Implementação: Escalação Contínua de Alarmes

## Visão Geral

Implementação incremental do sistema de escalação contínua, começando pelo módulo backend de estado e serialização, seguido pela Celery task de ciclo, endpoints da API, integração com fluxo existente, frontend e testes de propriedade.

## Tarefas

- [x] 1. Criar módulo de escalação e modelo de estado (`worker/escalation.py`)
  - [x] 1.1 Implementar funções `serialize_state` e `deserialize_state` para o estado de escalação no Redis
    - Definir a estrutura `EscalationState` como dicionário com todos os campos obrigatórios (sensor_id, incident_id, tenant_id, attempt_count, max_attempts, interval_minutes, call_duration_seconds, mode, current_number_index, phone_numbers, status, started_at, next_attempt_at, last_attempt_at, acknowledged_by, acknowledged_at, call_history, device_type, problem_description)
    - Implementar serialização para JSON string e deserialização de volta para dict
    - _Requisitos: 9.1, 9.2, 9.5_

  - [ ]* 1.2 Escrever teste de propriedade para round-trip de serialização
    - **Propriedade 15: Round-trip de serialização do estado de escalação**
    - **Valida: Requisitos 9.2, 9.5**

  - [x] 1.3 Implementar validação de parâmetros de escalação
    - Criar função `validate_escalation_config(config)` que valida: `interval_minutes` ∈ [1, 60], `max_attempts` ∈ [1, 100], `call_duration_seconds` ∈ [10, 120]
    - Retornar erros descritivos indicando campo e limites válidos
    - _Requisitos: 4.1, 4.2, 4.3, 4.5, 4.6_

  - [ ]* 1.4 Escrever teste de propriedade para validação de parâmetros
    - **Propriedade 9: Validação de parâmetros dentro dos limites**
    - **Valida: Requisitos 4.1, 4.2, 4.3, 4.5, 4.6**

  - [x] 1.5 Implementar validação de formato E.164 para números de telefone
    - Criar função `validate_phone_number(number)` que aceita strings no formato E.164 (`+` seguido de 1 a 15 dígitos)
    - _Requisitos: 5.3_

  - [ ]* 1.6 Escrever teste de propriedade para validação E.164
    - **Propriedade 10: Validação de formato E.164 para números de telefone**
    - **Valida: Requisitos 5.3**

- [x] 2. Implementar lógica central de escalação (`worker/escalation.py`)
  - [x] 2.1 Implementar `start_escalation(sensor_id, incident_id, tenant_id, alert_data)`
    - Verificar se já existe escalação ativa para o sensor_id no Redis (prevenção de duplicata)
    - Verificar se o sensor já está reconhecido (`is_acknowledged`)
    - Verificar se a cadeia de escalação não está vazia
    - Criar estado inicial no Redis com chave `escalation:{sensor_id}` e TTL calculado
    - Agendar primeira task `escalation_cycle` via `apply_async`
    - Registrar entrada de início no histórico do incidente (`ai_analysis`)
    - _Requisitos: 1.1, 1.6, 5.5, 8.3, 8.4_

  - [ ]* 2.2 Escrever teste de propriedade para início de escalação
    - **Propriedade 1: Início de escalação cria estado válido**
    - **Valida: Requisitos 1.1**

  - [ ]* 2.3 Escrever teste de propriedade para prevenção de duplicata
    - **Propriedade 5: Prevenção de escalação duplicada (idempotência)**
    - **Valida: Requisitos 1.6**

  - [ ]* 2.4 Escrever teste de propriedade para sensor reconhecido
    - **Propriedade 13: Sensores já reconhecidos não iniciam escalação**
    - **Valida: Requisitos 8.3**

  - [x] 2.5 Implementar `acknowledge_escalation(sensor_id, user_id, notes)`
    - Marcar estado como `status = "acknowledged"` no Redis
    - Registrar `acknowledged_by`, `acknowledged_at` e notas
    - Remover estado de escalação ativa do Redis
    - Atualizar status do incidente para "acknowledged"
    - Registrar encerramento no histórico do incidente
    - _Requisitos: 2.1, 2.2, 2.3, 2.4, 8.5_

  - [ ]* 2.6 Escrever teste de propriedade para reconhecimento
    - **Propriedade 6: Reconhecimento para escalação e registra dados**
    - **Valida: Requisitos 2.1, 2.2, 2.3**

  - [x] 2.7 Implementar `stop_escalation(sensor_id, reason)` e `get_active_escalations(tenant_id)`
    - `stop_escalation`: para escalação por qualquer motivo (reconhecimento, resolução, expiração), limpa Redis, registra histórico
    - `get_active_escalations`: retorna lista de escalações ativas do tenant a partir do Redis
    - _Requisitos: 8.1, 8.2, 8.5, 9.3_

- [x] 3. Implementar Celery task de ciclo de escalação (`worker/tasks.py`)
  - [x] 3.1 Implementar task `escalation_cycle(sensor_id)` com self-scheduling
    - Adquirir lock distribuído no Redis (`escalation_lock:{sensor_id}`)
    - Ler estado de escalação do Redis
    - Verificar se foi reconhecido ou expirado → parar se sim
    - Executar chamadas conforme modo (simultâneo ou sequencial)
    - Modo simultâneo: disparar chamada para todos os números via Twilio
    - Modo sequencial: disparar chamada para número no `current_number_index`, incrementar índice com wrap-around
    - Registrar cada chamada no `call_history`
    - Incrementar `attempt_count`
    - Se `attempt_count >= max_attempts`: marcar como "expired", registrar no histórico
    - Senão: agendar próximo ciclo via `self.apply_async(eta=próximo_intervalo)`
    - Tratar rate-limit do Twilio (429): aguardar 60s
    - Tratar Redis indisponível: fallback para ligação única
    - `bind=True, max_retries=3, default_retry_delay=30`
    - _Requisitos: 1.2, 1.3, 1.4, 1.5, 3.1, 3.2, 3.3, 3.5, 7.1, 7.2, 7.4, 7.5_

  - [ ]* 3.2 Escrever teste de propriedade para continuação de escalação
    - **Propriedade 2: Escalação continua enquanto não reconhecida e abaixo do máximo**
    - **Valida: Requisitos 1.2**

  - [ ]* 3.3 Escrever teste de propriedade para parada ao atingir máximo
    - **Propriedade 3: Escalação para ao atingir máximo de tentativas**
    - **Valida: Requisitos 1.3**

  - [ ]* 3.4 Escrever teste de propriedade para crescimento do histórico
    - **Propriedade 4: Histórico de chamadas cresce a cada ciclo**
    - **Valida: Requisitos 1.4**

  - [ ]* 3.5 Escrever teste de propriedade para modo simultâneo
    - **Propriedade 7: Modo simultâneo liga para todos os números**
    - **Valida: Requisitos 3.1**

  - [ ]* 3.6 Escrever teste de propriedade para modo sequencial com wrap-around
    - **Propriedade 8: Modo sequencial liga para um número e faz wrap-around**
    - **Valida: Requisitos 3.2, 3.3**

  - [x] 3.7 Implementar task de recuperação de escalações ativas no startup do worker
    - Ao iniciar, buscar todas as chaves `escalation:*` no Redis com `status == "active"`
    - Para cada escalação ativa sem task agendada, reagendar `escalation_cycle`
    - _Requisitos: 7.3_

- [x] 4. Checkpoint — Verificar módulo de escalação e tasks
  - Garantir que todos os testes passam, perguntar ao usuário se houver dúvidas.

- [x] 5. Criar endpoints da API de escalação (`api/routers/escalation.py`)
  - [x] 5.1 Criar router FastAPI e implementar `GET /api/v1/escalation/active`
    - Retornar lista de escalações ativas do tenant com campos: sensor_name, device_type, problem_description, started_at, attempt_count, next_attempt_at, status
    - Tratar Redis indisponível com status 503
    - _Requisitos: 9.3, 6.2_

  - [ ]* 5.2 Escrever teste de propriedade para campos obrigatórios na resposta
    - **Propriedade 11: Resposta da API de escalações ativas contém todos os campos obrigatórios**
    - **Valida: Requisitos 6.2**

  - [x] 5.3 Implementar `POST /api/v1/escalation/{sensor_id}/acknowledge`
    - Chamar `acknowledge_escalation` do módulo de escalação
    - Retornar 404 se não houver escalação ativa, 409 se já reconhecida/expirada
    - _Requisitos: 9.4, 2.1, 2.2_

  - [x] 5.4 Implementar `GET /api/v1/escalation/config` e `PUT /api/v1/escalation/config`
    - GET: retornar configuração de escalação do `notification_config` do tenant
    - PUT: validar parâmetros (limites), validar números E.164, salvar no `notification_config.escalation`
    - Retornar 400 para parâmetros fora dos limites
    - _Requisitos: 4.4, 4.5, 4.6, 5.4_

  - [x] 5.5 Implementar `GET /api/v1/escalation/resources` e `PUT /api/v1/escalation/resources`
    - GET: retornar lista de recursos monitorados para escalação do tenant
    - PUT: validar que cada recurso existe e está ativo no banco, salvar em `notification_config.escalation.escalation_resources`
    - Retornar 400 para recursos inexistentes ou inativos
    - _Requisitos: 10.1, 10.2, 10.3, 10.4, 10.7, 10.8_

  - [ ]* 5.6 Escrever teste de propriedade para validação de recursos
    - **Propriedade 17: Validação de recursos na atualização da lista**
    - **Valida: Requisitos 10.8**

  - [x] 5.7 Implementar `GET /api/v1/escalation/history`
    - Retornar histórico recente de escalações encerradas (reconhecidas, expiradas, resolvidas)
    - _Requisitos: 6.3_

  - [x] 5.8 Registrar router de escalação no `api/main.py`
    - Adicionar `include_router` para o novo router de escalação
    - _Requisitos: (infraestrutura)_

- [x] 6. Integração com fluxo existente
  - [x] 6.1 Modificar `_trigger_datacenter_emergency` em `api/routers/metrics.py`
    - Substituir ligação direta por chamada a `start_escalation`
    - Verificar se recurso está na lista de escalação ou é sensor padrão de datacenter antes de iniciar escalação
    - Manter fallback para ligação única se Redis indisponível
    - _Requisitos: 1.1, 10.5, 10.6, 10.10, 7.2_

  - [ ]* 6.2 Escrever teste de propriedade para trigger baseado na lista de recursos
    - **Propriedade 16: Trigger de escalação baseado na lista de recursos**
    - **Valida: Requisitos 10.5, 10.6, 10.10**

  - [x] 6.3 Modificar `acknowledge_incident` em `api/routers/incidents.py`
    - Ao reconhecer incidente via endpoint existente, chamar `stop_escalation` para o sensor associado
    - _Requisitos: 8.2_

  - [x] 6.4 Modificar auto-resolução em `worker/tasks.py`
    - Ao auto-resolver incidente (sensor voltou ao normal), chamar `stop_escalation`
    - _Requisitos: 8.1_

  - [ ]* 6.5 Escrever teste de propriedade para mudança de estado do incidente
    - **Propriedade 12: Mudança de estado do incidente para escalação**
    - **Valida: Requisitos 8.1, 8.2**

  - [ ]* 6.6 Escrever teste de propriedade para eventos de ciclo de vida
    - **Propriedade 14: Eventos do ciclo de vida criam entradas no histórico**
    - **Valida: Requisitos 8.4, 8.5**

  - [x] 6.7 Implementar limpeza automática de recursos removidos
    - Quando sensor/servidor for removido do sistema, remover da lista `escalation_resources` e parar escalação ativa se houver
    - _Requisitos: 10.9_

- [x] 7. Checkpoint — Verificar backend completo
  - Garantir que todos os testes passam, perguntar ao usuário se houver dúvidas.

- [x] 8. Implementar frontend — Componente de Escalação (`frontend/src/components/EscalationConfig.js`)
  - [x] 8.1 Criar componente base `EscalationConfig` com seção de configuração de parâmetros
    - Campos: modo de chamada (toggle simultâneo/sequencial), intervalo entre ciclos, máximo de retentativas, duração da chamada
    - Validação client-side dos limites antes de submeter
    - Chamadas a `GET /api/v1/escalation/config` e `PUT /api/v1/escalation/config`
    - Exibir mensagens de erro para valores fora dos limites
    - _Requisitos: 3.4, 4.1, 4.2, 4.3, 4.5, 4.6_

  - [x] 8.2 Implementar seção de Cadeia de Escalação
    - Lista de números com nome do contato e número de telefone
    - Adicionar, remover e reordenar números (drag-and-drop)
    - Validação de formato E.164 ao adicionar
    - Sincronização com `to_numbers` da configuração Twilio
    - _Requisitos: 5.1, 5.2, 5.3, 5.4_

  - [x] 8.3 Implementar seção de Recursos Monitorados para Escalação
    - Lista de recursos configurados com nome, tipo, status e data de inclusão
    - Seletor com busca por nome ou tipo para adicionar recursos
    - Botão para remover recursos individuais
    - Chamadas a `GET /api/v1/escalation/resources` e `PUT /api/v1/escalation/resources`
    - _Requisitos: 10.1, 10.2, 10.3, 10.4_

  - [x] 8.4 Implementar seção de Alarmes Ativos com polling
    - Lista de alarmes ativos com: nome do sensor, tipo de dispositivo, descrição, horário de início, tentativas, próxima tentativa, status
    - Botão de reconhecimento ao lado de cada alarme (chama `POST /api/v1/escalation/{sensor_id}/acknowledge`)
    - Polling a cada 10 segundos via `GET /api/v1/escalation/active`
    - _Requisitos: 6.1, 6.2, 6.4, 6.5, 2.5_

  - [x] 8.5 Implementar seção de Histórico Recente
    - Alarmes reconhecidos, expirados ou resolvidos movidos para esta seção
    - Chamada a `GET /api/v1/escalation/history`
    - _Requisitos: 6.3_

  - [x] 8.6 Adicionar rota e link no Sidebar/MainLayout
    - Adicionar link para página de escalação no `Sidebar.js`
    - Adicionar rota para `EscalationConfig` no `MainLayout.js`
    - _Requisitos: (infraestrutura)_

- [x] 9. Checkpoint final — Verificar integração completa
  - Garantir que todos os testes passam, perguntar ao usuário se houver dúvidas.

## Notas

- Tarefas marcadas com `*` são opcionais e podem ser puladas para um MVP mais rápido
- Cada tarefa referencia requisitos específicos para rastreabilidade
- Checkpoints garantem validação incremental
- Testes de propriedade validam propriedades universais de corretude com Hypothesis
- Testes unitários validam exemplos específicos e edge cases
