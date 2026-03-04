# 🔍 Diagnóstico: Sensor Docker "Aguardando Dados"

## 📊 Análise da Situação

Você adicionou o sensor Docker novamente, mas ele ainda mostra "Aguardando dados". Vou analisar o que pode estar acontecendo:

### ❌ Problema Identificado

A probe **NÃO foi reiniciada** após as correções. Os logs mostram que ela ainda está tentando usar HTTPS (SSL), o que significa que está rodando com a configuração antiga.

**Evidência nos logs:**
```
2026-02-19 12:32:07 - ERROR - Error sending heartbeat: [SSL: WRONG_VERSION_NUMBER]
```

Isso indica que:
1. ❌ Probe não foi reiniciada
2. ❌ Ainda usa configuração antiga (HTTPS)
3. ❌ Não consegue enviar métricas para API
4. ❌ DockerCollector não está ativo
5. ❌ Sensor não recebe dados

## 🔧 Solução: Reiniciar Probe Corretamente

### Passo 1: Parar Probe Atual

**Opção A - Se você tem a janela aberta:**
1. Vá na janela onde a probe está rodando
2. Pressione `Ctrl + C`
3. Aguarde a probe parar

**Opção B - Forçar parada:**
```powershell
# Parar todos os processos Python
taskkill /F /IM python.exe
```

**Opção C - Usar script (Recomendado):**
```bash
cd probe
reiniciar_probe.bat
```

### Passo 2: Verificar Configuração

Antes de iniciar, verifique se a configuração está correta:

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

Se mostrar `https://`, edite manualmente e mude para `http://`.

### Passo 3: Iniciar Probe Atualizada

```bash
cd probe
python probe_core.py
```

### Passo 4: Verificar Logs

Você deve ver:
```
INFO - Coruja Probe started
INFO - Initialized 10 collectors
INFO - Sending heartbeat to API
INFO - Sent 112 metrics successfully
```

**NÃO deve aparecer:**
```
ERROR - [SSL: WRONG_VERSION_NUMBER]
```

## 🔍 Checklist de Verificação

### 1. Probe Parada
```powershell
# Verificar se há Python rodando
Get-Process python -ErrorAction SilentlyContinue
```

Se aparecer algum processo, pare-o.

### 2. Configuração Correta
```bash
type probe\probe_config.json | findstr "api_url"
```

Deve mostrar: `"api_url": "http://localhost:8000"`

### 3. Probe Iniciada
```bash
cd probe
python probe_core.py
```

### 4. Logs Sem Erro SSL
```bash
# Ver últimas linhas do log
Get-Content probe\probe.log -Tail 20
```

Não deve ter erro SSL.

### 5. Métricas Sendo Enviadas
Aguarde 1-2 minutos e veja nos logs:
```
INFO - Sent X metrics successfully
```

### 6. Docker Coletado
```bash
Get-Content probe\probe.log | Select-String -Pattern "docker|Docker"
```

Deve mostrar:
```
INFO - Coletadas X métricas Docker
```

### 7. Frontend Atualizado
1. Acesse http://localhost:3000
2. Vá em Servidores → Selecione servidor
3. Recarregue página (F5)
4. Sensor Docker deve mostrar dados

## 🐛 Troubleshooting

### Problema 1: Probe não para

**Solução:**
```powershell
# Forçar parada de todos os Python
taskkill /F /IM python.exe

# Ou específico
Get-Process python | Stop-Process -Force
```

### Problema 2: Ainda mostra erro SSL

**Causa:** Configuração não foi atualizada

**Solução:**
1. Pare a probe
2. Edite `probe\probe_config.json`
3. Mude `https://` para `http://`
4. Salve o arquivo
5. Inicie a probe novamente

### Problema 3: Docker não coleta

**Causa:** Docker Desktop não está rodando

**Solução:**
1. Abra Docker Desktop
2. Aguarde inicializar
3. Teste: `docker ps`
4. Reinicie a probe

### Problema 4: Métricas não são enviadas

**Causa:** API não está rodando

**Solução:**
```bash
# Verificar se API está rodando
docker ps | findstr coruja-api

# Se não estiver, inicie
docker-compose up -d
```

### Problema 5: Sensor ainda "Aguardando dados"

**Possíveis causas:**
1. Probe não reiniciada → Reinicie
2. Erro SSL → Corrija configuração
3. Docker não rodando → Inicie Docker Desktop
4. API não rodando → Inicie containers
5. Nome do sensor diferente → Verifique nome exato

## 📊 Fluxo Correto

```
1. PARAR PROBE
   ↓
   Ctrl+C ou taskkill
   
2. VERIFICAR CONFIG
   ↓
   probe_config.json deve ter http://
   
3. INICIAR PROBE
   ↓
   python probe_core.py
   
4. AGUARDAR COLETA
   ↓
   1-2 minutos
   
5. VERIFICAR LOGS
   ↓
   Sem erro SSL
   "Sent X metrics successfully"
   
6. RECARREGAR FRONTEND
   ↓
   F5 na página
   
7. VERIFICAR SENSOR
   ↓
   Deve mostrar dados
```

## 🎯 Comandos Rápidos

### Parar Probe
```powershell
taskkill /F /IM python.exe
```

### Verificar Config
```bash
type probe\probe_config.json
```

### Iniciar Probe
```bash
cd probe
python probe_core.py
```

### Ver Logs
```bash
Get-Content probe\probe.log -Tail 20 -Wait
```

### Testar Docker
```bash
docker ps
docker version
```

### Verificar API
```bash
curl http://localhost:8000/docs
```

## ✅ Resultado Esperado

Após seguir os passos:

### Logs da Probe
```
2026-02-19 15:40:00 - INFO - Coruja Probe started
2026-02-19 15:40:00 - INFO - Initialized 10 collectors
2026-02-19 15:40:00 - INFO - Sending heartbeat to API
2026-02-19 15:41:00 - INFO - Coletadas 15 métricas Docker
2026-02-19 15:41:00 - DEBUG - Sending 112 metrics
2026-02-19 15:41:00 - INFO - Sent 112 metrics successfully
```

### Frontend
```
Sensor: Docker Containers Total
Valor: 6 containers
Status: OK ●
Atualizado: 19/02/2026 15:41:30
```

## 📝 Resumo

### O Que Aconteceu
1. ✅ Correções foram aplicadas nos arquivos
2. ❌ Probe NÃO foi reiniciada
3. ❌ Probe ainda usa configuração antiga (HTTPS)
4. ❌ Erro SSL impede envio de métricas
5. ❌ Sensor não recebe dados

### O Que Fazer
1. **PARAR** a probe atual (Ctrl+C ou taskkill)
2. **VERIFICAR** probe_config.json (deve ter http://)
3. **INICIAR** probe novamente (python probe_core.py)
4. **AGUARDAR** 1-2 minutos
5. **RECARREGAR** frontend (F5)
6. **VERIFICAR** sensor Docker

### Tempo Estimado
- Parar probe: 10 segundos
- Verificar config: 10 segundos
- Iniciar probe: 10 segundos
- Aguardar coleta: 1-2 minutos
- Total: ~2-3 minutos

---

**Data**: 19/02/2026 - 15:35
**Status**: ⚠️ Probe precisa ser reiniciada
**Ação Crítica**: Parar e reiniciar probe com nova configuração
