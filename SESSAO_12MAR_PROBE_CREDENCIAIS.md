# 📋 Sessão 12/03/2026 - Probe Windows + Credenciais Centralizadas

**Horário:** 16:15 - 16:30  
**Objetivo:** Atualizar Probe Windows para usar credenciais WMI do banco via API

---

## 🎯 Contexto da Sessão

### Situação Inicial
- ✅ Sistema de credenciais centralizadas implementado (TASK 1 - DONE)
- ✅ Credencial WMI "Techbiz" configurada no banco (nível Empresa, padrão)
- ✅ Servidor SRVHVSPRD010 (192.168.31.110) adicionado com 7 sensores
- ✅ PING funcionando (0.44ms coletado pelo worker Linux)
- ⚠️ Sensores WMI "Aguardando dados..." (Probe não busca credenciais do banco)

### Pergunta do Usuário
> "Precisa atualizar a probe?"

**Resposta:** SIM! A Probe Windows ainda não foi atualizada para buscar credenciais do banco via API.

---

## ✅ Implementações Realizadas

### 1. Nova Função: `_get_server_credential(server_id)`
**Arquivo:** `probe/probe_core.py`

```python
def _get_server_credential(self, server_id):
    """
    Busca credencial do servidor via API (sistema moderno como PRTG)
    Usa herança: Servidor → Grupo → Empresa
    """
    # Chama: GET /api/v1/credentials/resolve/{server_id}
    # Retorna credencial descriptografada com herança resolvida
```

**Características:**
- Busca credencial via endpoint `/credentials/resolve/{server_id}`
- API resolve herança automaticamente (Servidor → Grupo → Empresa)
- Credencial retornada já descriptografada (API usa Fernet)
- Trata erros 404 (sem credencial) e outros HTTP errors
- Logs informativos para debug

### 2. Modificação: `_collect_wmi_remote(server)`
**Arquivo:** `probe/probe_core.py`

**Mudanças:**
- ❌ ANTES: Buscava credenciais do objeto `server` (campos `wmi_username`, `wmi_password`)
- ✅ DEPOIS: Busca credenciais do banco via `_get_server_credential(server_id)`
- ✅ Valida tipo de credencial (deve ser 'wmi')
- ✅ Logs com emojis (🔐, ⚠️, 💡) para facilitar identificação
- ✅ Mostra nome da credencial e nível de herança nos logs

---

## 🔄 Fluxo de Coleta (Após Atualização)

```
Probe (a cada 60s)
   ↓
GET /api/v1/probes/servers
   ↓
Para cada servidor Windows:
   ↓
GET /api/v1/credentials/resolve/{server_id}
   ↓
API resolve herança:
   1. Credencial específica do servidor?
   2. Se não, credencial do grupo?
   3. Se não, credencial padrão da empresa?
   ↓
API retorna credencial "Techbiz" descriptografada
   ↓
Probe coleta métricas WMI:
   - CPU Usage
   - Memory Usage
   - Disk C:
   - Uptime
   - Network In/Out
   ↓
POST /api/v1/metrics/batch
   ↓
Dashboard atualizado ✅
```

---

## 📝 Arquivos Criados/Modificados

### Modificados
1. **probe/probe_core.py**
   - Adicionada função `_get_server_credential(server_id)`
   - Modificada função `_collect_wmi_remote(server)`
   - Logs informativos com emojis

### Criados (Documentação)
1. **ATUALIZAR_PROBE_CREDENCIAIS_AGORA.txt**
   - Instruções passo a passo para atualizar Probe no Windows
   - Comandos Git e PowerShell
   - Logs esperados e troubleshooting

2. **RESUMO_PROBE_CREDENCIAIS_12MAR.md**
   - Documentação técnica completa
   - Fluxo de coleta detalhado
   - Exemplos de código antes/depois
   - Validação e próximos passos

3. **commit_probe_credenciais.ps1**
   - Script PowerShell para fazer commit
   - Instruções de próximos passos após commit

4. **SESSAO_12MAR_PROBE_CREDENCIAIS.md** (este arquivo)
   - Resumo da sessão
   - Contexto e implementações

---

## 🚀 Próximos Passos (Para o Usuário)

### 1. Enviar para Git
```bash
cd ~/Coruja\ Monitor
./commit_probe_credenciais.ps1
```

