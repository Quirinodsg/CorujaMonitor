# Melhoria: Instalador com Credenciais Customizáveis

## 📅 Data: 24 de Fevereiro de 2026

## 🎯 Objetivo

Permitir que o usuário digite manualmente o usuário, senha e domínio durante a instalação, ao invés de apenas usar o usuário detectado automaticamente.

---

## ✅ O Que Foi Modificado

### Instalador Completo com Serviço
**Arquivo**: `probe/install_completo_com_servico.bat`

### Antes
- Detectava usuário atual automaticamente
- Só pedia a senha
- Usava hostname como domínio

### Depois
- Detecta usuário atual mas permite customizar
- Permite digitar usuário diferente
- Permite digitar senha
- Permite digitar domínio customizado
- Mostra resumo das credenciais antes de continuar

---

## 🎮 Como Funciona Agora

### Passo 1: Detecção Automática
```
[2/12] Detectando informacoes do sistema...
[OK] Usuario detectado: andre.quirino
[OK] Computador: DESKTOP-ABC123
```

### Passo 2: Configuração de Credenciais
```
========================================
  CREDENCIAIS PARA MONITORAMENTO WMI
========================================

Usuario detectado: andre.quirino
Computador: DESKTOP-ABC123

Voce pode:
1. Pressionar ENTER para usar o usuario detectado
2. Digitar um usuario diferente

Usuario (ENTER para usar 'andre.quirino'): _
```

**Opções**:
- Pressionar ENTER → Usa `andre.quirino`
- Digitar `administrador` → Usa `administrador`
- Digitar `EMPRESA\admin` → Usa `EMPRESA\admin`

### Passo 3: Senha
```
Senha do usuario andre.quirino: ********
```

### Passo 4: Domínio
```
Dominio/Workgroup:
- Para maquina local: pressione ENTER ou digite o nome do computador
- Para dominio: digite o nome do dominio (ex: EMPRESA)

Dominio (ENTER para 'DESKTOP-ABC123'): _
```

**Opções**:
- Pressionar ENTER → Usa `DESKTOP-ABC123` (local)
- Digitar `EMPRESA` → Usa domínio `EMPRESA`
- Digitar `WORKGROUP` → Usa workgroup `WORKGROUP`

### Passo 5: Resumo
```
========================================
  RESUMO DAS CREDENCIAIS
========================================
Usuario: andre.quirino
Dominio: DESKTOP-ABC123
Senha: ********
========================================

Pressione qualquer tecla para continuar...
```

---

## 📋 Exemplos de Uso

### Exemplo 1: Usuário Local (Padrão)
```
Usuario: [ENTER]           → andre.quirino
Senha: minhasenha123
Dominio: [ENTER]           → DESKTOP-ABC123

Resultado:
  Usuario: andre.quirino
  Dominio: DESKTOP-ABC123
```

### Exemplo 2: Usuário Administrador Local
```
Usuario: administrador
Senha: senhaadmin
Dominio: [ENTER]           → DESKTOP-ABC123

Resultado:
  Usuario: administrador
  Dominio: DESKTOP-ABC123
```

### Exemplo 3: Usuário de Domínio
```
Usuario: admin
Senha: senhadominio
Dominio: EMPRESA

Resultado:
  Usuario: admin
  Dominio: EMPRESA
```

### Exemplo 4: Usuário com Domínio no Nome
```
Usuario: EMPRESA\admin
Senha: senhadominio
Dominio: EMPRESA

Resultado:
  Usuario: EMPRESA\admin
  Dominio: EMPRESA
```

### Exemplo 5: Workgroup
```
Usuario: monitor
Senha: senhamonitor
Dominio: WORKGROUP

Resultado:
  Usuario: monitor
  Dominio: WORKGROUP
```

---

## 🔧 Arquivo de Credenciais Gerado

O instalador cria `wmi_credentials.json`:

### Exemplo 1: Local
```json
{
  "DESKTOP-ABC123": {
    "username": "andre.quirino",
    "password": "minhasenha123",
    "domain": "DESKTOP-ABC123"
  }
}
```

### Exemplo 2: Domínio
```json
{
  "EMPRESA": {
    "username": "admin",
    "password": "senhadominio",
    "domain": "EMPRESA"
  }
}
```

---

## 🎯 Vantagens

### Antes
❌ Só podia usar usuário atual  
❌ Não podia especificar domínio  
❌ Menos flexível  

### Depois
✅ Pode usar qualquer usuário  
✅ Pode especificar domínio  
✅ Pode usar usuário de domínio  
✅ Pode usar administrador local  
✅ Mais flexível e profissional  
✅ Mostra resumo antes de continuar  

