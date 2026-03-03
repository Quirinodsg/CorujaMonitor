# ✅ Correção: Token da Probe

## 🎉 Progresso!

A probe reiniciou com sucesso e agora está usando **HTTP** (sem erro SSL)!

### ✅ O Que Funcionou
```
✅ Probe reiniciada
✅ Configuração HTTP carregada
✅ Conexão com API estabelecida
✅ 28 métricas coletadas
```

## ❌ Novo Problema Identificado

**Erro:** `401 Unauthorized - Invalid probe token`

**Logs:**
```
ERROR - Failed to send metrics: 401 - {"detail":"Invalid probe token"}
```

### Causa
O arquivo `probe_config.json` estava com `probe_token` vazio:
```json
{
  "probe_token": ""
}
```

A API requer um token válido para autenticar a probe.

## ✅ Solução Aplicada

### 1. Token Encontrado
Busquei no banco de dados e encontrei a probe cadastrada:
```
ID: 1
Nome: Quirino-Matriz
Token: W_YxHARNTlE3G8bxoXhWt0FknTPysGnKFX_visaP_G4
```

### 2. Configuração Atualizada
Atualizei `probe/probe_config.json`:
```json
{
  "api_url": "http://localhost:8000",
  "probe_token": "W_YxHARNTlE3G8bxoXhWt0FknTPysGnKFX_visaP_G4",
  "collection_interval": 60,
  "monitored_services": [],
  "udm_targets": []
}
```

### 3. Script Criado
Criei `probe/aplicar_token.bat` para reiniciar com o token.

## 🚀 Como Aplicar

### Execute o script:
```bash
cd probe
aplicar_token.bat
```

Ou manualmente:
1. Vá na janela "Coruja Probe"
2. Pressione Ctrl+C
3. Execute: `python probe_core.py`

## ✅ Verificação

### Logs CORRETOS (após aplicar token):
```
INFO - Coruja Probe started
INFO - Initialized 10 collectors
INFO - Sending heartbeat to API
INFO - Sent 28 metrics successfully
INFO - Coletadas X métricas Docker
```

### Logs ERRADOS (ainda sem token):
```
ERROR - Failed to send metrics: 401 - {"detail":"Invalid probe token"}
```

## 📊 Métricas Coletadas

A probe já está coletando:
```
28 métricas incluindo:
- Ping (8.8.8.8): 262ms (warning)
- CPU
- Memória
- Disco
- Uptime
- Network IN/OUT
- Docker (se disponível)
```

## 🎯 Resultado Esperado

Após aplicar o token:

### 1. Logs da Probe
```
2026-02-19 13:35:00 - INFO - Sent 28 metrics successfully
2026-02-19 13:35:00 - INFO - Coletadas 15 métricas Docker
```

### 2. Frontend
```
Sensor: Docker Containers Total
Valor: 6 containers
Status: OK ●
Atualizado: 19/02/2026 13:35:30
```

## 📋 Checklist

- [x] Probe reiniciada (HTTP funcionando)
- [x] Token encontrado no banco
- [x] probe_config.json atualizado
- [x] Script aplicar_token.bat criado
- [ ] **Probe reiniciada com token** ← EXECUTE aplicar_token.bat
- [ ] Métricas enviadas com sucesso
- [ ] Sensor Docker mostrando dados

## 🔍 Troubleshooting

### Problema: Ainda mostra erro 401

**Solução:**
```bash
# Verifique se o token está no arquivo
type probe\probe_config.json | findstr probe_token

# Deve mostrar:
"probe_token": "W_YxHARNTlE3G8bxoXhWt0FknTPysGnKFX_visaP_G4"

# Se estiver vazio, edite manualmente:
notepad probe\probe_config.json
```

### Problema: Token diferente

Se você tiver outra probe cadastrada, busque o token correto:
```bash
docker exec coruja-postgres psql -U coruja -d coruja_monitor -c "SELECT id, name, token FROM probes;"
```

## 📁 Arquivos Atualizados

1. ✅ `probe/probe_config.json` - Token adicionado
2. ✅ `probe/aplicar_token.bat` - Script de aplicação
3. ✅ `CORRECAO_TOKEN_PROBE.md` - Esta documentação

## 🎉 Resumo

### Antes
```
❌ Erro SSL (HTTPS)
❌ Probe não conectava
❌ Sem métricas
```

### Agora
```
✅ HTTP funcionando
✅ Probe conecta à API
✅ 28 métricas coletadas
⏳ Aguardando token para enviar
```

### Após Aplicar Token
```
✅ HTTP funcionando
✅ Probe autenticada
✅ Métricas enviadas
✅ Sensor Docker funcionando
```

---

**AÇÃO FINAL:** Execute `probe\aplicar_token.bat` AGORA!
**TEMPO:** 30 segundos
**RESULTADO:** Sistema 100% funcional
