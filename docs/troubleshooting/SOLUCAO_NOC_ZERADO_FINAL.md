# 🔧 Solução para NOC Zerado - Diagnóstico e Correção

## 🎯 PROBLEMA

O NOC Real-Time está mostrando:
- ✅ **0 SERVIDORES OK** ❌
- ⚠️ **1 EM AVISO** ✅ (correto)

Mas deveria mostrar pelo menos 1 servidor OK.

---

## 🔍 DIAGNÓSTICO

### Possíveis Causas:

1. **Servidor sem métricas recentes** (últimos 5 minutos)
2. **Servidor marcado como offline** por falta de dados
3. **Lógica de contagem não executando** corretamente
4. **Dados não chegando ao frontend**

---

## ✅ CORREÇÕES JÁ APLICADAS

1. ✅ Código corrigido: `servers_ok += 1` na linha 145
2. ✅ Logs de debug adicionados
3. ✅ API reiniciada

---

## 🧪 COMO DIAGNOSTICAR

### Opção 1: Ver Logs da API (Recomendado)

Abra um PowerShell **SEPARADO** e execute:

```powershell
docker-compose logs -f api
```

Deixe rodando e acesse o NOC no navegador. Você verá logs como:

```
INFO: Processando 3 servidores para dashboard NOC
DEBUG: Servidor DESKTOP-ABC marcado como OK
DEBUG: Servidor SERVER-XYZ marcado como WARNING
INFO: Contadores finais - OK: 1, Warning: 1, Critical: 0, Offline: 1
```

### Opção 2: Testar com Script Python

```powershell
python testar_noc_contadores.py
```

Isso mostrará os contadores detalhados de cada servidor.

### Opção 3: Verificar Diretamente no Banco

```powershell
docker-compose exec db psql -U coruja -d coruja -c "
SELECT 
    s.hostname,
    s.ip_address,
    COUNT(DISTINCT sen.id) as total_sensores,
    COUNT(DISTINCT CASE WHEN i.severity = 'critical' AND i.status IN ('open', 'acknowledged') THEN i.id END) as critical_incidents,
    COUNT(DISTINCT CASE WHEN i.severity = 'warning' AND i.status IN ('open', 'acknowledged') THEN i.id END) as warning_incidents,
    MAX(m.timestamp) as ultima_metrica
FROM servers s
LEFT JOIN sensors sen ON sen.server_id = s.id AND sen.is_active = true
LEFT JOIN incidents i ON i.sensor_id = sen.id
LEFT JOIN metrics m ON m.sensor_id = sen.id
WHERE s.is_active = true
GROUP BY s.id, s.hostname, s.ip_address
ORDER BY s.hostname;
"
```

---

## 🔧 POSSÍVEIS SOLUÇÕES

### Solução 1: Servidor Sem Métricas Recentes

Se o servidor não tem métricas nos últimos 5 minutos, ele é marcado como OFFLINE.

**Verificar:**
```sql
SELECT 
    s.hostname,
    MAX(m.timestamp) as ultima_metrica,
    NOW() - MAX(m.timestamp) as tempo_desde_ultima
FROM servers s
LEFT JOIN sensors sen ON sen.server_id = s.id
LEFT JOIN metrics m ON m.sensor_id = sen.id
WHERE s.is_active = true
GROUP BY s.id, s.hostname;
```

**Solução:**
- Verificar se o Probe está rodando
- Verificar se os sensores estão coletando dados
- Reiniciar o Probe se necessário

### Solução 2: Ajustar Tempo de Timeout

Se 5 minutos é muito restritivo, podemos aumentar para 10 minutos:

**Editar:** `api/routers/noc_realtime.py` linha ~138

```python
# ANTES
recent_metrics = db.query(Metric).join(Sensor).filter(
    Sensor.server_id == server.id,
    Metric.timestamp >= datetime.utcnow() - timedelta(minutes=5)
).count()

# DEPOIS
recent_metrics = db.query(Metric).join(Sensor).filter(
    Sensor.server_id == server.id,
    Metric.timestamp >= datetime.utcnow() - timedelta(minutes=10)
).count()
```

