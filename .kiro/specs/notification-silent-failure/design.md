# Notification Silent Failure — Bugfix Design

## Overview

O sistema Coruja Monitor falhava silenciosamente ao enviar notificações em três cenários distintos:

1. **Bug 1 — Tenant lookup via server_id**: Sensores HTTP standalone (sem `server_id`) resultavam em `tenant = None` e o dispatch era descartado sem log de erro visível.
2. **Bug 2 — Auto-resolve sem notificação**: Incidentes auto-resolvidos faziam apenas `db.commit()` sem chamar `dispatch_resolution_task`, resultando em nenhum email/Teams de "problema resolvido".
3. **Bug 3 — `_send_reboot_email` com tenant hardcoded**: A função buscava sempre `Tenant.id == 1`, quebrando em ambientes multi-tenant.

A estratégia de fix é: (1) adicionar fallback `probe_id → Probe.tenant_id` no dispatcher, (2) chamar `dispatch_resolution_task.delay()` no auto-resolve, (3) remover `_send_reboot_email` (código morto com tenant hardcoded — o reboot já usa `dispatch_notifications_task` corretamente).

Os commits b64cf4a e 57892fd já implementaram os fixes 1 e 2. Esta fase formaliza o design, define as propriedades de correção e planeja os testes de propriedade (Hypothesis).

---

## Glossary

- **Bug_Condition (C)**: Conjunto de entradas que disparam qualquer um dos três bugs — sensor sem `server_id`/`probe_id`, auto-resolve sem dispatch, ou reboot com tenant hardcoded.
- **Property (P)**: Comportamento correto esperado para entradas em C — tenant resolvido via probe, resolução notificada, tenant correto usado.
- **Preservation**: Comportamento existente para entradas fora de C que não deve ser alterado pelo fix.
- **`dispatch_notifications`**: Função em `worker/notification_dispatcher.py` que carrega incident/sensor/tenant e despacha notificações por canal.
- **`dispatch_resolution`**: Função em `worker/notification_dispatcher.py` que envia notificação de resolução (email + teams) quando um incidente é resolvido.
- **`evaluate_all_thresholds`**: Task Celery em `worker/tasks.py` que avalia métricas, cria/resolve incidentes e chama os dispatchers.
- **`_send_reboot_email`**: Função morta em `worker/tasks.py` — definida mas nunca chamada. Contém `tenant_id == 1` hardcoded. Deve ser removida.
- **`DEFAULT_MATRIX`**: Dicionário em `notification_dispatcher.py` que mapeia `sensor_type → [canais]`. Alinhado com a UI de configuração.
- **`sensor_type='system'`**: Tipo de sensor que detecta reboot. Gera incidente já resolvido (informativo) e notifica via `dispatch_notifications_task`.
- **`METRIC_ONLY_TYPES`**: `{'network_in', 'network_out'}` — sensores que coletam métricas mas nunca geram notificações.

---

## Bug Details

### Bug Condition

Os bugs se manifestam em três caminhos distintos dentro do fluxo de notificação:

- **Bug 1**: `dispatch_notifications` e `dispatch_resolution` buscavam tenant exclusivamente via `server.tenant_id`. Quando `sensor.server_id` é `None` (sensores HTTP standalone), `server` é `None` e `tenant_id` ficava `None`, abortando o dispatch silenciosamente.
- **Bug 2**: O bloco de auto-resolve em `evaluate_all_thresholds` fazia `db.commit()` e `logger.info()` mas não chamava `dispatch_resolution_task.delay(incident.id)`.
- **Bug 3**: `_send_reboot_email` usava `db.query(Tenant).filter(Tenant.id == 1)` hardcoded em vez de derivar o tenant do servidor.

**Formal Specification:**
```
FUNCTION isBugCondition(X)
  INPUT: X of type DispatchInput {
    sensor: Sensor,
    incident: Incident,
    server: Server | None,
    dispatch_resolution_called: bool,
    tenant_id_used: int | None
  }
  OUTPUT: boolean

  // Bug 1: sensor standalone sem server_id e sem probe_id
  IF X.sensor.server_id IS NULL AND X.sensor.probe_id IS NULL THEN
    RETURN true
  END IF

  // Bug 2: auto-resolve sem dispatch de resolução
  IF X.incident.status = 'resolved'
     AND X.incident.resolution_notes CONTAINS 'Auto-resolvido: sensor voltou ao normal'
     AND X.dispatch_resolution_called = false THEN
    RETURN true
  END IF

  // Bug 3: reboot email com tenant hardcoded (código morto — a ser removido)
  IF X.sensor.sensor_type = 'system'
     AND X.tenant_id_used = 1
     AND X.server IS NOT NULL
     AND X.server.tenant_id != 1 THEN
    RETURN true
  END IF

  RETURN false
END FUNCTION
```

