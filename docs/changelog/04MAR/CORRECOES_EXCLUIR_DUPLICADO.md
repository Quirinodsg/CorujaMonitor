# Correções: Excluir Servidor e Validação de IP Duplicado

## ✅ Funcionalidades Implementadas

### 1. Excluir Servidor

**Problema**: Não havia opção para excluir servidores da interface.

**Solução**: Implementado endpoint de exclusão e botão na interface.

#### Backend (API)

**Arquivo**: `api/routers/servers.py`

```python
@router.delete("/{server_id}")
async def delete_server(
    server_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a server and all its associated data (sensors, metrics, incidents)
    """
    server = db.query(Server).filter(
        Server.id == server_id,
        Server.tenant_id == current_user.tenant_id
    ).first()
    
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    # Delete associated data in order
    from models import Sensor, Metric, Incident
    
    # Get all sensors for this server
    sensors = db.query(Sensor).filter(Sensor.server_id == server_id).all()
    sensor_ids = [s.id for s in sensors]
    
    if sensor_ids:
        # Delete incidents for these sensors
        db.query(Incident).filter(Incident.sensor_id.in_(sensor_ids)).delete()
        
        # Delete metrics for these sensors
        db.query(Metric).filter(Metric.sensor_id.in_(sensor_ids)).delete()
        
        # Delete sensors
        db.query(Sensor).filter(Sensor.server_id == server_id).delete()
    
    # Delete server
    db.delete(server)
    db.commit()
    
    return {"message": f"Server '{server.hostname}' deleted successfully"}
```

**O que é excluído**:
- ✅ Servidor
- ✅ Todos os sensores do servidor
- ✅ Todas as métricas dos sensores
- ✅ Todos os incidentes dos sensores

#### Frontend (Interface)

**Arquivo**: `frontend/src/components/Servers.js`

```javascript
const handleDeleteServer = async (serverId, serverName, e) => {
  e.stopPropagation(); // Prevent server selection
  
  if (!window.confirm(`⚠️ ATENÇÃO: Tem certeza que deseja remover o servidor "${serverName}"?\n\nIsso irá remover:\n- O servidor\n- Todos os sensores\n- Todas as métricas\n- Todos os incidentes\n\nEsta ação NÃO pode ser desfeita!`)) {
    return;
  }

  try {
    await api.delete(`/api/v1/servers/${serverId}`);
    
    // Clear selection if deleted server was selected
    if (selectedServer && selectedServer.id === serverId) {
      setSelectedServer(null);
      setSensors([]);
      setMetrics({});
    }
    
    loadServers();
    alert('Servidor removido com sucesso!');
  } catch (error) {
    console.error('Erro ao remover servidor:', error);
    alert('Erro ao remover servidor: ' + (error.response?.data?.detail || error.message));
  }
};
```

**Botão adicionado**:
```jsx
<button 
  className="btn-delete-small"
  onClick={(e) => handleDeleteServer(server.id, server.hostname, e)}
  title="Excluir servidor"
>
  🗑️
</button>
```

**Arquivo**: `frontend/src/components/Management.css`

```css
.btn-delete-small {
  background: transparent;
  border: none;
  cursor: pointer;
  font-size: 16px;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background 0.2s, color 0.2s;
  color: #666;
}

.btn-delete-small:hover {
  background: #fee;
  color: #f44336;
}
```

---

### 2. Validação de IP Duplicado

**Problema**: Era possível adicionar servidores com o mesmo IP, causando confusão.

**Solução**: Validação no backend que verifica se o IP já existe antes de criar o servidor.

#### Backend (API)

**Arquivo**: `api/routers/servers.py`

```python
@router.post("/", response_model=ServerResponse)
async def create_server(
    server: ServerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # ... validações anteriores ...
    
    # Check for duplicate IP address
    if server.ip_address:
        existing_server = db.query(Server).filter(
            Server.ip_address == server.ip_address,
            Server.tenant_id == current_user.tenant_id,
            Server.is_active == True
        ).first()
        
        if existing_server:
            raise HTTPException(
                status_code=400, 
                detail=f"Servidor com IP {server.ip_address} já existe: {existing_server.hostname} (ID: {existing_server.id})"
            )
    
    # ... continua criação do servidor ...
```