---

## 📖 Casos de Uso

### Caso 1: Ambiente Entra ID (Seu Caso)
```
Usuario: andre.quirino       (usuário local com permissões)
Senha: [sua senha]
Dominio: [ENTER]             (computador local)
```

### Caso 2: Active Directory
```
Usuario: admin               (usuário do domínio)
Senha: [senha do domínio]
Dominio: EMPRESA             (nome do domínio)
```

### Caso 3: Administrador Local
```
Usuario: administrador       (admin local)
Senha: [senha admin]
Dominio: [ENTER]             (computador local)
```

### Caso 4: Workgroup
```
Usuario: monitor             (usuário criado)
Senha: [senha]
Dominio: WORKGROUP           (workgroup)
```

### Caso 5: Monitoramento Remoto
```
Usuario: EMPRESA\svc_monitor (conta de serviço)
Senha: [senha da conta]
Dominio: EMPRESA             (domínio)
```

---

## 🚀 Como Usar Agora

### 1. Executar Instalador
```batch
# Botão direito → Executar como administrador
probe/install_completo_com_servico.bat
```

### 2. Configurar Credenciais

**Para seu ambiente (Entra ID)**:
```
Usuario: [ENTER]              → Usa andre.quirino
Senha: [sua senha]
Dominio: [ENTER]              → Usa DESKTOP-ABC123
```

**Para ambiente com domínio**:
```
Usuario: admin                → Usuário do domínio
Senha: [senha do domínio]
Dominio: EMPRESA              → Nome do domínio
```

**Para usar administrador local**:
```
Usuario: administrador        → Admin local
Senha: [senha admin]
Dominio: [ENTER]              → Computador local
```

### 3. Verificar Resumo
```
========================================
  RESUMO DAS CREDENCIAIS
========================================
Usuario: andre.quirino
Dominio: DESKTOP-ABC123
Senha: ********
========================================
```

Pressione qualquer tecla para continuar se estiver correto.

### 4. Aguardar Instalação

O instalador vai continuar normalmente:
- Configurar Firewall, DCOM, WMI
- Criar arquivos de configuração
- Instalar dependências
- Criar tarefa agendada
- Iniciar probe

---

## 🔍 Verificação

Após instalação, verifique o arquivo criado:

```batch
type wmi_credentials.json
```

Deve mostrar:
```json
{
  "DESKTOP-ABC123": {
    "username": "andre.quirino",
    "password": "suasenha",
    "domain": "DESKTOP-ABC123"
  }
}
```

---

## 📝 Notas Importantes

### Segurança
- A senha é armazenada em texto plano no arquivo JSON
- O arquivo deve ter permissões restritas
- Apenas o usuário que instalou deve ter acesso

### Domínio vs Computador
- **Computador local**: Use hostname (ex: DESKTOP-ABC123)
- **Domínio**: Use nome do domínio (ex: EMPRESA)
- **Workgroup**: Use WORKGROUP ou nome do workgroup

### Formato do Usuário
- **Local**: `usuario` ou `COMPUTADOR\usuario`
- **Domínio**: `usuario` ou `DOMINIO\usuario`
- **Email**: Não use formato email (ex: usuario@empresa.com)

---

## 🐛 Troubleshooting

### Problema: Credenciais não funcionam

**Verificar formato**:
```batch
type wmi_credentials.json
```

**Testar WMI manualmente**:
```powershell
Get-WmiObject -Class Win32_OperatingSystem -ComputerName localhost -Credential (Get-Credential)
```

### Problema: Domínio não encontrado

**Verificar se está no domínio**:
```batch
echo %USERDOMAIN%
```

**Usar computador local se não estiver em domínio**:
```
Dominio: [ENTER]  → Usa hostname
```

---

## ✅ Resumo da Melhoria

### O Que Mudou
- ✅ Permite digitar usuário customizado
- ✅ Permite digitar domínio customizado
- ✅ Mostra resumo das credenciais
- ✅ Mais flexível para diferentes ambientes

### Como Usar
1. Execute o instalador
2. Pressione ENTER para usar valores detectados
3. Ou digite valores customizados
4. Verifique o resumo
5. Continue a instalação

### Vantagens
- Funciona em qualquer ambiente
- Suporta Entra ID, Active Directory, Workgroup
- Permite usar diferentes usuários
- Mais profissional e flexível

---

**Instalador agora suporta credenciais customizáveis!** 🚀

Execute novamente o instalador e configure as credenciais conforme necessário.
