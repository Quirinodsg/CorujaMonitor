# ✅ SOLUÇÃO FINAL - Login Servidor Linux

## 🎯 Situação Atual

- ✅ Código corrigido no Windows (192.168.31.245)
- ❌ Código NÃO está no servidor Linux (192.168.31.161)
- ❌ Git não está no PATH do PowerShell
- ✅ GitHub Desktop está instalado

---

## 🚀 SOLUÇÃO MAIS SIMPLES

Use o **GitHub Desktop** (interface gráfica) para fazer commit e push.

### Passo 1: No GitHub Desktop

1. Abra o **GitHub Desktop**
2. Selecione o repositório **CorujaMonitor**
3. Veja os arquivos modificados no lado esquerdo
4. Marque todos (especialmente `Login.js`)
5. No campo "Summary", digite:
   ```
   fix: Corrigir URL da API no Login
   ```
6. Clique em **"Commit to master"**
7. Clique em **"Push origin"**
8. Aguarde o upload terminar

### Passo 2: No Servidor Linux

Copie e cole este comando:

```bash
cd ~/CorujaMonitor && docker compose down && git pull origin master && docker compose build --no-cache && docker compose up -d && sleep 30
```

Aguarde 5-10 minutos (rebuild demora ~3 minutos)

### Passo 3: Testar

Acesse no navegador:
- **URL:** http://192.168.31.161:3000
- **Email:** admin@coruja.com
- **Senha:** admin123

---

## 📊 O Que Foi Mudado

**Arquivo:** `frontend/src/components/Login.js` (linha 74-75)

**ANTES:**
```javascript
const response = await axios.post('http://localhost:8000/api/v1/auth/login', payload);
```

**DEPOIS:**
```javascript
const API_URL = process.env.REACT_APP_API_URL || window.location.origin.replace(':3000', ':8000');
const response = await axios.post(`${API_URL}/api/v1/auth/login`, payload);
```

**Como funciona:**
- Detecta automaticamente o IP que você está acessando
- Funciona de qualquer máquina da rede
- Não precisa configurar nada

---

## 🆘 Alternativa (Se não quiser usar GitHub Desktop)

Execute este comando no servidor Linux para corrigir diretamente:

```bash
cd ~/CorujaMonitor && \
python3 << 'EOF'
with open('frontend/src/components/Login.js', 'r') as f:
    content = f.read()
content = content.replace(
    "const response = await axios.post('http://localhost:8000/api/v1/auth/login', payload);",
    "const API_URL = process.env.REACT_APP_API_URL || window.location.origin.replace(':3000', ':8000');\n      const response = await axios.post(`${API_URL}/api/v1/auth/login`, payload);"
)
with open('frontend/src/components/Login.js', 'w') as f:
    f.write(content)
print("✅ Corrigido!")
EOF
docker compose restart frontend && sleep 30
```

---

## 📅 Data
05/03/2026

## 🎯 Conclusão
Use o GitHub Desktop (interface gráfica) - é a forma mais simples e segura!
