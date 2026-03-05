# 🏗️ RECOMENDAÇÃO DE ARQUITETURA - Servidor e Probes

## 🎯 Resposta Direta

**✅ RECOMENDADO: Servidor Linux + Probes Windows**

Esta é a arquitetura ideal e mais comum em ambientes corporativos.

---

## 📊 Comparação de Arquiteturas

### Opção 1: Servidor Linux + Probes Windows ⭐ RECOMENDADO

```
┌─────────────────────────────────────────────────────────────┐
│                    SERVIDOR CENTRAL                         │
│                      (Linux)                                │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Frontend │  │   API    │  │ Database │  │ AI Agent │  │
│  │  React   │  │  FastAPI │  │ Postgres │  │  Ollama  │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
│                                                             │
│  Docker Compose - Ubuntu/Debian/CentOS                     │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTPS/REST API
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│ PROBE 1       │   │ PROBE 2       │   │ PROBE 3       │
│ (Windows)     │   │ (Windows)     │   │ (Windows)     │
│               │   │               │   │               │
│ • WMI         │   │ • WMI         │   │ • WMI         │
│ • SNMP        │   │ • SNMP        │   │ • SNMP        │
│ • Ping        │   │ • Ping        │   │ • Ping        │
│ • Serviços    │   │ • Serviços    │   │ • Serviços    │
└───────────────┘   └───────────────┘   └───────────────┘
  Filial SP           Filial RJ           Filial BH
```

**Vantagens:**
- ✅ Servidor Linux: Mais estável, seguro e performático
- ✅ Menor consumo de recursos no servidor
- ✅ Docker funciona melhor no Linux
- ✅ Custos menores (Linux é gratuito)
- ✅ Melhor para produção e alta disponibilidade
- ✅ Probes Windows: Acesso nativo a WMI e Active Directory
- ✅ Instalação MSI simplificada nas probes
- ✅ Integração perfeita com ambientes Windows corporativos

**Desvantagens:**
- ⚠️ Requer conhecimento básico de Linux
- ⚠️ Comandos diferentes (bash vs PowerShell)

---

### Opção 2: Servidor Windows + Probes Windows

```
┌─────────────────────────────────────────────────────────────┐
│                    SERVIDOR CENTRAL                         │
│                     (Windows Server)                        │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Frontend │  │   API    │  │ Database │  │ AI Agent │  │
│  │  React   │  │  FastAPI │  │ Postgres │  │  Ollama  │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
│                                                             │
│  Docker Desktop - Windows Server 2019/2022                 │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTPS/REST API
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│ PROBE 1       │   │ PROBE 2       │   │ PROBE 3       │
│ (Windows)     │   │ (Windows)     │   │ (Windows)     │
└───────────────┘   └───────────────┘   └───────────────┘
```

**Vantagens:**
- ✅ Ambiente 100% Windows (familiar para equipe Windows)
- ✅ Mesmos comandos PowerShell em todo ambiente
- ✅ Integração nativa com Active Directory
- ✅ Suporte Microsoft unificado

**Desvantagens:**
- ❌ Licença Windows Server (custo adicional)
- ❌ Maior consumo de recursos (RAM/CPU)
- ❌ Docker Desktop no Windows tem limitações
- ❌ Performance inferior ao Linux
- ❌ Menos estável para containers 24/7

---

### Opção 3: Servidor Linux + Probes Linux

```
┌─────────────────────────────────────────────────────────────┐
│                    SERVIDOR CENTRAL                         │
│                      (Linux)                                │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│ PROBE 1       │   │ PROBE 2       │   │ PROBE 3       │
│ (Linux)       │   │ (Linux)       │   │ (Linux)       │
│               │   │               │   │               │
│ • SNMP        │   │ • SNMP        │   │ • SNMP        │
│ • Ping        │   │ • Ping        │   │ • Ping        │
│ • SSH         │   │ • SSH         │   │ • SSH         │
│ ❌ WMI        │   │ ❌ WMI        │   │ ❌ WMI        │
└───────────────┘   └───────────────┘   └───────────────┘
```

**Vantagens:**
- ✅ Ambiente 100% Linux (open source)
- ✅ Sem custos de licenciamento
- ✅ Performance máxima

**Desvantagens:**
- ❌ SEM suporte a WMI (monitoramento Windows limitado)
- ❌ SEM integração nativa com Active Directory
- ❌ Não monitora serviços Windows nativamente
- ❌ Instalação mais complexa em ambientes Windows

---

## 🏆 Recomendação por Cenário

### Cenário 1: Ambiente Corporativo Windows (MAIS COMUM)

**Recomendação: Servidor Linux + Probes Windows** ⭐

```
Servidor: Ubuntu Server 22.04 LTS (VM ou físico)
Probes: Windows 10/11 ou Windows Server
```

