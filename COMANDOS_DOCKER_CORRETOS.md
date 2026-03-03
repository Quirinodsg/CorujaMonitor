# Comandos Docker Corretos - Coruja Monitor

## Nomes dos Serviços

No `docker-compose.yml`, os serviços são:
- `postgres` (container: coruja-postgres)
- `redis` (container: coruja-redis)
- `api` (container: coruja-api)
- `worker` (container: coruja-worker)
- `ai-agent` (container: coruja-ai-agent)
- `frontend` (container: coruja-frontend)

## Comandos Corretos

### Reiniciar Serviços Individuais

```bash
# Reiniciar frontend
docker-compose restart frontend

# Reiniciar API
docker-compose restart api

# Reiniciar AI Agent
docker-compose restart ai-agent

# Reiniciar worker
docker-compose restart worker
```

### Reiniciar Todos os Serviços

```bash
docker-compose restart
```

### Ver Logs

```bash
# Logs do frontend
docker-compose logs -f frontend

# Logs da API
docker-compose logs -f api

# Logs do AI Agent
docker-compose logs -f ai-agent

# Logs de todos
docker-compose logs -f
```

### Reconstruir e Reiniciar

```bash
# Reconstruir frontend
docker-compose up -d --build frontend

# Reconstruir API
docker-compose up -d --build api

# Reconstruir AI Agent
docker-compose up -d --build ai-agent

# Reconstruir tudo
docker-compose up -d --build
```

### Parar e Iniciar

```bash
# Parar tudo (mantém volumes)
docker-compose stop

# Iniciar tudo
docker-compose start

# Parar e remover containers (mantém volumes)
docker-compose down

# Parar e remover TUDO incluindo volumes (CUIDADO!)
docker-compose down -v
```

## Solução para Interface Perdida

Se você executou `docker-compose down` e perdeu as alterações:

### Opção 1: Reiniciar Apenas o Frontend (Recomendado)

```bash
# Ir para a pasta raiz do projeto
cd "C:\Users\andre.quirino\Coruja Monitor"

# Reiniciar apenas o frontend
docker-compose restart frontend

# Aguardar 10 segundos e fazer hard refresh no navegador
# Ctrl + Shift + R
```

### Opção 2: Reconstruir o Frontend

```bash
# Ir para a pasta raiz
cd "C:\Users\andre.quirino\Coruja Monitor"

# Reconstruir e reiniciar frontend
docker-compose up -d --build frontend

# Aguardar compilação (pode levar 1-2 minutos)
# Fazer hard refresh: Ctrl + Shift + R
```

### Opção 3: Verificar se Arquivos Locais Estão Corretos

```bash
# Verificar se Management.css tem as alterações
type frontend\src\components\Management.css | findstr "320px"

# Deve mostrar: grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
```

## Verificar Status

```bash
# Ver containers rodando
docker ps

# Ver todos os containers
docker ps -a

# Ver uso de recursos
docker stats
```

## Limpar Cache do Docker (Se Necessário)

```bash
# Limpar imagens não usadas
docker image prune -a

# Limpar tudo (CUIDADO!)
docker system prune -a --volumes
```

## Problema Atual: Interface Resetada

### Diagnóstico

1. Você executou `docker-compose down` que removeu os containers
2. Ao fazer `docker-compose up -d`, o frontend foi reconstruído
3. Os arquivos locais ainda têm as alterações (verificado)
4. O container pode estar usando cache antigo

### Solução Rápida

```bash
# 1. Ir para pasta raiz
cd "C:\Users\andre.quirino\Coruja Monitor"

# 2. Parar frontend
docker-compose stop frontend

# 3. Remover container do frontend
docker rm coruja-frontend

# 4. Reconstruir sem cache
docker-compose build --no-cache frontend

# 5. Iniciar frontend
docker-compose up -d frontend

# 6. Aguardar 30 segundos

# 7. Abrir navegador e fazer hard refresh
# Ctrl + Shift + R no Chrome/Edge
```

### Verificar se Funcionou

1. Abrir http://localhost:3000
2. Login: admin@coruja.com / admin123
3. Ir em "Servidores"
4. Verificar se:
   - Cards estão mais largos (320px)
   - Cards estão menos altos
   - Cores têm bom contraste
   - Card "Sistema" mostra "Sistema" (não hostname)

## Atalho: Script de Restart Completo

Criar arquivo `restart_frontend.bat`:

```batch
@echo off
echo Reiniciando Frontend do Coruja Monitor...
cd "C:\Users\andre.quirino\Coruja Monitor"
docker-compose stop frontend
docker rm coruja-frontend
docker-compose build --no-cache frontend
docker-compose up -d frontend
echo.
echo Aguarde 30 segundos e faça Ctrl+Shift+R no navegador
pause
```

Executar: `restart_frontend.bat`
