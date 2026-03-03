# 🔍 Auto-Descoberta de IP Implementada - 02 Março 2026

## ✅ Problema Resolvido

A probe estava falhando quando o IP do servidor mudava, causando timeout de conexão.

## 🚀 Solução Implementada

### 1. Auto-Descoberta no Startup

A probe agora testa automaticamente múltiplos endereços ao iniciar:

```python
# Tenta em ordem:
1. localhost:8000
2. 127.0.0.1:8000
3. IP local da máquina:8000
```

### 2. Reconexão Automática

Quando detecta falha de conexão, a probe:
- Detecta timeout/erro de conexão
- Recarrega configuração
- Testa novamente todos os endereços
- Atualiza automaticamente o arquivo `probe_config.json`

### 3. Arquivos Modificados

**probe/config.py**
- Adicionado `_test_api_connection()` - testa se API está acessível
- Adicionado `_auto_discover_api()` - busca servidor em múltiplos IPs
- Modificado `load_config()` - testa e auto-descobre na inicialização

**probe/probe_core.py**
- Adicionado `_reconnect_api()` - reconecta quando há falha
- Modificado `_send_metrics()` - detecta erros de conexão e reconecta
- Modificado `_send_heartbeat()` - detecta erros de conexão e reconecta

## 📋 Como Funciona

### Fluxo de Auto-Descoberta

```
1. Probe inicia
   ↓
2. Lê probe_config.json
   ↓
3. Testa URL configurada
   ↓
4. Se falhar → Auto-descobre
   ├─ Testa localhost:8000
   ├─ Testa 127.0.0.1:8000
   └─ Testa IP_LOCAL:8000
   ↓
5. Encontrou? → Atualiza config
   ↓
6. Continua operação normal
```

### Fluxo de Reconexão

```
Durante operação:
   ↓
Envia métricas/heartbeat
   ↓
Timeout/Erro de conexão?
   ↓
SIM → Reconecta
   ├─ Recarrega config
   ├─ Auto-descobre novo IP
   └─ Atualiza config
   ↓
Continua operação
```

## 🧪 Como Testar

### Teste Manual

```powershell
# 1. Parar probe
taskkill /F /IM python.exe

# 2. Editar probe/probe_config.json - colocar IP inválido
{
  "api_url": "http://192.168.999.999:8000",
  ...
}

# 3. Iniciar probe
cd probe
python probe_core.py

# 4. Observar logs - deve auto-descobrir e corrigir
```

### Teste Automatizado

```powershell
.\testar_auto_descoberta.ps1
```

## 📊 Logs Esperados

```
🔍 Procurando configuração em: probe_config.json
✅ Configuração encontrada: probe_config.json
📡 Testando API URL: http://192.168.999.999:8000
⚠️  API não acessível em http://192.168.999.999:8000
🔍 Auto-descobrindo servidor API...
   Tentando: http://localhost:8000
✅ Servidor encontrado em: http://localhost:8000
🔄 Atualizando URL de http://192.168.999.999:8000 para http://localhost:8000
✅ API acessível em http://localhost:8000
```

## 🎯 Benefícios

1. **Zero Configuração Manual** - Probe encontra servidor automaticamente
2. **Resiliente a Mudanças** - Adapta-se quando IP muda
3. **Sem Downtime** - Reconecta automaticamente durante operação
4. **Logs Claros** - Fácil diagnosticar problemas de conexão

## 🔧 Configuração

Não é necessária configuração adicional. O sistema funciona automaticamente.

### Endereços Testados (em ordem)

1. `http://localhost:8000` - Servidor local
2. `http://127.0.0.1:8000` - Loopback
3. `http://{IP_LOCAL}:8000` - IP da máquina

## ⚠️ Notas Importantes

- A probe sempre prefere `localhost` quando disponível
- O arquivo `probe_config.json` é atualizado automaticamente
- Timeout de teste: 3 segundos por endereço
- Reconexão é tentada a cada falha de envio

## 🔄 Próximos Passos

Sistema está pronto para uso. Mudanças de IP serão detectadas e corrigidas automaticamente.

## 📝 Status

✅ Implementado
✅ Testado
✅ Documentado
✅ Pronto para produção
