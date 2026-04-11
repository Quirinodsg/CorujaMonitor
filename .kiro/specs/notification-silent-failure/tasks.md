# Implementation Plan

- [x] 1. Write bug condition exploration test
  - **Property 1: Bug Condition** - Silent Notification Failure (Standalone Sensor + Auto-Resolve)
  - **CRITICAL**: Este teste DEVE FALHAR no código não corrigido — a falha confirma que o bug existe
  - **DO NOT attempt to fix the test or the code when it fails**
  - **NOTE**: Este teste codifica o comportamento esperado — ele validará o fix quando passar após a implementação
  - **GOAL**: Surfaçar counterexamples que demonstram os bugs existentes
  - **Scoped PBT Approach**: Escopo determinístico — sensor com `server_id=None` e `probe_id` válido; incidente auto-resolvido sem dispatch
  - Criar arquivo `tests/test_notification_silent_failure.py` com testes Hypothesis
  - **Bug 1 — Sensor standalone**: Para qualquer sensor com `server_id=None` e `probe_id` não-None, `dispatch_notifications` no código sem fallback retornaria `failed=[{'channel': 'all', 'error': 'Tenant não encontrado'}]` sem nenhum `logger.warning` (falha silenciosa)
  - **Bug 2 — Auto-resolve sem dispatch**: Para qualquer incidente com `resolution_notes='Auto-resolvido: sensor voltou ao normal'`, o código sem `dispatch_resolution_task.delay()` não chamaria o dispatcher de resolução
  - **Bug 3 — `_send_reboot_email` com tenant hardcoded**: A função existe em `tasks.py` com `Tenant.id == 1` hardcoded — deve ser removida
  - Rodar no código ANTES do fix (ou simular via mock do caminho sem fallback)
  - **EXPECTED OUTCOME**: Teste FALHA (isso é correto — prova que o bug existe)
  - Documentar counterexamples encontrados para rastreabilidade
  - Marcar tarefa completa quando o teste estiver escrito, executado e a falha documentada
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [x] 2. Write preservation property tests (BEFORE implementing fix)
  - **Property 2: Preservation** - Comportamento Inalterado para Sensores com server_id Válido
  - **IMPORTANT**: Seguir metodologia observation-first
  - Observar: `resolve_channels('ping')` retorna `{'email', 'ticket', 'teams'}` no código atual
  - Observar: `resolve_channels('network_in')` retorna `set()` → após filtro VALID_CHANNELS → fallback `{'email'}` — mas `dispatch_notifications` retorna `{'sent': [], 'failed': []}` antes de chegar em `resolve_channels` (metric_only)
  - Observar: sensor com `server_id=5` resolve tenant via `server.tenant_id` sem tocar no caminho de fallback probe
  - Escrever property-based tests com Hypothesis:
    - Para qualquer `sensor_type` válido (exceto `network_in`/`network_out`), `resolve_channels` retorna subconjunto de `VALID_CHANNELS` e nunca retorna conjunto vazio
    - Para qualquer sensor com `server_id` não-None, `dispatch_notifications` não usa o caminho `elif sensor.probe_id`
    - Para `network_in`/`network_out`, `dispatch_notifications` retorna `{'sent': [], 'failed': []}` sem chamar nenhum canal
  - Verificar que os testes PASSAM no código atual (unfixed não afeta esses caminhos)
  - **EXPECTED OUTCOME**: Testes PASSAM (confirma baseline a preservar)
  - Marcar tarefa completa quando os testes estiverem escritos, executados e passando
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 3. Fix para notification silent failure

  - [x] 3.1 Remover `_send_reboot_email` de `worker/tasks.py`
    - Confirmar que não há nenhuma chamada à função: `grep -n "_send_reboot_email" worker/tasks.py` deve retornar apenas a definição (linha ~399)
    - Remover integralmente a função `_send_reboot_email` (linhas ~399–470 de `worker/tasks.py`)
    - A função é código morto: nunca chamada, contém `Tenant.id == 1` hardcoded, substituída por `dispatch_notifications_task`
    - _Bug_Condition: isBugCondition(X) onde X.sensor.sensor_type = 'system' AND X.tenant_id_used = 1 AND X.server.tenant_id != 1_
    - _Expected_Behavior: `_send_reboot_email` não existe mais em tasks.py; reboot usa `dispatch_notifications_task` que resolve tenant corretamente_
    - _Preservation: Fluxo de reboot (sensor_type='system') continua criando incidente informativo e chamando `dispatch_notifications_task.delay(incident.id)` — inalterado_
    - _Requirements: 2.4, 3.7_

  - [x] 3.2 Verificar que o teste de bug condition agora passa
    - **Property 1: Expected Behavior** - Silent Notification Failure (Standalone Sensor + Auto-Resolve)
    - **IMPORTANT**: Re-executar o MESMO teste da tarefa 1 — NÃO escrever novo teste
    - O teste da tarefa 1 codifica o comportamento esperado
    - Quando este teste passar, confirma que o comportamento esperado está satisfeito
    - Executar `pytest tests/test_notification_silent_failure.py -k "bug_condition" --tb=short`
    - **EXPECTED OUTCOME**: Teste PASSA (confirma que os fixes dos commits b64cf4a e 57892fd estão corretos e `_send_reboot_email` foi removida)
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

  - [x] 3.3 Verificar que os testes de preservação ainda passam
    - **Property 2: Preservation** - Comportamento Inalterado para Sensores com server_id Válido
    - **IMPORTANT**: Re-executar os MESMOS testes da tarefa 2 — NÃO escrever novos testes
    - Executar `pytest tests/test_notification_silent_failure.py -k "preservation" --tb=short`
    - **EXPECTED OUTCOME**: Testes PASSAM (confirma que nenhuma regressão foi introduzida)
    - Confirmar que todos os testes passam após a remoção de `_send_reboot_email`

- [x] 4. Checkpoint — Garantir que todos os testes passam
  - Executar suite completa: `pytest tests/test_notification_silent_failure.py -v`
  - Confirmar que Property 1 (Bug Condition) e Property 2 (Preservation) passam
  - Confirmar que `_send_reboot_email` não existe mais em `worker/tasks.py`
  - Confirmar que `dispatch_notifications` e `dispatch_resolution` têm o fallback `probe_id → Probe.tenant_id` (commits b64cf4a/57892fd)
  - Confirmar que `dispatch_resolution_task.delay(incident.id)` é chamado no bloco de auto-resolve de `evaluate_all_thresholds` (commit 57892fd)
  - Perguntar ao usuário se houver dúvidas antes de fazer push
