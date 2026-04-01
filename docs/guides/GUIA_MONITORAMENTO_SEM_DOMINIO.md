# Monitoramento de Máquinas SEM Domínio (Workgroup)

## ✅ Sim, Funciona Perfeitamente!

O Coruja Monitor funciona em máquinas **sem domínio**, apenas na mesma rede. É o mesmo conceito do PRTG, Zabbix e CheckMK.

---

## 🏗️ Arquitetura

### Cenário: 2 Máquinas na Mesma Rede (Sem Domínio)

```
┌─────────────────────────────────────────────────────────┐
│                    Rede Local (LAN)                      │
│                  192.168.0.0/24                          │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────────────┐      ┌──────────────────────┐ │
│  │  Máquina A (Servidor)│      │  Máquina B (Cliente) │ │
│  │  192.168.0.100       │      │  192.168.0.101       │ │
│  │                      │      │                      │ │
│  │  ✓ Docker           │      │  ✓ Windows 10/11    │ │
│  │  ✓ Coruja API       │◄─────┤  ✓ Probe instalada  │ │
│  │  ✓ Coruja Frontend  │      │  ✓ WMI habilitado   │ │
│  │  ✓ PostgreSQL       │      │  ✓ Usuário local    │ │
│  │                      │      │     MonitorUser     │ │
│  └──────────────────────┘      └──────────────────────┘ │
│         ▲                                                │
│         │                                                │
│         └─── Acesso Web: http://192.168.0.100:3000      │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

---

## 🔧 Como Funciona

### 1. Máquina A (Servidor Coruja)
- Roda Docker com Coruja Monitor
- Tem a interface web
- Recebe métricas das probes

### 2. Máquina B (Monitorada)
- Instala probe Python
- Cria usuário local `MonitorUser`
- Habilita WMI para acesso remoto
- Probe coleta métricas localmente
- Envia para Máquina A via HTTP

---

## 📋 Instalação Passo a Passo

### Máquina A (Servidor Coruja) - Já Instalado ✓

Você já tem o servidor rodando em:
```
http://localhost:3000
```

### Máquina B (Cliente a Monitorar)

#### 1. Copie a Pasta `probe` para Máquina B

```
\\192.168.0.100\C$\Users\user\Coruja Monitor\probe
```

Copie para:
```
C:\Coruja Monitor\probe\
```

#### 2. Execute o Instalador (Como Administrador)

```bash
cd C:\Coruja Monitor\probe
install_workgroup.bat
```

**O instalador vai:**
1. ✓ Criar usuário local `MonitorUser` com senha forte
2. ✓ Adicionar aos grupos necessários (Administradores, Performance Monitor, etc)
3. ✓ Configurar Firewall para WMI
4. ✓ Configurar DCOM
5. ✓ Criar `wmi_credentials.json` com as credenciais
6. ✓ Criar `probe_config.json` apontando para Máquina A

#### 3. Configurar API URL

Quando o instalador perguntar:
```
Digite o IP do servidor Coruja Monitor:
IP (ex: 192.168.0.100): 192.168.0.100

Digite o token da probe:
Token: [copie da interface web]
```

#### 4. Instalar Python e Dependências

```bash
# Baixar Python 3.8+
https://www.python.org/downloads/

# Instalar dependências
pip install -r requirements.txt
```

#### 5. Iniciar Probe

```bash
python probe_core.py
```

---

## 🔐 Autenticação Sem Domínio

### Como Funciona?

Quando **não há domínio**, usamos **autenticação local**:

```json
// wmi_credentials.json na Máquina B
{
  "MAQUINA-B": {
    "username": "MonitorUser",
    "password": "senha_gerada_automaticamente",
    "domain": "MAQUINA-B"  // Nome do computador como "domínio"
  }
}
```

### Fluxo de Autenticação

1. Probe na Máquina B coleta métricas **localmente** (sem WMI remoto)
2. Probe envia métricas para API na Máquina A via HTTP
3. API armazena no PostgreSQL
4. Frontend mostra no dashboard

**Não precisa de WMI remoto entre máquinas!** Cada probe coleta localmente.

---

## 🌐 Monitoramento Remoto (Opcional)

Se você quiser que a **Máquina A monitore a Máquina B remotamente** (sem instalar probe):

### 1. Na Máquina B (Monitorada)

Execute `install_workgroup.bat` - ele vai:
- Criar usuário `MonitorUser`
- Habilitar WMI remoto
- Configurar firewall
- Gerar credenciais

### 2. Na Máquina A (Servidor)

Adicione as credenciais da Máquina B:

```json
// probe/wmi_credentials.json na Máquina A
{
  "192.168.0.101": {
    "username": "MonitorUser",
    "password": "senha_da_maquina_b",
    "domain": "MAQUINA-B"
  }
}
```

### 3. Adicione Servidor na Interface

1. Acesse http://192.168.0.100:3000
2. Vá em "Servidores" → "+ Adicionar Servidor"
3. Configure:
   - Hostname: MAQUINA-B
   - IP: 192.168.0.101
   - Protocolo: WMI
   - Credenciais: Serão lidas do arquivo JSON

---

## 🔥 Firewall - Portas Necessárias

### Máquina A (Servidor)
```
Entrada:
  - 3000/TCP (Frontend)
  - 8000/TCP (API)