### Examples

- **Bug 1 — Sensor CRM (HTTP standalone)**: `sensor.server_id = None`, `sensor.probe_id = 42`. Antes do fix: `tenant = None`, dispatch abortado sem log. Após fix: `probe = Probe(id=42, tenant_id=7)`, `tenant_id = 7`, notificação enviada normalmente.
- **Bug 1 — Sensor sem probe também**: `sensor.server_id = None`, `sensor.probe_id = None`. Após fix: `logger.warning("Tenant não encontrado para incidente X (sensor_id=Y, server_id=None, probe_id=None)")` e retorno explícito de falha.
- **Bug 2 — Auto-resolve silencioso**: Sensor HTTP volta ao normal, incidente resolvido. Antes do fix: nenhum email/Teams enviado. Após fix: `dispatch_resolution_task.delay(incident.id)` chamado, email "✅ RESOLVIDO" enviado.
- **Bug 3 — Reboot multi-tenant**: Servidor pertence ao tenant 5. `_send_reboot_email` buscava `Tenant.id == 1`, obtinha tenant errado. Fix: remover a função — o reboot já usa `dispatch_notifications_task` que resolve o tenant corretamente.

---

## Expected Behavior

### Preservation Requirements

**Unchanged Behaviors:**
- Sensores com `server_id` válido continuam buscando tenant via `server.tenant_id` (caminho principal inalterado).
- Sensores `ping` continuam forçando `priority=5` e notificando via email, ticket e teams.
- Sensores `network_in`/`network_out` continuam sendo ignorados (metric_only).
- Deduplicação de incidentes (não cria duplicatas para o mesmo sensor) permanece intacta.
- Tenants com `notification_matrix` customizada continuam usando sua matriz em vez da DEFAULT_MATRIX.
- Falha em um canal não impede os demais (try/except por canal permanece).
- Sensores `system` continuam criando incidente já resolvido (informativo) com cooldown de 1h.

**Scope:**
Todas as entradas onde `isBugCondition(X) = false` devem produzir comportamento idêntico ao código original. Isso inclui:
- Qualquer sensor com `server_id` válido (caminho principal).
- Incidentes resolvidos manualmente (não auto-resolve).
- Qualquer sensor que não seja `system` no contexto de reboot.

---

## Hypothesized Root Cause

1. **Lookup de tenant incompleto**: O código original assumia que todo sensor tem `server_id`. Sensores HTTP standalone criados diretamente via probe não têm `server_id`, apenas `probe_id`. O fallback para `probe.tenant_id` estava ausente.

2. **Omissão no bloco de auto-resolve**: O desenvolvedor adicionou o log e o `db.commit()` mas esqueceu de chamar o dispatcher de resolução. O padrão de chamar `dispatch_notifications_task.delay()` após criar incidente existia, mas não foi replicado para o caminho de resolução.

3. **Função legada com tenant hardcoded**: `_send_reboot_email` foi escrita quando o sistema era single-tenant. Com a migração para multi-tenant, o `tenant_id == 1` nunca foi atualizado. A função ficou como código morto após o reboot ser migrado para usar `dispatch_notifications_task`, mas não foi removida.

4. **Ausência de testes de propriedade**: Sem testes que gerem sensores com `server_id=None` ou que verifiquem que `dispatch_resolution_task` é chamado no auto-resolve, os bugs passaram despercebidos.

---

## Correctness Properties

Property 1: Bug Condition — Tenant Lookup via Probe para Sensores Standalone

_For any_ sensor onde `server_id IS NULL` e `probe_id IS NOT NULL`, a função `dispatch_notifications` (e `dispatch_resolution`) corrigida SHALL resolver o tenant via `Probe.tenant_id` e prosseguir com o dispatch normalmente, sem abortar silenciosamente.

**Validates: Requirements 2.1**

Property 2: Bug Condition — Warning Explícito para Sensor sem Tenant

_For any_ sensor onde `server_id IS NULL` e `probe_id IS NULL`, a função corrigida SHALL registrar um `logger.warning` identificando `sensor_id`, `server_id` e `probe_id`, e retornar `{'failed': [{'channel': 'all', 'error': 'Tenant não encontrado'}]}` em vez de falhar silenciosamente.

**Validates: Requirements 2.2**

Property 3: Bug Condition — Dispatch de Resolução no Auto-Resolve

_For any_ incidente auto-resolvido (sensor voltou ao normal), a task `evaluate_all_thresholds` corrigida SHALL chamar `dispatch_resolution_task.delay(incident.id)` após o `db.commit()`, garantindo que email e teams de resolução sejam enviados.

