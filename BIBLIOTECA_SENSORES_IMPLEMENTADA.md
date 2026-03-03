# 📚 Biblioteca de Sensores Independentes - Implementada

## ✅ O Que Foi Feito

Implementada uma **Biblioteca de Sensores** completamente independente da estrutura de servidores, permitindo adicionar e monitorar dispositivos e serviços que não estão vinculados a um servidor específico.

**🔌 NOVO: Teste de Conexão Integrado!**
- Botão "Testar Conexão" para validar credenciais antes de salvar
- Suporte para Azure, SNMP e HTTP
- Feedback visual imediato (sucesso/falha)
- Detalhes técnicos da conexão

## 🎯 Funcionalidades

### 1. Nova Aba no Menu Lateral
- **📚 Biblioteca de Sensores** - Nova opção no menu lateral
- Interface dedicada para gerenciar sensores independentes
- Separada da aba "Servidores" e "Sensores"

### 2. Tipos de Sensores Suportados

#### 📡 SNMP (Dispositivos de Rede)
- **Access Points (AP)** - Monitoramento WiFi
- **Ar-Condicionado** - Temperatura do datacenter
- **Nobreaks (UPS)** - Status de bateria
- **Impressoras** - Níveis de toner
- **Switches** - Portas e tráfego
- **Roteadores** - CPU, memória, interfaces
- **Storage** - Dell EqualLogic, NetApp, EMC, etc.

#### ☁️ Azure Services
- **Virtual Machines** - CPU, memória, disco
- **Web Apps** - Requisições, tempo de resposta
- **SQL Database** - DTU, storage, conexões
- **Storage Account** - Capacidade, transações
- **AKS** - Cluster Kubernetes
- **Functions** - Execuções, duração
- **Backup** - Status de backups
- **Load Balancer** - Health probes
- **Application Gateway** - Throughput
- **Cosmos DB** - RU consumption
- **Redis Cache** - CPU, memória, hits
- **Service Bus** - Mensagens ativas
- **Event Hub** - Mensagens entrantes/saintes
- **Key Vault** - API hits, latência

#### 🌐 HTTP/HTTPS
- Monitoramento de URLs
- Certificados SSL
- Tempo de resposta

#### 📦 Aplicações
- Serviços customizados
- APIs
- Microserviços

## 🏗️ Arquitetura

### Frontend

**Novo Componente**: `frontend/src/components/SensorLibrary.js`
- Interface completa para gerenciar sensores independentes
- Filtros por categoria
- Busca por nome/descrição
- Templates rápidos para configuração
- Modais de adicionar/editar

**Integração**:
- Adicionado ao `Sidebar.js`
- Adicionado ao `MainLayout.js`
- Rota: `sensor-library`

### Backend

**Endpoints Novos** em `api/routers/sensors.py`:

```python
POST   /api/v1/sensors/standalone      # Criar sensor independente
GET    /api/v1/sensors/standalone      # Listar sensores independentes
PUT    /api/v1/sensors/{id}            # Atualizar sensor
DELETE /api/v1/sensors/{id}            # Remover sensor
```

**Modelo de Dados**:
```python
class StandaloneSensorCreate:
    probe_id: int                    # Probe responsável pela coleta
    name: str                        # Nome do sensor
    sensor_type: str                 # Tipo (snmp, azure, http, etc.)
    category: str                    # Categoria (snmp, azure, storage, etc.)
    ip_address: Optional[str]        # IP do dispositivo
    
    # Configurações SNMP
    snmp_version: Optional[str]
    snmp_community: Optional[str]
    snmp_port: Optional[int]
    snmp_oid: Optional[str]
    
    # Configurações HTTP
    http_url: Optional[str]
    http_method: Optional[str]
    
    # Configurações Azure
    azure_subscription_id: Optional[str]
    azure_tenant_id: Optional[str]
    azure_client_id: Optional[str]
    azure_client_secret: Optional[str]
    azure_resource_type: Optional[str]
    azure_resource_name: Optional[str]
    
    # Thresholds
    threshold_warning: float = 80
    threshold_critical: float = 95
    description: Optional[str]
```

### Banco de Dados

**Migração**: `api/migrate_standalone_sensors.py`

Alterações no modelo `Sensor`:
- `server_id` agora é **opcional** (nullable=True)
- Adicionado `probe_id` para vincular diretamente à probe
- Sensores podem existir sem servidor (standalone)

```sql
ALTER TABLE sensors ALTER COLUMN server_id DROP NOT NULL;
ALTER TABLE sensors ADD COLUMN probe_id INTEGER REFERENCES probes(id);
CREATE INDEX idx_sensors_probe_id ON sensors(probe_id);
```

## 📋 Como Usar

### 0. Instalar Dependências

Antes de usar, instale as novas dependências:

```bash
cd api
pip install -r requirements.txt
```

Bibliotecas adicionadas:
- `azure-identity` - Autenticação Azure
- `azure-mgmt-resource` - Gerenciamento de recursos Azure
- `azure-mgmt-compute` - Azure VMs
- `azure-mgmt-monitor` - Azure Monitor
- `pysnmp` - Protocolo SNMP
- `requests` - Requisições HTTP

