# Guia: Instalador para Máquinas COM Domínio

## 📍 Localização

```
probe/install_automated.bat
```

**Caminho completo**:
```
C:\Users\user\Coruja Monitor\probe\install_automated.bat
```

---

## 🎯 Quando Usar

Use este instalador se a máquina:
- ✅ Está em um domínio Active Directory
- ✅ Tem usuários de domínio
- ✅ Ambiente corporativo com AD

---

## 🚀 Como Usar

### Passo 1: Copiar Pasta Probe

Copie a pasta `probe` para a máquina cliente:
```
De: C:\Users\user\Coruja Monitor\probe\
Para: C:\Coruja Monitor\probe\ (na máquina cliente)
```

---

### Passo 2: Executar Instalador (Como Administrador)

Na máquina cliente, abra CMD como Administrador:

```bash
cd C:\Coruja Monitor\probe
install_automated.bat
```

---

### Passo 3: Configurar

O instalador vai perguntar:

```
Digite o IP do servidor Coruja Monitor:
IP: 192.168.0.9

Digite o token da probe:
Token: [cole o token da interface web]

Digite o usuário de domínio (ex: DOMINIO\usuario):
Usuário: DOMINIO\MonitorUser

Digite a senha:
Senha: ********
```

---

## 🔧 O Que o Instalador Faz

1. ✓ Verifica privilégios de administrador
2. ✓ Cria usuário de domínio `MonitorUser` (se não existir)
3. ✓ Adiciona aos grupos necessários:
   - Administradores
   - Performance Monitor Users
   - Distributed COM Users
   - Remote Management Users
4. ✓ Configura Firewall para WMI
5. ✓ Configura DCOM
6. ✓ Cria `probe_config.json`
7. ✓ Cria `wmi_credentials.json` com credenciais de domínio
8. ✓ Testa WMI local
9. ✓ Cria tarefa agendada (opcional)

---

## 📋 Diferenças vs Workgroup

### install_automated.bat (Domínio)
```json
// wmi_credentials.json
{
  "MAQUINA-01": {
    "username": "MonitorUser",
    "password": "senha",
    "domain": "EMPRESA"  ← Domínio AD
  }
}
```

### install_workgroup.bat (Sem Domínio)
```json
// wmi_credentials.json
{
  "MAQUINA-01": {
    "username": "MonitorUser",
    "password": "senha",
    "domain": "MAQUINA-01"  ← Nome da máquina
  }
}
```

---

## ⚠️ Pré-requisitos (Domínio)

### No Active Directory:

1. **Criar usuário de domínio** (se não existir):
```
Nome: MonitorUser
Domínio: EMPRESA
Senha: [senha forte]
```

2. **Adicionar aos grupos**:
- Domain Admins (ou)
- Grupo customizado com permissões WMI

3. **Configurar GPO** (opcional):
- Habilitar WMI remoto
- Configurar firewall
- Permitir acesso DCOM

---

## 🔐 Segurança em Domínio

### Opção 1: Usuário de Domínio Dedicado (Recomendado)
```
Usuário: EMPRESA\MonitorUser
Permissões: Apenas leitura + WMI
Grupos: Performance Monitor Users, Distributed COM Users
```

### Opção 2: Conta de Serviço (Produção)
```
Usuário: EMPRESA\svc_monitor
Tipo: Managed Service Account (MSA)
Permissões: Mínimas necessárias
```

### Opção 3: Group Managed Service Account (Melhor)
```
Usuário: EMPRESA\gMSA_Monitor
Tipo: gMSA
Rotação automática de senha
```

---

## 🌐 Monitoramento Multi-Domínio

Se você tem múltiplos domínios:

### Opção A: Trust entre Domínios
```
DOMINIO-A ←→ Trust ←→ DOMINIO-B
Use usuário de um domínio para monitorar ambos
```

