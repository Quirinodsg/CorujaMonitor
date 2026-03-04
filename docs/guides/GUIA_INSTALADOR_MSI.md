# 📦 Guia Completo - Instalador MSI Coruja Monitor

## 🎯 Visão Geral

Substituímos os instaladores .BAT por instaladores MSI profissionais que oferecem:

- ✅ Interface gráfica moderna
- ✅ Instalação silenciosa para GPO
- ✅ Rollback automático
- ✅ Registro no Painel de Controle
- ✅ Suporte a instalação em massa
- ✅ Atualizações automáticas

## 📋 Arquivos Criados

```
installer/
├── CorujaProbe.wxs              # Definição do instalador WiX
├── CustomActions.wxs            # Ações customizadas (usuário, firewall, etc)
├── build-msi.ps1                # Script para compilar o MSI
├── deploy-mass.ps1              # Script para instalação em massa
├── computers-example.txt        # Exemplo de lista de computadores
├── README_INSTALADOR_MSI.md     # Documentação completa
└── templates/
    └── probe_config.json        # Template de configuração
```

## 🚀 Início Rápido

### 1. Instalar WiX Toolset
```powershell
# Download
https://github.com/wixtoolset/wix3/releases

# Instale WiX Toolset 3.11+
# Reinicie o PowerShell após instalação
```

### 2. Compilar o MSI
```powershell
cd installer
.\build-msi.ps1
```

### 3. Instalar em Uma Máquina
```powershell
# Duplo clique no MSI ou:
msiexec /i output\CorujaMonitorProbe-1.0.0.msi
```

### 4. Instalar em Múltiplas Máquinas
```powershell
# Edite computers.txt com lista de máquinas
notepad computers.txt

# Execute instalação em massa
.\deploy-mass.ps1 -ComputersFile computers.txt `
                  -MsiPath output\CorujaMonitorProbe-1.0.0.msi `
                  -ApiIP 192.168.0.9 `
                  -ProbeToken "seu-token-aqui"
```

## 📊 Comparação: MSI vs BAT

| Recurso | MSI ✅ | BAT ❌ |
|---------|--------|--------|
| Interface gráfica | Sim | Não |
| Instalação silenciosa | Sim | Limitado |
| Rollback automático | Sim | Não |
| GPO Support | Sim | Não |
| Painel de Controle | Sim | Não |
| Atualizações | Automático | Manual |
| Instalação em massa | Sim | Difícil |
| Logs estruturados | Sim | Básico |

## 🎨 Recursos do Instalador MSI

### Durante a Instalação
1. ✅ Cria usuário `MonitorUser` com senha aleatória forte
2. ✅ Adiciona aos grupos: Administrators, Remote Management Users, Performance Monitor Users
3. ✅ Configura Firewall para WMI (portas 135, 1024-65535)
4. ✅ Habilita DCOM para acesso remoto
5. ✅ Configura permissões WMI
6. ✅ Instala arquivos da probe
7. ✅ Cria `probe_config.json` com configurações
8. ✅ Cria `wmi_credentials.json` com credenciais
9. ✅ Instala dependências Python (`pip install -r requirements.txt`)
10. ✅ Cria serviço Windows (opcional)
11. ✅ Cria atalhos no Menu Iniciar e Desktop

### Interface do Instalador
- Tela de boas-vindas
- Aceite de licença
- Configuração customizada:
  - IP do servidor Coruja
  - Token da probe
  - Tipo de instalação (Workgroup/Entra ID/Domain/Remote)
- Escolha de diretório
- Progresso visual
- Conclusão com resumo

## 🔧 Instalação Silenciosa

### Básica
```powershell
msiexec /i CorujaMonitorProbe-1.0.0.msi /quiet /qn
```

### Com Parâmetros
```powershell
msiexec /i CorujaMonitorProbe-1.0.0.msi /quiet /qn ^
  API_IP=192.168.0.9 ^
  PROBE_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... ^
  INSTALL_TYPE=WORKGROUP
```

### Com Log
```powershell
msiexec /i CorujaMonitorProbe-1.0.0.msi /l*v install.log
```

## 🏢 Instalação via GPO (Group Policy)

### Passo 1: Preparar MSI
```powershell
# Copiar MSI para compartilhamento de rede
copy CorujaMonitorProbe-1.0.0.msi \\servidor\compartilhamento\instaladores\
```

### Passo 2: Criar GPO
```
1. Abra Group Policy Management Console (gpmc.msc)
2. Crie nova GPO: "Instalar Coruja Monitor Probe"
3. Edite a GPO
4. Navegue: Computer Configuration → Policies → Software Settings → Software Installation
5. Clique direito → New → Package
6. Selecione: \\servidor\compartilhamento\instaladores\CorujaMonitorProbe-1.0.0.msi
7. Escolha: "Assigned" (instalação automática)
```

### Passo 3: Configurar Parâmetros (Opcional)
```
1. Clique direito no pacote → Properties
2. Aba "Modifications"
3. Adicione arquivo .MST com configurações
```

### Passo 4: Vincular GPO
```
1. Vincule a GPO à OU que contém os computadores
2. Aguarde replicação do AD
```

### Passo 5: Forçar Aplicação
```powershell
# Em cada computador ou remotamente
gpupdate /force
```

## 📦 Instalação em Massa

### Método 1: Script PowerShell (Recomendado)
```powershell
# Criar lista de computadores
@"
SERVER01
SERVER02
WS-TI-001
WS-TI-002
"@ | Out-File computers.txt

