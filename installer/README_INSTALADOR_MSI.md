# Instalador MSI - Coruja Monitor Probe

## 📦 Sobre o Instalador MSI

O instalador MSI (Microsoft Installer) é o formato padrão profissional para instalação de software no Windows. Oferece:

- ✅ Interface gráfica profissional
- ✅ Instalação/desinstalação limpa
- ✅ Suporte a GPO (Group Policy)
- ✅ Instalação silenciosa
- ✅ Rollback automático em caso de erro
- ✅ Registro no Painel de Controle
- ✅ Atualizações automáticas

## 🛠️ Pré-requisitos para Compilar

### 1. WiX Toolset
```
Download: https://github.com/wixtoolset/wix3/releases
Versão: 3.11 ou superior
```

Instale o WiX Toolset e reinicie o PowerShell.

### 2. Python 3.8+
O instalador MSI irá verificar se Python está instalado no sistema de destino.

## 🔨 Como Compilar o MSI

### Método 1: Script Automático (Recomendado)
```powershell
cd installer
.\build-msi.ps1
```

### Método 2: Com Versão Customizada
```powershell
.\build-msi.ps1 -Version "1.2.3"
```

### Método 3: Limpar e Recompilar
```powershell
.\build-msi.ps1 -Clean -Version "1.0.0"
```

### Método 4: Manual
```powershell
# Compilar
candle.exe CorujaProbe.wxs -ext WixUtilExtension -ext WixUIExtension

# Linkar
light.exe CorujaProbe.wixobj -out CorujaMonitorProbe.msi -ext WixUtilExtension -ext WixUIExtension
```

## 📥 Como Instalar

### Instalação Interativa (GUI)
```powershell
# Duplo clique no MSI ou:
msiexec /i CorujaMonitorProbe-1.0.0.msi
```

O instalador irá:
1. Mostrar tela de boas-vindas
2. Aceitar licença
3. Solicitar configurações:
   - IP do servidor Coruja
   - Token da probe
   - Tipo de instalação (Workgroup/Entra ID/Domain)
4. Escolher diretório de instalação
5. Instalar arquivos
6. Configurar sistema (usuário, firewall, WMI)
7. Criar atalhos

### Instalação Silenciosa
```powershell
# Instalação completamente silenciosa
msiexec /i CorujaMonitorProbe-1.0.0.msi /quiet /qn

# Com parâmetros
msiexec /i CorujaMonitorProbe-1.0.0.msi /quiet /qn ^
  API_IP=192.168.0.9 ^
  PROBE_TOKEN=seu-token-aqui ^
  INSTALL_TYPE=WORKGROUP
```

### Instalação com Log
```powershell
msiexec /i CorujaMonitorProbe-1.0.0.msi /l*v install.log
```

## 🗑️ Como Desinstalar

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
msiexec /x {PRODUCT-CODE-AQUI} /quiet
```

## 🔧 Parâmetros de Instalação

| Parâmetro | Descrição | Exemplo |
|-----------|-----------|---------|
| `API_IP` | IP do servidor Coruja | `192.168.0.9` |
| `PROBE_TOKEN` | Token de autenticação | `abc123...` |
| `INSTALL_TYPE` | Tipo de instalação | `WORKGROUP`, `ENTRAID`, `DOMAIN`, `REMOTE` |
| `DOMAIN_USER` | Usuário de domínio (se DOMAIN) | `DOMINIO\usuario` |
| `DOMAIN_PASS` | Senha de domínio (se DOMAIN) | `senha123` |
| `INSTALLFOLDER` | Diretório de instalação | `C:\Program Files\CorujaMonitor` |

### Exemplo Completo
```powershell
msiexec /i CorujaMonitorProbe-1.0.0.msi /quiet /qn ^
  API_IP=192.168.1.100 ^
  PROBE_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... ^
  INSTALL_TYPE=WORKGROUP ^
  INSTALLFOLDER="C:\Coruja"
