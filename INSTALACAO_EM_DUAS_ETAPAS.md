# Instalação em Duas Etapas - Coruja Monitor

## 🎯 Solução para Travamento na Criação de Usuário

Se o instalador está travando na parte de criação de usuário, use a instalação em duas etapas:

1. **Etapa 1**: Configurar probe (SEM criar usuário)
2. **Etapa 2**: Criar usuário depois

---

## 📋 ETAPA 1: Configurar Probe (Sem Usuário)

### Execute este instalador:

```
probe/install_sem_usuario.bat
```

**O que ele faz:**
- ✅ Configura Firewall
- ✅ Configura DCOM
- ✅ Configura WMI
- ✅ Cria `probe_config.json` (pronto)
- ✅ Cria `wmi_credentials.json` (template)
- ❌ NÃO cria usuário (pula essa parte)

**Como executar:**
1. Clique com botão direito
2. "Executar como administrador"
3. Configure IP e token quando perguntar

---

## 📋 ETAPA 2: Criar Usuário

### Depois, execute este script:

```
probe/criar_usuario.bat
```

**O que ele faz:**
- ✅ Cria usuário MonitorUser
- ✅ Adiciona aos grupos necessários
- ✅ Atualiza `wmi_credentials.json` automaticamente
- ✅ Testa WMI

**Como executar:**
1. Clique com botão direito
2. "Executar como administrador"
3. Pronto! Usuário criado e arquivo atualizado

---

## 🚀 Passo a Passo Completo

### 1. Executar Instalador Sem Usuário

```batch
# Como Admin
cd "C:\Coruja Monitor\probe"
install_sem_usuario.bat
```

**Configure quando perguntar:**
- IP: `192.168.0.9`
- Token: [cole o token da interface web]

**Resultado:**
- ✅ `probe_config.json` criado e pronto
- ✅ `wmi_credentials.json` criado (template)
- ✅ Firewall, DCOM, WMI configurados

---

### 2. Criar Usuário

```batch
# Como Admin
cd "C:\Coruja Monitor\probe"
criar_usuario.bat
```

**Resultado:**
- ✅ Usuário MonitorUser criado
- ✅ `wmi_credentials.json` atualizado automaticamente
- ✅ Senha gerada e mostrada na tela

---

### 3. Instalar Python e Dependências

```batch
# Baixar Python
https://www.python.org/downloads/

# Instalar dependências
pip install -r requirements.txt
```

---

### 4. Iniciar Probe

```batch
python probe_core.py
```

**Deixe a janela aberta!**

---

### 5. Verificar no Dashboard

1. Acesse: http://192.168.0.9:3000
2. Menu: Servidores
3. Aguarde 2-3 minutos
4. Máquina deve aparecer!

---

## 📁 Arquivos Criados

### Após Etapa 1 (install_sem_usuario.bat)

```
probe_config.json (PRONTO):
{
  "api_url": "http://192.168.0.9:8000",
  "probe_token": "seu_token_aqui",
  "collection_interval": 60,
  "log_level": "INFO"
}

wmi_credentials.json (TEMPLATE):
{
  "SEU-COMPUTADOR": {
    "username": "SEU_USUARIO_AQUI",
    "password": "SUA_SENHA_AQUI",
    "domain": "SEU-COMPUTADOR"
  }
}
```

### Após Etapa 2 (criar_usuario.bat)

```
wmi_credentials.json (ATUALIZADO):
{
  "SEU-COMPUTADOR": {
    "username": "MonitorUser",
    "password": "Monitor@12345678",
    "domain": "SEU-COMPUTADOR"
  }
}
```

---

## 🔧 Opção Alternativa: Usar Usuário Existente

Se você já tem um usuário e não quer criar MonitorUser:

### 1. Execute install_sem_usuario.bat

```batch
install_sem_usuario.bat
```

### 2. Edite wmi_credentials.json Manualmente

Abra `wmi_credentials.json` no Notepad e edite:

```json
{
  "SEU-COMPUTADOR": {
    "username": "seu_usuario_existente",
    "password": "senha_do_usuario",
    "domain": "SEU-COMPUTADOR"
  }
}
```

### 3. Certifique-se que o usuário tem permissões

```batch
# Adicionar aos grupos necessários
net localgroup Administrators seu_usuario_existente /add
```

---

## 💡 Vantagens da Instalação em Duas Etapas

### ✅ Vantagens

1. **Não trava** na criação de usuário
2. **Mais controle** sobre cada etapa
3. **Pode usar usuário existente** se quiser
4. **Mais fácil de debugar** problemas
5. **Pode testar** configuração antes de criar usuário

### ⚠️ Desvantagens

1. Precisa executar dois scripts
2. Mais passos para seguir

---

## 🆘 Troubleshooting

### Etapa 1 Travou?

**Problema**: `install_sem_usuario.bat` travou

**Solução**: Pressione Ctrl+C e execute novamente. Ele pula passos já feitos.

---

### Etapa 2 Não Cria Usuário?

**Problema**: `criar_usuario.bat` falha ao criar usuário

**Solução Manual**:
```batch
# Criar usuário manualmente
net user MonitorUser SuaSenha@123 /add /passwordchg:no /expires:never
net localgroup Administrators MonitorUser /add

# Editar wmi_credentials.json
notepad wmi_credentials.json
```

---

### Arquivo wmi_credentials.json Não Atualiza?

**Problema**: Arquivo não foi atualizado após criar usuário

**Solução**: Edite manualmente:
```batch
notepad wmi_credentials.json
```

Substitua:
- `"username": "SEU_USUARIO_AQUI"` → `"username": "MonitorUser"`
- `"password": "SUA_SENHA_AQUI"` → `"password": "sua_senha"`

---

## 📊 Comparação de Instaladores

| Instalador | Cria Usuário | Trava? | Uso |
|------------|--------------|--------|-----|
| install_simples.bat | Sim | Pode travar | Instalação completa |
| install_sem_usuario.bat | Não | Não trava | ⭐ Etapa 1 |
| criar_usuario.bat | Sim | Não trava | ⭐ Etapa 2 |
| install_debug.bat | Sim | Pode travar | Debug |

---

## ✅ Checklist

### Etapa 1 (Configurar Probe)
- [ ] Executar `install_sem_usuario.bat` como admin
- [ ] Configurar IP: 192.168.0.9
- [ ] Configurar token da probe
- [ ] Verificar `probe_config.json` criado
- [ ] Verificar `wmi_credentials.json` criado (template)

### Etapa 2 (Criar Usuário)
- [ ] Executar `criar_usuario.bat` como admin
- [ ] Anotar senha gerada
- [ ] Verificar `wmi_credentials.json` atualizado
- [ ] Verificar usuário criado: `net user MonitorUser`

### Finalização
- [ ] Instalar Python
- [ ] Instalar dependências: `pip install -r requirements.txt`
- [ ] Iniciar probe: `python probe_core.py`
- [ ] Verificar no dashboard (2-3 min)

---

## 🎯 Resumo

**Problema**: Instalador trava na criação de usuário  
**Solução**: Instalação em duas etapas  

**Etapa 1**: `install_sem_usuario.bat` (configura tudo, menos usuário)  
**Etapa 2**: `criar_usuario.bat` (cria usuário e atualiza arquivo)  

**Resultado**: Instalação completa sem travamentos! 🚀

---

## 📞 Arquivos Importantes

```
probe/
├── install_sem_usuario.bat    ← Etapa 1 (sem usuário)
├── criar_usuario.bat          ← Etapa 2 (criar usuário)
├── install_simples.bat        ← Instalação completa
└── install_debug.bat          ← Debug completo

Raiz/
└── INSTALACAO_EM_DUAS_ETAPAS.md  ← Este guia
```

---

**Use a instalação em duas etapas para evitar travamentos!** 🚀