**Validates: Requirements 2.3**

Property 4: Preservation — Sensores com server_id Válido

_For any_ sensor onde `server_id IS NOT NULL`, a função corrigida SHALL produzir exatamente o mesmo resultado que a função original — tenant resolvido via `server.tenant_id`, canais resolvidos pela matriz, notificações enviadas.

**Validates: Requirements 3.1, 3.2, 3.3**

Property 5: Preservation — Deduplicação e Metric-Only

_For any_ sensor do tipo `network_in` ou `network_out`, e _for any_ sensor com incidente já aberto, o comportamento SHALL permanecer idêntico ao original — sem notificações para metric-only, sem duplicatas de incidente.

**Validates: Requirements 3.3, 3.4**

---

## Fix Implementation

### Changes Required

**File**: `worker/tasks.py`

**Change 1 — Remover `_send_reboot_email` (código morto)**

A função `_send_reboot_email` (linhas ~399–470) nunca é chamada no código atual. O reboot já usa `dispatch_notifications_task.delay(incident.id)` que resolve o tenant corretamente. A função deve ser removida integralmente.

```python
# REMOVER completamente:
def _send_reboot_email(db, sensor, server_name, uptime_minutes):
    ...
```

**Verificação**: Confirmar com `grep -n "_send_reboot_email" worker/tasks.py` que não há nenhuma chamada à função antes de remover.

---

**File**: `worker/notification_dispatcher.py`

**Change 2 — Fallback probe_id (já implementado em b64cf4a)**

Já presente em `dispatch_notifications` e `dispatch_resolution`:
```python
if server:
    tenant_id = server.tenant_id
elif sensor.probe_id:
    from models import Probe
    probe = db.query(Probe).filter(Probe.id == sensor.probe_id).first()
    tenant_id = probe.tenant_id if probe else None
else:
    tenant_id = None
```

**Change 3 — Warning explícito para tenant não encontrado (já implementado em b64cf4a)**

Já presente:
```python
if not tenant:
    logger.warning(f"Tenant não encontrado para incidente {incident_id} (sensor_id={sensor.id}, server_id={sensor.server_id}, probe_id={sensor.probe_id})")
    return {'sent': sent, 'failed': [{'channel': 'all', 'error': 'Tenant não encontrado'}]}
```

---

**File**: `worker/tasks.py`

**Change 4 — dispatch_resolution_task no auto-resolve (já implementado em 57892fd)**

Já presente no bloco `else` (sensor OK):
```python
try:
    from notification_dispatcher import dispatch_resolution_task
    dispatch_resolution_task.delay(incident.id)
except Exception as _ne:
    logger.warning(f"Falha ao despachar notificação de resolução: {_ne}")
```

---

### Summary of Remaining Work

| Mudança | Status | Arquivo |
|---------|--------|---------|
| Fallback probe_id no dispatch | ✅ Implementado (b64cf4a) | notification_dispatcher.py |
| Warning explícito tenant não encontrado | ✅ Implementado (b64cf4a) | notification_dispatcher.py |
| dispatch_resolution no auto-resolve | ✅ Implementado (57892fd) | tasks.py |
| Remover `_send_reboot_email` | ⏳ Pendente | tasks.py |
| Testes de propriedade (Hypothesis) | ⏳ Pendente | tests/test_notification_silent_failure.py |

---

## Testing Strategy

### Validation Approach

A estratégia segue duas fases: primeiro verificar que os bugs são reproduzíveis no código não corrigido (exploratory), depois validar que o fix funciona e que o comportamento existente é preservado (fix checking + preservation checking).

Como os fixes já estão implementados, os testes de propriedade serão escritos para validar o estado atual corrigido e servir como regressão.

### Exploratory Bug Condition Checking

**Goal**: Confirmar que os bugs eram reproduzíveis antes dos commits b64cf4a/57892fd. Documentar os counterexamples para rastreabilidade.

**Test Plan**: Simular as condições de bug com mocks e verificar o comportamento defeituoso.

**Test Cases**:
1. **Bug 1 — Sensor standalone sem fallback**: Criar sensor com `server_id=None`, `probe_id=42`. No código sem fallback, `tenant` seria `None` e o dispatch retornaria `{'failed': [{'channel': 'all', 'error': 'Tenant não encontrado'}]}` sem log de warning. (Falha silenciosa confirmada)
2. **Bug 2 — Auto-resolve sem dispatch**: Simular sensor voltando ao normal. No código sem `dispatch_resolution_task.delay()`, nenhuma notificação de resolução seria enviada. (Omissão confirmada)
3. **Bug 3 — Reboot multi-tenant**: Servidor com `tenant_id=5`. `_send_reboot_email` buscaria `Tenant.id == 1`, obtendo tenant errado. (Hardcode confirmado)