```

## 🚀 Distribuição via GPO (Group Policy)

### 1. Copiar MSI para compartilhamento de rede
```powershell
copy CorujaMonitorProbe-1.0.0.msi \\servidor\compartilhamento\
```

### 2. Criar GPO
```
1. Abra Group Policy Management
2. Crie nova GPO: "Instalar Coruja Probe"
3. Edite a GPO
4. Computer Configuration → Policies → Software Settings → Software Installation
5. New → Package
6. Selecione o MSI do compartilhamento de rede
7. Escolha "Assigned"
```

### 3. Vincular GPO à OU
```
Vincule a GPO à OU que contém os computadores
```

### 4. Forçar atualização
```powershell
gpupdate /force
```

## 📋 O Que o Instalador Faz

### Durante a Instalação
1. ✅ Cria usuário `MonitorUser` com senha aleatória
2. ✅ Adiciona usuário aos grupos necessários
3. ✅ Configura Firewall para WMI
4. ✅ Habilita DCOM
5. ✅ Configura permissões WMI
6. ✅ Copia arquivos da probe
7. ✅ Cria arquivo `probe_config.json`
8. ✅ Cria arquivo `wmi_credentials.json`
9. ✅ Instala dependências Python
10. ✅ Cria serviço Windows (opcional)
11. ✅ Cria atalhos no Menu Iniciar
12. ✅ Cria atalho na Área de Trabalho (opcional)

### Durante a Desinstalação
1. ✅ Para o serviço (se existir)
2. ✅ Remove o serviço
3. ✅ Remove arquivos
4. ✅ Remove atalhos
5. ✅ Remove entradas do registro
6. ✅ Mantém logs e configurações (opcional)

## 📁 Estrutura de Arquivos Instalados

```
C:\Program Files\CorujaMonitor\
├── Probe\
│   ├── probe_core.py
│   ├── config.py
│   ├── requirements.txt
│   ├── probe_config.json
│   ├── wmi_credentials.json
│   └── collectors\
│       ├── system_collector.py
│       ├── ping_collector.py
│       ├── docker_collector.py
│       ├── snmp_collector.py
│       ├── kubernetes_collector.py
│       └── wmi_remote_collector.py
└── logs\
```

## 🔐 Segurança

### Credenciais
- Senha gerada aleatoriamente (16+ caracteres)
- Armazenada em `wmi_credentials.json` (permissões restritas)
- Usuário com privilégios mínimos necessários

### Firewall
- Apenas portas WMI necessárias
- Regras específicas para o serviço

### Permissões
- Instalação requer privilégios de administrador
- Arquivos protegidos contra modificação

## 🐛 Troubleshooting

### Erro: "WiX Toolset não encontrado"
```powershell
# Instale WiX Toolset
# https://github.com/wixtoolset/wix3/releases

# Verifique instalação
$env:WIX
```

### Erro: "Arquivos fonte não encontrados"
```powershell
# Verifique estrutura de diretórios
cd installer
ls ..\probe\*.py
```

### Erro: "Python não encontrado"
```powershell
# Instale Python 3.8+
# https://www.python.org/downloads/

# Verifique instalação
python --version
```

### Instalação falha silenciosamente
```powershell
# Execute com log
msiexec /i CorujaMonitorProbe-1.0.0.msi /l*v install.log

# Analise o log
notepad install.log
```

### Desinstalação não remove tudo
```powershell
# Remover manualmente
Remove-Item "C:\Program Files\CorujaMonitor" -Recurse -Force

# Remover serviço
sc delete CorujaProbe

# Remover usuário
net user MonitorUser /delete
```

## 📊 Comparação: MSI vs BAT

| Recurso | MSI | BAT |
|---------|-----|-----|
| Interface gráfica | ✅ Sim | ❌ Não |
| Instalação silenciosa | ✅ Sim | ⚠️ Limitado |
| Rollback automático | ✅ Sim | ❌ Não |
| GPO Support | ✅ Sim | ❌ Não |
| Painel de Controle | ✅ Sim | ❌ Não |
| Atualizações | ✅ Automático | ❌ Manual |
| Complexidade | ⚠️ Média | ✅ Simples |
| Tamanho | ⚠️ Maior | ✅ Menor |

## 🎯 Casos de Uso

### Para Empresas Pequenas (1-10 máquinas)
```powershell
# Use instalação interativa
# Duplo clique no MSI em cada máquina
```

### Para Empresas Médias (10-100 máquinas)
```powershell
# Use instalação silenciosa com script
$computers = Get-Content computers.txt
foreach ($computer in $computers) {
    Copy-Item CorujaMonitorProbe-1.0.0.msi "\\$computer\C$\Temp\"
    Invoke-Command -ComputerName $computer -ScriptBlock {
        msiexec /i C:\Temp\CorujaMonitorProbe-1.0.0.msi /quiet /qn
    }
}
```

### Para Empresas Grandes (100+ máquinas)
```powershell
# Use GPO (Group Policy)
# Veja seção "Distribuição via GPO"
```

## 📞 Suporte

Para problemas ou dúvidas:
1. Verifique os logs: `C:\Program Files\CorujaMonitor\logs\`
2. Execute com log: `msiexec /i ... /l*v install.log`
3. Consulte a documentação completa

## 🔄 Atualizações

Para atualizar uma instalação existente:
```powershell
# O MSI detecta versão anterior e atualiza automaticamente
msiexec /i CorujaMonitorProbe-1.1.0.msi
```

---

**Versão:** 1.0.0  
**Data:** 03 de Março de 2026  
**Autor:** Coruja Monitor Team
