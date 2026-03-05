# 🔧 CORRIGIR ERRO: PostgreSQL Authentication Failed

## 🎯 Problema

```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) 
connection to server at "postgres" (172.18.0.3), port 5432 failed: 
FATAL: password authentication failed for user "coruja"
```

**Causa**: A senha do PostgreSQL no container não corresponde à senha no arquivo `.env`

---

## ✅ SOLUÇÃO RÁPIDA (2 minutos)

### OPÇÃO 1: Resetar PostgreSQL (RECOMENDADO)

```bash
# 1. Parar todos os containers
docker compose down

# 2. Remover volume do PostgreSQL (apaga dados!)
docker volume rm corujamonitor_postgres_data

# 3. Recriar tudo
docker compose up -d

# 4. Aguardar 30 segundos
sleep 30

# 5. Verificar logs
docker logs coruja-api --tail 20
```

---

### OPÇÃO 2: Script Automático

```bash
# Tornar script executável
chmod +x corrigir_senha_postgres.sh

# Executar
./corrigir_senha_postgres.sh
```

---

### OPÇÃO 3: Passo a Passo Manual

#### PASSO 1: Parar containers

```bash
docker compose down
```

#### PASSO 2: Listar volumes

```bash
docker volume ls | grep postgres
```

**Saída esperada:**
```
local     corujamonitor_postgres_data
```

#### PASSO 3: Remover volume do PostgreSQL

```bash
# Tente este comando primeiro
docker volume rm corujamonitor_postgres_data

# Se não funcionar, tente este
docker volume rm coruja-monitor_postgres_data

# Ou este (nome do diretório)
docker volume rm $(basename $(pwd))_postgres_data
```

#### PASSO 4: Verificar se foi removido

```bash
docker volume ls | grep postgres
```

**Deve retornar vazio!**

#### PASSO 5: Recriar containers

```bash
docker compose up -d
```

#### PASSO 6: Aguardar inicialização

```bash
# Aguardar 30 segundos
sleep 30

# Verificar status
docker compose ps
```

**Todos devem estar "Up"!**

#### PASSO 7: Verificar logs

```bash
docker logs coruja-api --tail 20
```

**Não deve ter mais erro de senha!**

#### PASSO 8: Criar usuário admin

```bash
docker compose exec api python init_admin.py
```

---

## 🔍 Verificar se Funcionou

### Testar API

```bash
curl http://localhost:8000/health
```

**Deve retornar:**
```json
{"status":"healthy"}
```

### Testar conexão com banco

```bash
docker compose exec postgres psql -U coruja -d coruja_monitor -c "SELECT 1;"
```

**Deve retornar:**
```
 ?column? 
----------
        1
(1 row)
```

### Ver containers rodando

```bash
docker compose ps
```

**Todos devem estar "Up":**
```
NAME                IMAGE                    STATUS
coruja-api          coruja-api               Up
coruja-frontend     coruja-frontend          Up
coruja-postgres     postgres:15-alpine       Up (healthy)
coruja-redis        redis:7-alpine           Up (healthy)
coruja-worker       coruja-worker            Up
coruja-ai-agent     coruja-ai-agent          Up
coruja-ollama       ollama/ollama:latest     Up
```

---

## 🚨 Se Ainda Não Funcionar

### Verificar senha no .env

```bash
cat .env | grep POSTGRES_PASSWORD
```

**Deve mostrar:**
```
POSTGRES_PASSWORD=coruja_secure_password
```

### Verificar se .env está sendo lido

```bash
docker compose config | grep POSTGRES_PASSWORD
```

**Deve mostrar a mesma senha!**

### Forçar recriação completa

```bash
# Parar e remover tudo
docker compose down -v

# Remover imagens
docker compose down --rmi all

# Rebuild completo
docker compose build --no-cache

# Iniciar
docker compose up -d
```

---

## 📋 Checklist de Diagnóstico

- [ ] Arquivo `.env` existe no diretório
- [ ] Senha no `.env` está correta
- [ ] Volume do PostgreSQL foi removido
- [ ] Containers foram recriados
- [ ] PostgreSQL está "healthy"
- [ ] API consegue conectar ao banco
- [ ] Não há erros nos logs

---

## 🔒 Mudar Senha do PostgreSQL (Opcional)

Se quiser usar uma senha diferente:

### PASSO 1: Editar .env

```bash
nano .env
```

**Mudar linha:**
```bash
POSTGRES_PASSWORD=SuaNovaSenhaSegura123!
```

**Salvar:** `Ctrl + X`, `Y`, `Enter`

### PASSO 2: Resetar PostgreSQL

```bash
docker compose down
docker volume rm corujamonitor_postgres_data
docker compose up -d
```

---

## 📞 Comandos Úteis

```bash
# Ver logs da API
docker logs coruja-api --tail 50

# Ver logs do PostgreSQL
docker logs coruja-postgres --tail 50

# Ver logs em tempo real
docker logs -f coruja-api

# Entrar no container da API
docker compose exec api bash

# Entrar no PostgreSQL
docker compose exec postgres psql -U coruja -d coruja_monitor

# Reiniciar apenas API
docker compose restart api

# Ver variáveis de ambiente da API
docker compose exec api env | grep POSTGRES
```

---

## 🎯 Resumo da Solução

**Problema**: Senha do PostgreSQL incorreta

**Solução**:
1. Parar containers: `docker compose down`
2. Remover volume: `docker volume rm corujamonitor_postgres_data`
3. Recriar: `docker compose up -d`
4. Aguardar 30s
5. Verificar: `docker logs coruja-api`

**Tempo**: 2 minutos

---

**Data**: 05/03/2026  
**Status**: ✅ SOLUÇÃO DOCUMENTADA  
**Plataforma**: Linux (Ubuntu)  
**Autor**: Kiro AI Assistant
