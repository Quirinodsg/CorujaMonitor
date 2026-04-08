# Plano de Implementação: Matriz de Notificação Inteligente

## Visão Geral

Implementação incremental do Dispatcher de notificações, começando pelo módulo core (`resolve_channels`), seguido pelas funções de envio, integração com `evaluate_all_thresholds`, API, frontend e testes property-based.

## Tarefas

- [x] 1. Criar módulo `worker/notification_dispatcher.py` com `resolve_channels` e constantes
  - [x] 1.1 Criar `worker/notification_dispatcher.py` com `VALID_CHANNELS`, `VALID_SENSOR_TYPES`, `DEFAULT_MATRIX` e função `resolve_channels(sensor_type, custom_matrix)`
    - Implementar regras: custom_matrix sobrescreve default, fallback `{"email"}` para tipos desconhecidos, filtrar canais inválidos, garantir resultado não-vazio
    - _Requisitos: 10.1, 10.2, 10.3, 10.4, 10.5, 8.1_

  - [ ]* 1.2 Escrever property test: Determinismo da resolução de canais
    - **Propriedade 1: Determinismo da resolução de canais**
    - **Valida: Requisitos 10.1, 10.2**
    - Arquivo: `tests/test_notification_matrix.py`

  - [ ]* 1.3 Escrever property test: Email sempre presente
    - **Propriedade 2: Email sempre presente**
    - **Valida: Requisitos 8.1**

  - [ ]* 1.4 Escrever property test: Resultado não-vazio
    - **Propriedade 3: Resultado não-vazio**
    - **Valida: Requisitos 10.3**

  - [ ]* 1.5 Escrever property test: Fallback seguro para tipos desconhecidos
    - **Propriedade 4: Fallback seguro para tipos desconhecidos**
    - **Valida: Requisitos 10.4**

  - [ ]* 1.6 Escrever property test: Custom matrix sobrescreve default com fallback
    - **Propriedade 5: Custom matrix sobrescreve default com fallback**
    - **Valida: Requisitos 11.6, 11.7**

  - [ ]* 1.7 Escrever property test: Somente canais válidos
    - **Propriedade 6: Somente canais válidos**
    - **Valida: Requisitos 10.1, 10.5**

- [x] 2. Checkpoint — Garantir que `resolve_channels` e property tests passam
  - Garantir que todos os testes passam, perguntar ao usuário se houver dúvidas.

- [x] 3. Criar funções de envio sync e `dispatch_notifications` Celery task
  - [x] 3.1 Criar `send_sms_notification_sync(config, incident_data)` em `worker/tasks.py`
    - Função síncrona baseada na versão async `send_twilio_notification` do router
    - Usa `twilio.rest.Client` para enviar SMS
    - Retorna `{'success': bool, 'error'?: str}`
    - _Requisitos: 7.1, 7.3_

  - [x] 3.2 Criar `send_whatsapp_notification_sync(config, incident_data)` em `worker/tasks.py`
    - Função síncrona baseada na versão async `send_twilio_whatsapp` do router
    - Usa `twilio.rest.Client` para enviar WhatsApp
    - Retorna `{'success': bool, 'error'?: str}`
    - _Requisitos: 7.2, 7.3_

  - [x] 3.3 Criar `send_ticket_sync(notification_config, incident_data)` em `worker/tasks.py`
    - Wrapper que detecta sistema de tickets habilitado (TOPdesk, Conecta, GLPI, Dynamics 365) e chama a função sync correspondente
    - Retorna `{'success': bool, 'error'?: str}`
    - _Requisitos: 2.1, 2.2, 2.4, 2.5_

  - [x] 3.4 Criar `dispatch_notifications(incident_id)` como Celery task em `worker/notification_dispatcher.py`
    - Carregar incident, sensor, server, tenant do banco
    - Forçar `priority=5` para `sensor_type='ping'`
    - Ignorar `network_in`/`network_out` (metric_only)
    - Chamar `resolve_channels(sensor_type, tenant.notification_matrix)`
    - Para cada canal: try/except isolado chamando a função de envio correspondente
    - `phone_call` → chamar `start_escalation()` com dados do tenant
    - Retornar `{sent: [...], failed: [...]}`
    - _Requisitos: 1.1, 1.4, 4.1, 5.1, 5.2, 6.1, 6.2, 9.1, 9.2, 9.3, 9.4_

  - [ ]* 3.5 Escrever property test: Isolamento de falhas entre canais
    - **Propriedade 7: Isolamento de falhas entre canais**
    - **Valida: Requisitos 9.1, 9.2, 7.3**

  - [ ]* 3.6 Escrever property test: Completude do resultado de dispatch
    - **Propriedade 8: Completude do resultado de dispatch**
    - **Valida: Requisitos 9.3**

  - [ ]* 3.7 Escrever property test: Prioridade forçada para PING
    - **Propriedade 9: Prioridade forçada para PING**
    - **Valida: Requisitos 5.1, 5.2**