**Mensagem de erro**:
```
Servidor com IP 192.168.0.38 já existe: DESKTOP-P9VGN04 (ID: 4)
```

---

## 🧪 Como Testar

### Teste 1: Excluir Servidor

1. Ir para página "Servidores"
2. Localizar um servidor de teste
3. Clicar no botão 🗑️ (lixeira) ao lado do servidor
4. Confirmar a exclusão no alerta
5. Verificar que:
   - ✅ Servidor foi removido da lista
   - ✅ Sensores foram removidos
   - ✅ Métricas foram removidas
   - ✅ Incidentes foram removidos

**Verificar no banco**:
```bash
# Antes de excluir, anotar o ID do servidor (ex: 5)

# Verificar sensores
docker exec coruja-postgres psql -U coruja -d coruja_monitor -c "SELECT COUNT(*) FROM sensors WHERE server_id = 5;"

# Excluir servidor pela interface

# Verificar que foi removido
docker exec coruja-postgres psql -U coruja -d coruja_monitor -c "SELECT COUNT(*) FROM sensors WHERE server_id = 5;"
# Deve retornar 0
```

### Teste 2: IP Duplicado

1. Ir para página "Servidores"
2. Clicar em "Adicionar Servidor"
3. Preencher com um IP que já existe (ex: 192.168.0.38)
4. Tentar salvar
5. Verificar que:
   - ❌ Servidor NÃO é criado
   - ✅ Mensagem de erro aparece: "Servidor com IP 192.168.0.38 já existe: DESKTOP-P9VGN04 (ID: 4)"

**Teste via API**:
```bash
# Tentar criar servidor com IP duplicado
curl -X POST http://localhost:8000/api/v1/servers/ \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "probe_id": 1,
    "hostname": "TESTE-DUPLICADO",
    "ip_address": "192.168.0.38"
  }'

# Resposta esperada:
# {
#   "detail": "Servidor com IP 192.168.0.38 já existe: DESKTOP-P9VGN04 (ID: 4)"
# }
```

---

## 📊 Fluxo de Exclusão

```
┌─────────────────────────────────────────────────────────────┐
│                    INTERFACE WEB                            │
│                                                             │
│  Usuário clica em 🗑️ no servidor                           │
│                                                             │
│  ⚠️ Confirmação:                                            │
│  "Tem certeza que deseja remover o servidor?"              │
│  "Isso irá remover:"                                        │
│  "- O servidor"                                             │
│  "- Todos os sensores"                                      │
│  "- Todas as métricas"                                      │
│  "- Todos os incidentes"                                    │
│                                                             │
│  [Cancelar] [OK]                                            │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
              ┌────────────────────────┐
              │   API DELETE           │
              │   /api/v1/servers/{id} │
              │                        │
              │  1. Verificar tenant   │
              │  2. Buscar sensores    │
              │  3. Excluir incidentes │
              │  4. Excluir métricas   │
              │  5. Excluir sensores   │
              │  6. Excluir servidor   │
              └────────────┬───────────┘
                           ↓
              ┌────────────────────────┐
              │   BANCO DE DADOS       │
              │                        │
              │  DELETE FROM incidents │
              │  DELETE FROM metrics   │
              │  DELETE FROM sensors   │
              │  DELETE FROM servers   │
              └────────────────────────┘
```

---

## 📊 Fluxo de Validação de IP

```
┌─────────────────────────────────────────────────────────────┐
│                    INTERFACE WEB                            │
│                                                             │
│  Adicionar Servidor:                                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Hostname: NOVO-SERVER                               │   │
│  │ IP: 192.168.0.38                                    │   │
│  │ Probe: [selecionar]                                 │   │
│  │                                                     │   │
│  │ [Salvar]                                            │   │
│  └─────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
              ┌────────────────────────┐
              │   API POST             │
              │   /api/v1/servers/     │
              │                        │
              │  1. Verificar probe    │
              │  2. Verificar IP       │
              └────────────┬───────────┘
                           ↓
              ┌────────────────────────┐
              │   BANCO DE DADOS       │
              │                        │
              │  SELECT * FROM servers │
              │  WHERE ip_address =    │
              │    '192.168.0.38'      │
              │  AND tenant_id = 1     │
              │  AND is_active = true  │
              └────────────┬───────────┘
                           ↓
                    ┌──────┴──────┐
                    │             │
              IP Existe?      IP Livre?
                    │             │
                    ↓             ↓
         ┌──────────────┐  ┌──────────────┐
         │ ❌ ERRO 400  │  │ ✅ CRIAR     │
         │              │  │ SERVIDOR     │
         │ "Servidor    │  │              │
         │ com IP já    │  │ + Sensores   │
         │ existe"      │  │   padrão     │
         └──────────────┘  └──────────────┘
```

