# Guia: Monitoramento com Entra ID (Azure AD)

## 🎯 Seu Cenário

Sua empresa usa:
- ✅ **Entra ID** (antigo Azure AD)
- ✅ Máquinas **joined** ao Entra ID
- ❌ **SEM** domínio Active Directory local tradicional
- ✅ Autenticação via Microsoft 365 / Azure

---

## 📍 Instalador Específico

```
probe/install_entraid.bat
```

**Caminho completo**:
```
C:\Users\user\Coruja Monitor\probe\install_entraid.bat
```

---

## 🔍 Entendendo o Cenário

### Entra ID (Azure AD) vs Active Directory Tradicional

| Aspecto | AD Tradicional | Entra ID (Azure AD) |
|---------|----------------|---------------------|
| Localização | On-premises | Cloud (Azure) |
| Autenticação | Servidor local | Microsoft 365 |
| Usuários | DOMINIO\usuario | usuario@empresa.com |
| WMI | Usuário de domínio | **Usuário local** ⚠️ |
| GPO | Sim | Intune |

---

## ⚠️ Importante: WMI com Entra ID

### Por que usar usuário local?

**Entra ID não suporta WMI diretamente!**

```
❌ NÃO FUNCIONA:
   usuario@empresa.com para WMI

✅ FUNCIONA:
   Usuário LOCAL na máquina
```

### Solução

O instalador cria um **usuário local** `MonitorUser` na máquina, mesmo ela estando no Entra ID. Isso é:
- ✅ Normal
- ✅ Seguro
- ✅ Recomendado pela Microsoft
- ✅ Usado por PRTG, Zabbix, etc

---

## 🚀 Como Usar

### Passo 1: Verificar se Máquina está no Entra ID

Abra PowerShell e execute:
```powershell
dsregcmd /status
```

Procure por:
```
AzureAdJoined : YES  ← Máquina no Entra ID
DomainJoined : NO    ← Sem domínio local
```

---

### Passo 2: Copiar Pasta Probe

Copie a pasta `probe` para a máquina:
```
De: C:\Users\user\Coruja Monitor\probe\
Para: C:\Coruja Monitor\probe\ (na máquina cliente)
```

---

### Passo 3: Executar Instalador (Como Administrador)

```bash
cd C:\Coruja Monitor\probe
install_entraid.bat
```

---

### Passo 4: Configurar

O instalador vai perguntar:

```
IP do servidor: 192.168.0.9
Token: [cole o token da interface web]
```

---

### Passo 5: Instalar Python e Dependências

```bash
# Baixar Python: https://www.python.org/downloads/
# Marcar "Add Python to PATH"

pip install -r requirements.txt
```

---

### Passo 6: Iniciar Probe

```bash
python probe_core.py
```

---

## 🔐 Segurança com Entra ID

### Usuário Local vs Entra ID

```
┌─────────────────────────────────────────────────┐
│         Máquina no Entra ID                      │
├─────────────────────────────────────────────────┤
│                                                   │
│  👤 Usuários Entra ID (Cloud)                   │
│     └─ usuario@empresa.com                       │
│        └─ Login Windows ✓                        │
│        └─ Microsoft 365 ✓                        │
│        └─ WMI ❌ (não suportado)                │
│                                                   │
│  👤 Usuário Local (Máquina)                     │
│     └─ MonitorUser                               │
│        └─ Login Windows ✓                        │
│        └─ WMI ✓ (funciona!)                     │
│        └─ Apenas para monitoramento              │
│                                                   │
└─────────────────────────────────────────────────┘
```

### Boas Práticas

1. **Senha Forte**: Gerada automaticamente pelo instalador
2. **Permissões Mínimas**: Apenas leitura + WMI
3. **Auditoria**: Logs de acesso WMI
4. **Rotação**: Trocar senha periodicamente

---

## 🌐 Arquitetura Entra ID

```
┌─────────────────────────────────────────────────┐
│              Microsoft Cloud                     │
│         Entra ID (Azure AD)                      │
│                                                   │
│  👥 Usuários: usuario@empresa.com               │
│  🔐 Autenticação: Microsoft 365                 │
│  📱 Intune: Gerenciamento de dispositivos       │
│                                                   │
└──────────────────┬──────────────────────────────┘
                   │
                   │ Internet
                   │
┌──────────────────▼──────────────────────────────┐
│           Rede Local (192.168.0.0/24)           │
├─────────────────────────────────────────────────┤
│                                                   │
│  ┌────────────────┐      ┌────────────────────┐ │
│  │ Servidor Coruja│      │ Máquina Entra ID   │ │
│  │ 192.168.0.9    │      │ 192.168.0.X        │ │
│  │                │      │                    │ │
│  │ ✓ Docker       │◄─────┤ ✓ Entra ID Join   │ │
│  │ ✓ API          │      │ ✓ Probe Python    │ │
│  │ ✓ Frontend     │      │ ✓ Usuario Local   │ │
│  │                │      │   MonitorUser      │ │
│  └────────────────┘      └────────────────────┘ │
│                                                   │
└─────────────────────────────────────────────────┘
```

