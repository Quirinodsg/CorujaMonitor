# TOPOLOGIA DO SISTEMA CORUJA MONITOR

## 🖥️ MÁQUINAS

### 1. DESKTOP-P9VGN04 (Notebook com Kiro)
- **Função**: Desenvolvimento
- **Sistema**: Windows
- **Localização**: `C:\Users\andre.quirino\Coruja Monitor`
- **Uso**: Edição de código, Git, testes
- **NÃO é monitorada**

### 2. SRVSONDA001 (Máquina Windows)
- **Função**: Servidor monitorado + Probe
- **Sistema**: Windows
- **Localização Probe**: `C:\Program Files\CorujaMonitor\Probe`
- **Probe**: Instalada como serviço Windows
- **Token**: V-PTetiHvbNsZgrkY14PFGRfyv6jPBZxdTb76Z2M7YY
- **Envia métricas para**: SRVCMONITOR001:8000
- **É MONITORADA** ✓

### 3. SRVCMONITOR001 (Máquina Linux)
- **Função**: Servidor de aplicação (API + Frontend + Banco)
- **Sistema**: Linux
- **IP**: 192.168.31.161
- **Localização**: `/home/administrador/CorujaMonitor`
- **Serviços**:
  - API: Porta 8000 (Docker)
  - Frontend: Porta 3000 (Docker)
  - PostgreSQL: Porta 5432 (Docker)
- **Acesso**: Via PuTTY (SSH)

## 🔄 FLUXO DE DADOS

```
SRVSONDA001 (Probe)
    ↓ (coleta métricas a cada 60s)
    ↓ (envia via HTTP)
    ↓
SRVCMONITOR001:8000 (API)
    ↓ (armazena no banco)
    ↓
PostgreSQL (Docker)
    ↑ (consulta dados)
    ↑
SRVCMONITOR001:3000 (Frontend)
    ↑ (acesso via navegador)
    ↑
Usuário (http://192.168.31.161:3000)
```

## 📁 ESTRUTURA DE PASTAS

### DESKTOP-P9VGN04 (Desenvolvimento)
```
C:\Users\andre.quirino\Coruja Monitor\
├── api/                    # Backend (FastAPI)
├── frontend/               # Frontend (React)
├── probe/                  # Código da Probe
├── .git/                   # Repositório Git
└── [arquivos de config]
```

### SRVSONDA001 (Produção - Probe)
```
C:\Program Files\CorujaMonitor\Probe\
├── probe_core.py
├── config.yaml
├── collectors/
│   ├── disk_collector.py   # ← Precisa do filtro CD-ROM
│   ├── system_collector.py
│   └── [outros coletores]
└── logs/
```

### SRVCMONITOR001 (Produção - Servidor)
```
/home/administrador/CorujaMonitor/
├── api/                    # Backend (Docker)
├── frontend/               # Frontend (Docker)
├── docker-compose.yml
├── .git/                   # Repositório Git
└── [arquivos de config]
```

## 🔧 FLUXO DE ATUALIZAÇÃO

### 1. Desenvolvimento (DESKTOP-P9VGN04)
```bash
# Editar código
# Testar localmente
git add .
git commit -m "mensagem"
git push origin master
```

### 2. Servidor (SRVCMONITOR001)
```bash
git pull origin master
docker-compose restart api frontend
```

### 3. Probe (SRVSONDA001)
```
# Copiar arquivo manualmente:
# De: DESKTOP-P9VGN04
# Para: SRVSONDA001

# Reiniciar serviço
REINICIAR_PROBE_AGORA.bat
```

## 🎯 PROBLEMA ATUAL

### Disco D (CD-ROM) aparece como sensor
- **Onde**: SRVSONDA001
- **Causa**: `disk_collector.py` não filtra CD-ROM
- **Solução**: Atualizar `disk_collector.py` com filtros

### Exclusão via web não funciona
- **Erro**: "Sem resposta do servidor"
- **Causa**: Código de fallback não está no servidor
- **Solução**: Enviar correções para Git e atualizar servidor

## ✅ PLANO DE CORREÇÃO

1. **DESKTOP-P9VGN04**: Enviar correções para Git
2. **SRVCMONITOR001**: Fazer git pull e reiniciar containers
3. **SRVCMONITOR001**: Deletar sensor do banco
4. **SRVSONDA001**: Copiar `disk_collector.py` atualizado
5. **SRVSONDA001**: Reiniciar serviço da probe

## 📝 OBSERVAÇÕES

- DESKTOP-P9VGN04 e SRVSONDA001 são máquinas Windows diferentes
- SRVSONDA001 é a máquina que está sendo monitorada
- SRVCMONITOR001 é o servidor Linux que roda a aplicação
- Git está em DESKTOP-P9VGN04 e SRVCMONITOR001 (não em SRVSONDA001)
- Probe em SRVSONDA001 precisa ser atualizada manualmente

