# 🎯 DESIGN: GRUPOS + AZURE MONITORING COMPLETO

## 📋 REQUISITOS

### 1. Sistema de Grupos Hierárquicos
- Criar grupos raiz
- Criar subgrupos (hierarquia infinita)
- Mover grupos entre níveis
- Excluir grupos (com confirmação)
- Sensores devem pertencer a grupos obrigatoriamente

### 2. Monitoramento Azure Completo
- Wizard guiado por tipo de serviço
- Teste de credenciais antes de salvar
- Descoberta automática de recursos
- Seleção múltipla de recursos
- Monitoramento automático após configuração

## 🏗️ ARQUITETURA

### Banco de Dados - Tabela `sensor_groups`
```sql
CREATE TABLE sensor_groups (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER REFERENCES tenants(id),
    name VARCHAR(255) NOT NULL,
    parent_id INTEGER REFERENCES sensor_groups(id),
    description TEXT,
    icon VARCHAR(50) DEFAULT '📁',
    color VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_sensor_groups_tenant ON sensor_groups(tenant_id);
CREATE INDEX idx_sensor_groups_parent ON sensor_groups(parent_id);
```

### Modificação na Tabela `sensors`
```sql
ALTER TABLE sensors ADD COLUMN group_id INTEGER REFERENCES sensor_groups(id);
CREATE INDEX idx_sensors_group ON sensors(group_id);
```

## 📚 BASE DE CONHECIMENTO AZURE (Zabbix + PRTG)

### Serviços Azure Suportados

#### 1. Virtual Machines (VMs)
**Métricas**:
- CPU Usage (%)
- Memory Usage (%)
- Disk Read/Write (MB/s)
- Network In/Out (MB/s)
- VM Status (Running/Stopped/Deallocated)

**Requisitos**:
- Subscription ID
- Tenant ID
- Client ID (App Registration)
- Client Secret
- Resource Group (opcional)

**Permissões Necessárias**:
- `Reader` role no subscription ou resource group
- `Monitoring Reader` para métricas

#### 2. Storage Accounts
**Métricas**:
- Used Capacity (GB)
- Transactions (count)
- Ingress/Egress (MB)
- Availability (%)
- Success Rate (%)

**Requisitos**:
- Mesmas credenciais de VM
- Storage Account Name

#### 3. SQL Databases
**Métricas**:
- DTU Usage (%)
- Storage Usage (%)
- Connection Count
- Deadlocks
- Query Performance

**Requisitos**:
- Mesmas credenciais de VM
- Server Name
- Database Name

#### 4. App Services
**Métricas**:
- Response Time (ms)
- Request Count
- HTTP Errors (4xx, 5xx)
- CPU/Memory Usage
- Instance Count

#### 5. Azure Functions
**Métricas**:
- Execution Count
- Execution Duration (ms)
- Error Count
- Success Rate (%)

#### 6. Load Balancers
**Métricas**:
- Data Path Availability
- Health Probe Status
- SNAT Connection Count
- Byte Count

#### 7. Application Insights
**Métricas**:
- Request Rate
- Failed Requests
- Response Time
- Exceptions
- Page Views

#### 8. Cosmos DB
**Métricas**:
- Request Units (RU/s)
- Storage Usage
- Throttled Requests
- Availability

#### 9. Azure Kubernetes (AKS)
**Métricas**:
- Node CPU/Memory
- Pod Count
- Container Restarts
- Cluster Health

#### 10. Azure Cache (Redis)
**Métricas**:
- Cache Hits/Misses
- Connected Clients
- Used Memory
- Server Load

## 🎨 INTERFACE - WIZARD AZURE

### Passo 1: Autenticação
```
┌─────────────────────────────────────────┐
│ 🔐 Credenciais Azure                    │
├─────────────────────────────────────────┤
│ Subscription ID: [________________]     │
│ Tenant ID:       [________________]     │
│ Client ID:       [________________]     │
│ Client Secret:   [________________]     │
│                                         │
│ [?] Como obter credenciais              │
│                                         │
│ [Testar Conexão]  [Próximo >]          │
└─────────────────────────────────────────┘
```

