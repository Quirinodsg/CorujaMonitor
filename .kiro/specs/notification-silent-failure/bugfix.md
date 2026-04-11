# Bugfix Requirements Document

## Introduction

O sistema Coruja Monitor falha silenciosamente ao enviar notificações (email + Teams) em três cenários críticos:

1. **Sensores HTTP standalone** (ex: sensor do CRM) não têm `server_id`, então a busca de tenant via `server.tenant_id` retorna `None` — a notificação é descartada sem nenhum log de erro visível.
2. **Auto-resolve sem notificação de resolução** — quando um incidente é resolvido automaticamente (sensor voltou ao normal), o código fazia apenas `db.commit()` sem chamar o dispatcher, resultando em nenhum email/Teams de "problema resolvido".
3. **`_send_reboot_email` com `tenant_id == 1` hardcoded** — a função de email de reboot busca sempre o tenant de ID 1, quebrando em ambientes multi-tenant onde o servidor pertence a outro tenant.

O impacto é direto: o site CRM ficou fora por 15 minutos sem nenhum alerta, e reboots de máquinas não geram notificações para tenants com ID diferente de 1. O Zabbix (sistema paralelo) enviou os alertas normalmente para os mesmos eventos.

---

## Bug Analysis

### Current Behavior (Defect)

1.1 WHEN um sensor HTTP standalone (sem `server_id`) gera um incidente THEN o sistema descarta a notificação silenciosamente sem enviar email nem Teams e sem registrar erro nos logs

1.2 WHEN `sensor.server_id` é `None` e `sensor.probe_id` também é `None` THEN o sistema retorna `tenant = None` e aborta o dispatch sem nenhuma mensagem de erro identificável

1.3 WHEN um incidente é auto-resolvido porque o sensor voltou ao normal THEN o sistema apenas faz `db.commit()` e não chama o dispatcher de resolução, resultando em nenhuma notificação de "problema resolvido"

1.4 WHEN `_send_reboot_email` é chamada para um servidor cujo tenant tem `id != 1` THEN o sistema busca `Tenant.id == 1` hardcoded, obtém o tenant errado (ou nenhum), e envia o email para o destinatário incorreto ou não envia nada

1.5 WHEN o worker tenta executar `run_aiops_pipeline_v3` THEN o sistema falha com `No module named 'ai_agents'` e registra erro no log, potencialmente interrompendo o fluxo de notificações encadeadas

### Expected Behavior (Correct)

2.1 WHEN um sensor HTTP standalone (sem `server_id`) gera um incidente THEN o sistema SHALL buscar o tenant via `sensor.probe_id → Probe.tenant_id` e, se encontrado, enviar as notificações normalmente

2.2 WHEN `sensor.server_id` é `None` e `sensor.probe_id` também é `None` THEN o sistema SHALL registrar um warning claro nos logs identificando o sensor e o incidente, e retornar falha explícita em vez de descartar silenciosamente

2.3 WHEN um incidente é auto-resolvido porque o sensor voltou ao normal THEN o sistema SHALL chamar `dispatch_resolution_task.delay(incident.id)` para enviar notificação de resolução via email e Teams

2.4 WHEN `_send_reboot_email` é chamada para qualquer servidor THEN o sistema SHALL buscar o tenant correto a partir do `server.tenant_id` em vez de usar `tenant_id == 1` hardcoded

2.5 WHEN o módulo `ai_agents` não está disponível no path do worker THEN o sistema SHALL continuar executando as notificações normalmente, pois o AIOps é enriquecimento opcional e não deve bloquear o fluxo principal

### Unchanged Behavior (Regression Prevention)

3.1 WHEN um sensor com `server_id` válido gera um incidente THEN o sistema SHALL CONTINUE TO buscar o tenant via `server.tenant_id` e enviar notificações normalmente

3.2 WHEN um sensor `ping` gera um incidente THEN o sistema SHALL CONTINUE TO forçar `priority=5` e enviar notificações via email, ticket e Teams

3.3 WHEN um sensor do tipo `network_in` ou `network_out` gera uma métrica THEN o sistema SHALL CONTINUE TO ignorar notificações (metric_only)

3.4 WHEN um incidente já existe aberto para o mesmo sensor THEN o sistema SHALL CONTINUE TO não criar incidente duplicado (deduplicação preservada)

3.5 WHEN o tenant tem uma `notification_matrix` customizada THEN o sistema SHALL CONTINUE TO usar essa matriz em vez da DEFAULT_MATRIX para resolver os canais

3.6 WHEN um canal de notificação falha (ex: SMTP indisponível) THEN o sistema SHALL CONTINUE TO tentar os demais canais de forma isolada (try/except por canal)

3.7 WHEN um sensor do tipo `system` detecta reboot THEN o sistema SHALL CONTINUE TO criar o incidente já resolvido (informativo) e aplicar cooldown de 1 hora por sensor

---

## Bug Condition Pseudocode

### Bug Condition C(X) — Identifica entradas que disparam os bugs

```pascal
FUNCTION isBugCondition(X)
  INPUT: X of type DispatchInput { sensor, incident, tenant_lookup_path }
  OUTPUT: boolean

  // Bug 1: sensor standalone sem server_id
  IF X.sensor.server_id IS NULL AND X.sensor.probe_id IS NULL THEN
    RETURN true
  END IF

  // Bug 2: auto-resolve sem dispatch de resolução
  IF X.incident.status = 'resolved' AND X.incident.resolution_source = 'auto'
     AND dispatch_resolution_called = false THEN
    RETURN true
  END IF

  // Bug 3: reboot email com tenant hardcoded
  IF X.sensor.sensor_type = 'system' AND tenant_id_used = 1
     AND X.server.tenant_id != 1 THEN
    RETURN true
  END IF

  RETURN false
END FUNCTION
```

### Property: Fix Checking

```pascal
// Para todos os inputs que disparam o bug, o comportamento corrigido deve ser:
FOR ALL X WHERE isBugCondition(X) DO
  result ← dispatch_notifications'(X)

  // Bug 1: tenant encontrado via probe ou warning explícito
  IF X.sensor.server_id IS NULL THEN
    ASSERT (result.tenant_resolved_via_probe = true)
        OR (result.warning_logged = true AND result.failed contains 'Tenant não encontrado')
  END IF

  // Bug 2: resolução notificada
  IF X.incident.status = 'resolved' AND X.incident.resolution_source = 'auto' THEN
    ASSERT dispatch_resolution_called = true
  END IF

  // Bug 3: tenant correto usado no email de reboot
  IF X.sensor.sensor_type = 'system' THEN
    ASSERT tenant_id_used = X.server.tenant_id
  END IF
END FOR
```

### Property: Preservation Checking

```pascal
// Para todos os inputs que NÃO disparam o bug, o comportamento deve ser idêntico ao original:
FOR ALL X WHERE NOT isBugCondition(X) DO
  ASSERT dispatch_notifications(X) = dispatch_notifications'(X)
END FOR
```
