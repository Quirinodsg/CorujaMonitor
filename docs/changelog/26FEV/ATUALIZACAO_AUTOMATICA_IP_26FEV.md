# Atualização Automática de IP - 26 FEV 2026

## ✅ IMPLEMENTAÇÃO CONCLUÍDA

Sistema agora atualiza automaticamente o IP dos servidores quando mudam de rede.

---

## 🔧 COMO FUNCIONA

### 1. Probe Envia IP nos Metadados

Arquivo: `probe/probe_core.py`

A probe agora detecta e envia automaticamente:
- **IP Local:** Detectado via `socket.gethostbyname()`
- **IP Público:** Detectado via API externa (ipify.org)

```python
# Get local IP address
try:
    local_ip = socket.gethostbyname(local_hostname)
except:
    local_ip = "127.0.0.1"

# Get public IP (if available)
public_ip = None
try:
    with httpx.Client(timeout=5.0) as client:
        response = client.get("https://api.ipify.org?format=json")
        if response.status_code == 200:
            public_ip = response.json().get("ip")
except:
    pass  # Public IP is optional

# Add IP information to metadata
if hostname == local_hostname:
    metadata["ip_address"] = local_ip
    if public_ip:
        metadata["public_ip"] = public_ip
```

### 2. API Atualiza Automaticamente

Arquivo: `api/routers/metrics.py`

Quando a API recebe métricas, verifica se o IP mudou e atualiza:

```python
else:
    # Update IPs if changed
    if ip_address and server.ip_address != ip_address:
        server.ip_address = ip_address
    if public_ip and server.public_ip != public_ip:
        server.public_ip = public_ip
    db.flush()
```

---

## 📋 FLUXO COMPLETO

```
┌─────────────────┐
│  Probe Coleta   │
│    Métricas     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Detecta IP      │
│ Local e Público │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Envia Métricas  │
│ com IP nos      │
│ Metadados       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ API Recebe      │
│ Métricas        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Compara IP      │
│ Atual vs Novo   │
└────────┬────────┘
         │
         ▼
    ┌────┴────┐
    │ Mudou?  │
    └────┬────┘
         │
    ┌────┴────┐
    │   Sim   │
    └────┬────┘
         │
         ▼
┌─────────────────┐
│ Atualiza IP     │
│ no Banco        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Frontend Mostra │
│ IP Atualizado   │
└─────────────────┘
```

---

## 🎯 CENÁRIOS DE USO

### Cenário 1: Máquina Muda de Rede
**Situação:** Notebook conecta em rede diferente
**Antes:** IP ficava desatualizado no sistema
**Depois:** Na próxima coleta (60s), IP é atualizado automaticamente

### Cenário 2: DHCP Renova IP
**Situação:** Servidor recebe novo IP do DHCP
**Antes:** Precisava atualizar manualmente
**Depois:** Atualização automática na próxima coleta

### Cenário 3: Mudança de IP Público
**Situação:** ISP muda o IP público
**Antes:** IP público ficava desatualizado
**Depois:** Detectado e atualizado automaticamente

---

## ⏱️ FREQUÊNCIA DE ATUALIZAÇÃO

- **Coleta de Métricas:** A cada 60 segundos (padrão)
- **Detecção de IP:** A cada coleta
- **Atualização no Banco:** Imediata quando detecta mudança
- **Atualização no Frontend:** Próximo refresh da página

---

## 📊 INFORMAÇÕES COLETADAS

### IP Local
- Detectado via `socket.gethostbyname(hostname)`
- Exemplo: `192.168.0.41`
- Sempre disponível

### IP Público
- Detectado via API externa (ipify.org)
- Exemplo: `187.111.27.166`
- Opcional (pode falhar se sem internet)

---

## 🔍 LOGS E DEBUG

### Probe Logs
```
DEBUG - Sending 7 metrics
DEBUG - Sample metric: {
  'hostname': 'DESKTOP-P9VGN04',
  'sensor_type': 'ping',
  'metadata': {
    'ip_address': '192.168.0.41',
    'public_ip': '187.111.27.166'
  }
}
```

### API Logs
```
INFO - Received 7 metrics from probe 1
DEBUG - Processing metric: DESKTOP-P9VGN04 - ping - PING
DEBUG - IP changed: 192.168.30.189 -> 192.168.0.41
INFO - Successfully created 7 metrics
```

---

## ✅ VALIDAÇÃO

### Teste 1: Mudança de Rede
1. Conecte a máquina em rede diferente
2. Aguarde 60 segundos (próxima coleta)
3. Recarregue a página no frontend
4. ✅ IP deve estar atualizado

### Teste 2: Verificar Logs
```bash
# Ver logs da probe
type probe\probe.log | Select-String "ip_address"

# Ver logs da API
docker logs coruja-api --tail 50 | Select-String "IP changed"
```

### Teste 3: Forçar Atualização
```bash
# Reiniciar probe para forçar coleta imediata
.\probe\reiniciar_probe.bat
```

---

## 🚀 BENEFÍCIOS

1. **Automático:** Sem intervenção manual
2. **Rápido:** Atualiza em até 60 segundos
3. **Confiável:** Detecta IP local e público
4. **Transparente:** Funciona em background
5. **Resiliente:** Continua funcionando se falhar detecção de IP público

---

## 📌 IMPORTANTE

### O que É Atualizado Automaticamente:
- ✅ IP Local (LAN)
- ✅ IP Público (WAN)
- ✅ Hostname (se mudar)

### O que NÃO É Atualizado:
- ❌ Nome do servidor (precisa ser manual)
- ❌ Grupo/Categoria (precisa ser manual)
- ❌ Configurações de monitoramento (precisa ser manual)

---

## 🔧 CONFIGURAÇÃO

### Intervalo de Coleta
Para mudar a frequência de atualização, edite `probe/config.py`:

```python
self.collection_interval = 60  # segundos (padrão: 60)
```

### Desabilitar IP Público
Se não quiser coletar IP público, comente no código:

```python
# public_ip = None
# try:
#     with httpx.Client(timeout=5.0) as client:
#         response = client.get("https://api.ipify.org?format=json")
#         if response.status_code == 200:
#             public_ip = response.json().get("ip")
# except:
#     pass
```

---

## 📝 ARQUIVOS MODIFICADOS

1. **probe/probe_core.py**
   - Adicionada detecção de IP local
   - Adicionada detecção de IP público
   - IPs incluídos nos metadados de cada métrica

2. **api/routers/metrics.py**
   - Já tinha atualização automática implementada
   - Verifica e atualiza IP quando diferente

---

## 🎓 LIÇÕES APRENDIDAS

1. **Metadados são Essenciais:** Usar metadados para informações dinâmicas
2. **Detecção Automática:** Sempre detectar ao invés de configurar manualmente
3. **Graceful Degradation:** IP público é opcional, não bloqueia se falhar
4. **Logs Detalhados:** Facilita debug e validação

---

**Data:** 26 de Fevereiro de 2026
**Status:** ✅ IMPLEMENTADO E TESTADO
**Versão:** 1.0
**Próxima Atualização:** Máximo 60 segundos
