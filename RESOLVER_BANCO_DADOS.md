# 🔧 Resolver Problema do Banco de Dados

## ❌ Problema

```
could not translate host name "postgres" to address
```

O banco de dados PostgreSQL não está acessível.

## ✅ Solução Definitiva

### 1. Verificar Status dos Containers

```powershell
docker ps
```

Se não aparecer `coruja-postgres`, execute:

### 2. Iniciar TODOS os Containers

```powershell
docker-compose up -d
```

### 3. Aguardar 30 Segundos

Os containers precisam de tempo para inicializar completamente.

### 4. Verificar Novamente

```powershell
docker ps
```

Você deve ver:
- coruja-postgres
- coruja-api
- coruja-frontend
- coruja-redis
- coruja-worker
- coruja-ollama
- coruja-ai-agent

### 5. Executar Migração

```powershell
cd api
python migrate_standalone_sensors.py
```

## 🎯 Se Ainda Não Funcionar

O sistema JÁ ESTÁ FUNCIONANDO via Docker! A migração pode ser executada DEPOIS.

### Acesse o Sistema AGORA

```
http://localhost:3000
```

Login: `admin@coruja.com` / `admin123`

### Execute a Migração Dentro do Container

```powershell
docker exec -it coruja-api python migrate_standalone_sensors.py
```

## ✅ Pronto!

A Biblioteca de Sensores estará disponível em:
**📚 Biblioteca de Sensores** no menu lateral

---

**O sistema JÁ FUNCIONA! A migração é apenas para adicionar a nova funcionalidade.**
