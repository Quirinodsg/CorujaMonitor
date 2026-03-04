# 🚀 Instruções: Reiniciar Probe AGORA

## ⚠️ AÇÃO NECESSÁRIA

A probe está rodando com configuração antiga. Você precisa reiniciá-la manualmente.

## 📋 Passo a Passo (2 minutos)

### Passo 1: Encontrar a Janela da Probe

Procure uma janela de terminal/cmd/PowerShell que mostra logs como:
```
ERROR - Error sending heartbeat: [SSL: WRONG_VERSION_NUMBER]
```

### Passo 2: Parar a Probe

**Na janela da probe, pressione:**
```
Ctrl + C
```

Aguarde até ver:
```
Coruja Probe stopped
```

### Passo 3: Verificar Configuração

No mesmo terminal, execute:
```bash
type probe_config.json
```

**Deve mostrar:**
```json
{
  "api_url": "http://localhost:8000",
  ...
}
```

✅ Se mostrar `http://` → Está correto, prossiga
❌ Se mostrar `https://` → Edite o arquivo e mude para `http://`

### Passo 4: Iniciar Probe Atualizada

No mesmo terminal:
```bash
python probe_core.py
```

### Passo 5: Verificar Logs

Você deve ver:
```
INFO - Coruja Probe started
INFO - Initialized 10 collectors
INFO - Sending heartbeat to API
```

**Aguarde 1 minuto e veja:**
```
INFO - Sent 112 metrics successfully
```

✅ **SEM** erro SSL!

### Passo 6: Aguardar Coleta Docker

Aguarde mais 1-2 minutos. Você verá:
```
INFO - Coletadas X métricas Docker
```

### Passo 7: Verificar Frontend

1. Acesse http://localhost:3000
2. Vá em **Servidores** → Selecione servidor
3. Pressione **F5** para recarregar
4. Sensor Docker deve mostrar dados

## 🎯 Resultado Esperado

### Logs da Probe (Correto)
```
2026-02-19 15:40:00,000 - __main__ - INFO - Coruja Probe started
2026-02-19 15:40:00,001 - __main__ - INFO - Initialized 10 collectors
2026-02-19 15:40:00,002 - __main__ - INFO - Sending heartbeat to API
2026-02-19 15:41:00,000 - __main__ - DEBUG - Sending 112 metrics
2026-02-19 15:41:00,001 - __main__ - INFO - Sent 112 metrics successfully
2026-02-19 15:41:00,002 - collectors.docker_collector - INFO - Coletadas 15 métricas Docker
```

### Frontend (Correto)
```
Sensor: Docker Containers Total
Valor: 6 containers
Status: OK ●
Atualizado: 19/02/2026 15:41:30
```

## ❌ Se Ainda Houver Erro SSL

Se após reiniciar ainda aparecer:
```
ERROR - [SSL: WRONG_VERSION_NUMBER]
```

**Faça:**

1. **Pare a probe** (Ctrl+C)

2. **Edite o arquivo de configuração:**
   ```bash
   notepad probe_config.json
   ```

3. **Mude esta linha:**
   ```json
   "api_url": "https://localhost:8000",
   ```
   
   **Para:**
   ```json
   "api_url": "http://localhost:8000",
   ```

4. **Salve** (Ctrl+S) e **feche** o Notepad

5. **Inicie novamente:**
   ```bash
   python probe_core.py
   ```

## 🔍 Verificação Rápida

### Comando 1: Ver se probe está rodando
```powershell
Get-Process python
```

### Comando 2: Ver últimos logs
```powershell
Get-Content probe.log -Tail 10
```

### Comando 3: Verificar configuração
```bash
type probe_config.json | findstr api_url
```

Deve mostrar: `"api_url": "http://localhost:8000"`

## ⏱️ Timeline

```
00:00 - Parar probe (Ctrl+C)
00:10 - Verificar config
00:20 - Iniciar probe
00:30 - Ver logs (sem erro SSL)
01:30 - Primeira coleta de métricas
02:30 - Coleta Docker
03:00 - Recarregar frontend
03:10 - Sensor mostra dados ✅
```

## 📞 Checklist Final

- [ ] Encontrei a janela da probe
- [ ] Parei com Ctrl+C
- [ ] Verifiquei probe_config.json (http://)
- [ ] Iniciei com python probe_core.py
- [ ] Vi "Coruja Probe started" nos logs
- [ ] Vi "Sent X metrics successfully"
- [ ] NÃO vi erro SSL
- [ ] Aguardei 2 minutos
- [ ] Recarreguei frontend (F5)
- [ ] Sensor Docker mostra dados

## 🎉 Sucesso!

Quando tudo estiver funcionando:
- ✅ Probe conecta à API (HTTP)
- ✅ Métricas são enviadas
- ✅ Docker é coletado
- ✅ Sensor mostra dados
- ✅ Sem erros SSL

---

**AÇÃO IMEDIATA:** Vá até a janela da probe e pressione Ctrl+C
**TEMPO TOTAL:** 2-3 minutos
**DIFICULDADE:** Fácil
