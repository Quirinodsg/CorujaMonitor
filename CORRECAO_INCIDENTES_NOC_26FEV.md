# Correção: Incidentes e NOC - 26 FEV 2026

## ✅ CORREÇÕES IMPLEMENTADAS

### 1. Auto-Resolução de Incidentes Reconhecidos

**Problema:** Incidente reconhecido não fechava automaticamente quando o problema era resolvido

**Causa:** Worker só fechava incidentes com status "open", ignorando "acknowledged"

**Solução:** Worker agora fecha incidentes com status "open" OU "acknowledged"

**Arquivo:** `worker/tasks.py`

```python
# ANTES: Só fechava incidentes "open"
open_incidents = db.query(Incident).filter(
    Incident.sensor_id == sensor.id,
    Incident.status == "open"
).all()

# DEPOIS: Fecha incidentes "open" E "acknowledged"
open_incidents = db.query(Incident).filter(
    Incident.sensor_id == sensor.id,
    Incident.status.in_(['open', 'acknowledged'])
).all()

for incident in open_incidents:
    incident.status = "resolved"
    incident.resolved_at = datetime.utcnow()
    incident.resolution_notes = "Auto-resolvido: sensor voltou ao normal"
    db.commit()
```

---

### 2. NOC Mostrando Todos os Servidores

**Problema:** Servidor sumia do NOC quando não tinha incidentes ativos

**Causa:** Endpoint do heatmap não estava mostrando servidores sem incidentes

**Solução:** Endpoint agora mostra TODOS os servidores ativos, independente de terem incidentes

**Arquivo:** `api/routers/noc.py`

```python
# Busca TODOS os servidores ativos
if current_user.role == 'admin':
    servers = db.query(Server).filter(Server.is_active == True).all()
else:
    servers = db.query(Server).filter(
        Server.tenant_id == current_user.tenant_id,
        Server.is_active == True
    ).all()

# Para cada servidor, verifica incidentes ativos
for server in servers:
    critical_incident = db.query(Incident).join(Sensor).filter(
        Sensor.server_id == server.id,
        Incident.status.in_(['open', 'acknowledged']),
        Incident.severity == 'critical'
    ).first()
    
    # Se não tem incidente, calcula disponibilidade real
    if not critical_incident and not warning_incident:
        # Calcula baseado em métricas das últimas 24h
        ...
```

---

## 🔧 COMO FUNCIONA AGORA

### Auto-Resolução de Incidentes:

```
┌─────────────────┐
│ Sensor Volta    │
│ ao Normal       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Worker Detecta  │
│ (a cada 60s)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Busca Incidentes│
│ open OU         │
│ acknowledged    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Fecha Incidente │
│ status=resolved │
│ + timestamp     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Dashboard       │
│ Atualiza        │
└─────────────────┘
```

### NOC Heatmap:

```
┌─────────────────┐
│ Busca TODOS     │
│ Servidores      │
│ Ativos          │
└────────┬────────┘
         │
         ▼
    ┌────┴────┐
    │ Tem     │
    │Incidente│
    │ Ativo?  │
    └────┬────┘
         │
    ┌────┴────┐
    │   Sim   │
    └────┬────┘
         │
         ▼
┌─────────────────┐
│ Status baseado  │
│ no Incidente    │
│ (critical/warn) │
└─────────────────┘
         │
    ┌────┴────┐
    │   Não   │
    └────┬────┘
         │
         ▼
┌─────────────────┐
│ Calcula         │
│ Disponibilidade │
│ (últimas 24h)   │
└─────────────────┘
```

---

## 📋 ARQUIVOS MODIFICADOS

1. **worker/tasks.py**
   - Linha 85-93: Auto-resolução agora inclui incidentes "acknowledged"
   - Adiciona log de resolução
   - Define resolution_notes

2. **api/routers/noc.py**
   - Endpoint `/heatmap`: Mostra todos os servidores ativos
   - Prioriza incidentes ativos sobre métricas
   - Adiciona IP do servidor no retorno

3. **probe/probe_config.json**
   - Atualizado IP da API: 192.168.30.189 → 192.168.0.41

---

## 🚀 PARA APLICAR AS CORREÇÕES

### Passo 1: Reiniciar Worker
```bash
docker-compose restart worker
```

### Passo 2: Reiniciar API
```bash
docker-compose restart api
```

### Passo 3: Reiniciar Probe
```bash
# Parar probe atual
taskkill /F /FI "WINDOWTITLE eq *probe*"

# Aguardar 2 segundos
timeout /t 2

# Iniciar probe
cd probe
python probe_core.py
```

### Passo 4: Verificar
1. Acesse o Dashboard
2. Reconheça um incidente
3. Aguarde o sensor voltar ao normal
4. Aguarde 60 segundos (próxima verificação do worker)
5. ✅ Incidente deve ser fechado automaticamente

---

## ✅ VALIDAÇÃO

### Teste 1: Auto-Resolução
1. Crie um incidente (ex: ping alto)
2. Reconheça o incidente (status = acknowledged)
3. Aguarde o ping voltar ao normal
4. Aguarde 60 segundos
5. ✅ Incidente deve ser fechado automaticamente

### Teste 2: NOC Heatmap
1. Acesse o NOC
2. Verifique se TODOS os servidores aparecem
3. ✅ Servidores sem incidentes devem aparecer em verde
4. ✅ Servidores com incidentes devem aparecer em amarelo/vermelho

### Teste 3: Logs
```bash
# Ver logs do worker
docker logs coruja-worker --tail 50 | Select-String "auto-resolvido"

# Ver logs da API
docker logs coruja-api --tail 50 | Select-String "heatmap"
```

---

## 📊 COMPORTAMENTO ESPERADO

### Dashboard:
- ⚠️ 1 Incidente Aberto → Reconhecer
- ✅ 0 Incidentes Abertos (após sensor normalizar + 60s)

### NOC:
- Mostra TODOS os servidores
- Atualiza a cada 5 segundos
- Servidores OK = verde
- Servidores com aviso = amarelo
- Servidores críticos = vermelho

---

## 🔍 TROUBLESHOOTING

### Incidente não fecha automaticamente:
1. Verificar se worker está rodando: `docker ps | Select-String worker`
2. Verificar logs do worker: `docker logs coruja-worker --tail 50`
3. Verificar se sensor realmente voltou ao normal
4. Aguardar até 60 segundos (intervalo do worker)

### Servidor não aparece no NOC:
1. Verificar se servidor está ativo: `Server.is_active == True`
2. Verificar logs da API: `docker logs coruja-api --tail 50`
3. Recarregar página do NOC (F5)
4. Verificar se há métricas recentes (últimas 24h)

### Probe não conecta:
1. Verificar IP em `probe/probe_config.json`
2. Deve ser: `http://192.168.0.41:8000`
3. Reiniciar probe após mudar configuração
4. Verificar se API está respondendo: `curl http://192.168.0.41:8000/docs`

---

## 💡 MELHORIAS FUTURAS

1. **Notificações de Auto-Resolução**
   - Enviar notificação quando incidente é auto-resolvido
   - Incluir tempo de resolução

2. **NOC em Tempo Real**
   - WebSocket para atualização instantânea
   - Sem necessidade de polling a cada 5s

3. **Histórico de Incidentes**
   - Mostrar incidentes resolvidos recentemente
   - Timeline de eventos

---

**Data:** 26 de Fevereiro de 2026
**Status:** ✅ IMPLEMENTADO
**Versão:** 1.0
**Requer Reinicialização:** Sim (Worker, API, Probe)
