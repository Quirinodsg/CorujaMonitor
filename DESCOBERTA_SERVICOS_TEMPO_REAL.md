# Descoberta de Serviços em Tempo Real

## Funcionalidade Implementada

Quando você clica em "Adicionar Sensor" e escolhe "Serviço do Windows", o sistema agora:

1. **Conecta na máquina em tempo real** via WMI
2. **Lista TODOS os serviços** que estão rodando ou parados
3. **Mostra o status atual** de cada serviço (Running, Stopped, Paused)
4. **Mostra o tipo de inicialização** (Auto, Manual, Disabled)
5. **Permite selecionar** o serviço desejado da lista

## Arquitetura

```
Frontend (Servers.js)
    ↓ Clica "Adicionar Sensor" → Tipo: Serviço
    ↓ Chama API
API (probe_commands.py)
    ↓ GET /api/v1/probe-commands/services/{server_id}
    ↓ Conecta via WMI local (se servidor local)
    ↓ Retorna lista de serviços
Frontend
    ↓ Exibe lista em dropdown
    ↓ Usuário seleciona serviço
    ↓ Cria sensor
```

## Arquivos Criados/Modificados

### Backend (API)

1. **`api/routers/probe_commands.py`** (NOVO)
   - Endpoint: `GET /api/v1/probe-commands/services/{server_id}`
   - Endpoint: `GET /api/v1/probe-commands/disks/{server_id}`
   - Conecta via WMI local para descobrir serviços e discos
   - Retorna lista completa com status em tempo real

2. **`api/main.py`** (JÁ INCLUÍDO)
   - Router `probe_commands` já estava incluído

### Probe

3. **`probe/collectors/wmi_remote_collector.py`** (MODIFICADO)
   - Adicionado método: `discover_services()`
   - Adicionado método: `discover_disks()`
   - Usa WMI para listar todos os serviços e discos

4. **`probe/discovery_server.py`** (NOVO - FUTURO)
   - Servidor HTTP na probe para descoberta remota
   - Endpoints: `/discover/services` e `/discover/disks`
   - Permite descoberta em servidores remotos via WMI

### Frontend

5. **`frontend/src/components/Servers.js`** (JÁ IMPLEMENTADO)
   - Função `loadAvailableServices()` já existe
   - Função `loadAvailableDisks()` já existe
   - Dropdown com lista de serviços já funciona
   - Usa endpoint correto: `/api/v1/probe-commands/services/{server_id}`

## Como Funciona

### Para Servidor Local (onde a probe está instalada)

1. API detecta que é servidor local
2. Executa comando WMI localmente:
   ```batch
   wmic service get Name,DisplayName,State,StartMode /format:csv
   ```
3. Parse do resultado CSV
4. Retorna lista de serviços com:
   - `name`: Nome técnico (ex: "W3SVC")
   - `display_name`: Nome amigável (ex: "IIS Web Server")
   - `status`: Estado atual (running, stopped, paused)
   - `start_type`: Tipo de inicialização (auto, manual, disabled)

### Para Servidores Remotos (futuro)

1. API chama probe discovery server
2. Probe conecta via WMI remoto usando credenciais
3. Executa query WMI no servidor remoto
4. Retorna lista de serviços

## Exemplo de Resposta da API

```json
{
  "server_id": 1,
  "hostname": "DESKTOP-P9VGN04",
  "services": [
    {
      "name": "W3SVC",
      "display_name": "IIS Web Server",
      "status": "running",
      "start_type": "auto"
    },
    {
      "name": "MSSQLSERVER",
      "display_name": "SQL Server (MSSQLSERVER)",
      "status": "stopped",
      "start_type": "manual"
    },
    {
      "name": "Spooler",
      "display_name": "Print Spooler",
      "status": "running",
      "start_type": "auto"
    }
  ],
  "count": 3
}
```

## Interface do Usuário

### Modal "Adicionar Sensor"

1. Seleciona tipo: **Serviço do Windows**
2. Sistema carrega automaticamente lista de serviços
3. Mostra loading: "🔄 Carregando serviços..."
4. Exibe dropdown com serviços:
   ```
   ▼ Selecione um serviço
     🟢 IIS Web Server (W3SVC) - Running
     🔴 SQL Server (MSSQLSERVER) - Stopped
     🟢 Print Spooler (Spooler) - Running
     ...
   ```
5. Usuário seleciona serviço
6. Nome do sensor é preenchido automaticamente: `service_W3SVC`
7. Clica "Adicionar"
8. Sensor é criado e começa a monitorar

## Benefícios

✅ **Sem digitação manual** - Não precisa saber o nome técnico do serviço
✅ **Sem erros de digitação** - Seleciona da lista
✅ **Vê status atual** - Sabe se o serviço está rodando antes de adicionar
✅ **Descoberta automática** - Lista todos os serviços disponíveis
✅ **Tempo real** - Conecta na máquina e busca informações atualizadas

## Fallback

Se não conseguir conectar via WMI (sem credenciais ou erro), retorna lista padrão:
- W3SVC (IIS Web Server)
- MSSQLSERVER (SQL Server)
- MySQL (MySQL Server)
- Spooler (Print Spooler)
- EventLog (Windows Event Log)
- WinRM (Windows Remote Management)
- TermService (Remote Desktop Services)

## Próximos Passos

### Fase 1: Servidor Local (IMPLEMENTADO)
✅ Descoberta de serviços via WMI local
✅ Descoberta de discos via WMI local
✅ Endpoint na API
✅ Interface no frontend

### Fase 2: Servidores Remotos (FUTURO)
- [ ] Probe Discovery Server (porta 8002)
- [ ] WMI remoto com credenciais
- [ ] Integração API → Probe → WMI Remoto

### Fase 3: Melhorias (FUTURO)
- [ ] Cache de serviços descobertos (5 minutos)
- [ ] Filtro de busca na lista de serviços
- [ ] Ícones por tipo de serviço
- [ ] Indicador de serviços críticos
- [ ] Sugestões de serviços comuns por tipo de servidor

## Testando

1. Acesse http://localhost:3000
2. Vá em "Servidores"
3. Selecione seu servidor
4. Clique "Adicionar Sensor"
5. Selecione tipo: "Serviço do Windows"
6. Aguarde carregar a lista
7. Selecione um serviço
8. Clique "Adicionar"
9. Sensor criado com sucesso!

## Status

✅ Backend implementado
✅ WMI local funcionando
✅ Frontend já preparado
✅ Endpoint correto configurado
⏳ Aguardando teste do usuário
