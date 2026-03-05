# 🔧 SOLUÇÃO SEM GIT - Copiar Arquivo Diretamente

## ⚠️ Situação
- Git não está disponível no Windows
- Mudanças não foram enviadas para o repositório
- Servidor Linux não tem o código atualizado

## ✅ SOLUÇÃO RÁPIDA: Copiar arquivo via SCP

---

### 📍 OPÇÃO 1: Usar WinSCP ou FileZilla

1. **Baixe WinSCP:** https://winscp.net/eng/download.php

2. **Conecte no servidor Linux:**
   - Host: `192.168.31.161`
   - Usuário: `administrador`
   - Senha: (sua senha)

3. **Navegue até:**
   - Servidor: `/home/administrador/CorujaMonitor/frontend/src/components/`

4. **Copie o arquivo:**
   - Do Windows: `C:\Users\andre.quirino\Coruja Monitor\frontend\src\components\Login.js`
   - Para Linux: `/home/administrador/CorujaMonitor/frontend/src/components/Login.js`

5. **No servidor Linux, execute:**
   ```bash
   cd ~/CorujaMonitor
   docker compose restart frontend
   sleep 30
   ```

---

### 📍 OPÇÃO 2: Copiar conteúdo manualmente

1. **No Windows, abra o arquivo:**
   ```
   C:\Users\andre.quirino\Coruja Monitor\frontend\src\components\Login.js
   ```

2. **Copie TODO o conteúdo do arquivo** (Ctrl+A, Ctrl+C)

3. **No servidor Linux, execute:**
   ```bash
   nano ~/CorujaMonitor/frontend/src/components/Login.js
   ```

4. **Apague todo o conteúdo** (Ctrl+K várias vezes)

5. **Cole o novo conteúdo** (Ctrl+Shift+V ou botão direito)

6. **Salve:** Ctrl+X, Y, Enter

7. **Reinicie o frontend:**
   ```bash
   cd ~/CorujaMonitor
   docker compose restart frontend
   sleep 30
   ```

---

### 📍 OPÇÃO 3: Editar apenas as linhas 74-75 no Linux

**Mais rápido e seguro!**

1. **No servidor Linux, execute:**
   ```bash
   nano ~/CorujaMonitor/frontend/src/components/Login.js
   ```

2. **Pressione Ctrl+W** (buscar)

3. **Digite:** `localhost:8000/api/v1/auth/login`

4. **Pressione Enter** (vai para a linha 74)

5. **Apague a linha 74 inteira** (Ctrl+K)

6. **Digite estas DUAS linhas:**
   ```javascript
         const API_URL = process.env.REACT_APP_API_URL || window.location.origin.replace(':3000', ':8000');
         const response = await axios.post(`${API_URL}/api/v1/auth/login`, payload);
   ```

7. **Salve:** Ctrl+X, Y, Enter

8. **Reinicie o frontend:**
   ```bash
   cd ~/CorujaMonitor
   docker compose restart frontend
   sleep 30
   ```

---

### 📍 OPÇÃO 4: Usar comando sed (mais técnico)

```bash
cd ~/CorujaMonitor

# Fazer backup
cp frontend/src/components/Login.js frontend/src/components/Login.js.backup

# Aplicar mudança
sed -i "74s|.*|      const API_URL = process.env.REACT_APP_API_URL || window.location.origin.replace(':3000', ':8000');\n      const response = await axios.post(\`\${API_URL}/api/v1/auth/login\`, payload);|" frontend/src/components/Login.js

# Reiniciar
docker compose restart frontend
sleep 30
```

---

## 🧪 TESTAR

Após qualquer opção, teste no navegador:
- URL: `http://192.168.31.161:3000`
- Email: `admin@coruja.com`
- Senha: `admin123`

---

## 🔍 VERIFICAR SE FUNCIONOU

```bash
# Ver se a mudança foi aplicada
grep -n "API_URL" ~/CorujaMonitor/frontend/src/components/Login.js

# Deve mostrar:
# 74:      const API_URL = process.env.REACT_APP_API_URL || window.location.origin.replace(':3000', ':8000');
```

---

## 📊 RECOMENDAÇÃO

**Use a OPÇÃO 3** (editar apenas as linhas 74-75) - é a mais rápida e segura!

---

## 📅 Data
05/03/2026

## 🎯 Objetivo
Atualizar Login.js no servidor Linux sem usar Git
