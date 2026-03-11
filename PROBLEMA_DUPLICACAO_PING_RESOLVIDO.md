# 🔧 PROBLEMA: Duplicação de Sensores PING - RESOLVIDO

**Data**: 11 Março 2026  
**Status**: ✅ Correções Aplicadas (pendente reiniciar serviços)

---

## 🐛 PROBLEMAS IDENTIFICADOS

### 1. Worker Criando Sensores Duplicados

**Causa**: Worker buscava sensor com `name == 'ping'` (minúsculo), mas API normaliza para `name == 'PING'` (maiúsculo).

**Resultado**: Worker não encontrava sensor existente e criava novo a cada execução.

```python
# ANTES (worker/tasks.py - ERRADO)
ping_sensor = db.query(Sensor).filter(
    Sensor.server_id == server.id,
    Sensor.sensor_type == 'ping',
    Sensor.name == 'ping'  # ❌ Minúsculo
).first()
```

**Correção Aplicada**:
```python
# DEPOIS (worker/tasks.py - CORRETO)
ping_sensor = db.query(Sensor).filter(
    Sensor.server_id == server.id,
    Sensor.sensor_type == 'ping'  # ✅ Busca qualquer nome
).first()

if not ping_sensor:
    ping_sensor = Sensor(
        server_id=server.id,
        sensor_type='ping',
        name='PING',  # ✅ Maiúsculo para consistência
        threshold_warning=100,
        threshold_critical=200,
        is_active=True
    )
else:
    # Normalizar nome para PING (maiúsculo)
    if ping_sensor.name != 'PING':
        ping_sensor.name = 'PING'
        db.commit()
```

---

### 2. Probe Ainda Enviando Métricas PING

**Causa**: Função `_collect_ping_only()` na probe ainda ativa, enviando métricas PING para API.

**Resultado**: API criava sensores PING mesmo após worker criar.

**Correção Aplicada**:
```python
# probe/probe_core.py
def _collect_ping_only(self, server):
    """
    DESABILITADO: PING agora é feito direto do servidor Linux (worker).
    Mantido apenas para compatibilidade com código legado.
    """
    logger.info(f"⚠️ PING desabilitado na probe - feito pelo servidor central (worker)")
    return  # Não coleta PING
```

---

### 3. Sensores "Desconhecidos" (Unknown)

**Causa**: Probe enviando sensores com tipo `unknown` que não são filtrados.

**Solução**: Script de limpeza em `LIMPAR_SENSORES_COMPLETO_AGORA.txt`

---

### 4. Incidentes de PING Não Resolvem

**Causa**: Incidentes antigos de PING ficam abertos mesmo após servidor voltar.

**Solução**: Script para fechar todos os incidentes de PING em `LIMPAR_SENSORES_COMPLETO_AGORA.txt`

---

## ✅ CORREÇÕES APLICADAS

### Arquivos Modificados

1. **worker/tasks.py**
   - Busca sensor PING sem filtrar por nome
   - Cria sensor com nome `PING` (maiúsculo)
   - Normaliza nome de sensores existentes para `PING`

2. **probe/probe_core.py**
   - Função `_collect_ping_only()` desabilitada
   - Retorna sem fazer nada
   - Log informativo sobre desabilitação

---

## 🚀 PRÓXIMOS PASSOS

### 1. Reiniciar Serviços (Linux)

```bash
# Reiniciar worker
docker-compose restart worker
sleep 10
docker logs coruja-worker --tail 50 | grep -i ping

# Reiniciar API
docker-compose restart api
sleep 10
docker logs coruja-api --tail 20
```

### 2. Reiniciar Probe (Windows - SRVSONDA001)

```cmd
net stop CorujaProbe
timeout /t 5
net start CorujaProbe
type "C:\Program Files\CorujaMonitor\Probe\probe.log" | findstr /i "ping"
```

### 3. Limpar Sensores Duplicados

Ver arquivo: `LIMPAR_SENSORES_COMPLETO_AGORA.txt`

