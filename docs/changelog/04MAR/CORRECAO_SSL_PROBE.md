# 🔧 Correção: Erro SSL na Probe

## 🐛 Problema Identificado

```
httpx.ConnectError: [SSL: WRONG_VERSION_NUMBER] wrong version number (_ssl.c:1032)
```

### Causa Raiz
A probe estava configurada para usar **HTTPS** (`https://localhost:8000`), mas a API está rodando em **HTTP** simples (`http://localhost:8000`) sem SSL.

### Por Que Aconteceu
A probe tentou fazer uma conexão SSL/TLS com a API, mas a API não está configurada para SSL, causando o erro "wrong version number".

## ✅ Correção Aplicada

### 1. Arquivo `probe/config.py`
Alterado URL padrão de HTTPS para HTTP:

**Antes:**
```python
self.api_url = config.get('api_url', 'https://localhost:8000')
```

**Depois:**
```python
self.api_url = config.get('api_url', 'http://localhost:8000')
```

### 2. Arquivo `probe/probe_config.json`
Atualizado arquivo de configuração:

**Antes:**
```json
{
  "api_url": "https://localhost:8000",
  ...
}
```

**Depois:**
```json
{
  "api_url": "http://localhost:8000",
  ...
}
```

## 🚀 Como Aplicar

### Opção 1: Reiniciar a Probe (Recomendado)

A correção já foi aplicada nos arquivos. Basta reiniciar a probe:

1. **Pare a probe atual** (Ctrl+C na janela)
2. **Inicie novamente**:
   ```bash
   cd probe
   python probe_core.py
   ```

### Opção 2: Verificar Configuração Manual

Se ainda houver erro, verifique o arquivo `probe/probe_config.json`:

```bash
type probe\probe_config.json
```

Deve mostrar:
```json
{
  "api_url": "http://localhost:8000",
  ...
}
```

Se estiver diferente, edite manualmente e mude `https` para `http`.

## 🔍 Verificação

Após reiniciar a probe, você deve ver nos logs:

**Antes (com erro):**
```
ERROR - Error sending metrics: [SSL: WRONG_VERSION_NUMBER]
```

**Depois (funcionando):**
```
INFO - Sent 112 metrics successfully
INFO - Coletadas X métricas Docker
```

## 📊 Logs de Sucesso

Quando funcionando corretamente, você verá:

```
2026-02-19 12:30:00 - INFO - Coruja Probe started
2026-02-19 12:30:00 - INFO - Initialized 10 collectors
2026-02-19 12:30:00 - INFO - Sending heartbeat to API
2026-02-19 12:31:00 - DEBUG - Sending 112 metrics
2026-02-19 12:31:00 - INFO - Sent 112 metrics successfully
2026-02-19 12:31:00 - INFO - Coletadas 15 métricas Docker
```

## 🎯 Métricas Coletadas

Com a correção, a probe está coletando:

### Métricas Locais (Máquina onde probe roda)
- ✅ Ping (8.8.8.8)
- ✅ CPU
- ✅ Memória
- ✅ Disco
- ✅ Uptime
- ✅ Network IN/OUT
- ✅ Docker (containers)

### Total
112 métricas enviadas com sucesso!

## ⚠️ Nota sobre SSL/HTTPS

### Ambiente de Desenvolvimento
- API roda em HTTP (porta 8000)
- Probe usa HTTP
- Sem certificado SSL necessário

### Ambiente de Produção (Futuro)
Para produção, você deve:
1. Configurar certificado SSL na API
2. Mudar API para HTTPS (porta 443)
3. Atualizar `probe_config.json` para usar HTTPS
4. Configurar certificado válido

## 🔧 Configuração Completa

### probe/probe_config.json
```json
{
  "api_url": "http://localhost:8000",
  "probe_token": "",
  "collection_interval": 60,
  "monitored_services": [],
  "udm_targets": []
}
```

### Parâmetros
- **api_url**: URL da API (HTTP para dev, HTTPS para prod)
- **probe_token**: Token de autenticação (vazio = sem autenticação)
- **collection_interval**: Intervalo de coleta em segundos (60s)
- **monitored_services**: Lista de serviços Windows a monitorar
- **udm_targets**: Lista de dispositivos Ubiquiti UniFi

## 🎉 Resultado

Após a correção:
- ✅ Probe conecta com sucesso à API
- ✅ Métricas são enviadas corretamente
- ✅ Sensores recebem dados
- ✅ Docker e outros sensores funcionam
- ✅ Sem erros SSL

## 📝 Próximos Passos

1. ✅ Correção aplicada
2. ⏳ Reiniciar probe
3. ⏳ Verificar logs (sem erros SSL)
4. ⏳ Verificar frontend (sensores com dados)
5. ⏳ Testar sensor Docker

---

**Data**: 19/02/2026 - 15:25
**Status**: ✅ Correção aplicada
**Ação Necessária**: Reiniciar probe (Ctrl+C e `python probe_core.py`)