### Opção B: Usuário Local em Cada Domínio
```
DOMINIO-A\MonitorUser → Monitora DOMINIO-A
DOMINIO-B\MonitorUser → Monitora DOMINIO-B
```

### Opção C: Probe em Cada Domínio
```
Probe-A → Monitora DOMINIO-A
Probe-B → Monitora DOMINIO-B
Ambas enviam para mesmo servidor Coruja
```

---

## 🧪 Testar Instalação

### 1. Testar WMI Local
```bash
wmic computersystem get name,domain
```

### 2. Testar WMI Remoto (de outra máquina)
```bash
wmic /node:MAQUINA-01 /user:EMPRESA\MonitorUser /password:senha computersystem get name
```

### 3. Testar Conectividade com API
```bash
curl http://192.168.0.9:8000/health
```

### 4. Iniciar Probe
```bash
cd C:\Coruja Monitor\probe
python probe_core.py
```

---

## 🆘 Troubleshooting Domínio

### Erro: "Usuário não encontrado"
```
Solução:
1. Verificar se usuário existe no AD
2. Usar formato correto: DOMINIO\usuario
3. Verificar se domínio está acessível
```

### Erro: "Acesso negado"
```
Solução:
1. Verificar permissões do usuário
2. Adicionar aos grupos necessários
3. Verificar GPO não está bloqueando
```

### Erro: "Domínio não acessível"
```
Solução:
1. Verificar conectividade com DC
2. ping DOMINIO.local
3. nslookup DOMINIO.local
4. Verificar DNS
```

### Erro: "WMI remoto não funciona"
```
Solução:
1. Verificar firewall
2. Verificar GPO de firewall
3. Testar: netsh advfirewall show allprofiles
4. Habilitar regras WMI no GPO
```

---

## 📊 Comparação: Workgroup vs Domínio

| Aspecto | Workgroup | Domínio |
|---------|-----------|---------|
| Instalador | `install_workgroup.bat` | `install_automated.bat` |
| Usuário | Local | Domínio |
| Autenticação | Local | Active Directory |
| Gerenciamento | Manual | GPO |
| Segurança | Básica | Avançada |
| Escalabilidade | Pequena | Grande |
| Complexidade | Baixa | Média |

---

## 🎯 Recomendações

### Para Ambientes Pequenos (< 10 máquinas)
✅ Use `install_workgroup.bat`
- Mais simples
- Menos dependências
- Configuração rápida

### Para Ambientes Médios (10-50 máquinas)
✅ Use `install_automated.bat` com usuário de domínio
- Gerenciamento centralizado
- Mais seguro
- Facilita manutenção

### Para Ambientes Grandes (> 50 máquinas)
✅ Use `install_automated.bat` com gMSA
- Rotação automática de senha
- Auditoria completa
- Compliance

---

## 📝 Checklist Instalação Domínio

### Pré-instalação
- [ ] Criar usuário no Active Directory
- [ ] Adicionar aos grupos necessários
- [ ] Configurar GPO (se necessário)
- [ ] Testar conectividade com DC

### Instalação
- [ ] Copiar pasta probe
- [ ] Executar install_automated.bat (como Admin)
- [ ] Configurar IP: 192.168.0.9
- [ ] Configurar token
- [ ] Configurar usuário de domínio
- [ ] Configurar senha

### Pós-instalação
- [ ] Instalar Python
- [ ] Instalar dependências
- [ ] Iniciar probe
- [ ] Verificar no dashboard
- [ ] Testar WMI remoto

---

## 🔗 Arquivos Relacionados

- `probe/install_workgroup.bat` - Instalador sem domínio
- `probe/install_remote.bat` - Apenas WMI remoto
- `GUIA_MONITORAMENTO_SEM_DOMINIO.md` - Guia workgroup
- `PASSO_A_PASSO_NOVA_EMPRESA.md` - Criar empresa e máquina

---

**Para a maioria dos casos, recomendo usar `install_workgroup.bat` por ser mais simples!** 🚀