### 1. Executar Migração

```bash
cd api
python migrate_standalone_sensors.py
```

### 2. Acessar a Biblioteca

1. Faça login no sistema
2. Clique em **📚 Biblioteca de Sensores** no menu lateral
3. Clique em **+ Adicionar Sensor**

### 3. Adicionar Sensor SNMP (Ex: Access Point)

1. Selecione a **Probe** responsável
2. Escolha categoria **SNMP**
3. Clique no template **Access Point**
4. Preencha:
   - Nome: `AP-Sala-01`
   - IP: `192.168.1.100`
   - Community: `public`
   - OID: (já preenchido pelo template)
5. Clique em **Adicionar Sensor**

### 4. Adicionar Sensor Azure (Ex: Web App)

1. Selecione a **Probe** responsável
2. Escolha categoria **Microsoft Azure**
3. Clique no template **Azure Web App**
4. Preencha:
   - Nome: `Azure-WebApp-Producao`
   - Subscription ID
   - Tenant ID
   - Client ID
   - Client Secret
   - Tipo de Recurso: `Web App`
   - Nome do Recurso: `my-webapp`
5. Clique em **Adicionar Sensor**

### 5. Adicionar Sensor de Temperatura

1. Selecione a **Probe** responsável
2. Escolha categoria **SNMP**
3. Clique no template **Ar-Condicionado**
4. Preencha:
   - Nome: `AC-Datacenter-Principal`
   - IP: `192.168.1.50`
   - Community: `public`
   - OID: `1.3.6.1.4.1.9.9.13.1.3.1.3` (temperatura)
   - Threshold Warning: `28°C`
   - Threshold Critical: `32°C`
5. Clique em **Adicionar Sensor**

## 🔍 Filtros e Busca

- **Filtro por Categoria**: Dropdown com todas as categorias
- **Busca**: Campo de texto para buscar por nome ou descrição
- **Visualização em Cards**: Cada sensor exibido em card com:
  - Ícone da categoria
  - Nome
  - IP (se aplicável)
  - Descrição
  - Thresholds
  - Ações (Editar/Remover)

## 🎨 Templates Rápidos

Ao selecionar uma categoria, são exibidos até 6 templates rápidos:
- **SNMP**: Access Point, Ar-Condicionado, Nobreak, Impressora, Switch, Roteador
- **Azure**: VM, Web App, SQL, Storage, AKS, Functions
- **Storage**: Dell EqualLogic, NetApp, EMC VNX, HP 3PAR, Synology, QNAP
- **Network**: HTTP, HTTPS, SSL Certificate, DNS Query

Clicar em um template preenche automaticamente:
- Nome padrão
- Tipo de sensor
- OIDs SNMP (se aplicável)
- Thresholds recomendados
- Descrição

## 🔄 Integração com Probes

- Cada sensor independente é vinculado a uma **Probe**
- A probe é responsável por coletar os dados
- Suporta coleta via:
  - **SNMP** (v1, v2c, v3)
  - **HTTP/HTTPS**
  - **Azure API**
  - **Protocolos customizados**

## 📊 Métricas e Incidentes

- Sensores independentes geram métricas normalmente
- Incidentes são criados quando thresholds são ultrapassados
- Aparecem no Dashboard e NOC
- Suportam análise de IA e auto-remediação

## 🎯 Casos de Uso

### Monitoramento de Infraestrutura
- Access Points WiFi em toda empresa
- Ar-condicionado do datacenter
- Nobreaks e UPS
- Switches e roteadores core

### Monitoramento Cloud
- Recursos Azure sem servidor local
- Web Apps e Functions
- Bancos de dados gerenciados
- Storage accounts

### Monitoramento de Aplicações
- APIs externas
- Microserviços
- Serviços SaaS
- Endpoints HTTP

### Monitoramento de Storage
- SANs Dell EqualLogic
- NAS Synology/QNAP
- Storage NetApp
- Arrays HP 3PAR

## 📝 Diferenças: Biblioteca vs Servidores

| Aspecto | Servidores | Biblioteca |
|---------|-----------|------------|
| **Vinculação** | Sensores vinculados a servidor | Sensores independentes |
| **Criação** | Sensores criados automaticamente | Criação manual |
| **Tipos** | CPU, Memória, Disco, Serviços | SNMP, Azure, HTTP, Custom |
| **Uso** | Monitorar servidores Windows/Linux | Monitorar dispositivos, cloud, apps |
| **Probe** | Herdada do servidor | Selecionada manualmente |

## ✅ Benefícios

1. **Flexibilidade**: Monitore qualquer dispositivo ou serviço
2. **Organização**: Sensores agrupados por categoria
3. **Templates**: Configuração rápida com templates pré-definidos
4. **Independência**: Não precisa criar servidor fictício
5. **Escalabilidade**: Adicione centenas de sensores facilmente
6. **Cloud-Ready**: Suporte nativo para Azure e outros clouds

