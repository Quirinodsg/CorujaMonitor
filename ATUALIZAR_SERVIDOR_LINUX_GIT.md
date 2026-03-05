# 🔄 ATUALIZAR SERVIDOR LINUX VIA GIT

## 📋 RESUMO
Fazer commit das correções no servidor local e baixar no servidor Linux

---

## 🖥️ PARTE 1: NO SERVIDOR LOCAL (192.168.31.245)

### Passo 1: Verificar mudanças
```powershell
cd "C:\Users\andre.quirino\Coruja Monitor"
git status
```

### Passo 2: Adicionar arquivos corrigidos
```powershell
git add frontend/src/components/Login.js
git add PASSO_A_PASSO_LOGIN_LINUX.md
git add CORRIGIR_AGORA.txt
git add corrigir_login_manual.sh
git add corrigir_login_linux.sh
git add ATUALIZAR_SERVIDOR_LINUX_GIT.md
```

### Passo 3: Fazer commit
```powershell
git commit -m "fix: Corrigir URL da API no Login.js para funcionar em rede

- Substituir localhost:8000 por detecção dinâmica do IP
- Usar window.location.origin para pegar IP atual
- Adicionar scripts de correção para servidor Linux
- Documentação completa do processo"
```

### Passo 4: Fazer push
```powershell
git push origin main
```

Se der erro de branch, tente:
```powershell
git push origin master
```

---

## 🐧 PARTE 2: NO SERVIDOR LINUX (192.168.31.161)

### Passo 1: Parar containers
```bash
cd ~/CorujaMonitor
docker compose down
```

### Passo 2: Fazer backup do banco de dados
```bash
docker compose up -d postgres
sleep 5
docker compose exec -T postgres pg_dump -U coruja coruja_monitor > backup_antes_atualizacao_$(date +%Y%m%d_%H%M%S).sql
docker compose down
```

### Passo 3: Atualizar código do Git
```bash
git fetch origin
git pull origin main
```

Se der erro de branch, tente:
```bash
git pull origin master
```

### Passo 4: Verificar se Login.js foi atualizado
```bash
grep -n "API_URL" frontend/src/components/Login.js
```

**Resultado esperado:** Deve mostrar a linha com `const API_URL = process.env.REACT_APP_API_URL`

### Passo 5: Rebuild completo
```bash
docker compose build --no-cache
```

### Passo 6: Subir containers
```bash
docker compose up -d
```

### Passo 7: Verificar status
```bash
docker compose ps
```

Todos devem estar "Up"

### Passo 8: Aguardar inicialização
```bash
sleep 30
```

### Passo 9: Testar API
```bash
curl -X POST http://192.168.31.161:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin@coruja.com","password":"admin123"}'
```

**Resultado esperado:** JSON com `access_token`

### Passo 10: Testar no navegador
Acesse: `http://192.168.31.161:3000`
- Email: `admin@coruja.com`
- Senha: `admin123`

---

## 🆘 SE O GIT PULL DER CONFLITO

### Opção 1: Descartar mudanças locais
```bash
cd ~/CorujaMonitor
git reset --hard HEAD
git pull origin main
```

### Opção 2: Fazer stash das mudanças
```bash
cd ~/CorujaMonitor
git stash
git pull origin main
```

### Opção 3: Clonar novamente (CUIDADO: perde tudo)
```bash
cd ~
mv CorujaMonitor CorujaMonitor_backup_$(date +%Y%m%d_%H%M%S)
git clone https://github.com/SEU_USUARIO/CorujaMonitor.git
cd CorujaMonitor
```

Depois restaurar o .env:
```bash
cp ~/CorujaMonitor_backup_*/.env .env
```

---

## 📊 VERIFICAÇÃO FINAL

### Checklist:
- [ ] Código atualizado do Git
- [ ] Login.js contém `API_URL` (linha 74)
- [ ] Containers rodando (7 containers Up)
- [ ] API responde com token
- [ ] Login funciona no navegador
- [ ] Dashboard carrega corretamente

### Comandos de verificação:
```bash
# Ver versão do código
cd ~/CorujaMonitor
git log --oneline -1

# Ver containers
docker compose ps

# Ver logs do frontend
docker logs coruja-frontend --tail 20

# Ver logs da API
docker logs coruja-api --tail 20

# Testar API
curl http://192.168.31.161:8000/health
```

---

## 🔍 O QUE FOI MUDADO NO CÓDIGO

### Arquivo: `frontend/src/components/Login.js`

**ANTES (linha 74):**
```javascript
const response = await axios.post('http://localhost:8000/api/v1/auth/login', payload);
```

**DEPOIS (linhas 74-75):**
```javascript
const API_URL = process.env.REACT_APP_API_URL || window.location.origin.replace(':3000', ':8000');
const response = await axios.post(`${API_URL}/api/v1/auth/login`, payload);
```

### Como funciona:
1. `window.location.origin` → Pega a URL que você está acessando
   - Exemplo: `http://192.168.31.161:3000`
2. `.replace(':3000', ':8000')` → Troca porta 3000 por 8000
   - Resultado: `http://192.168.31.161:8000`
3. Usa essa URL dinâmica para fazer login

### Benefícios:
- ✅ Funciona em localhost (192.168.31.161:3000 → 192.168.31.161:8000)
- ✅ Funciona de qualquer máquina da rede
- ✅ Não precisa configurar variável de ambiente
- ✅ Detecta automaticamente o IP correto

---

## 📅 Data
05/03/2026

## 🎯 Objetivo
Atualizar servidor Linux com código corrigido do Git para resolver problema de login em rede.
