# Correções: Adicionar Servidor e Sensores Padrão

## ✅ Problemas Corrigidos

### 1. Sensores Padrão Não Criados Automaticamente

**Problema**: Ao adicionar um servidor novo pelo IP, os sensores padrão não eram criados automaticamente.

**Solução**: Modificado `api/routers/servers.py` para criar automaticamente 7 sensores padrão quando um servidor Windows é adicionado:

```python
default_sensors = [
    "PING" (ping),
    "cpu_usage" (cpu),
    "memory_usage" (memory),
    "disk_C_" (disk),
    "uptime" (system),
    "network_in" (network),
    "network_out" (network)
]
```

### 2. Campos WMI Não Disponíveis na Interface

**Problema**: Não havia campos para configurar usuário/senha WMI remoto.

**Solução**: 
- ✅ Adicionados campos no banco de dados (migração executada)
- ✅ Adicionados campos na API (`ServerCreate` e `ServerResponse`)
- ✅ Implementada criptografia de senha WMI (Fernet)
- ⏭️ Próximo passo: Adicionar campos na interface web

**Novos campos:**
- `wmi_username` - Usuário para WMI remoto
- `wmi_password_encrypted` - Senha criptografada
- `wmi_domain` - Domínio Windows (opcional)
- `wmi_enabled` - Habilitar monitoramento WMI remoto

### 3. Visualizar Serviços Rodando na Máquina

**Problema**: Não conseguia ver os serviços rodando em tempo real para adicionar.

**Solução**: O endpoint já existe (`/api/v1/probe-commands/services/{probe_id}`), mas precisa melhorar a interface para mostrar os serviços disponíveis.

---

## 📝 Mudanças Aplicadas

### Arquivo: `api/routers/servers.py`

#### 1. Importações Adicionadas
```python
from cryptography.fernet import Fernet
import os
```

#### 2. Funções de Criptografia
```python
def get_cipher():
    """Get Fernet cipher for password encryption"""
    key = os.getenv('WMI_ENCRYPTION_KEY')
    if not key:
        key = Fernet.generate_key().decode()
    return Fernet(key.encode())

def encrypt_password(password: str) -> str:
    """Encrypt WMI password"""
    cipher = get_cipher()
    return cipher.encrypt(password.encode()).decode()

def decrypt_password(encrypted: str) -> str:
    """Decrypt WMI password"""
    cipher = get_cipher()
    return cipher.decrypt(encrypted.encode()).decode()
```

#### 3. Modelo ServerCreate Atualizado
```python
class ServerCreate(BaseModel):
    # ... campos existentes ...
    # Novos campos WMI
    wmi_username: Optional[str] = None
    wmi_password: Optional[str] = None
    wmi_domain: Optional[str] = None
    wmi_enabled: Optional[bool] = False
```

#### 4. Criação Automática de Sensores
```python
@router.post("/", response_model=ServerResponse)
async def create_server(...):
    # ... criar servidor ...
    
    # Auto-create default sensors for Windows servers
    if server.device_type == 'server' and server.monitoring_protocol == 'wmi':
        default_sensors = [
            {"name": "PING", "sensor_type": "ping", ...},
            {"name": "cpu_usage", "sensor_type": "cpu", ...},
            {"name": "memory_usage", "sensor_type": "memory", ...},
            {"name": "disk_C_", "sensor_type": "disk", ...},
            {"name": "uptime", "sensor_type": "system", ...},
            {"name": "network_in", "sensor_type": "network", ...},
            {"name": "network_out", "sensor_type": "network", ...}
        ]
        
        for sensor_data in default_sensors:
            sensor = Sensor(...)
            db.add(sensor)
        
        db.commit()
```

### Arquivo: `api/requirements.txt`

Adicionada dependência:
```
cryptography==41.0.7
```

### Arquivo: `api/migrate_wmi_credentials.py`

Migração executada com sucesso:
```sql
ALTER TABLE servers ADD COLUMN wmi_username VARCHAR(255);
ALTER TABLE servers ADD COLUMN wmi_password_encrypted TEXT;
ALTER TABLE servers ADD COLUMN wmi_domain VARCHAR(255);
ALTER TABLE servers ADD COLUMN wmi_enabled BOOLEAN DEFAULT FALSE;
```

---

## 🧪 Como Testar

### 1. Adicionar Novo Servidor

1. Ir para página "Servidores"
2. Clicar em "Adicionar Servidor"
3. Preencher:
   - **Probe**: Selecionar probe existente
   - **Hostname**: Nome do servidor
   - **IP**: 192.168.0.100 (exemplo)
   - **Tipo de Dispositivo**: Server
   - **Protocolo**: WMI
4. Clicar em "Salvar"

**Resultado Esperado**:
- ✅ Servidor criado
- ✅ 7 sensores padrão criados automaticamente
- ✅ Sensores aparecem na lista

### 2. Verificar Sensores Criados

Após adicionar o servidor, verificar se os seguintes sensores foram criados:
- 📡 PING
- 🖥️ cpu_usage
- 💾 memory_usage
- 💿 disk_C_
- ⏱️ uptime
- 🌐 network_in
- 🌐 network_out

