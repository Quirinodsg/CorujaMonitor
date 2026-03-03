# Como Instalar Nova Probe - Guia Rápido

## 🎯 NOVO: Instalador com Início Automático

**Agora temos um instalador que:**
- ✅ Instala tudo automaticamente
- ✅ Inicia a probe imediatamente
- ✅ Configura para iniciar com o Windows
- ✅ Não precisa deixar janela aberta!

---

## ✅ SOLUÇÃO MAIS RÁPIDA (RECOMENDADO)

### Use o instalador completo com serviço:

```
probe/install_completo_com_servico.bat
```

**Como usar:**
1. Execute como **Administrador** (botão direito → Executar como administrador)
2. Siga as instruções na tela
3. A probe vai iniciar automaticamente e rodar em segundo plano
4. Vai iniciar automaticamente quando o Windows reiniciar

**Verificar instalação:**
```
probe/verificar_instalacao.bat
```

---

## 📋 Opções de Instaladores

### 1. Instalador Completo com Serviço (RECOMENDADO)
```
probe/install_completo_com_servico.bat
```
- Detecta usuário atual automaticamente
- Configura tudo (Firewall, DCOM, WMI)
- Cria serviço Windows para início automático
- Inicia probe imediatamente em segundo plano
- **Não precisa deixar janela aberta!**

### 2. Instalador com Usuário Atual
```
probe/install_usuario_atual.bat
```
- Detecta usuário atual
- Só pede senha
- Mais rápido
- Precisa iniciar probe manualmente

### 3. Instalador Sem Usuário
```
probe/install_sem_usuario.bat
```
- Pula criação de usuário
- Cria apenas template
- Para configurar depois

### 4. Instalador Universal (Menu)
```
probe/INSTALAR_AQUI.bat
```
- Menu com opções
- Workgroup, Entra ID, Active Directory
- Mais completo mas mais demorado

---

## 📋 Passo a Passo Completo

### 1. Copiar Token da Probe

Antes de instalar, pegue o token:

1. Acesse: http://192.168.0.9:3000
2. Login: admin@coruja.com / admin123
3. Menu lateral → **"Empresas"**
4. Clique na empresa (ex: TENSO)
5. Clique em **"+ Nova Probe"**
6. Digite nome: "Probe Filial SP" (ou outro nome)
7. **Copie o token** que aparece (Ctrl+C)

---

### 2. Copiar Pasta Probe para Nova Máquina

**Da sua máquina (192.168.0.9)**:
```
C:\Users\andre.quirino\Coruja Monitor\probe\
```

**Para a máquina nova**:
```
C:\Coruja Monitor\probe\
```

**Dica**: Use compartilhamento de rede, pendrive ou OneDrive.

---

### 3. Executar Instalador (NA MÁQUINA NOVA)

