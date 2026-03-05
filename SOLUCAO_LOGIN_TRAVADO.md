# 🔧 SOLUÇÃO: Login Travado na Tela

## 🎯 Problema

Após digitar email e senha e clicar em "ACESSAR SISTEMA", a tela fica travada/carregando infinitamente.

## 🔍 Causas Comuns

1. **CORS bloqueando requisições** (mais comum)
2. **URL da API incorreta no frontend**
3. **WAF bloqueando requisições**
4. **Cache do navegador**

---

## ✅ SOLUÇÃO RÁPIDA (3 comandos)

Execute no servidor Linux:

```bash
# 1. Tornar script executável
chmod +x corrigir_login.sh

# 2. Executar correção
./corrigir_login.sh

# 3. Limpar cache do navegador e tentar novamente
```

---

## 🔧 SOLUÇÃO MANUAL

### PASSO 1: Verificar URL da API no Frontend

```bash
# Ver configuração atual
docker compose exec frontend env | grep REACT_APP_API_URL
```

**Deve mostrar:**
```
REACT_APP_API_URL=http://localhost:8000
```

**Se estiver diferente, corrigir:**

```bash
# Editar .env
nano .env

# Mudar linha para:
REACT_APP_API_URL=http://localhost:8000

# Salvar: Ctrl+X, Y, Enter

# Reiniciar frontend
docker compose restart frontend
```

---

### PASSO 2: Testar Login via API Diretamente

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@coruja.com","password":"admin123"}'
```

**Deve retornar:**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "admin@coruja.com",
    "role": "admin"
  }
}
```

**Se retornar erro**, veja PASSO 4.

---

### PASSO 3: Verificar Console do Navegador

1. Abra o navegador
2. Pressione **F12** (DevTools)
3. Vá na aba **Console**
4. Tente fazer login
5. Procure por erros em vermelho

**Erros comuns:**

#### Erro: "CORS policy"
```
Access to fetch at 'http://localhost:8000/auth/login' from origin 
'http://localhost:3000' has been blocked by CORS policy
```

**Solução:**
```bash
# Verificar se CORS está configurado
docker logs coruja-api --tail 50 | grep CORS

# Reiniciar API
docker compose restart api
```

#### Erro: "Failed to fetch" ou "Network Error"
```
Failed to fetch
```

**Solução:**
```bash
# API não está acessível
# Verificar se está rodando
docker compose ps

# Reiniciar
docker compose restart api frontend
```

---

### PASSO 4: Desabilitar WAF Temporariamente

O WAF pode estar bloqueando requisições de login.

```bash
# Editar main.py
nano api/main.py
```

**Procure por esta linha e comente:**
```python
# app.add_middleware(WAFMiddleware)  # COMENTADO TEMPORARIAMENTE
```

**Salvar e reiniciar:**
```bash
docker compose restart api
```

**Testar login novamente.**

---

### PASSO 5: Limpar Cache do Navegador

1. Pressione **Ctrl + Shift + Delete**
2. Selecione:
   - ✅ Cookies
   - ✅ Cache
   - ✅ Dados de sites
3. Período: **Tudo**
4. Clique em **Limpar dados**
5. Feche e abra o navegador
6. Tente novamente

**OU use modo anônimo:**
- Chrome: **Ctrl + Shift + N**
- Firefox: **Ctrl + Shift + P**

---

### PASSO 6: Verificar Logs em Tempo Real

```bash
# Terminal 1: Logs da API
docker logs -f coruja-api

# Terminal 2: Logs do Frontend
docker logs -f coruja-frontend
```

**Tente fazer login e observe os logs.**

---

## 🚀 SOLUÇÃO DEFINITIVA

Se nada funcionar, execute reset completo:

```bash
# 1. Parar tudo
docker compose down

# 2. Limpar cache do Docker
docker system prune -f

# 3. Rebuild sem cache
docker compose build --no-cache

# 4. Iniciar
docker compose up -d

# 5. Aguardar 60 segundos
sleep 60

# 6. Verificar
docker compose ps
docker logs coruja-api --tail 20
docker logs coruja-frontend --tail 20

# 7. Testar
curl http://localhost:8000/health
```

---

## 📊 Checklist de Diagnóstico

Execute cada comando e anote o resultado:

```bash
# 1. API está saudável?
curl http://localhost:8000/health
# Esperado: {"status":"healthy"}

# 2. Login funciona via API?
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@coruja.com","password":"admin123"}'
# Esperado: {"access_token":"..."}

# 3. Frontend está rodando?
curl http://localhost:3000
# Esperado: HTML da página

# 4. Containers estão UP?
docker compose ps
# Esperado: Todos "Up"

# 5. Há erros nos logs?
docker logs coruja-api --tail 50 | grep -i error
docker logs coruja-frontend --tail 50 | grep -i error
# Esperado: Nenhum erro crítico
```

---

## 🎯 Solução por Sintoma

### Sintoma: Botão fica girando infinitamente

**Causa**: Frontend não consegue se comunicar com API

**Solução**:
```bash
# Verificar URL da API
docker compose exec frontend env | grep REACT_APP_API_URL

# Deve ser: http://localhost:8000
# Se não for, editar .env e reiniciar
```

---

### Sintoma: Erro "Invalid credentials"

**Causa**: Senha incorreta ou usuário não existe

**Solução**:
```bash
# Recriar usuário admin
docker compose exec api python init_admin.py

# Tentar novamente com:
# Email: admin@coruja.com
# Senha: admin123
```

---

### Sintoma: Erro 500 Internal Server Error

**Causa**: Erro no backend

**Solução**:
```bash
# Ver logs detalhados
docker logs coruja-api --tail 100

# Reiniciar API
docker compose restart api
```

---

### Sintoma: Erro CORS

**Causa**: CORS não configurado corretamente

**Solução**:
```bash
# Verificar se CORS está habilitado
docker logs coruja-api --tail 50 | grep CORS

# Reiniciar API
docker compose restart api
```

---

## 📞 Comandos Úteis

```bash
# Ver todos os logs
docker compose logs --tail 50

# Reiniciar tudo
docker compose restart

# Entrar no container da API
docker compose exec api bash

# Testar login manualmente
python3 -c "
import requests
r = requests.post('http://localhost:8000/auth/login', 
    json={'email':'admin@coruja.com','password':'admin123'})
print(r.status_code)
print(r.json())
"

# Ver variáveis de ambiente
docker compose exec api env
docker compose exec frontend env
```

---

## ✅ Resultado Esperado

Após a correção:

1. ✅ Digite email: `admin@coruja.com`
2. ✅ Digite senha: `admin123`
3. ✅ Clique em "ACESSAR SISTEMA"
4. ✅ Sistema redireciona para Dashboard
5. ✅ Você está logado!

---

**Data**: 05/03/2026  
**Status**: ✅ SOLUÇÃO DOCUMENTADA  
**Plataforma**: Linux (Ubuntu)  
**Autor**: Kiro AI Assistant
