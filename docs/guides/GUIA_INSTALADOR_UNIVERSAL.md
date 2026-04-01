# Guia: Instalador Universal Coruja Monitor

## 🎯 Um Instalador para Todos os Cenários

O instalador universal (`install.bat`) detecta automaticamente o tipo de máquina e oferece todas as opções em um único arquivo.

---

## 📍 Localização

```
probe/install.bat
```

**Caminho completo**:
```
C:\Users\user\Coruja Monitor\probe\install.bat
```

---

## 🚀 Como Usar

### Passo 1: Executar como Administrador

```bash
cd C:\Coruja Monitor\probe
install.bat
```

**Ou**: Clique com botão direito → "Executar como administrador"

---

### Passo 2: Escolher Opção

```
========================================
  CORUJA MONITOR - INSTALADOR UNIVERSAL
========================================

Escolha o tipo de instalacao:

1. Workgroup (Sem dominio)
   - Maquinas em workgroup
   - Rede local simples
   - Usuario local

2. Entra ID / Azure AD
   - Maquinas joined ao Entra ID
   - Microsoft 365 / Azure
   - Usuario local para WMI

3. Active Directory (Dominio)
   - Dominio AD tradicional
   - On-premises
   - Usuario de dominio

4. WMI Remoto (Sem probe)
   - Apenas configurar WMI remoto
   - Nao instala probe
   - Para monitoramento centralizado

5. Detectar Automaticamente
   - Sistema detecta o tipo
   - Recomendado se nao souber

0. Sair

========================================
Digite sua opcao (0-5):
```

---

## 📋 Opções Detalhadas

### Opção 1: Workgroup (Sem Domínio)

**Quando usar:**
- ✅ Máquina em workgroup
- ✅ Rede local simples
- ✅ Sem Active Directory
- ✅ Sem Entra ID

**O que faz:**
1. Cria usuário local `MonitorUser`
2. Configura WMI, DCOM, Firewall
3. Cria `wmi_credentials.json`
4. Cria `probe_config.json`

---

### Opção 2: Entra ID / Azure AD

**Quando usar:**
- ✅ Máquina joined ao Entra ID
- ✅ Microsoft 365 / Azure
- ✅ Autenticação cloud

**O que faz:**
1. Detecta vinculação ao Entra ID
2. Cria usuário local para WMI
3. Configura tudo automaticamente
4. Mostra status do Entra ID

---

### Opção 3: Active Directory (Domínio)

**Quando usar:**
- ✅ Máquina em domínio AD
- ✅ Active Directory on-premises
- ✅ Quer usar usuário de domínio

**O que faz:**
1. Solicita usuário de domínio
2. Configura WMI com credenciais AD
3. Cria arquivos de configuração
4. Testa conectividade

---

### Opção 4: WMI Remoto (Sem Probe)

**Quando usar:**
- ✅ Apenas configurar WMI remoto
- ✅ Não quer instalar probe
- ✅ Monitoramento centralizado

**O que faz:**
1. Configura Firewall para WMI
2. Configura DCOM
3. Testa WMI local
4. **NÃO** instala probe Python

---

### Opção 5: Detectar Automaticamente ⭐ RECOMENDADO

**Quando usar:**
- ✅ Não sabe qual opção escolher
- ✅ Quer que o sistema decida
- ✅ Primeira instalação

**O que faz:**
1. Verifica se está no Entra ID
2. Verifica se está em domínio AD
3. Se nenhum, assume Workgroup
4. Pede confirmação antes de instalar

---

## 🎯 Fluxo de Detecção Automática

```
Detectar Automaticamente
│
├─ Verifica Entra ID (dsregcmd /status)
│  └─ AzureAdJoined: YES?
│     └─ SIM → Instalar Entra ID
│
├─ Verifica Domínio AD (wmic computersystem)
│  └─ Domain != WORKGROUP?
│     └─ SIM → Instalar Domínio
│
└─ Nenhum detectado
   └─ Instalar Workgroup
```

---

## 📊 Comparação das Opções

| Opção | Usuário | WMI | Probe | Uso |
|-------|---------|-----|-------|-----|
| 1. Workgroup | Local | Sim | Sim | Rede simples |
| 2. Entra ID | Local | Sim | Sim | Microsoft 365 |
| 3. Domínio AD | Domínio | Sim | Sim | AD tradicional |
| 4. WMI Remoto | - | Sim | Não | Apenas WMI |
| 5. Auto | Detecta | Sim | Sim | Recomendado |

---

## 🔧 O Que Cada Instalação Faz