**Opção A - Instalador Completo com Serviço (RECOMENDADO)**:
1. Vá até: `C:\Coruja Monitor\probe\`
2. Clique com botão direito em: `install_completo_com_servico.bat`
3. Escolha: **"Executar como administrador"**
4. Siga as instruções na tela
5. A probe vai iniciar automaticamente!

**Opção B - Instalador com Usuário Atual**:
1. Vá até: `C:\Coruja Monitor\probe\`
2. Clique com botão direito em: `install_usuario_atual.bat`
3. Escolha: **"Executar como administrador"**
4. Depois execute: `python probe_core.py`

**Opção C - Instalador Universal (Menu)**:
1. Vá até: `C:\Coruja Monitor\probe\`
2. Duplo clique em: `INSTALAR_AQUI.bat`
3. Clique em **SIM** na janela UAC
4. Escolha opção 2 ou 5 no menu

---

### 4. Configurar (se usar instalador completo)

O instalador vai perguntar:

```
Digite o IP do servidor Coruja (ex: 192.168.0.9):
```
**Digite**: `192.168.0.9`

```
Digite o token da probe:
```
**Cole o token** que você copiou (Ctrl+V)

```
Digite a senha do usuario [seu_usuario]:
```
**Digite sua senha** (a senha do usuário atual do Windows)

---

### 5. Aguardar Instalação

O instalador vai:
- ✓ Detectar usuário atual
- ✓ Configurar Firewall
- ✓ Configurar DCOM e WMI
- ✓ Criar arquivos de configuração
- ✓ Verificar Python
- ✓ Instalar dependências
- ✓ Criar serviço Windows
- ✓ **Iniciar probe automaticamente!**

**Aguarde até "INSTALAÇÃO CONCLUÍDA!"**

---

### 6. Verificar Instalação

Execute o verificador:
```bash
cd C:\Coruja Monitor\probe
verificar_instalacao.bat
```

Ele vai mostrar:
- ✓ Arquivos de configuração
- ✓ Python instalado
- ✓ Dependências instaladas
- ✓ Tarefa agendada criada
- ✓ Probe rodando
- ✓ Log da probe

---

### 7. Instalar Python (se necessário)

Se o instalador avisar que Python não está instalado:

1. Baixe: https://www.python.org/downloads/
2. Execute o instalador
3. **MARQUE**: "Add Python to PATH"
4. Clique em "Install Now"
5. Teste no CMD: `python --version`
6. Execute o instalador novamente

---

### 8. Gerenciar Probe

**Ver se está rodando:**
```bash
tasklist | findstr python
```

**Ver log:**
```bash
type probe.log
```

**Parar probe:**
- Procure "Coruja Probe" na barra de tarefas
- Feche a janela

**Iniciar probe manualmente:**
```bash
start_probe.bat
```

**Desabilitar início automático:**
```bash
schtasks /delete /tn "CorujaProbe" /f
```

**Habilitar início automático novamente:**
```bash
schtasks /create /tn "CorujaProbe" /tr "python C:\Coruja Monitor\probe\probe_core.py" /sc onstart /ru SYSTEM /rl HIGHEST /f
```

---

### 9. Verificar no Dashboard

1. Volte para: http://192.168.0.9:3000
2. Menu lateral → **"Servidores"**
3. Aguarde 2-3 minutos
4. A nova máquina deve aparecer automaticamente!
5. Os sensores vão aparecer com status real

**Nota**: Com o instalador completo, a probe já está rodando em segundo plano. Não precisa deixar janela aberta!

---

## 🔧 Troubleshooting

### Janela fechou novamente?

Execute como admin:
1. Clique com botão direito em `install_completo_com_servico.bat`
2. Escolha "Executar como administrador"

### Probe não está rodando?

Verifique:
```bash
# Ver processos Python
tasklist | findstr python

# Ver tarefa agendada
schtasks /query /tn "CorujaProbe"

# Ver log
type probe.log

# Iniciar manualmente
start_probe.bat
```

### Probe não conecta?

Teste conectividade:
```bash
ping 192.168.0.9
curl http://192.168.0.9:8000/health
```

### Python não encontrado?

Instale Python e marque "Add Python to PATH":
- https://www.python.org/downloads/

### Máquina não aparece no dashboard?

1. Aguarde 2-3 minutos
2. Verifique se probe está rodando: `tasklist | findstr python`
3. Verifique o log: `type probe.log`
4. Faça Ctrl+Shift+R no navegador

### Sensores não aparecem?

Os sensores aparecem automaticamente quando a probe envia as primeiras métricas:
1. Aguarde 2-3 minutos após iniciar a probe
2. Verifique o log para ver se está coletando: `type probe.log`
3. Verifique se há erros no log
4. Recarregue a página do dashboard (Ctrl+Shift+R)

---

## 📁 Arquivos Criados

Após instalação:

```
C:\Coruja Monitor\probe\
├── probe_config.json          ← Configuração da probe
├── wmi_credentials.json       ← Credenciais WMI
├── probe_core.py              ← Código da probe
├── collectors/                ← Coletores
├── requirements.txt           ← Dependências
├── probe.log                  ← Log da probe (criado ao iniciar)
└── logs/                      ← Logs antigos
```

**Tarefa Agendada Windows:**
- Nome: `CorujaProbe`
- Tipo: Iniciar com o sistema
- Comando: `python C:\Coruja Monitor\probe\probe_core.py`
- Usuário: SYSTEM
- Privilégio: Mais alto

---

## ✅ Checklist Completo

### Antes de Instalar
- [ ] Copiar token da interface web (Empresas → + Nova Probe)
- [ ] Copiar pasta probe para máquina nova
- [ ] Anotar IP do servidor (192.168.0.9)
- [ ] Verificar se tem Python instalado (opcional)

### Durante Instalação (Instalador Completo)
- [ ] Executar `install_completo_com_servico.bat` como admin
- [ ] Configurar IP: 192.168.0.9
- [ ] Colar token da probe
- [ ] Digitar senha do usuário atual
- [ ] Aguardar instalação completa

### Após Instalação
- [ ] Executar `verificar_instalacao.bat` para verificar
- [ ] Verificar se probe está rodando: `tasklist | findstr python`
- [ ] Verificar log: `type probe.log`
- [ ] Verificar tarefa agendada: `schtasks /query /tn "CorujaProbe"`

### Verificação no Dashboard
- [ ] Aguardar 2-3 minutos
- [ ] Acessar http://192.168.0.9:3000
- [ ] Ir em "Servidores"
- [ ] Verificar máquina apareceu
- [ ] Verificar sensores coletando (CPU, Memória, Disco, etc)

---

## 🎯 Resumo Ultra Rápido

### Método 1: Instalador Completo (RECOMENDADO)

```bash
# 1. Pegar token em http://192.168.0.9:3000
Empresas → + Nova Probe → Copiar token

