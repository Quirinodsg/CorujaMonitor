# 🚨 SOLUÇÃO FINAL - Probe e Incidentes

## Diagnóstico Completo

### Problema 1: Probe Errada Rodando
- **Localização**: `C:\Users\andre.quirino\OneDrive - Techbiz Forense Digital Ltda\Desktop\Coruja Monitor\probe\`
- **IP Tentando Conectar**: 192.168.30.189 (ANTIGO)
- **Status**: Falhando ao enviar métricas
- **Impacto**: Sensores não atualizam desde ontem 14:25

### Problema 2: Incidente Não Fecha
- **Incidente**: PING ainda aberto
- **Causa**: Probe não está enviando métricas atualizadas
- **Worker**: Não pode auto-resolver sem métricas novas

### Problema 3: Configuração Correta Não Sendo Usada
- **Diretório Correto**: `C:\Users\andre.quirino\Coruja Monitor\`
- **Config Correta**: `probe/probe_config.json` com IP 192.168.0.41
- **Problema**: Probe errada está rodando

---

## ✅ SOLUÇÃO DEFINITIVA

### Opção 1: Manual (RECOMENDADO)

#### Passo 1: Encontre e Pare a Probe Antiga

1. Abra o Gerenciador de Tarefas (Ctrl+Shift+Esc)
2. Vá para a aba "Detalhes"
3. Encontre todos os processos "python.exe"
4. Clique com botão direito > "Finalizar tarefa" em TODOS
5. Confirme que não há mais processos Python rodando

#### Passo 2: Feche os Incidentes Manualmente

Abra PowerShell neste diretório e execute:

```powershell
docker-compose exec api python fechar_incidentes_resolvidos.py
```

Aguarde a saída mostrar quantos incidentes foram fechados.

#### Passo 3: Reinicie os Serviços

```powershell
docker-compose restart worker
docker-compose restart api
```

Aguarde 10 segundos.

#### Passo 4: Inicie a Probe Correta

```powershell
python probe\probe_core.py
```

Deixe o terminal aberto e monitore os logs.

### Opção 2: Script Automático

Execute este comando único:

```powershell
# Parar tudo
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# Aguardar
Start-Sleep -Seconds 3

# Fechar incidentes
docker-compose exec api python fechar_incidentes_resolvidos.py

# Reiniciar serviços
docker-compose restart worker
docker-compose restart api

# Aguardar
Start-Sleep -Seconds 10

