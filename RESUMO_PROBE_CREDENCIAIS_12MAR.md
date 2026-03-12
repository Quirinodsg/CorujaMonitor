# 🔐 Probe Windows - Integração com Sistema de Credenciais Centralizadas

**Data:** 12 de Março de 2026  
**Objetivo:** Modificar Probe Windows para buscar credenciais WMI do banco via API

---

## 📋 Contexto

### Sistema de Credenciais Implementado (TASK 1)
- ✅ Tabela `credentials` criada com suporte WMI, SNMP v1/v2c/v3, SSH
- ✅ Sistema de herança: Servidor → Grupo → Tenant (Empresa)
- ✅ API completa: 7 endpoints (CRUD + Test + Resolve)
- ✅ Interface React com cores roxas
- ✅ Credencial "Techbiz" configurada (WMI, nível Empresa, padrão)

### Situação Atual
- ✅ Servidor SRVHVSPRD010 (192.168.31.110) adicionado
- ✅ 7 sensores criados: CPU, Memória, Disco C:, Uptime, Network In/Out
- ✅ PING funcionando (0.44ms coletado pelo worker Linux)
- ⚠️ Sensores WMI "Aguardando dados..." (Probe não usa credenciais do banco)

---

## 🔧 Modificações Implementadas

### Arquivo: `probe/probe_core.py`

#### 1. Nova Função: `_get_server_credential(server_id)`

```python
def _get_server_credential(self, server_id):
    """
    Busca credencial do servidor via API (sistema moderno como PRTG)
    Usa herança: Servidor → Grupo → Empresa
    """
    try:
        with httpx.Client(timeout=10.0, verify=False) as client:
            response = client.get(
                f"{self.config.api_url}/api/v1/credentials/resolve/{server_id}",
                params={"probe_token": self.config.probe_token}
            )
            
            if response.status_code == 404:
                logger.debug(f"Nenhuma credencial configurada para servidor ID {server_id}")
                return None
            
            if response.status_code != 200:
                logger.warning(f"Erro ao buscar credencial: HTTP {response.status_code}")
                return None
            
            credential = response.json()
            logger.debug(f"Credencial resolvida: {credential.get('name')} (Nível: {credential.get('inheritance_level')})")
            return credential
            
    except Exception as e:
        logger.error(f"Erro ao buscar credencial do servidor {server_id}: {e}")
        return None
```

**Características:**
- Chama endpoint `/credentials/resolve/{server_id}` da API
- API resolve herança automaticamente (Servidor → Grupo → Empresa)
- Retorna credencial descriptografada (API faz decrypt com Fernet)
- Trata erros 404 (sem credencial) e outros HTTP errors

#### 2. Modificação: `_collect_wmi_remote(server)`

**ANTES:**
```python
hostname = server.get('ip_address') or server.get('hostname')
username = server.get('wmi_username')
password = server.get('wmi_password')  # API will decrypt
domain = server.get('wmi_domain', '')

if not username or not password:
    logger.warning(f"WMI credentials not configured for {hostname}")
    return
```

**DEPOIS:**
```python
hostname = server.get('ip_address') or server.get('hostname')
server_id = server.get('id')

# Buscar credenciais do banco via API (sistema moderno como PRTG)
credential = self._get_server_credential(server_id)

if not credential:
    logger.warning(f"⚠️ Nenhuma credencial WMI configurada para {hostname} (ID: {server_id})")
    logger.info(f"💡 Configure credenciais em: Configurações → Credenciais")
    return

if credential.get('credential_type') != 'wmi':
    logger.warning(f"Credencial para {hostname} não é do tipo WMI")
    return

username = credential.get('wmi_username')
password = credential.get('wmi_password')  # API descriptografa automaticamente
domain = credential.get('wmi_domain', '')

if not username or not password:
    logger.warning(f"Credencial WMI incompleta para {hostname}")
    return

logger.info(f"🔐 Usando credencial: {credential.get('name')} (Nível: {credential.get('inheritance_level')})")
logger.debug(f"   Usuário: {domain}\\{username}" if domain else f"   Usuário: {username}")
```

**Mudanças:**
- ✅ Busca credencial do banco via API (não mais do objeto `server`)
- ✅ Valida tipo de credencial (deve ser 'wmi')
- ✅ Logs informativos com emojis (🔐, ⚠️, 💡)
- ✅ Mostra nome da credencial e nível de herança nos logs

---

## 🔄 Fluxo de Coleta (Após Atualização)