```bash
# Diagnosticar
docker exec -it coruja-postgres psql -U coruja -d coruja_monitor -c "SELECT srv.hostname, s.id, s.name, COUNT(m.id) as metricas FROM servers srv JOIN sensors s ON s.server_id = srv.id LEFT JOIN metrics m ON m.sensor_id = s.id WHERE s.sensor_type = 'ping' GROUP BY srv.hostname, s.id, s.name ORDER BY srv.hostname, metricas DESC;"

# Deletar duplicados (SUBSTITUA os IDs!)
docker exec -it coruja-postgres psql -U coruja -d coruja_monitor -c "DELETE FROM remediation_logs WHERE incident_id IN (SELECT id FROM incidents WHERE sensor_id IN (41, 42));"
docker exec -it coruja-postgres psql -U coruja -d coruja_monitor -c "DELETE FROM incidents WHERE sensor_id IN (41, 42);"
docker exec -it coruja-postgres psql -U coruja -d coruja_monitor -c "DELETE FROM metrics WHERE sensor_id IN (41, 42);"
docker exec -it coruja-postgres psql -U coruja -d coruja_monitor -c "DELETE FROM sensors WHERE id IN (41, 42);"
```

### 4. Deletar Sensores Desconhecidos

```bash
# Deletar sensores unknown
docker exec -it coruja-postgres psql -U coruja -d coruja_monitor -c "DELETE FROM remediation_logs WHERE incident_id IN (SELECT id FROM incidents WHERE sensor_id IN (SELECT id FROM sensors WHERE sensor_type = 'unknown'));"
docker exec -it coruja-postgres psql -U coruja -d coruja_monitor -c "DELETE FROM incidents WHERE sensor_id IN (SELECT id FROM sensors WHERE sensor_type = 'unknown');"
docker exec -it coruja-postgres psql -U coruja -d coruja_monitor -c "DELETE FROM metrics WHERE sensor_id IN (SELECT id FROM sensors WHERE sensor_type = 'unknown');"
docker exec -it coruja-postgres psql -U coruja -d coruja_monitor -c "DELETE FROM sensors WHERE sensor_type = 'unknown';"
```

### 5. Fechar Incidentes de PING

```bash
# Fechar incidentes de PING abertos
docker exec -it coruja-postgres psql -U coruja -d coruja_monitor -c "UPDATE incidents SET status = 'resolved', resolved_at = NOW(), resolution_notes = 'Fechado automaticamente - sistema de PING migrado para worker' WHERE sensor_id IN (SELECT id FROM sensors WHERE sensor_type = 'ping') AND status != 'resolved';"
```

### 6. Enviar para Git

```bash
# Windows (Git Bash)
cd ~/Coruja\ Monitor
git add worker/tasks.py probe/probe_core.py LIMPAR_SENSORES_COMPLETO_AGORA.txt PROBLEMA_DUPLICACAO_PING_RESOLVIDO.md
git commit -m "fix: Corrigir duplicação de sensores PING e desabilitar PING na probe"
git push origin master

# Linux
cd /home/administrador/CorujaMonitor
git pull origin master
```

---

## 📊 RESULTADO ESPERADO

### Banco de Dados

```
hostname        | total_ping
----------------+------------
SRVCMONITOR001  |          1
SRVSONDA001     |          1
```

### Logs Worker

```
🏓 Iniciando PING de todos os servidores...
📊 Encontrados 2 servidores ativos para fazer PING
✅ PING concluído para 2 servidores
```

### Logs Probe

```
⚠️ PING desabilitado na probe - feito pelo servidor central (worker)
```

### Dashboard

- 1 sensor PING por servidor
- Nome: PING (maiúsculo)
- Latências atualizando a cada 60s
- Sem sensores desconhecidos
- Sem incidentes de PING abertos

---

## 🎯 RESUMO

**Problema**: Worker e probe criando sensores PING duplicados devido a inconsistência de nomes (minúsculo vs maiúsculo).

**Solução**: 
1. Worker busca sensor sem filtrar por nome e normaliza para `PING`
2. Probe desabilitada para não enviar métricas PING
3. Script de limpeza para remover duplicados e sensores desconhecidos

**Status**: ✅ Correções aplicadas, pendente reiniciar serviços e limpar banco

---

## 📚 Arquivos de Referência

- `LIMPAR_SENSORES_COMPLETO_AGORA.txt` - Script completo de limpeza
- `PROBLEMA_DUPLICACAO_PING_RESOLVIDO.md` - Este arquivo
- `worker/tasks.py` - Worker corrigido
- `probe/probe_core.py` - Probe desabilitada