### Todas as Opções (1, 2, 3)
1. ✓ Verificar privilégios de administrador
2. ✓ Criar/configurar usuário
3. ✓ Adicionar aos grupos necessários
4. ✓ Configurar Firewall para WMI
5. ✓ Configurar DCOM
6. ✓ Configurar segurança WMI
7. ✓ Criar `wmi_credentials.json`
8. ✓ Criar `probe_config.json`
9. ✓ Testar WMI local

### Opção 4 (WMI Remoto)
1. ✓ Configurar Firewall
2. ✓ Configurar DCOM
3. ✓ Testar WMI
4. ❌ NÃO cria usuário
5. ❌ NÃO instala probe

---

## 📝 Exemplo de Uso

### Cenário 1: Não Sei Qual Usar

```bash
# Execute o instalador
install.bat

# Escolha opção 5 (Detectar Automaticamente)
Digite sua opcao: 5

# Sistema detecta e pergunta
[DETECTADO] Entra ID (Azure AD)
Confirma instalacao para Entra ID? (S/N): S

# Instalação prossegue automaticamente
```

---

### Cenário 2: Sei que é Entra ID

```bash
# Execute o instalador
install.bat

# Escolha opção 2
Digite sua opcao: 2

# Configure quando perguntar
IP do servidor: 192.168.0.9
Token: [cole o token]

# Pronto!
```

---

### Cenário 3: Apenas WMI Remoto

```bash
# Execute o instalador
install.bat

# Escolha opção 4
Digite sua opcao: 4

# Apenas configura WMI, não instala probe
```

---

## 🆘 Troubleshooting

### Erro: "Execute como Administrador"
```
Solução:
Clique com botão direito no install.bat
Escolha "Executar como administrador"
```

### Erro: "Opção inválida"
```
Solução:
Digite apenas o número (0-5)
Não digite letras ou símbolos
```

### Detecção automática não funciona
```
Solução:
Use opção manual (1, 2 ou 3)
Escolha baseado no seu cenário
```

### Instalação falha no meio
```
Solução:
1. Anote em qual passo falhou
2. Execute novamente
3. Escolha mesma opção
4. Instalador pula passos já feitos
```

---

## 🎯 Qual Opção Escolher?

### Use Opção 1 (Workgroup) se:
- ❌ Não tem domínio
- ❌ Não tem Entra ID
- ✅ Rede local simples

### Use Opção 2 (Entra ID) se:
- ✅ Usa Microsoft 365
- ✅ Máquinas no Azure AD
- ✅ Autenticação cloud

### Use Opção 3 (Domínio) se:
- ✅ Tem Active Directory
- ✅ Servidor de domínio local
- ✅ Usuários DOMINIO\usuario

### Use Opção 4 (WMI Remoto) se:
- ✅ Não quer instalar probe
- ✅ Monitoramento centralizado
- ✅ Apenas configurar WMI

### Use Opção 5 (Auto) se:
- ❓ Não sabe qual usar
- ✅ Primeira vez
- ✅ Quer que sistema decida

---

## 📚 Arquivos Criados

Após instalação, você terá:

```
C:\Coruja Monitor\probe\
├── probe_config.json          ← Configuração da probe
├── wmi_credentials.json       ← Credenciais WMI
├── probe_core.py              ← Código da probe
├── collectors/                ← Coletores de métricas
├── requirements.txt           ← Dependências Python
└── logs/                      ← Logs (criado ao iniciar)
```

---

## 🚀 Próximos Passos

Após instalação:

### 1. Instalar Python
```
https://www.python.org/downloads/
Marcar "Add Python to PATH"
```

### 2. Instalar Dependências
```bash
cd C:\Coruja Monitor\probe
pip install -r requirements.txt
```

### 3. Iniciar Probe
```bash
python probe_core.py
```

### 4. Verificar no Dashboard
```
http://192.168.0.9:3000
Servidores → Aguardar 2-3 minutos
```

---

## 🔗 Documentação Relacionada

- `PASSO_A_PASSO_NOVA_EMPRESA.md` - Criar empresa e máquina
- `GUIA_RAPIDO_INSTALACAO.md` - Guia rápido
- `GUIA_ENTRA_ID_AZURE_AD.md` - Específico Entra ID
- `GUIA_INSTALADOR_DOMINIO.md` - Específico Domínio
- `GUIA_MONITORAMENTO_SEM_DOMINIO.md` - Específico Workgroup

---

## ✅ Vantagens do Instalador Universal

1. **Um Único Arquivo**: Não precisa escolher qual baixar
2. **Menu Interativo**: Fácil de usar
3. **Detecção Automática**: Sistema decide por você
4. **Todas as Opções**: Workgroup, Entra ID, Domínio, WMI
5. **Validação**: Verifica privilégios e configuração
6. **Feedback**: Mostra progresso em cada passo

---

**Use `install.bat` - Um instalador para todos os cenários!** 🚀
