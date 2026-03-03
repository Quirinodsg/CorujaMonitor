# 🔄 Guia Rápido: Reiniciar Probe com Suporte Docker

## ✅ O Que Foi Feito

1. ✅ Criado coletor Docker (`probe/collectors/docker_collector.py`)
2. ✅ Atualizado probe_core.py para incluir o coletor
3. ✅ Criado script de inicialização (`probe/start_probe.bat`)

## 🚀 Como Reiniciar a Probe

### Passo 1: Verificar se Probe Está Rodando

Abra PowerShell e execute:
```powershell
Get-Process python -ErrorAction SilentlyContinue
```

Se aparecer algum processo Python, pode ser a probe rodando.

### Passo 2: Parar Probe Atual (se estiver rodando)

**Opção A**: Se você tem uma janela de terminal com a probe rodando:
- Pressione `Ctrl + C` na janela
- Ou feche a janela

**Opção B**: Se não sabe onde está rodando:
```powershell
# Parar todos os processos Python (cuidado!)
Stop-Process -Name python -Force
```

### Passo 3: Iniciar Probe Atualizada

**Opção A - Usando o script (Recomendado)**:
```bash
cd probe
start_probe.bat
```

**Opção B - Manualmente**:
```bash
cd probe
python probe_core.py
```

### Passo 4: Verificar Logs

Você deve ver no terminal:
```
INFO - Initialized 10 collectors
INFO - Coruja Probe started
INFO - Coletadas X métricas Docker
```

Se Docker não estiver disponível, verá:
```
WARNING - Docker não está disponível ou não está rodando
```

## 🐳 Verificar Docker Desktop

Antes de iniciar a probe, certifique-se que Docker Desktop está rodando:

1. Abra Docker Desktop
2. Aguarde até ver "Docker Desktop is running"
3. Teste no terminal:
   ```bash
   docker version
   docker ps
   ```

## ⏱️ Aguardar Coleta

Após iniciar a probe:
1. Aguarde 1-2 minutos
2. A probe coleta métricas a cada 60 segundos
3. Recarregue o frontend (F5)
4. O sensor Docker deve mostrar dados

## 🔍 Verificar se Funcionou

### No Terminal da Probe
Deve aparecer periodicamente:
```
INFO - Coletadas X métricas Docker
INFO - Sent X metrics to API
```

### No Frontend
1. Acesse http://localhost:3000
2. Vá em Servidores → Selecione servidor
3. O sensor Docker deve mostrar:
   - Valor numérico (ex: "6 containers")
   - Status (OK/Warning/Critical)
   - Timestamp atualizado

## 🐛 Se Não Funcionar

### 1. Docker não está rodando
```bash
# Verificar Docker
docker version

# Se der erro, abra Docker Desktop e aguarde inicializar
```

### 2. Probe não está coletando
```bash
# Ver logs da probe
cd probe
type probe.log | findstr /i "docker"
```

### 3. Erro de permissão
Execute o terminal como Administrador:
- Clique com botão direito no PowerShell
- Selecione "Executar como Administrador"
- Execute novamente: `cd probe` e `python probe_core.py`

## 📊 Comandos Úteis

### Ver processos Python rodando
```powershell
Get-Process python
```

### Ver últimas linhas do log
```powershell
Get-Content probe/probe.log -Tail 20
```

### Testar Docker
```bash
docker ps
docker stats --no-stream
```

### Parar probe
```powershell
# Na janela da probe: Ctrl + C
# Ou forçar:
Stop-Process -Name python -Force
```

## ✅ Checklist

- [ ] Docker Desktop está rodando
- [ ] `docker version` funciona no terminal
- [ ] `docker ps` mostra containers
- [ ] Probe antiga foi parada
- [ ] Probe nova foi iniciada com `python probe_core.py`
- [ ] Logs mostram "Initialized 10 collectors"
- [ ] Aguardou 1-2 minutos
- [ ] Recarregou frontend (F5)
- [ ] Sensor Docker mostra dados

## 🎯 Resultado Esperado

Após seguir os passos, você verá no frontend:

```
Sensor: Docker Containers Total
Valor: 6 containers
Status: OK ●
Atualizado: 19/02/2026 15:05:30
```

Em vez de:
```
Sensor: Docker
Aguardando dados...
```

---

**Tempo estimado**: 2-3 minutos
**Dificuldade**: Fácil
**Requer**: Docker Desktop rodando + Python
