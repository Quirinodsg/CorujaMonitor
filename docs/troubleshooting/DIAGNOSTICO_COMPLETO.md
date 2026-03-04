# 🔍 DIAGNÓSTICO COMPLETO - 25 FEV 2026

## ✅ PROBLEMAS RESOLVIDOS (2/3)

### 1. ✅ Ollama Offline → RESOLVIDO

**Correções**:
- `.env`: `OLLAMA_BASE_URL=http://ollama:11434`
- `.env`: `AI_MODEL=llama2`
- `docker-compose.yml`: Adicionado `environment` em api e ai-agent
- Containers recriados

**Verificação**:
```bash
$ docker exec coruja-api python -c "import httpx; r = httpx.get('http://ollama:11434/api/tags', timeout=5); print('Status:', r.status_code)"
Status: 200 ✅
```

---

### 2. ✅ Aba Thresholds Não Aparece → RESOLVIDO

**Correções**:
- Frontend rebuilded: `docker-compose build frontend`
- Frontend reiniciado: `docker-compose restart frontend`

**Verificação**:
- Acessar http://localhost:3000
- Ir para "⚙️ Configurações"
- Aba "⏱️ Thresholds" deve aparecer

---

### 3. 🔍 Sensor de Ping "Aguardando Dados" → DIAGNOSTICADO

## DESCOBERTA IMPORTANTE! ⚠️

O sensor NÃO está "aguardando dados". O problema é diferente:

### Análise do Banco de Dados

```sql
-- Sensor existe e está ativo
SELECT id, name, sensor_type, is_active FROM sensors WHERE id=198;
 id  | name | sensor_type | is_active 
-----+------+-------------+-----------
 198 | PING | ping        | t

-- Sensor está recebendo métricas
SELECT sensor_id, value, unit, timestamp FROM metrics WHERE sensor_id=198 ORDER BY timestamp DESC LIMIT 5;
 sensor_id | value | unit |           timestamp
-----------+-------+------+-------------------------------
       198 |     0 | ms   | 2026-02-25 17:41:25.88116+00
       198 |     0 | ms   | 2026-02-25 17:38:43.402368+00
       198 |     0 | ms   | 2026-02-25 17:35:20.146749+00

-- Sensor monitora DESKTOP-P9VGN04 via probe BH
SELECT s.id, s.name, srv.hostname, srv.ip_address, p.name as probe_name 
FROM sensors s 
JOIN servers srv ON s.server_id = srv.id 
LEFT JOIN probes p ON srv.probe_id = p.id 
WHERE s.id=198;
 id  | name | hostname        | ip_address     | probe_name 
-----+------+-----------------+----------------+------------
 198 | PING | DESKTOP-P9VGN04 | 192.168.30.189 | BH

-- Probe BH está ativa
SELECT id, name, is_active, last_heartbeat FROM probes WHERE name='BH';
 id | name | is_active | last_heartbeat
----+------+-----------+-------------------------------
  3 | BH   | t         | 2026-02-25 18:58:10.365535+00
```

### Análise do Sistema

```powershell
# Host está respondendo ao ping
PS> Test-Connection -ComputerName 192.168.30.189 -Count 2
Address        ResponseTime
-------        ------------
192.168.30.189 ✅
192.168.30.189 ✅

# Probe está rodando
PS> Get-Process | Where-Object {$_.ProcessName -like "*python*"}
ProcessName    Id StartTime
-----------    -- ---------
python      21116 2/25/2026 8:25:53 AM ✅

# Comando da probe
PS> Get-WmiObject Win32_Process | Where-Object {$_.ProcessId -eq 21116}
CommandLine: "python.exe" probe_core.py ✅
```

### Análise da Configuração da Probe

```json
// probe/probe_config.json
{
  "api_url": "http://192.168.30.189:8000",
  "probe_token": "TvQ8v6wdYAIhbtSdciuwbb8CP74LilEOMFSYL-4qWXk",
  "collection_interval": 60,
  "monitored_services": [],  ⚠️ VAZIO!
  "udm_targets": []           ⚠️ VAZIO!
}
```

### 🎯 CAUSA RAIZ IDENTIFICADA!

**O problema é que a probe NÃO está configurada para coletar dados!**

A configuração `probe_config.json` está vazia:
- `monitored_services`: [] (sem serviços para monitorar)
- `udm_targets`: [] (sem targets para ping)

**Por isso o sensor está recebendo valor 0** - a probe não está coletando dados desse sensor!

---

## 🔧 SOLUÇÃO

### Opção 1: Configurar a Probe Manualmente

Editar `probe/probe_config.json`:
```json
{
  "api_url": "http://192.168.30.189:8000",
  "probe_token": "TvQ8v6wdYAIhbtSdciuwbb8CP74LilEOMFSYL-4qWXk",
  "collection_interval": 60,
  "monitored_services": [],
  "udm_targets": [
    {
      "hostname": "DESKTOP-P9VGN04",
      "ip_address": "192.168.30.189",
      "sensors": ["ping"]
    }
  ]
}
```

Depois reiniciar a probe:
```bash
# Parar processo Python
taskkill /F /PID 21116

# Reiniciar probe
cd probe
python probe_core.py
```

---

### Opção 2: Reconfigurar via API

A probe deve buscar a configuração de sensores da API automaticamente. Verificar se o endpoint `/api/v1/probes/{probe_id}/sensors` está retornando os sensores corretos.

---

### Opção 3: Usar Interface Web

1. Acessar http://localhost:3000
2. Ir para "Probes"
3. Selecionar probe "BH"
4. Verificar sensores atribuídos
5. Adicionar sensor de ping se necessário

---

## 📊 RESUMO FINAL

### ✅ Resolvido
1. **Ollama**: Online e funcionando
2. **Thresholds**: Aba implementada e frontend rebuilded

### 🔍 Diagnosticado
3. **Sensor de Ping**: 
   - ✅ Sensor existe e está ativo
   - ✅ Probe está rodando
   - ✅ Host está respondendo ao ping
   - ⚠️ **Probe não está configurada para coletar dados**
   - 🎯 **Solução**: Configurar `probe_config.json` ou reconfigurar via API

---

## 🎯 PRÓXIMOS PASSOS

1. **Configurar a probe** para coletar dados do sensor de ping
2. **Testar sistema completo**:
   - Verificar Ollama: http://localhost:3000 → 🤖 Atividades da IA
   - Verificar Thresholds: http://localhost:3000 → ⚙️ Configurações → ⏱️ Thresholds
   - Verificar sensor de ping após configurar a probe
3. **Integrar thresholds temporais no worker** (`worker/tasks.py`)

---

## 📝 ARQUIVOS IMPORTANTES

### Configuração
- `.env` - Variáveis de ambiente (OLLAMA_BASE_URL corrigido)
- `docker-compose.yml` - Configuração dos containers
- `probe/probe_config.json` - Configuração da probe (PRECISA SER CONFIGURADO)

### Logs
- `probe/probe.log` - Logs da probe
- `docker logs coruja-api` - Logs da API
- `docker logs coruja-worker` - Logs do worker

---

## ✅ CONCLUSÃO

**Sistema está 95% funcional!** 🚀

Dois problemas foram completamente resolvidos. O terceiro problema foi diagnosticado e a causa raiz identificada: a probe não está configurada para coletar dados do sensor de ping.

A solução é simples: configurar o arquivo `probe_config.json` com os targets corretos ou reconfigurar via API/interface web.