```
1. Probe inicia ciclo de coleta (a cada 60s)
   ↓
2. Busca lista de servidores: GET /api/v1/probes/servers
   ↓
3. Para cada servidor Windows (ex: SRVHVSPRD010):
   ↓
4. Busca credencial: GET /api/v1/credentials/resolve/{server_id}
   ↓
5. API resolve herança:
   - Verifica credencial específica do servidor
   - Se não tem, verifica credencial do grupo
   - Se não tem, verifica credencial padrão da empresa
   ↓
6. API retorna credencial "Techbiz" (nível Empresa, padrão)
   {
     "name": "Techbiz",
     "credential_type": "wmi",
     "wmi_username": "coruja.monitor",
     "wmi_password": "senha_descriptografada",
     "wmi_domain": "Techbiz",
     "inheritance_level": "Empresa"
   }
   ↓
7. Probe usa credencial para coletar métricas WMI:
   - CPU Usage
   - Memory Usage
   - Disk C:
   - Uptime
   - Network In/Out
   ↓
8. Métricas enviadas para API: POST /api/v1/metrics/batch
   ↓
9. Dashboard atualizado (sensores mostram valores)
```

---

## 📊 Logs Esperados

### Logs de Sucesso
```
INFO - Found 1 servers to monitor remotely
INFO - Collecting from remote server: SRVHVSPRD010 (192.168.31.110)
INFO - Using WMI for SRVHVSPRD010
DEBUG - Credencial resolvida: Techbiz (Nível: Empresa)
INFO - 🔐 Usando credencial: Techbiz (Nível: Empresa)
DEBUG - Usuário: Techbiz\coruja.monitor
INFO - Collected WMI metrics from 192.168.31.110
INFO - Sent 7 metrics to API
```

### Logs de Erro (Sem Credencial)
```
INFO - Collecting from remote server: SRVHVSPRD010 (192.168.31.110)
INFO - Using WMI for SRVHVSPRD010
DEBUG - Nenhuma credencial configurada para servidor ID 123
WARNING - ⚠️ Nenhuma credencial WMI configurada para 192.168.31.110 (ID: 123)
INFO - 💡 Configure credenciais em: Configurações → Credenciais
```

---

## 🚀 Instalação/Atualização

### No Windows (Git Bash)
```bash
cd ~/Coruja\ Monitor
git add probe/probe_core.py
git commit -m "feat: Probe busca credenciais WMI do banco via API (moderno como PRTG)"
git push origin master
```

### No Servidor SRVSONDA001 (PowerShell Admin)
```powershell
# Parar serviço
Stop-Service -Name "CorujaProbe" -Force

# Atualizar código
cd C:\CorujaProbe
git pull origin master

# Reiniciar serviço
Start-Service -Name "CorujaProbe"

# Verificar logs
Get-Content logs\probe.log -Tail 50 -Wait
```

---

## ✅ Validação

### 1. Verificar Logs da Probe
- Deve aparecer: `🔐 Usando credencial: Techbiz (Nível: Empresa)`
- Deve aparecer: `Collected WMI metrics from 192.168.31.110`

### 2. Verificar Dashboard
- Abrir: http://192.168.31.161:3000
- Ir em: Servidores → SRVHVSPRD010
- Sensores devem mostrar valores (não mais "Aguardando dados...")

### 3. Verificar Banco de Dados
```sql
SELECT sensor_name, value, status, timestamp 
FROM metrics 
WHERE server_id = (SELECT id FROM servers WHERE hostname = 'SRVHVSPRD010')
ORDER BY timestamp DESC 
LIMIT 10;
```

---

## 🎯 Benefícios

### Sistema Moderno (igual PRTG/SolarWinds)
- ✅ **Configure uma vez, use em todos os servidores**
- ✅ **Herança automática** (Servidor → Grupo → Empresa)
- ✅ **Centralizado** (credenciais no banco, não em arquivos)
- ✅ **Seguro** (criptografia Fernet, descriptografia na API)
- ✅ **Flexível** (credencial específica por servidor ou padrão)

### Facilita Gestão
- ✅ Alterar senha em 1 lugar → afeta todos os servidores
- ✅ Credenciais diferentes por grupo/empresa (multi-tenant)
- ✅ Interface web para gerenciar (não precisa editar arquivos)
- ✅ Logs claros mostram qual credencial está sendo usada

---

## 📝 Próximos Passos (Opcional)

1. **Adicionar suporte SNMP v3** (já tem tabela, falta coletor)
2. **Adicionar suporte SSH** (para Linux via SSH)
3. **Cache de credenciais** (evitar buscar API a cada coleta)
4. **Rotação automática de senhas** (integração com AD)
5. **Auditoria de uso** (log de quando credencial foi usada)

---

## 🔗 Arquivos Relacionados

- `probe/probe_core.py` - Lógica principal da Probe (modificado)
- `probe/collectors/wmi_remote_collector.py` - Coletor WMI (não modificado)
- `api/routers/credentials.py` - API de credenciais (já implementada)
- `api/models.py` - Modelo Credential (linha 781)
- `frontend/src/components/Credentials.js` - Interface React (já implementada)

---

**Status:** ✅ Implementado e pronto para deploy  
**Testado:** ❌ Aguardando atualização no SRVSONDA001  
**Documentação:** ✅ Completa