### 3. Verificar no Banco de Dados

```bash
docker exec coruja-postgres psql -U coruja -d coruja_monitor -c "SELECT id, hostname, wmi_username, wmi_enabled FROM servers ORDER BY id DESC LIMIT 5;"
```

```bash
docker exec coruja-postgres psql -U coruja -d coruja_monitor -c "SELECT id, server_id, name, sensor_type FROM sensors WHERE server_id = [ID_DO_SERVIDOR];"
```

---

## ⏭️ Próximos Passos

### 1. Atualizar Interface Web (Frontend)

Adicionar campos WMI no formulário de adicionar servidor:

**Arquivo**: `frontend/src/components/Servers.js`

```javascript
const [newServer, setNewServer] = useState({
  // ... campos existentes ...
  wmi_username: '',
  wmi_password: '',
  wmi_domain: '',
  wmi_enabled: false
});
```

**Modal de Adicionar Servidor**:
```jsx
{/* Seção WMI Remoto (Opcional) */}
<div className="form-section">
  <h4>🔐 WMI Remoto (Opcional - Agentless)</h4>
  <p className="help-text">
    Configure apenas se quiser monitorar sem instalar sonda no servidor
  </p>
  
  <label>
    <input
      type="checkbox"
      checked={newServer.wmi_enabled}
      onChange={(e) => setNewServer({...newServer, wmi_enabled: e.target.checked})}
    />
    Habilitar WMI Remoto
  </label>
  
  {newServer.wmi_enabled && (
    <>
      <input
        type="text"
        placeholder="Usuário WMI (ex: Administrator)"
        value={newServer.wmi_username}
        onChange={(e) => setNewServer({...newServer, wmi_username: e.target.value})}
      />
      
      <input
        type="password"
        placeholder="Senha WMI"
        value={newServer.wmi_password}
        onChange={(e) => setNewServer({...newServer, wmi_password: e.target.value})}
      />
      
      <input
        type="text"
        placeholder="Domínio (opcional)"
        value={newServer.wmi_domain}
        onChange={(e) => setNewServer({...newServer, wmi_domain: e.target.value})}
      />
    </>
  )}
</div>
```

### 2. Melhorar Visualização de Serviços Disponíveis

**Objetivo**: Mostrar lista de serviços rodando na máquina para facilitar adição.

**Implementação**:
```javascript
const loadAvailableServices = async () => {
  if (!selectedServer) return;
  
  setLoadingServices(true);
  try {
    const response = await api.get(`/api/v1/probe-commands/services/${selectedServer.probe_id}`);
    setAvailableServices(response.data);
  } catch (error) {
    console.error('Erro ao carregar serviços:', error);
  } finally {
    setLoadingServices(false);
  }
};
```

**Interface**:
```jsx
<div className="available-services">
  <h4>Serviços Disponíveis</h4>
  <button onClick={loadAvailableServices}>
    🔄 Carregar Serviços
  </button>
  
  {loadingServices && <p>Carregando...</p>}
  
  {availableServices.length > 0 && (
    <ul>
      {availableServices.map(service => (
        <li key={service.name}>
          <span>{service.display_name}</span>
          <span className={`status ${service.state}`}>
            {service.state}
          </span>
          <button onClick={() => addServiceSensor(service.name)}>
            + Adicionar
          </button>
        </li>
      ))}
    </ul>
  )}
</div>
```

### 3. Adicionar Chave de Criptografia no .env

**Arquivo**: `.env`

```bash
# WMI Password Encryption Key
WMI_ENCRYPTION_KEY=sua_chave_aqui
```

**Gerar chave**:
```python
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

---

## 📊 Resumo das Correções

| Problema | Status | Solução |
|----------|--------|---------|
| Sensores padrão não criados | ✅ CORRIGIDO | Auto-criação de 7 sensores ao adicionar servidor |
| Campos WMI não disponíveis | ✅ BACKEND OK | Campos adicionados na API e banco |
| Interface sem campos WMI | ⏭️ PENDENTE | Precisa atualizar frontend |
| Visualizar serviços | ⏭️ PENDENTE | Endpoint existe, melhorar interface |

---

## 🎯 Teste Rápido

1. **Adicionar servidor novo**:
   ```
   Hostname: TESTE-SERVER
   IP: 192.168.0.100
   Probe: [selecionar probe existente]
   ```

2. **Verificar sensores criados**:
   ```bash
   docker exec coruja-postgres psql -U coruja -d coruja_monitor -c "SELECT name, sensor_type FROM sensors WHERE server_id = (SELECT id FROM servers WHERE hostname = 'TESTE-SERVER');"
   ```

3. **Resultado esperado**:
   ```
        name      | sensor_type
   ---------------+-------------
    PING          | ping
    cpu_usage     | cpu
    memory_usage  | memory
    disk_C_       | disk
    uptime        | system
    network_in    | network
    network_out   | network
   ```

---

**Data**: 13/02/2026 17:15 UTC
**Status**: Backend corrigido, frontend pendente
**Próximo**: Atualizar interface web com campos WMI