### Passo 2: Tipo de Serviço
```
┌─────────────────────────────────────────┐
│ ☁️ Selecione o Serviço Azure            │
├─────────────────────────────────────────┤
│ ○ Virtual Machines                      │
│ ○ Storage Accounts                      │
│ ○ SQL Databases                         │
│ ○ App Services                          │
│ ○ Azure Functions                       │
│ ○ Load Balancers                        │
│ ○ Application Insights                  │
│ ○ Cosmos DB                             │
│ ○ Kubernetes (AKS)                      │
│ ○ Azure Cache (Redis)                   │
│                                         │
│ [< Voltar]  [Descobrir Recursos >]     │
└─────────────────────────────────────────┘
```

### Passo 3: Descoberta de Recursos
```
┌─────────────────────────────────────────┐
│ 🔍 Recursos Encontrados (15)            │
├─────────────────────────────────────────┤
│ ☑ vm-prod-web-01 (East US)             │
│ ☑ vm-prod-api-01 (East US)             │
│ ☐ vm-dev-test-01 (West US)             │
│ ☑ vm-prod-db-01 (East US)              │
│ ...                                     │
│                                         │
│ [Selecionar Todos] [Limpar Seleção]    │
│                                         │
│ [< Voltar]  [Configurar Métricas >]    │
└─────────────────────────────────────────┘
```

### Passo 4: Configuração de Métricas
```
┌─────────────────────────────────────────┐
│ 📊 Métricas para Monitorar              │
├─────────────────────────────────────────┤
│ ☑ CPU Usage (%)                         │
│   Warning: [80] Critical: [95]          │
│                                         │
│ ☑ Memory Usage (%)                      │
│   Warning: [80] Critical: [95]          │
│                                         │
│ ☑ Disk I/O (MB/s)                       │
│   Warning: [100] Critical: [200]        │
│                                         │
│ ☑ Network Traffic (MB/s)                │
│   Warning: [50] Critical: [100]         │
│                                         │
│ ☑ VM Status                             │
│                                         │
│ Intervalo de Coleta: [5] minutos       │
│                                         │
│ [< Voltar]  [Criar Sensores]           │
└─────────────────────────────────────────┘
```

### Passo 5: Seleção de Grupo
```
┌─────────────────────────────────────────┐
│ 📁 Selecione o Grupo                    │
├─────────────────────────────────────────┤
│ ▼ 🌐 Cloud Services                     │
│   ▼ ☁️ Azure                            │
│     ○ Production VMs                    │
│     ○ Development VMs                   │
│   ▼ 🔥 AWS                              │
│     ○ EC2 Instances                     │
│                                         │
│ [+ Criar Novo Grupo]                    │
│                                         │
│ [< Voltar]  [Finalizar]                │
└─────────────────────────────────────────┘
```

## 🔧 ENDPOINTS API

### Grupos
```python
POST   /api/v1/sensor-groups              # Criar grupo
GET    /api/v1/sensor-groups              # Listar grupos (hierárquico)
GET    /api/v1/sensor-groups/{id}         # Detalhes do grupo
PUT    /api/v1/sensor-groups/{id}         # Atualizar grupo
DELETE /api/v1/sensor-groups/{id}         # Excluir grupo
POST   /api/v1/sensor-groups/{id}/move    # Mover grupo
```

### Azure Discovery
```python
POST   /api/v1/azure/test-credentials     # Testar credenciais
POST   /api/v1/azure/discover-resources   # Descobrir recursos
POST   /api/v1/azure/create-sensors       # Criar sensores em massa
GET    /api/v1/azure/service-types        # Listar tipos de serviço
```

## 📦 PRÓXIMOS PASSOS

1. Criar migração do banco (sensor_groups)
2. Criar endpoints de grupos
3. Criar interface de gerenciamento de grupos
4. Criar wizard Azure completo
5. Implementar descoberta de recursos Azure
6. Criar collectors para métricas Azure
7. Testar fluxo completo

## 🎯 PRIORIDADE

1. **ALTA**: Sistema de grupos (base para tudo)
2. **ALTA**: Wizard Azure VMs (caso de uso principal)
3. **MÉDIA**: Outros serviços Azure
4. **BAIXA**: Otimizações e melhorias

Esta é uma implementação GRANDE. Vamos fazer por partes?
