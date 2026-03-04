# ⚡ Comandos Rápidos - Copiar e Colar

## 🚀 Reiniciar Probe (AGORA)

### 1. Parar Probe Atual
```powershell
# Encontre a janela da probe e pressione: Ctrl + C
```

### 2. Verificar Configuração
```bash
cd probe
type probe_config.json
```

**Deve mostrar:** `"api_url": "http://localhost:8000"`

### 3. Iniciar Probe
```bash
python probe_core.py
```

### 4. Verificar Logs (Nova Janela)
```powershell
Get-Content probe\probe.log -Tail 20 -Wait
```

## 🔍 Verificações

### Ver se Probe Está Rodando
```powershell
Get-Process python
```

### Ver Últimos Logs
```powershell
Get-Content probe\probe.log -Tail 30
```

### Buscar Erro SSL
```powershell
Get-Content probe\probe.log | Select-String "SSL"
```

### Buscar Métricas Docker
```powershell
Get-Content probe\probe.log | Select-String "docker"
```

### Buscar Envio de Métricas
```powershell
Get-Content probe\probe.log | Select-String "Sent.*metrics"
```

## 🐳 Docker

### Ver Containers Rodando
```bash
docker ps
```

### Ver Todos os Containers
```bash
docker ps -a
```

### Testar Docker
```bash
docker version
```

## 🌐 API

### Testar API
```bash
curl http://localhost:8000/docs
```

### Ver Containers do Sistema
```bash
docker ps --filter "name=coruja"
```

### Ver Logs da API
```bash
docker logs coruja-api --tail 50
```

## 📊 Frontend

### Acessar Sistema
```
http://localhost:3000
```

### Login
```
Email: admin@coruja.com
Senha: admin123
```

## 🔧 Troubleshooting

### Parar Todos os Python
```powershell
Get-Process python | Stop-Process -Force
```

### Editar Configuração
```bash
notepad probe\probe_config.json
```

### Reiniciar Containers Docker
```bash
docker-compose restart
```

### Ver Logs de Todos os Containers
```bash
docker-compose logs --tail 50
```

## ✅ Sequência Completa (Copie Tudo)

```bash
# 1. Vá para pasta probe
cd probe

# 2. Pare a probe (Ctrl+C na janela dela)

# 3. Verifique configuração
type probe_config.json

# 4. Inicie probe
python probe_core.py

# 5. Em outra janela, monitore logs
Get-Content probe.log -Tail 20 -Wait
```

## 🎯 Resultado Esperado

Após executar, você deve ver:
```
INFO - Coruja Probe started
INFO - Initialized 10 collectors
INFO - Sending heartbeat to API
INFO - Sent 112 metrics successfully
```

**SEM** erro SSL!

## ⏱️ Timeline

```
00:00 - Parar probe (Ctrl+C)
00:10 - Verificar config
00:20 - Iniciar probe
00:30 - Ver "Probe started"
01:30 - Ver "Sent metrics"
02:30 - Ver "Docker coletado"
03:00 - Recarregar frontend (F5)
03:10 - Sensor mostra dados ✅
```

---

**AÇÃO:** Copie os comandos acima e execute na ordem
**TEMPO:** 2-3 minutos
**RESULTADO:** Sensor Docker funcionando