### 2. Atualizar Probe no Windows (SRVSONDA001)
```powershell
# PowerShell como Administrador
Stop-Service -Name "CorujaProbe" -Force
cd C:\CorujaProbe
git pull origin master
Start-Service -Name "CorujaProbe"
Get-Content logs\probe.log -Tail 50 -Wait
```

### 3. Verificar Dashboard (após 60 segundos)
- Abrir: http://192.168.31.161:3000
- Ir em: Servidores → SRVHVSPRD010
- Sensores devem mostrar valores (não mais "Aguardando dados...")

---

## 📊 Logs Esperados

### ✅ Sucesso
```
INFO - Found 1 servers to monitor remotely
INFO - Collecting from remote server: SRVHVSPRD010 (192.168.31.110)
INFO - Using WMI for SRVHVSPRD010
INFO - 🔐 Usando credencial: Techbiz (Nível: Empresa)
DEBUG - Usuário: Techbiz\coruja.monitor
INFO - Collected WMI metrics from 192.168.31.110
INFO - Sent 7 metrics to API
```

### ⚠️ Sem Credencial
```
WARNING - ⚠️ Nenhuma credencial WMI configurada para 192.168.31.110 (ID: 123)
INFO - 💡 Configure credenciais em: Configurações → Credenciais
```

---

## 🎉 Benefícios do Sistema

### Sistema Moderno (igual PRTG/SolarWinds)
- ✅ Configure uma vez, use em todos os servidores
- ✅ Herança automática (Servidor → Grupo → Empresa)
- ✅ Centralizado (credenciais no banco, não em arquivos)
- ✅ Seguro (criptografia Fernet)
- ✅ Flexível (credencial específica ou padrão)

### Facilita Gestão
- ✅ Alterar senha em 1 lugar → afeta todos os servidores
- ✅ Credenciais diferentes por grupo/empresa (multi-tenant)
- ✅ Interface web para gerenciar
- ✅ Logs claros mostram qual credencial está sendo usada

---

## 📈 Status das Tasks

### TASK 1: Sistema de Credenciais Centralizadas
**Status:** ✅ DONE (implementado na sessão anterior)
- Tabela `credentials` criada
- API completa (7 endpoints)
- Interface React com cores roxas
- Credencial "Techbiz" configurada
- Sistema de herança funcionando

### TASK 2: Atualizar Probe Windows
**Status:** ✅ IMPLEMENTADO (aguardando deploy)
- Código modificado: `probe/probe_core.py`
- Função `_get_server_credential()` criada
- Função `_collect_wmi_remote()` modificada
- Documentação completa criada
- Aguardando: Atualização no servidor SRVSONDA001

---

## 🔗 Arquivos Importantes

### Código
- `probe/probe_core.py` - Lógica principal da Probe (modificado)
- `probe/collectors/wmi_remote_collector.py` - Coletor WMI (não modificado)
- `api/routers/credentials.py` - API de credenciais (já implementada)
- `api/models.py` - Modelo Credential (linha 781)

### Documentação
- `ATUALIZAR_PROBE_CREDENCIAIS_AGORA.txt` - Instruções de deploy
- `RESUMO_PROBE_CREDENCIAIS_12MAR.md` - Documentação técnica
- `SESSAO_12MAR_PROBE_CREDENCIAIS.md` - Resumo da sessão

### Scripts
- `commit_probe_credenciais.ps1` - Script de commit

---

## ⏱️ Tempo de Implementação

- Análise do código existente: 5 min
- Implementação das modificações: 10 min
- Criação da documentação: 10 min
- **Total:** ~25 minutos

---

## ✅ Validação Futura

Após deploy no SRVSONDA001:

1. **Logs da Probe**
   - Verificar mensagem: `🔐 Usando credencial: Techbiz`
   - Verificar mensagem: `Collected WMI metrics from 192.168.31.110`

2. **Dashboard**
   - Sensores SRVHVSPRD010 devem mostrar valores
   - Status deve mudar de "Aguardando dados..." para valores reais

3. **Banco de Dados**
   ```sql
   SELECT sensor_name, value, status, timestamp 
   FROM metrics 
   WHERE server_id = (SELECT id FROM servers WHERE hostname = 'SRVHVSPRD010')
   ORDER BY timestamp DESC 
   LIMIT 10;
   ```

---

**Status Final:** ✅ Implementação completa, aguardando deploy  
**Próximo Passo:** Usuário executar `commit_probe_credenciais.ps1` e atualizar SRVSONDA001