---

## 🎯 Casos de Uso

### Caso 1: Servidor de Teste

**Cenário**: Adicionou um servidor para testar e agora quer remover.

**Solução**:
1. Ir para "Servidores"
2. Localizar o servidor de teste
3. Clicar em 🗑️
4. Confirmar exclusão
5. Servidor e todos os dados são removidos

### Caso 2: IP Duplicado por Engano

**Cenário**: Tentou adicionar um servidor mas digitou o IP errado (que já existe).

**Resultado**:
- ❌ Sistema bloqueia a criação
- ✅ Mostra mensagem: "Servidor com IP 192.168.0.38 já existe: DESKTOP-P9VGN04"
- ✅ Usuário pode corrigir o IP antes de salvar

### Caso 3: Servidor Desativado

**Cenário**: Servidor foi desligado permanentemente.

**Solução**:
1. Excluir o servidor pela interface
2. Todos os dados históricos são removidos
3. Libera o IP para ser usado em outro servidor

---

## ⚠️ Avisos Importantes

### Exclusão é Permanente

- ❌ **NÃO há como desfazer** a exclusão
- ❌ **Todos os dados são perdidos**: sensores, métricas, incidentes
- ✅ Sempre confirme antes de excluir
- ✅ Considere fazer backup do banco antes de excluir servidores importantes

### Validação de IP

- ✅ Verifica apenas IPs **ativos** (is_active = true)
- ✅ Verifica apenas no **mesmo tenant** (multi-tenant safe)
- ⚠️ Se você desativar um servidor, o IP fica "liberado" para outro servidor

---

## 📝 Comandos Úteis

### Verificar servidores com mesmo IP
```bash
docker exec coruja-postgres psql -U coruja -d coruja_monitor -c "SELECT id, hostname, ip_address, is_active FROM servers WHERE ip_address = '192.168.0.38';"
```

### Contar dados de um servidor antes de excluir
```bash
# Substituir 5 pelo ID do servidor
docker exec coruja-postgres psql -U coruja -d coruja_monitor -c "
SELECT 
  (SELECT COUNT(*) FROM sensors WHERE server_id = 5) as sensores,
  (SELECT COUNT(*) FROM metrics WHERE sensor_id IN (SELECT id FROM sensors WHERE server_id = 5)) as metricas,
  (SELECT COUNT(*) FROM incidents WHERE sensor_id IN (SELECT id FROM sensors WHERE server_id = 5)) as incidentes;
"
```

### Verificar se exclusão foi completa
```bash
# Após excluir servidor ID 5
docker exec coruja-postgres psql -U coruja -d coruja_monitor -c "
SELECT 
  (SELECT COUNT(*) FROM servers WHERE id = 5) as servidor,
  (SELECT COUNT(*) FROM sensors WHERE server_id = 5) as sensores,
  (SELECT COUNT(*) FROM metrics WHERE sensor_id IN (SELECT id FROM sensors WHERE server_id = 5)) as metricas;
"
# Todos devem retornar 0
```

---

## 📊 Resumo das Mudanças

| Arquivo | Mudança | Descrição |
|---------|---------|-----------|
| `api/routers/servers.py` | Novo endpoint | DELETE /api/v1/servers/{id} |
| `api/routers/servers.py` | Validação | Verifica IP duplicado ao criar |
| `frontend/src/components/Servers.js` | Nova função | handleDeleteServer() |
| `frontend/src/components/Servers.js` | Novo botão | 🗑️ Excluir servidor |
| `frontend/src/components/Management.css` | Novo estilo | .btn-delete-small |

---

**Data**: 13/02/2026 17:20 UTC
**Status**: ✅ IMPLEMENTADO E TESTADO
**Serviços**: API e Frontend reiniciados
