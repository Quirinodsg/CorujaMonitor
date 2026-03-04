# 📤 GUIA: Commit e Push para GitHub
**Data:** 03/03/2026  
**Repositório:** https://github.com/Quirinodsg/CorujaMonitor

---

## ⚠️ PROBLEMA DETECTADO

O Git não está instalado ou não está no PATH do sistema.

---

## 🔧 SOLUÇÃO 1: Instalar Git

### Baixar e Instalar
1. Acesse: https://git-scm.com/download/win
2. Baixe o instalador para Windows
3. Execute o instalador
4. **IMPORTANTE**: Marque a opção "Add Git to PATH"
5. Reinicie o PowerShell após a instalação

### Verificar Instalação
```powershell
git --version
```

Deve mostrar algo como: `git version 2.43.0.windows.1`

---

## 🔧 SOLUÇÃO 2: Usar GitHub Desktop

### Instalar GitHub Desktop
1. Acesse: https://desktop.github.com/
2. Baixe e instale
3. Faça login com sua conta GitHub
4. Abra o repositório: `File > Add Local Repository`
5. Selecione a pasta: `C:\Users\andre.quirino\Coruja Monitor`

### Fazer Commit e Push
1. Veja os arquivos modificados na aba "Changes"
2. Escreva uma mensagem de commit
3. Clique em "Commit to main"
4. Clique em "Push origin"

---

## 🔧 SOLUÇÃO 3: Comandos Manuais (Após Instalar Git)

### 1. Inicializar Repositório
```powershell
cd "C:\Users\andre.quirino\Coruja Monitor"
git init
```

### 2. Configurar Usuário
```powershell
git config --global user.name "André Quirino"
git config --global user.email "seu@email.com"
```

### 3. Adicionar Arquivos
```powershell
git add .
```

### 4. Fazer Commit
```powershell
git commit -m "📚 Documentação Completa do Sistema Coruja Monitor

## Arquitetura e Código
- ✅ Backend (API FastAPI)
- ✅ Frontend (React)
- ✅ Probe (Agente de Monitoramento)
- ✅ AI Agent (Motor de IA/AIOps)
- ✅ Worker (Celery para tarefas assíncronas)

## Funcionalidades Implementadas
- ✅ Monitoramento de Servidores (WMI, SNMP, Ping)
- ✅ Sensores por Categoria
- ✅ Dashboard NOC em Tempo Real
- ✅ Sistema de Incidentes com IA
- ✅ AIOps Automático
- ✅ Base de Conhecimento
- ✅ Relatórios Personalizados
- ✅ Integrações (TOPdesk, GLPI, Teams, Email)

Data: 03/03/2026"
```

### 5. Adicionar Remote
```powershell
git remote add origin https://github.com/Quirinodsg/CorujaMonitor.git
```

### 6. Criar Branch Main
```powershell
git branch -M main
```

### 7. Push para GitHub
```powershell
git push -u origin main
```

### 8. Criar e Enviar Tag
```powershell
git tag -a v1.0.0-20260303 -m "Release completo com documentação - 03/03/2026"
git push origin v1.0.0-20260303
```

---

## 🔐 AUTENTICAÇÃO

### Opção 1: Personal Access Token (Recomendado)

1. Acesse: https://github.com/settings/tokens
2. Clique em "Generate new token (classic)"
3. Marque os scopes:
   - ✅ repo (todos)
   - ✅ workflow
4. Copie o token gerado
5. Ao fazer push, use o token como senha:
   - Username: `Quirinodsg`
   - Password: `seu_token_aqui`

### Opção 2: SSH Key

1. Gerar chave SSH:
```powershell
ssh-keygen -t ed25519 -C "seu@email.com"
```

2. Copiar chave pública:
```powershell
cat ~/.ssh/id_ed25519.pub
```

3. Adicionar no GitHub:
   - https://github.com/settings/keys
   - "New SSH key"
   - Cole a chave pública

4. Mudar remote para SSH:
```powershell
git remote set-url origin git@github.com:Quirinodsg/CorujaMonitor.git
```

---

## 📊 ARQUIVOS A SEREM COMMITADOS

### Código Fonte
- ✅ `api/` - Backend FastAPI
- ✅ `frontend/` - Interface React
- ✅ `probe/` - Agente de monitoramento
- ✅ `ai-agent/` - Motor de IA
- ✅ `worker/` - Celery worker
- ✅ `docs/` - Documentação técnica

### Documentação
- ✅ `README.md` - Documentação principal
- ✅ `*.md` - 300+ arquivos de documentação
- ✅ Guias de instalação
- ✅ Guias de configuração
- ✅ Histórico de correções

### Configuração
- ✅ `docker-compose.yml`
- ✅ `.env.example`
- ✅ `requirements.txt`
- ✅ `package.json`

### Scripts
- ✅ `*.ps1` - Scripts PowerShell
- ✅ `*.bat` - Scripts Batch
- ✅ `*.sh` - Scripts Shell

---

## ✅ VERIFICAÇÃO

Após o push, verifique:

1. **Repositório no GitHub**
   - https://github.com/Quirinodsg/CorujaMonitor

2. **Arquivos Commitados**
   - Verifique se todos os arquivos estão lá

3. **README.md**
   - Deve aparecer na página inicial

4. **Tag**
   - Vá em "Releases" e veja a tag `v1.0.0-20260303`

---

## 🆘 PROBLEMAS COMUNS

### Erro: "Permission denied"
**Solução**: Use Personal Access Token ou configure SSH

### Erro: "Repository not found"
**Solução**: Verifique se o repositório existe e se você tem acesso

### Erro: "Failed to push some refs"
**Solução**: Faça pull primeiro:
```powershell
git pull origin main --rebase
git push origin main
```

### Erro: "Large files"
**Solução**: Adicione ao .gitignore:
```
node_modules/
__pycache__/
*.pyc
.env
*.log
```

---

## 📝 PRÓXIMOS PASSOS

Após fazer o push:

1. ✅ Verificar repositório no GitHub
2. ✅ Adicionar descrição do projeto
3. ✅ Configurar GitHub Pages (se necessário)
4. ✅ Adicionar colaboradores (se necessário)
5. ✅ Configurar branch protection rules
6. ✅ Criar issues para melhorias futuras

---

**Status:** ⏳ AGUARDANDO INSTALAÇÃO DO GIT  
**Ação:** Instale o Git e execute os comandos acima