# 2. Na máquina nova (botão direito → Executar como admin)
C:\Coruja Monitor\probe\install_completo_com_servico.bat

# 3. Configurar
IP: 192.168.0.9
Token: [colar]
Senha: [sua senha do Windows]

# 4. Aguardar instalação
# A probe vai iniciar automaticamente!

# 5. Verificar
C:\Coruja Monitor\probe\verificar_instalacao.bat

# 6. Ver no dashboard
http://192.168.0.9:3000 → Servidores
# Aguarde 2-3 minutos para sensores aparecerem
```

### Método 2: Instalador Rápido (Manual)

```bash
# 1. Pegar token em http://192.168.0.9:3000
Empresas → + Nova Probe → Copiar token

# 2. Na máquina nova (botão direito → Executar como admin)
C:\Coruja Monitor\probe\install_usuario_atual.bat

# 3. Configurar
IP: 192.168.0.9
Token: [colar]
Senha: [sua senha]

# 4. Instalar dependências
pip install -r requirements.txt

# 5. Iniciar probe
python probe_core.py
# Deixar rodando!

# 6. Verificar
http://192.168.0.9:3000 → Servidores
```

---

## 📞 Arquivos Importantes

### Instaladores (em ordem de recomendação)
```
probe/install_completo_com_servico.bat   ← RECOMENDADO! (auto-start)
probe/install_usuario_atual.bat          ← Rápido (manual start)
probe/install_sem_usuario.bat            ← Sem usuário
probe/INSTALAR_AQUI.bat                  ← Universal (menu)
```

### Utilitários
```
probe/verificar_instalacao.bat           ← Verificar instalação
probe/start_probe.bat                    ← Iniciar probe manualmente
probe/check_task.bat                     ← Verificar tarefa agendada
probe/diagnostico_probe.bat              ← Diagnóstico completo
```

### Documentação
```
COMO_INSTALAR_NOVA_PROBE.md              ← Este arquivo
GUIA_INSTALADOR_UNIVERSAL.md             ← Guia completo
PASSO_A_PASSO_NOVA_EMPRESA.md            ← Passo a passo
GUIA_ENTRA_ID_AZURE_AD.md                ← Entra ID específico
```

---

## 🚀 Vantagens do Instalador Completo

### Instalador Completo com Serviço
✅ Instala tudo automaticamente  
✅ Inicia probe imediatamente  
✅ Configura início automático com Windows  
✅ Não precisa deixar janela aberta  
✅ Probe roda em segundo plano  
✅ Reinicia automaticamente após reboot  
✅ Mais profissional e confiável  

### Instalador Manual
✅ Mais controle sobre o processo  
✅ Pode ver output da probe  
❌ Precisa deixar janela aberta  
❌ Não inicia automaticamente  
❌ Para quando fecha a janela  

---

**Use `install_completo_com_servico.bat` para instalação profissional!** 🚀