**Expected Counterexamples**:
- Bug 1: `dispatch_notifications` retorna `failed` sem warning no log para sensor standalone.
- Bug 2: Nenhuma chamada a `dispatch_resolution_task` no fluxo de auto-resolve.
- Bug 3: `_send_reboot_email` usa `tenant_id=1` independente do servidor.

### Fix Checking

**Goal**: Verificar que para todas as entradas onde `isBugCondition(X) = true`, a função corrigida produz o comportamento esperado.

**Pseudocode:**
```
FOR ALL X WHERE isBugCondition(X) DO
  result := dispatch_notifications_fixed(X)

  IF X.sensor.server_id IS NULL AND X.sensor.probe_id IS NOT NULL THEN
    ASSERT result.tenant_resolved_via_probe = true
    ASSERT result.sent IS NOT EMPTY OR result.failed[0].error != 'Tenant não encontrado'
  END IF

  IF X.sensor.server_id IS NULL AND X.sensor.probe_id IS NULL THEN
    ASSERT warning_logged = true
    ASSERT result.failed[0].error = 'Tenant não encontrado'
  END IF

  IF X.incident.status = 'resolved' AND auto_resolve THEN
    ASSERT dispatch_resolution_called = true
  END IF
END FOR
```

### Preservation Checking

**Goal**: Verificar que para todas as entradas onde `isBugCondition(X) = false`, a função corrigida produz o mesmo resultado que a original.

**Pseudocode:**
```
FOR ALL X WHERE NOT isBugCondition(X) DO
  ASSERT dispatch_notifications_original(X) = dispatch_notifications_fixed(X)
END FOR
```

**Testing Approach**: Property-based testing com Hypothesis é recomendado porque:
- Gera automaticamente muitas combinações de `sensor_type`, `server_id`, `probe_id`, `tenant_id`.
- Captura edge cases que testes manuais perderiam (ex: `probe_id=0`, `tenant_id=None`, matriz customizada vazia).
- Fornece garantia forte de que o comportamento é preservado para todas as entradas não-buggy.

**Test Cases**:
1. **Preservation — Sensor com server_id**: Gerar sensores com `server_id` válido e verificar que o resultado é idêntico ao original.
2. **Preservation — Metric-only**: Verificar que `network_in`/`network_out` continuam retornando `{'sent': [], 'failed': []}`.
3. **Preservation — resolve_channels**: Verificar que a DEFAULT_MATRIX retorna os canais corretos para todos os `sensor_type` conhecidos.
4. **Preservation — Deduplicação**: Verificar que incidentes duplicados não são criados para o mesmo sensor.

### Unit Tests

- Testar `dispatch_notifications` com sensor `server_id=None`, `probe_id` válido → tenant resolvido via probe.
- Testar `dispatch_notifications` com sensor `server_id=None`, `probe_id=None` → warning logado, falha explícita.
- Testar `dispatch_resolution` com sensor standalone → mesmo fallback de tenant.
- Testar que `_send_reboot_email` não existe mais em `tasks.py` após remoção.
- Testar `resolve_channels` para todos os `sensor_type` da DEFAULT_MATRIX.

### Property-Based Tests (Hypothesis)

- **Property 1**: Para qualquer `sensor_type` válido e `custom_matrix=None`, `resolve_channels` retorna subconjunto de `VALID_CHANNELS` e nunca retorna conjunto vazio (fallback para `{'email'}`).
- **Property 2**: Para qualquer sensor com `server_id` não-None, `dispatch_notifications` não usa o caminho de fallback `probe_id`.
- **Property 3**: Para qualquer sensor com `server_id=None` e `probe_id` não-None, `dispatch_notifications` resolve tenant via probe (não retorna `'Tenant não encontrado'` se probe existe).
- **Property 4**: Para qualquer incidente auto-resolvido, `dispatch_resolution_task` é chamado exatamente uma vez.
- **Property 5**: Para qualquer `sensor_type` em `METRIC_ONLY_TYPES`, `dispatch_notifications` retorna `{'sent': [], 'failed': []}` sem chamar nenhum canal.

### Integration Tests

- Testar fluxo completo: sensor HTTP standalone → incidente criado → `dispatch_notifications_task` → email enviado (mock SMTP).
- Testar fluxo de resolução: sensor volta ao normal → `dispatch_resolution_task` → email "✅ RESOLVIDO" enviado.
- Testar fluxo de reboot: sensor `system` → incidente informativo criado → `dispatch_notifications_task` → email enviado para tenant correto (não hardcoded).
- Testar que `_send_reboot_email` não é chamada em nenhum fluxo após remoção.