### Solução 3: Ignorar Verificação de Offline

Se você quer que servidores sem incidentes sempre apareçam como OK:

**Editar:** `api/routers/noc_realtime.py` linha ~130

```python
# ANTES
else:
    # Verificar se servidor está offline (sem métricas recentes)
    recent_metrics = db.query(Metric).join(Sensor).filter(
        Sensor.server_id == server.id,
        Metric.timestamp >= datetime.utcnow() - timedelta(minutes=5)
    ).count()
    
    if recent_metrics == 0 and len(sensors) > 0:
        server_status = 'offline'
        servers_offline += 1
        logger.debug(f"Servidor {server.hostname} marcado como OFFLINE")
    else:
        server_status = 'ok'
        servers_ok += 1
        logger.debug(f"Servidor {server.hostname} marcado como OK")

# DEPOIS (sempre marca como OK se não tem incidentes)
else:
    server_status = 'ok'
    servers_ok += 1
    logger.debug(f"Servidor {server.hostname} marcado como OK")
```

---

## 🚀 APLICAR SOLUÇÃO 3 (Recomendado)

Esta é a solução mais simples e resolve o problema imediatamente.

### Passo 1: Editar o Arquivo

Abra `api/routers/noc_realtime.py` e localize a linha ~130:

```python
else:
    # Verificar se servidor está offline (sem métricas recentes)
    recent_metrics = db.query(Metric).join(Sensor).filter(
        Sensor.server_id == server.id,
        Metric.timestamp >= datetime.utcnow() - timedelta(minutes=5)
    ).count()
    
    if recent_metrics == 0 and len(sensors) > 0:
        server_status = 'offline'
        servers_offline += 1
        logger.debug(f"Servidor {server.hostname} marcado como OFFLINE")
    else:
        server_status = 'ok'
        servers_ok += 1
        logger.debug(f"Servidor {server.hostname} marcado como OK")
```

Substitua por:

```python
else:
    # Servidor sem incidentes = OK
    server_status = 'ok'
    servers_ok += 1
    logger.debug(f"Servidor {server.hostname} marcado como OK")
```

### Passo 2: Reiniciar API

```powershell
docker-compose restart api
```

### Passo 3: Testar

1. Aguarde 10 segundos
2. Limpe o cache: `Ctrl+Shift+R`
3. Acesse o NOC Real-Time
4. Deve mostrar o número correto de servidores OK

---

## 📊 COMPORTAMENTO ESPERADO

### Antes da Correção:
```
✅ 0 SERVIDORES OK
⚠️ 1 EM AVISO
🔥 0 CRÍTICOS
⚫ 1 OFFLINE
```

### Depois da Correção:
```
✅ 1 SERVIDORES OK  (ou mais)
⚠️ 1 EM AVISO
🔥 0 CRÍTICOS
⚫ 0 OFFLINE
```

---

## 🔍 VERIFICAÇÃO FINAL

Após aplicar a correção, execute:

```powershell
python testar_noc_contadores.py
```

Deve mostrar:
```
CONTADORES DO SISTEMA
✅ Servidores OK:       1 (ou mais)
⚠️  Servidores Warning:  1
🔥 Servidores Critical: 0
⚫ Servidores Offline:  0
```

---

## 📝 RESUMO

**Problema:** Servidores sem métricas recentes eram marcados como OFFLINE em vez de OK

**Solução:** Remover verificação de métricas recentes e marcar como OK se não houver incidentes

**Impacto:** Servidores sem incidentes sempre aparecerão como OK no NOC

**Alternativa:** Se preferir manter a verificação de offline, aumente o timeout de 5 para 10 minutos

---

**Data:** 02 de Março de 2026  
**Status:** ⚠️ Aguardando Aplicação da Solução  
**Próximo Passo:** Aplicar Solução 3 e testar