**Por quê?**
- Maioria dos servidores corporativos são Windows
- Necessário monitorar WMI, Active Directory, serviços Windows
- Servidor Linux oferece melhor custo-benefício
- Probes Windows têm instalação MSI simplificada

**Exemplo:**
```
Empresa com:
- 50 servidores Windows
- 20 estações de trabalho Windows
- Active Directory
- Exchange, SQL Server, IIS

Solução:
- 1 servidor Linux (Ubuntu) com Docker
- 3-5 probes Windows distribuídas
```

---

### Cenário 2: Ambiente Misto (Windows + Linux)

**Recomendação: Servidor Linux + Probes Windows + Probes Linux**

```
Servidor: Ubuntu Server 22.04 LTS
Probes Windows: Para monitorar servidores Windows
Probes Linux: Para monitorar servidores Linux
```

**Por quê?**
- Flexibilidade para monitorar ambos os ambientes
- Servidor Linux centralizado
- Probes especializadas por plataforma

---

### Cenário 3: Ambiente 100% Linux (RARO)

**Recomendação: Servidor Linux + Probes Linux**

```
Servidor: Ubuntu Server 22.04 LTS
Probes: Ubuntu/Debian/CentOS
```

**Por quê?**
- Não há servidores Windows para monitorar
- Ambiente homogêneo
- Máxima performance

---

### Cenário 4: Teste/Desenvolvimento Local

**Recomendação: Tudo no Windows (Docker Desktop)**

```
Servidor: Windows 10/11 com Docker Desktop
Probe: Mesma máquina ou VMs locais
```

**Por quê?**
- Ambiente de desenvolvimento
- Fácil de configurar
- Não requer servidor dedicado

---

## 💰 Análise de Custos

### Servidor Linux (Ubuntu Server)

```
Hardware: R$ 5.000 - R$ 15.000 (servidor físico)
OU
VM Cloud: R$ 200 - R$ 800/mês (AWS/Azure/GCP)

Software:
- Ubuntu Server: GRATUITO
- Docker: GRATUITO
- PostgreSQL: GRATUITO
- Ollama: GRATUITO

Total: Apenas hardware/cloud
```

### Servidor Windows

```
Hardware: R$ 5.000 - R$ 15.000 (servidor físico)
OU
VM Cloud: R$ 300 - R$ 1.200/mês (AWS/Azure/GCP)

Software:
- Windows Server 2022: R$ 3.000 - R$ 6.000 (licença)
- Docker Desktop: GRATUITO (uso comercial requer licença)
- PostgreSQL: GRATUITO
- Ollama: GRATUITO

Total: Hardware + Licença Windows
```

**Economia com Linux: R$ 3.000 - R$ 6.000 iniciais**

---

## 🔧 Requisitos de Hardware

### Servidor Central (Recomendado)

**Pequeno (até 50 dispositivos):**
```
CPU: 4 cores
RAM: 8 GB
Disco: 100 GB SSD
Rede: 1 Gbps
```

**Médio (50-200 dispositivos):**
```
CPU: 8 cores
RAM: 16 GB
Disco: 250 GB SSD
Rede: 1 Gbps
```

**Grande (200-1000 dispositivos):**
```
CPU: 16 cores
RAM: 32 GB
Disco: 500 GB SSD
Rede: 10 Gbps
```

### Probe (Windows ou Linux)

```
CPU: 2 cores
RAM: 2 GB
Disco: 20 GB
Rede: 100 Mbps

Pode ser:
- VM leve
- Máquina física antiga
- Container (se Linux)
```

---

## 🚀 Guia de Instalação Recomendado

### PASSO 1: Instalar Servidor Linux

```bash
# Ubuntu Server 22.04 LTS

# 1. Atualizar sistema
sudo apt update && sudo apt upgrade -y

# 2. Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 3. Instalar Docker Compose
sudo apt install docker-compose-plugin -y

# 4. Criar usuário para Docker
sudo usermod -aG docker $USER

# 5. Clonar repositório
git clone https://github.com/seu-usuario/coruja-monitor.git
cd coruja-monitor

# 6. Configurar .env
cp .env.example .env
nano .env

# 7. Iniciar sistema
docker compose up -d

# 8. Verificar
docker ps
```

**Acesso:**
- Frontend: http://IP_SERVIDOR:3000
- API: http://IP_SERVIDOR:8000

---

### PASSO 2: Instalar Probes Windows

```powershell
# Em cada máquina Windows que será probe

# 1. Baixar instalador MSI
# https://github.com/seu-usuario/coruja-monitor/releases

# 2. Executar instalador
.\CorujaProbe-1.0.0.msi

# 3. Configurar durante instalação:
# - URL do servidor: http://IP_SERVIDOR:8000
# - Nome da probe: PROBE-FILIAL-SP
# - Tenant: empresa

# 4. Verificar serviço
Get-Service CorujaProbe

# 5. Testar conectividade
Test-NetConnection IP_SERVIDOR -Port 8000
```