---

## 🔧 Diferenças dos Instaladores

### install_entraid.bat (Seu Caso) ⭐
```
✓ Máquinas no Entra ID (Azure AD)
✓ Cria usuário LOCAL
✓ Detecta tipo de join
✓ Mostra status Entra ID
✓ Configuração híbrida
```

### install_workgroup.bat
```
✓ Máquinas sem domínio
✓ Workgroup simples
✓ Cria usuário LOCAL
✓ Sem Entra ID
```

### install_automated.bat
```
✓ Active Directory tradicional
✓ Usa usuário de DOMÍNIO
✓ On-premises
✓ Não funciona com Entra ID
```

---

## 🧪 Testar Instalação

### 1. Verificar Status Entra ID
```powershell
dsregcmd /status
```

Deve mostrar:
```
AzureAdJoined : YES
DomainJoined : NO
```

### 2. Verificar Usuário Local
```bash
net user MonitorUser
```

### 3. Testar WMI Local
```bash
wmic computersystem get name,domain
```

### 4. Testar Conectividade
```bash
ping 192.168.0.9
curl http://192.168.0.9:8000/health
```

### 5. Iniciar Probe
```bash
python probe_core.py
```

---

## 🆘 Troubleshooting Entra ID

### Erro: "Usuário não pode fazer login"
```
Solução:
O usuário MonitorUser é APENAS para WMI, não para login.
Usuários Entra ID continuam fazendo login normalmente.
```

### Erro: "WMI não funciona com usuario@empresa.com"
```
Solução:
Correto! Use o usuário local MonitorUser criado pelo instalador.
Entra ID não suporta WMI diretamente.
```

### Erro: "Máquina não aparece no dashboard"
```
Solução:
1. Verificar se probe está rodando
2. Aguardar 2-3 minutos
3. Verificar logs da probe
4. Testar conectividade com API
```

### Erro: "Intune bloqueia usuário local"
```
Solução:
Configure política no Intune para permitir usuário local
para monitoramento. Ou use exceção para MonitorUser.
```

---

## 📊 Intune + Coruja Monitor

### Gerenciamento Híbrido

```
Intune (Cloud)
  └─ Gerenciamento de dispositivos
  └─ Políticas de segurança
  └─ Aplicativos

Coruja Monitor (On-premises)
  └─ Monitoramento de performance
  └─ Métricas em tempo real
  └─ Alertas e incidentes
```

### Complementares, não concorrentes!

- **Intune**: Gerencia configuração e segurança
- **Coruja**: Monitora performance e disponibilidade

---

## 🎯 Recomendações para Entra ID

### 1. Use install_entraid.bat
Específico para seu cenário, detecta Entra ID automaticamente.

### 2. Configure Intune
Permita usuário local MonitorUser para monitoramento.

### 3. Rotação de Senha
Configure rotação periódica da senha do MonitorUser.

### 4. Auditoria
Monitore acessos WMI nos logs do Windows.

### 5. Conditional Access
Configure políticas de acesso condicional no Entra ID.

---

## 📝 Checklist Entra ID

### Pré-instalação
- [ ] Verificar máquina está no Entra ID: `dsregcmd /status`
- [ ] Verificar conectividade com 192.168.0.9
- [ ] Copiar pasta probe

### Instalação
- [ ] Executar install_entraid.bat (como Admin)
- [ ] Configurar IP: 192.168.0.9
- [ ] Configurar token da probe
- [ ] Anotar senha do MonitorUser

### Pós-instalação
- [ ] Instalar Python
- [ ] Instalar dependências
- [ ] Iniciar probe
- [ ] Verificar no dashboard
- [ ] Configurar Intune (se necessário)

---

## 🔗 Arquivos Relacionados

- `probe/install_entraid.bat` ⭐ Use este!
- `probe/install_workgroup.bat` - Sem domínio
- `probe/install_automated.bat` - AD tradicional
- `PASSO_A_PASSO_NOVA_EMPRESA.md` - Criar empresa

---

## 💡 Resumo

```
Sua empresa: Entra ID (Azure AD)
Instalador: install_entraid.bat
Usuário WMI: Local (MonitorUser)
Autenticação: Híbrida (Entra ID + Local)
```

**Use `install_entraid.bat` para máquinas no Entra ID!** 🚀