## 🚀 Próximos Passos

1. Executar migração do banco de dados
2. Reiniciar API
3. Acessar a Biblioteca de Sensores
4. Adicionar seus primeiros sensores independentes
5. Configurar probes para coletar dados

## 📚 Arquivos Criados/Modificados

### Novos Arquivos
- `frontend/src/components/SensorLibrary.js` - Componente principal
- `api/migrate_standalone_sensors.py` - Migração do banco
- `BIBLIOTECA_SENSORES_IMPLEMENTADA.md` - Esta documentação

### Arquivos Modificados
- `frontend/src/components/Sidebar.js` - Adicionado item de menu
- `frontend/src/components/MainLayout.js` - Adicionada rota
- `api/routers/sensors.py` - Novos endpoints standalone
- `api/models.py` - Modelo Sensor atualizado

## 🎉 Conclusão

A Biblioteca de Sensores está completamente implementada e pronta para uso! Agora você pode monitorar Access Points, serviços Azure, ar-condicionado, nobreaks, impressoras e muito mais, tudo de forma independente e organizada.


## 🔌 Teste de Conexão

### Funcionalidade Implementada

Antes de adicionar um sensor, você pode **testar a conexão** para garantir que as credenciais e configurações estão corretas.

### Tipos de Teste Suportados

#### 1. Azure (☁️)
- Valida credenciais Azure (Subscription ID, Tenant ID, Client ID, Client Secret)
- Tenta listar resource groups para confirmar autenticação
- Retorna quantidade de resource groups encontrados
- **Erro comum**: "Invalid client secret" - Gere um novo secret no Azure Portal

#### 2. SNMP (📡)
- Testa conexão SNMP com o dispositivo
- Usa OID padrão `1.3.6.1.2.1.1.1.0` (sysDescr) se não especificado
- Valida IP, community string e porta
- Retorna valor do OID consultado
- **Erro comum**: "Timeout" - Verifique firewall e community string

#### 3. HTTP (🌐)
- Testa requisição HTTP/HTTPS
- Mede tempo de resposta
- Valida status code
- Ignora erros SSL para teste
- **Erro comum**: "Connection refused" - Verifique URL e porta

### Como Usar

1. Preencha as configurações do sensor (credenciais, IP, URL, etc.)
2. Clique no botão **"🔌 Testar Conexão"**
3. Aguarde o resultado:
   - ✅ **Sucesso**: Conexão estabelecida, pode adicionar o sensor
   - ❌ **Falha**: Verifique as credenciais e tente novamente
4. Após teste bem-sucedido, clique em **"Adicionar Sensor"**

### Exemplos de Resultado

**Azure - Sucesso:**
```
✅ Sucesso!
Conexão Azure estabelecida com sucesso! Encontrados 3 resource groups.

Detalhes:
- subscription_id: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
- tenant_id: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
- resource_groups_count: 3
```

**SNMP - Sucesso:**
```
✅ Sucesso!
Conexão SNMP estabelecida com sucesso!

Detalhes:
- ip_address: 192.168.1.100
- oid: 1.3.6.1.2.1.1.1.0
- value: Cisco IOS Software, Version 15.2...
```

**HTTP - Sucesso:**
```
✅ Sucesso!
Conexão HTTP estabelecida com sucesso!

Detalhes:
- url: https://example.com
- status_code: 200
- response_time: 145ms
```

**Azure - Falha:**
```
❌ Falha
Falha na autenticação Azure. Verifique as credenciais.

Erro: AADSTS7000215: Invalid client secret provided
```

### Benefícios

1. **Validação Prévia**: Evita criar sensores com credenciais inválidas
2. **Feedback Imediato**: Sabe na hora se está funcionando
3. **Troubleshooting**: Mensagens de erro detalhadas
4. **Economia de Tempo**: Não precisa esperar a probe coletar dados
5. **Confiança**: Adiciona sensor sabendo que vai funcionar

### Endpoint Backend

```python
POST /api/v1/sensors/test-connection

Body:
{
  "type": "azure",  // ou "snmp", "http"
  "subscription_id": "...",
  "tenant_id": "...",
  "client_id": "...",
  "client_secret": "...",
  // ... outros campos conforme o tipo
}

Response (Sucesso):
{
  "success": true,
  "message": "✅ Conexão Azure estabelecida com sucesso!",
  "details": { ... }
}

Response (Falha):
{
  "success": false,
  "message": "❌ Falha na autenticação Azure.",
  "error": "AADSTS7000215: Invalid client secret"
}
```

## 📦 Dependências Adicionadas

Atualize o `requirements.txt`:

```bash
# Azure SDK
azure-identity==1.15.0
azure-mgmt-resource==23.0.1
azure-mgmt-compute==30.5.0
azure-mgmt-monitor==6.0.2

# SNMP
pysnmp==4.4.12

# HTTP requests
requests==2.31.0
```

Instale com:
```bash
cd api
pip install -r requirements.txt
```
