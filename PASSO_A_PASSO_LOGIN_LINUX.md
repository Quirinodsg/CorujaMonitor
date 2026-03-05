# 🔧 CORRIGIR LOGIN - Servidor Linux (192.168.31.161)

## ⚠️ PROBLEMA
O frontend está usando `http://localhost:8000` ao invés de `http://192.168.31.161:8000`

Quando você acessa de outra máquina, o navegador tenta conectar no localhost da SUA máquina, não do servidor.

---

## ✅ SOLUÇÃO RÁPIDA (Opção 1 - Recomendada)

Execute estes comandos **NO SERVIDOR LINUX** (192.168.31.161):

```bash
# 1. Ir para o diretório
cd ~/CorujaMonitor

# 2. Restaurar do backup (se houver erro anterior)
cp frontend/src/components/Login.js.bak frontend/src/components/Login.js

# 3. Aplicar correção com Python
python3 << 'EOF'
import re
with open('frontend/src/components/Login.js', 'r') as f:
    content = f.read()
old_pattern = r"const response = await axios\.post\('http://localhost:8000/api/v1/auth/login', payload\);"
new_code = """const API_URL = process.env.REACT_APP_API_URL || window.location.origin.replace(':3000', ':8000');
      const response = await axios.post(`${API_URL}/api/v1/auth/login`, payload);"""
content = re.sub(old_pattern, new_code, content)
with open('frontend/src/components/Login.js', 'w') as f:
    f.write(content)
print("✅ Correção aplicada")
EOF

# 4. Verificar se funcionou
grep -n "API_URL" frontend/src/components/Login.js

# 5. Rebuild do frontend
docker compose build --no-cache frontend

# 6. Reiniciar frontend
docker compose up -d frontend

# 7. Aguardar
sleep 30
```

**Aguarde 2-3 minutos** e depois teste no navegador.

---

## 📝 SOLUÇÃO MANUAL (Opção 2)

Se preferir fazer manualmente, execute **NO SERVIDOR LINUX**:

### Passo 1: Ir para o diretório
```bash
cd ~/CorujaMonitor
```

### Passo 2: Fazer backup
```bash
cp frontend/src/components/Login.js frontend/src/components/Login.js.bak
```

### Passo 3: Editar o arquivo
```bash
nano frontend/src/components/Login.js
```

### Passo 4: Encontrar a linha 74
Procure por esta linha (use Ctrl+W para buscar):
```javascript
const response = await axios.post('http://localhost:8000/api/v1/auth/login', payload);
```

### Passo 5: Substituir por estas DUAS linhas
```javascript
const API_URL = process.env.REACT_APP_API_URL || window.location.origin.replace(':3000', ':8000');
const response = await axios.post(`${API_URL}/api/v1/auth/login`, payload);
```

### Passo 6: Salvar e sair
- Pressione `Ctrl+X`
- Pressione `Y` (Yes)
- Pressione `Enter`

### Passo 7: Rebuild do frontend
```bash
docker compose build --no-cache frontend
```

### Passo 8: Reiniciar frontend
```bash
docker compose up -d frontend
```

### Passo 9: Aguardar
```bash
sleep 30
```

---

## 🧪 TESTAR SE FUNCIONOU

### Teste 1: API funcionando
```bash
curl -X POST http://192.168.31.161:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin@coruja.com","password":"admin123"}'
```

**Resultado esperado:** Deve retornar um JSON com `access_token`

### Teste 2: Frontend funcionando
1. Abra o navegador
2. Acesse: `http://192.168.31.161:3000`
3. Digite:
   - Email: `admin@coruja.com`
   - Senha: `admin123`
4. Clique em "ACESSAR SISTEMA"

**Resultado esperado:** Login deve funcionar e entrar no dashboard

---

## 🔍 O QUE A CORREÇÃO FAZ

### ANTES (linha 74):
```javascript
const response = await axios.post('http://localhost:8000/api/v1/auth/login', payload);
```
❌ Sempre usa `localhost` (não funciona de outra máquina)

### DEPOIS (linhas 74-75):
```javascript
const API_URL = process.env.REACT_APP_API_URL || window.location.origin.replace(':3000', ':8000');
const response = await axios.post(`${API_URL}/api/v1/auth/login`, payload);
```
✅ Usa o IP que você está acessando

### Como funciona:
1. `window.location.origin` pega a URL atual (ex: `http://192.168.31.161:3000`)
2. `.replace(':3000', ':8000')` troca a porta para 8000
3. Resultado: `http://192.168.31.161:8000`

---

## 🆘 SE DER ERRO

### Erro: "Permission denied"
```bash
sudo chmod +x corrigir_login_linux.sh
./corrigir_login_linux.sh
```

### Erro: "docker compose: command not found"
```bash
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

### Erro: "Cannot connect to Docker daemon"
```bash
sudo systemctl start docker
sudo usermod -aG docker $USER
# Fazer logout e login novamente
```

### Frontend não inicia
```bash
# Ver logs
docker logs coruja-frontend --tail 50

# Reiniciar tudo
docker compose restart frontend
```

---

## 📊 STATUS DOS SERVIDORES

| Servidor | IP | Status | Login |
|----------|-----|--------|-------|
| **Local** | 192.168.31.245 | ✅ Funcionando | ✅ OK |
| **Linux** | 192.168.31.161 | ⚠️ Precisa correção | ❌ Travando |

---

## 📅 Data
05/03/2026

## 🎯 Objetivo
Fazer o login funcionar no servidor Linux quando acessado de qualquer máquina da rede.