---

## 📊 Comparação de Performance

### Servidor Linux vs Windows

| Métrica | Linux | Windows | Diferença |
|---------|-------|---------|-----------|
| Uso de RAM (idle) | 2 GB | 4 GB | -50% |
| Uso de CPU (idle) | 5% | 15% | -66% |
| Tempo de boot | 30s | 90s | -66% |
| Containers simultâneos | 100+ | 50 | +100% |
| Uptime médio | 99.9% | 99.5% | +0.4% |
| Custo de licença | R$ 0 | R$ 3.000+ | -100% |

---

## 🔒 Segurança

### Servidor Linux

**Vantagens:**
- ✅ Menos vulnerabilidades conhecidas
- ✅ Atualizações de segurança mais rápidas
- ✅ Firewall nativo (iptables/ufw)
- ✅ SELinux/AppArmor para isolamento
- ✅ Menos alvos de malware

**Configuração:**
```bash
# Firewall
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 8000/tcp  # API
sudo ufw enable

# Fail2ban (proteção contra brute force)
sudo apt install fail2ban -y
```

### Servidor Windows

**Vantagens:**
- ✅ Windows Defender integrado
- ✅ BitLocker para criptografia
- ✅ Integração com Active Directory

**Configuração:**
```powershell
# Firewall
New-NetFirewallRule -DisplayName "Coruja API" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "Coruja Frontend" -Direction Inbound -LocalPort 3000 -Protocol TCP -Action Allow
```

---

## 🎯 Decisão Final: Qual Escolher?

### Use Servidor Linux SE:

- ✅ Quer melhor performance
- ✅ Quer economizar em licenças
- ✅ Tem conhecimento básico de Linux
- ✅ Quer ambiente de produção robusto
- ✅ Planeja escalar para muitos dispositivos
- ✅ Quer máxima estabilidade 24/7

### Use Servidor Windows SE:

- ✅ Equipe só conhece Windows
- ✅ Já tem licença Windows Server
- ✅ Precisa de suporte Microsoft unificado
- ✅ Ambiente pequeno (< 50 dispositivos)
- ✅ Integração crítica com Active Directory no servidor

---

## 📋 Checklist de Decisão

```
[ ] Quantos dispositivos vou monitorar?
    < 50: Windows OK
    > 50: Linux recomendado

[ ] Qual o orçamento?
    Limitado: Linux (sem licença)
    Flexível: Ambos

[ ] Equipe tem conhecimento de Linux?
    Sim: Linux
    Não: Windows (mas vale aprender!)

[ ] Ambiente é majoritariamente Windows?
    Sim: Probes Windows (servidor pode ser Linux)
    Não: Probes Linux

[ ] Precisa de WMI/Active Directory?
    Sim: Probes Windows obrigatórias
    Não: Probes Linux OK

[ ] É produção ou teste?
    Produção: Linux recomendado
    Teste: Windows OK
```

---

## 🎉 Recomendação Final

### Para 90% dos casos:

```
✅ SERVIDOR: Ubuntu Server 22.04 LTS
✅ PROBES: Windows 10/11 ou Windows Server
✅ INSTALAÇÃO: Docker Compose no servidor
✅ INSTALAÇÃO PROBES: MSI automatizado
```

**Por quê?**
- Melhor custo-benefício
- Performance superior
- Estabilidade comprovada
- Probes Windows para monitorar ambiente corporativo
- Fácil de escalar
- Comunidade ativa

---

## 📞 Comandos Úteis

### Servidor Linux

```bash
# Ver status dos containers
docker ps

# Ver logs
docker logs coruja-api --tail 50

# Reiniciar sistema
docker compose restart

# Atualizar sistema
docker compose pull
docker compose up -d

# Backup
docker compose exec postgres pg_dump -U coruja coruja_monitor > backup.sql
```

### Servidor Windows

```powershell
# Ver status dos containers
docker ps

# Ver logs
docker logs coruja-api --tail 50

# Reiniciar sistema
docker-compose restart

# Atualizar sistema
docker-compose pull
docker-compose up -d
```

---

## 📚 Documentação Adicional

- `README.md` - Instalação geral
- `probe/INSTALACAO.md` - Instalação de probes
- `installer/README_INSTALADOR_MSI.md` - Instalador MSI
- `docs/architecture/ARQUITETURA_COMPLETA.md` - Arquitetura detalhada

---

**Data**: 04/03/2026  
**Status**: ✅ GUIA COMPLETO  
**Recomendação**: Servidor Linux + Probes Windows  
**Autor**: Kiro AI Assistant
