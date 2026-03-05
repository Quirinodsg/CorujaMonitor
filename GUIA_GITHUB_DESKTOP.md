# 🎯 GUIA RÁPIDO - GitHub Desktop

## 📋 Passos no GitHub Desktop

### 1️⃣ Abrir o Repositório
- Abra o GitHub Desktop
- Selecione o repositório: `CorujaMonitor` ou `Coruja Monitor`
- Caminho: `C:\Users\andre.quirino\Coruja Monitor`

### 2️⃣ Ver as Mudanças
Você deve ver na aba "Changes" os seguintes arquivos modificados:
- ✅ `frontend/src/components/Login.js` (PRINCIPAL)
- 📄 `PASSO_A_PASSO_LOGIN_LINUX.md`
- 📄 `SOLUCAO_FINAL_LOGIN.md`
- 📄 `COMANDOS_LINUX_CORRETOS.txt`
- 📄 `commit_correcao_login.ps1`
- 📄 E outros arquivos de documentação

### 3️⃣ Fazer Commit
1. **Marque todos os arquivos** (ou pelo menos o `Login.js`)

2. **No campo "Summary"**, digite:
   ```
   fix: Corrigir URL da API no Login para funcionar em rede
   ```

3. **No campo "Description"** (opcional), digite:
   ```
   - Substituir localhost:8000 por detecção dinâmica do IP
   - Usar window.location.origin para pegar IP atual
   - Adicionar documentação completa do processo
   
   Problema: Frontend usava URL hardcoded http://localhost:8000
   Solução: Detectar dinamicamente o IP usando window.location.origin
   ```

4. **Clique em "Commit to master"** (botão azul)

### 4️⃣ Fazer Push
1. **Clique em "Push origin"** (botão no topo)
2. Aguarde o upload terminar (barra de progresso)
3. ✅ Pronto! Mudanças enviadas para o GitHub

---

## 🐧 Depois no Servidor Linux

Copie e cole este comando:

```bash
cd ~/CorujaMonitor && \
docker compose down && \
git pull origin master && \
docker compose build --no-cache && \
docker compose up -d && \
sleep 30 && \
echo "" && \
echo "✅ PRONTO! Teste: http://192.168.31.161:3000"
```

**Tempo estimado:** 5-10 minutos (rebuild demora ~3 minutos)

---

## 🧪 Testar

Abra o navegador e acesse:
- **URL:** `http://192.168.31.161:3000`
- **Email:** `admin@coruja.com`
- **Senha:** `admin123`

---

## 📊 Checklist

- [ ] GitHub Desktop aberto
- [ ] Repositório selecionado
- [ ] Arquivos marcados (especialmente Login.js)
- [ ] Commit feito
- [ ] Push concluído
- [ ] Comando executado no Linux
- [ ] Containers rebuilded
- [ ] Login testado e funcionando

---

## 🔍 Verificar no GitHub

Após o push, você pode verificar no GitHub:
1. Acesse: `https://github.com/SEU_USUARIO/CorujaMonitor`
2. Veja o último commit
3. Clique em `frontend/src/components/Login.js`
4. Verifique se a linha 74 tem `API_URL`

---

## 📅 Data
05/03/2026

## 🎯 Objetivo
Fazer commit e push das correções usando GitHub Desktop