- [x] 4. Checkpoint — Garantir que dispatch_notifications e property tests passam
  - Garantir que todos os testes passam, perguntar ao usuário se houver dúvidas.

- [x] 5. Integrar Dispatcher no fluxo de criação de incidentes
  - [x] 5.1 Modificar `evaluate_all_thresholds()` em `worker/tasks.py`
    - Após criar incidente, chamar `dispatch_notifications.delay(incident.id)` em vez de depender apenas do AIOps
    - Manter `execute_aiops_analysis.delay(incident.id)` em paralelo (AIOps enriquece, não bloqueia)
    - Para sensor_type='system' (reboot): chamar dispatch_notifications para enviar email informativo
    - _Requisitos: 1.1, 1.2, 1.3, 1.4, 3.1, 3.2_

- [x] 6. Adicionar campo `notification_matrix` ao modelo Tenant e migração
  - [x] 6.1 Adicionar coluna `notification_matrix = Column(JSON)` ao modelo `Tenant` em `models.py`
    - _Requisitos: 11.4, 11.6_

  - [x] 6.2 Criar script de migração SQL: `ALTER TABLE tenants ADD COLUMN notification_matrix JSON`
    - _Requisitos: 11.4_

- [x] 7. Criar endpoints API para Matriz de Notificação
  - [x] 7.1 Adicionar modelos Pydantic `NotificationMatrixUpdate` e `NotificationMatrixResponse` em `api/routers/notifications.py`
    - _Requisitos: 11.5_

  - [x] 7.2 Implementar `GET /api/v1/notifications/matrix` — retorna matriz do tenant (ou default se ausente)
    - _Requisitos: 11.5, 11.7_

  - [x] 7.3 Implementar `PUT /api/v1/notifications/matrix` — salva matriz no `tenant.notification_matrix`
    - Validar que canais são válidos (interseção com VALID_CHANNELS)
    - _Requisitos: 11.4, 11.5_

  - [ ]* 7.4 Escrever property test: Round-trip da API de matriz
    - **Propriedade 10: Round-trip da API de matriz**
    - **Valida: Requisitos 11.4, 11.5**

- [x] 8. Checkpoint — Garantir que API endpoints e testes passam
  - Garantir que todos os testes passam, perguntar ao usuário se houver dúvidas.

- [x] 9. Criar componente frontend NotificationMatrix
  - [x] 9.1 Criar `frontend/src/components/NotificationMatrix.js`
    - Tabela com linhas = sensor_types, colunas = canais (Email, Teams, Chamado, SMS, WhatsApp, Ligação)
    - Checkboxes editáveis por célula
    - Carregar dados via GET `/notifications/matrix` no mount
    - Botão "Salvar" chama PUT `/notifications/matrix`
    - Botão "Adicionar Categoria" para sensor_types customizados
    - _Requisitos: 11.1, 11.2, 11.3, 11.4, 11.8_

  - [x] 9.2 Criar `frontend/src/components/NotificationMatrix.css`
    - Estilos para tabela, checkboxes e botões
    - _Requisitos: 11.1_

  - [x] 9.3 Integrar `NotificationMatrix` em `frontend/src/components/Settings.js`
    - Adicionar como seção dentro da aba de Notificações, acessível apenas para administradores
    - _Requisitos: 11.9_

- [x] 10. Checkpoint final — Garantir que todos os testes passam
  - Garantir que todos os testes passam, perguntar ao usuário se houver dúvidas.

## Notas

- Tarefas marcadas com `*` são opcionais e podem ser puladas para MVP mais rápido
- Cada tarefa referencia requisitos específicos para rastreabilidade
- Checkpoints garantem validação incremental
- Property tests validam propriedades universais de corretude
- Testes unitários validam exemplos específicos e edge cases