# Executar instalação
.\deploy-mass.ps1 -ComputersFile computers.txt `
                  -MsiPath output\CorujaMonitorProbe-1.0.0.msi `
                  -ApiIP 192.168.0.9 `
                  -ProbeToken "seu-token" `
                  -InstallType WORKGROUP
```

### Método 2: Paralelo (Mais Rápido)
```powershell
.\deploy-mass.ps1 -ComputersFile computers.txt `
                  -MsiPath output\CorujaMonitorProbe-1.0.0.msi `
                  -ApiIP 192.168.0.9 `
                  -ProbeToken "seu-token" `
                  -Parallel `
                  -MaxParallel 10
```

### Método 3: PDQ Deploy
```
1. Importe o MSI no PDQ Deploy
2. Configure parâmetros de instalação
3. Selecione computadores alvo
4. Execute deployment
```

## 🗑️ Desinstalação

### Método 1: Painel de Controle
```
Painel de Controle → Programas → Desinstalar um programa → Coruja Monitor Probe
```

### Método 2: Linha de Comando
```powershell
# Interativo
msiexec /x CorujaMonitorProbe-1.0.0.msi

# Silencioso
msiexec /x CorujaMonitorProbe-1.0.0.msi /quiet /qn
```

### Método 3: Por Product Code
```powershell
# Descobrir Product Code
wmic product where "name='Coruja Monitor Probe'" get IdentifyingNumber

# Desinstalar
msiexec /x {PRODUCT-CODE} /quiet
```

## 🔄 Atualizações

### Atualizar Versão Existente
```powershell
# O MSI detecta versão anterior e atualiza automaticamente
msiexec /i CorujaMonitorProbe-1.1.0.msi
```

### Forçar Reinstalação
```powershell
msiexec /i CorujaMonitorProbe-1.0.0.msi REINSTALL=ALL REINSTALLMODE=vomus
```

## 🐛 Troubleshooting

### Erro: "WiX Toolset não encontrado"
```powershell
# Solução: Instale WiX Toolset
https://github.com/wixtoolset/wix3/releases

# Verifique instalação
$env:WIX
```

### Erro: "Python não encontrado"
```powershell
# Solução: Instale Python 3.8+
https://www.python.org/downloads/

# Verifique
python --version
```

### Instalação falha silenciosamente
```powershell
# Solução: Execute com log detalhado
msiexec /i CorujaMonitorProbe-1.0.0.msi /l*v install.log

# Analise o log
notepad install.log
```

### Erro: "Acesso negado"
```powershell
# Solução: Execute como Administrador
# Clique direito → Executar como administrador
```

### Instalação em massa falha
```powershell
# Verifique conectividade
Test-Connection -ComputerName SERVER01

# Verifique permissões
# Usuário precisa ser admin local nas máquinas alvo

# Verifique firewall
# Portas WinRM (5985/5986) devem estar abertas
```

## 📁 Estrutura Pós-Instalação

```
C:\Program Files\CorujaMonitor\
├── Probe\
│   ├── probe_core.py
│   ├── config.py
│   ├── requirements.txt
│   ├── probe_config.json          # Configuração da probe
│   ├── wmi_credentials.json       # Credenciais do MonitorUser
│   └── collectors\
│       ├── system_collector.py
│       ├── ping_collector.py
│       ├── docker_collector.py
│       ├── snmp_collector.py
│       ├── kubernetes_collector.py
│       └── wmi_remote_collector.py
└── logs\
    └── probe.log

Menu Iniciar\Coruja Monitor\
├── Iniciar Coruja Probe
├── Configurar Probe
└── Desinstalar Coruja Probe

Desktop\
└── Coruja Probe (atalho)
```

## 🎯 Casos de Uso

### Pequena Empresa (1-10 máquinas)
```powershell
# Use instalação interativa
# Duplo clique no MSI em cada máquina
```

### Média Empresa (10-100 máquinas)
```powershell
# Use script de instalação em massa
.\deploy-mass.ps1 -ComputersFile computers.txt ...
```

### Grande Empresa (100+ máquinas)
```powershell
# Use GPO (Group Policy)
# Instalação automática em todas as máquinas do domínio
```

## 📞 Próximos Passos

1. ✅ Compile o MSI: `.\build-msi.ps1`
2. ✅ Teste em uma máquina: duplo clique no MSI
3. ✅ Configure GPO ou script de massa
4. ✅ Distribua para todas as máquinas

## 📚 Documentação Adicional

- `installer/README_INSTALADOR_MSI.md` - Documentação técnica completa
- `installer/CorujaProbe.wxs` - Código fonte do instalador
- `installer/CustomActions.wxs` - Ações customizadas

---

**Versão:** 1.0.0  
**Data:** 03 de Março de 2026  
**Status:** ✅ Pronto para produção