# Iniciar probe
python probe\probe_core.py
```

---

## 📊 Validação (IMPORTANTE)

### 1. Verifique os Logs da Probe

Você DEVE ver:

```
✅ Conectando em: http://192.168.0.41:8000
✅ Coletando métricas...
✅ Sent 372 metrics successfully
✅ Heartbeat sent successfully
```

Você NÃO deve ver:

```
❌ Error sending metrics
❌ Connecting to 192.168.30.189
❌ Connection timeout
```

### 2. Verifique a Interface Web

Acesse: http://192.168.0.41:3000

- **Sensores**: Timestamp deve ser ATUAL (não ontem 14:25)
- **Incidentes**: Deve mostrar "0 Incidentes Abertos"
- **NOC**: Servidor DESKTOP-P9VGN04 deve estar visível e verde

### 3. Aguarde 60 Segundos

A primeira coleta completa leva 60 segundos. Após isso:
- Todos os sensores devem atualizar
- Timestamps devem ser atuais
- Incidentes devem fechar automaticamente

---

## 🔍 Diagnóstico de Problemas

### Probe ainda conecta em 192.168.30.189

**Causa**: Probe errada ainda rodando

**Solução**:
1. Abra Gerenciador de Tarefas
2. Finalize TODOS os processos python.exe
3. Verifique que não há mais nenhum rodando
4. Inicie novamente: `python probe\probe_core.py`

### Sensores não atualizam

**Causa**: Probe não está enviando métricas

**Solução**:
1. Verifique logs da probe
2. Confirme que está conectando em 192.168.0.41:8000
3. Verifique se API está rodando: `docker-compose ps api`
4. Verifique logs da API: `docker-compose logs -f api --tail=50`

### Incidente não fecha

**Causa**: Métricas antigas no banco

**Solução**:
1. Execute: `docker-compose exec api python fechar_incidentes_resolvidos.py`
2. Aguarde probe enviar métricas novas (60 segundos)
3. Worker processará automaticamente

### Worker não processa

**Causa**: Worker não está rodando

**Solução**:
1. Verifique: `docker-compose ps worker`
2. Reinicie: `docker-compose restart worker`
3. Monitore: `docker-compose logs -f worker --tail=50`

---

## 🎯 Checklist Final

Marque cada item após validar:

- [ ] Todos os processos Python antigos foram parados
- [ ] Probe nova está rodando neste diretório
- [ ] Probe conecta em http://192.168.0.41:8000
- [ ] Probe envia métricas com sucesso
- [ ] Sensores mostram timestamp ATUAL
- [ ] Incidentes foram fechados (0 abertos)
- [ ] Servidor aparece no NOC
- [ ] Worker está rodando
- [ ] API está rodando

---

## 📁 Estrutura de Diretórios

### ✅ CORRETO (Use este)
```
C:\Users\andre.quirino\Coruja Monitor\
├── probe\
│   ├── probe_core.py
│   └── probe_config.json (IP: 192.168.0.41)
├── api\
├── frontend\
└── docker-compose.yml
```

### ❌ ERRADO (Não use este)
```
C:\Users\andre.quirino\OneDrive - Techbiz Forense Digital Ltda\Desktop\Coruja Monitor\
└── probe\
    ├── probe_core.py
    └── probe_config.json (IP: 192.168.30.189)
```

---

## 🔄 Fluxo Correto de Atualização

```
1. Probe coleta métricas (a cada 60s)
   ↓
2. Envia para API (http://192.168.0.41:8000)
   ↓
3. API salva no banco com timestamp atual
   ↓
4. Worker verifica sensores (a cada 60s)
   ↓
5. Se sensor OK e incidente aberto:
   → Fecha automaticamente
   → Atualiza timestamp de resolução
   ↓
6. Frontend mostra dados atualizados
```

---

## 🚀 Comandos Rápidos

### Ver processos Python rodando
```powershell
Get-Process python -ErrorAction SilentlyContinue | Select-Object Id, StartTime, Path
```

### Parar todos os processos Python
```powershell
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
```

### Ver última métrica de um sensor
```powershell
docker-compose exec api python -c "from database import SessionLocal; from models import Metric, Sensor; db = SessionLocal(); s = db.query(Sensor).filter(Sensor.sensor_type=='ping').first(); m = db.query(Metric).filter(Metric.sensor_id==s.id).order_by(Metric.timestamp.desc()).first(); print(f'Sensor: {s.name}, Valor: {m.value}, Status: {m.status}, Timestamp: {m.timestamp}')"
```

### Ver incidentes ativos
```powershell
docker-compose exec api python -c "from database import SessionLocal; from models import Incident; db = SessionLocal(); incidents = db.query(Incident).filter(Incident.status.in_(['open','acknowledged'])).all(); print(f'Incidentes ativos: {len(incidents)}'); [print(f'  - ID {i.id}: {i.title} ({i.status})') for i in incidents]"
```

### Reiniciar tudo
```powershell
docker-compose restart
```

---

## 📞 Resumo Executivo

**Problema**: Probe antiga rodando do OneDrive com IP errado, sensores não atualizam, incidente não fecha

**Solução**: Parar probe antiga, iniciar probe correta, fechar incidentes manualmente, aguardar 60s

**Validação**: Sensores com timestamp atual, 0 incidentes abertos, servidor no NOC

**Tempo**: 2-3 minutos + 60 segundos de espera

---

**Status**: Aguardando execução manual

**Próximo Passo**: Pare TODOS os processos Python e inicie a probe correta
