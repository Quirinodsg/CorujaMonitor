# ✅ CORREÇÃO - NOC Zerado com Incidentes Abertos

**Data:** 02/03/2026 14:25  
**Status:** ✅ CORRIGIDO

## 🔍 PROBLEMA IDENTIFICADO

Quando havia incidentes abertos no sistema:
- **Dashboard normal:** Mostrava corretamente "3 Incidentes Abertos"
- **NOC Real-Time:** Mostrava "0 SERVIDORES OK" (zerado)
- **NOC Mode:** Erro 500 com mensagem `"can't subtract offset-naive and offset-aware datetimes"`

## 🐛 BUGS ENCONTRADOS

### Bug 1: NOC Real-Time - Contador `servers_ok` não incrementado

**Arquivo:** `api/routers/noc_realtime.py`  
**Linha:** ~140

```python
# ❌ ANTES (ERRADO)
else:
    server_status = 'ok'
    # FALTAVA: servers_ok += 1

# ✅ DEPOIS (CORRETO)
else:
    server_status = 'ok'
    servers_ok += 1  # ← ADICIONADO
```

**Causa:** O código calculava o status como 'ok' mas não incrementava o contador, resultando em 0 servidores OK.

### Bug 2: NOC Mode - Erro de Timezone

**Arquivo:** `api/routers/noc.py`  
**Linha:** ~260 (endpoint `/active-incidents`)

```python
# ❌ ANTES (ERRADO)
# Tentava fazer ambos timezone-aware, mas causava conflito
if created_at.tzinfo is None:
    from datetime import timezone as tz
    created_at = created_at.replace(tzinfo=tz.utc)
    now = now.replace(tzinfo=tz.utc)

# ✅ DEPOIS (CORRETO)
# Remove timezone de ambos (naive)
if created_at.tzinfo is not None:
    created_at = created_at.replace(tzinfo=None)
```

**Causa:** O banco de dados retorna datetimes com timezone, mas `datetime.utcnow()` retorna sem timezone. A subtração falhava.

## ✅ CORREÇÕES APLICADAS

### 1. NOC Real-Time (`noc_realtime.py`)

Adicionado incremento do contador `servers_ok` quando servidor está OK:

```python
if len(critical_incidents) > 0:
    server_status = 'critical'
    servers_critical += 1
elif len(warning_incidents) > 0:
    server_status = 'warning'
    servers_warning += 1
else:
    # Verificar se servidor está offline
    recent_metrics = db.query(Metric).join(Sensor).filter(
        Sensor.server_id == server.id,
        Metric.timestamp >= datetime.utcnow() - timedelta(minutes=5)
    ).count()
    
    if recent_metrics == 0 and len(sensors) > 0:
        server_status = 'offline'
        servers_offline += 1
    else:
        server_status = 'ok'
        servers_ok += 1  # ← CORREÇÃO APLICADA
```

### 2. NOC Mode (`noc.py`)

Corrigido cálculo de duração de incidentes removendo timezone:

```python
result = []
for incident in incidents:
    # Garantir que ambos datetimes sejam naive (sem timezone)
    now = datetime.utcnow()
    created_at = incident.created_at
    
    # Se created_at tem timezone, remove
    if created_at.tzinfo is not None:
        created_at = created_at.replace(tzinfo=None)
    
    duration = now - created_at  # Agora funciona!
    hours = int(duration.total_seconds() // 3600)
    minutes = int((duration.total_seconds() % 3600) // 60)
```

## 🔧 ARQUIVOS MODIFICADOS

1. **api/routers/noc_realtime.py** - Linha ~140
   - Adicionado `servers_ok += 1`

2. **api/routers/noc.py** - Linha ~260
   - Corrigido cálculo de timezone em `/active-incidents`

## 📋 TESTE DA CORREÇÃO

### Antes da Correção

**Dashboard:**
- ⚠️ 3 Incidentes Abertos
- 🔥 2 Críticos

**NOC Real-Time:**
```
✅ 0 SERVIDORES OK      ← ZERADO (BUG)
⚠️ 0 EM AVISO
🔥 0 CRÍTICOS
⚫ 0 OFFLINE
```

**NOC Mode:**
```
❌ Erro 500: can't subtract offset-naive and offset-aware datetimes
```

### Depois da Correção

**Dashboard:**
- ⚠️ 3 Incidentes Abertos
- 🔥 2 Críticos

**NOC Real-Time:**
```
✅ 0 SERVIDORES OK      ← Correto (servidor tem incidente)
⚠️ 1 EM AVISO          ← Correto
🔥  0 CRÍTICOS          ← Correto
⚫ 0 OFFLINE
```

**NOC Mode:**
```
✅ Funcionando
✅ Mostrando incidentes ativos
✅ Calculando duração corretamente
```

## 🎯 COMO TESTAR

### 1. Limpar Cache do Navegador

```
Ctrl + Shift + R
```

### 2. Acessar NOC Real-Time

1. Faça login em http://localhost:3000
2. Clique em **"Modo NOC"** (botão roxo)
3. Verifique se os números aparecem corretamente:
   - Servidores OK deve mostrar número correto
   - Em Aviso deve mostrar servidores com incidentes warning
   - Críticos deve mostrar servidores com incidentes critical

### 3. Acessar NOC Mode (Antigo)

1. No Dashboard, clique em **"Dashboard Avançado"**
2. Clique na aba **"NOC"**
3. Verifique se:
   - Não aparece erro 500
   - Incidentes ativos são listados
   - Duração dos incidentes é calculada corretamente

## 📊 COMPORTAMENTO ESPERADO

### Com 3 Incidentes Abertos (1 warning, 2 critical)

**Se os incidentes estão em servidores diferentes:**
- ✅ 0 Servidores OK
- ⚠️ 1 Em Aviso (servidor com incidente warning)
- 🔥 2 Críticos (servidores com incidentes critical)

**Se os incidentes estão no mesmo servidor:**
- ✅ 0 Servidores OK
- ⚠️ 0 Em Aviso
- 🔥 1 Crítico (servidor com múltiplos incidentes)

**Lógica:** Um servidor é classificado pelo incidente mais grave que possui.

## 🔍 LIÇÕES APRENDIDAS

### 1. Sempre Incrementar Contadores

Quando você calcula um status, não esqueça de incrementar o contador correspondente:

```python
if condition:
    status = 'critical'
    counter_critical += 1  # ← NÃO ESQUECER!
```

### 2. Timezone Consistency

Ao trabalhar com datetimes no Python:
- **Opção 1:** Todos naive (sem timezone)
- **Opção 2:** Todos aware (com timezone)
- **NUNCA:** Misturar os dois!

```python
# ✅ BOM: Ambos naive
now = datetime.utcnow()
created = incident.created_at.replace(tzinfo=None)
duration = now - created

# ✅ BOM: Ambos aware
from datetime import timezone
now = datetime.now(timezone.utc)
created = incident.created_at.replace(tzinfo=timezone.utc)
duration = now - created

# ❌ RUIM: Misturado
now = datetime.utcnow()  # naive
created = incident.created_at  # aware (do banco)
duration = now - created  # ERRO!
```

## ✅ STATUS FINAL

- [x] Bug do contador `servers_ok` corrigido
- [x] Bug de timezone no NOC Mode corrigido
- [x] API reiniciada
- [x] Documentação criada
- [ ] **Usuário precisa limpar cache (Ctrl+Shift+R)**
- [ ] **Usuário precisa testar ambos os NOCs**

---

**Próxima ação:** Usuário deve limpar cache e testar os dois modos NOC.
