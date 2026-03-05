# ✅ SOLUÇÃO FINAL - Login Servidor Linux

## 🎯 Problema
Login travando no servidor Linux (192.168.31.161) quando acessado de outra máquina.

## 🔧 Causa
Frontend usando URL hardcoded `http://localhost:8000` ao invés de detectar o IP dinamicamente.

## 📋 Solução em 2 Passos

---

### 🖥️ PASSO 1: No Windows (192.168.31.245)

Abra PowerShell e execute:

```powershell
cd "C:\Users\andre.quirino\Coruja Monitor"
.\commit_correcao_login.ps1
```

Isso vai fazer commit e push das correções para o Git.

---

### 🐧 PASSO 2: No Servidor Linux (192.168.31.161)

Copie e cole este comando (tudo de uma vez):

```bash
cd ~/CorujaMonitor && docker compose down && git pull origin master && docker compose build --no-cache && docker compose up -d && sleep 30 && echo "" && echo "✅ PRONTO! Teste: http://192.168.31.161:3000"
```

**Tempo estimado:** 5-10 minutos (rebuild demora ~3 minutos)

---

## 🧪 PASSO 3: Testar

Abra o navegador e acesse:
- **URL:** `http://192.168.31.161:3000`
- **Email:** `admin@coruja.com`
- **Senha:** `admin123`

O login deve funcionar normalmente agora! 🎉

---

## 🔍 O Que Foi Mudado

### Arquivo: `frontend/src/components/Login.js` (linha 74-75)

**ANTES:**
```javascript
const response = await axios.post('http://localhost:8000/api/v1/auth/login', payload);
```

**DEPOIS:**
```javascript
const API_URL = process.env.REACT_APP_API_URL || window.location.origin.replace(':3000', ':8000');
const response = await axios.post(`${API_URL}/api/v1/auth/login`, payload);
```

### Como Funciona:
1. `window.location.origin` → Pega o IP que você está acessando
   - Exemplo: `http://192.168.31.161:3000`
2. `.replace(':3000', ':8000')` → Troca porta 3000 por 8000
   - Resultado: `http://192.168.31.161:8000`
3. Usa essa URL dinâmica para fazer login

### Benefícios:
- ✅ Funciona em localhost
- ✅ Funciona de qualquer máquina da rede
- ✅ Não precisa configurar variável de ambiente
- ✅ Detecta automaticamente o IP correto

---

## 🆘 Se Der Problema

### Erro no Git Pull (conflito):
```bash
cd ~/CorujaMonitor
git reset --hard HEAD
git pull origin master
docker compose build --no-cache
docker compose up -d
```

### Verificar se Login.js foi atualizado:
```bash
grep -n "API_URL" ~/CorujaMonitor/frontend/src/components/Login.js
```

Deve mostrar a linha 74 com `const API_URL`

### Ver logs do frontend:
```bash
docker logs coruja-frontend --tail 50
```

### Ver logs da API:
```bash
docker logs coruja-api --tail 50
```

---

## 📊 Status Final

| Item | Status |
|------|--------|
| Servidor Local (245) | ✅ Funcionando |
| Servidor Linux (161) | ⏳ Aguardando atualização |
| Código no Git | ⏳ Aguardando commit |
| Login em rede | ⏳ Será corrigido |

---

## 📅 Data
05/03/2026

## 🏁 Conclusão
Após executar os 2 passos, o login funcionará perfeitamente de qualquer máquina da rede!