Saída:
  - Todas (para coletar WMI remoto, se usar)
```

### Máquina B (Cliente)
```
Entrada:
  - 135/TCP (WMI/DCOM)
  - 1024-65535/TCP (WMI dinâmico)

Saída:
  - 8000/TCP (para enviar métricas à API)
```

### Configurar Firewall Windows

```bash
# Na Máquina B (já feito pelo instalador)
netsh advfirewall firewall set rule group="Windows Management Instrumentation (WMI)" new enable=yes
```

---

## ✅ Vantagens Sem Domínio

1. **Mais Simples**: Não precisa de Active Directory
2. **Mais Seguro**: Cada máquina tem seu próprio usuário local
3. **Mais Flexível**: Funciona em qualquer rede (casa, escritório, cloud)
4. **Igual ao PRTG**: Mesmo conceito dos grandes players

---

## 📊 Cenários de Uso

### Cenário 1: Probe Local (Recomendado)
```
Máquina B:
  - Instala probe
  - Coleta métricas localmente
  - Envia para Máquina A via HTTP
  
Vantagens:
  ✓ Mais rápido
  ✓ Menos tráfego de rede
  ✓ Funciona mesmo com firewall restritivo
```

### Cenário 2: WMI Remoto (Opcional)
```
Máquina A:
  - Probe conecta via WMI à Máquina B
  - Coleta métricas remotamente
  - Armazena no banco
  
Vantagens:
  ✓ Não precisa instalar nada na Máquina B
  ✓ Centralizado
  
Desvantagens:
  ✗ Precisa configurar WMI remoto
  ✗ Mais tráfego de rede
  ✗ Firewall precisa estar aberto
```

---

## 🧪 Teste de Conectividade

### Da Máquina B para Máquina A (API)

```bash
# Testar se API está acessível
curl http://192.168.0.100:8000/health

# Ou no navegador
http://192.168.0.100:8000/health
```

### Da Máquina A para Máquina B (WMI Remoto)

```bash
# Testar WMI remoto
wmic /node:192.168.0.101 /user:MonitorUser /password:senha computersystem get name
```

---

## 🆘 Troubleshooting

### Probe não conecta à API?
```bash
# Verificar se API está rodando
curl http://192.168.0.100:8000/health

# Verificar firewall
netsh advfirewall show allprofiles state

# Verificar probe_config.json
type probe_config.json
```

### WMI remoto não funciona?
```bash
# Verificar se WMI está habilitado
sc query winmgmt

# Verificar firewall
netsh advfirewall firewall show rule name=all | findstr WMI

# Testar localmente primeiro
wmic computersystem get name
```

### Credenciais não funcionam?
```bash
# Verificar se usuário existe
net user MonitorUser

# Verificar grupos
net user MonitorUser | findstr "Local Group"

# Resetar senha
net user MonitorUser nova_senha
```

---

## 📝 Resumo

### ✅ Funciona SEM Domínio?
**SIM!** Perfeitamente.

### ✅ Precisa de Active Directory?
**NÃO!** Funciona com usuários locais.

### ✅ Funciona em Workgroup?
**SIM!** É o cenário padrão.

### ✅ Precisa de VPN?
**NÃO!** Apenas mesma rede local.

### ✅ Funciona via Internet?
**SIM!** Basta abrir portas no roteador (não recomendado sem VPN).

---

## 🚀 Instaladores Disponíveis

1. **install_workgroup.bat** (NOVO) ✅
   - Para máquinas SEM domínio
   - Cria usuário local
   - Configura WMI local
   - Ideal para seu cenário

2. **install_automated.bat** (Antigo)
   - Para máquinas COM domínio
   - Usa usuário de domínio
   - Requer Active Directory

3. **install_remote.bat**
   - Para monitoramento remoto via WMI
   - Não instala probe
   - Apenas configura WMI remoto

---

**Use `install_workgroup.bat` para suas máquinas sem domínio!** 🎉
