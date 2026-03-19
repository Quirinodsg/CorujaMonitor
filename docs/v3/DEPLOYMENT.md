# Coruja Monitor v3.0 — Guia de Deploy

## Pré-requisitos

- Linux (Ubuntu 20.04+) com Docker e docker-compose instalados
- Git configurado
- Portas abertas: 3000 (frontend), 8000 (API), 8001 (AI agent), 5432 (PostgreSQL), 6379 (Redis)

---

## Deploy Inicial (Linux)

```bash
# 1. Clonar repositório
git clone <repo_url> /home/administrador/CorujaMonitor
cd /home/administrador/CorujaMonitor

# 2. Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas credenciais

# 3. Subir todos os serviços
docker-compose up -d

# 4. Executar migração v3 (cria tabelas novas)
docker exec coruja-api python3 migrate_v3.py

# 5. Verificar saúde
docker-compose ps
curl http://localhost:8000/health
```

---

## Atualização (Kiro → Linux)

```bash
# No Kiro (Windows — máquina de desenvolvimento):
git add -A
git commit -m "feat: descrição da mudança"
git push origin master

# No Linux:
cd /home/administrador/CorujaMonitor
git pull
docker-compose up -d --build api worker frontend
```

---

## Migração v3 — DDL

O script `api/migrate_v3.py` cria:
- `metrics_ts` — hypertable TimescaleDB com retention 90 dias
- `ai_feedback_actions` — ações dos agentes IA
- `topology_nodes` — grafo de topologia
- `intelligent_alerts` — alertas consolidados v3

```bash
# Executar migração
docker exec coruja-api python3 migrate_v3.py

# Verificar tabelas criadas
docker exec coruja-postgres psql -U coruja -d coruja_monitor -c "\dt"
```

---

## Bug ContainerConfig (docker-compose 1.29.2)

Se ocorrer `KeyError: 'ContainerConfig'` ao recriar containers:

```bash
docker ps -a | grep postgres | awk '{print $1}' | xargs -r docker rm -f
docker-compose up -d --no-deps postgres
docker-compose up -d
```

---

## Variáveis de Ambiente (.env)

```env
# Banco de dados
POSTGRES_DB=coruja_monitor
POSTGRES_USER=coruja
POSTGRES_PASSWORD=<senha>
DATABASE_URL=postgresql://coruja:<senha>@postgres:5432/coruja_monitor

# Redis
REDIS_URL=redis://redis:6379/0

# v3 Streaming
METRICS_STREAM_KEY=metrics_stream
EVENTS_STREAM_KEY=events_stream
STREAM_CONSUMER_GROUP=coruja-consumers
STREAM_BATCH_SIZE=500

# Segurança
SECRET_KEY=<chave-jwt>
ENCRYPTION_KEY=<chave-criptografia>

# AI
OLLAMA_BASE_URL=http://ollama:11434
AI_MODEL=llama2
```

---

## Sonda Windows (SRVSONDA001)

```powershell
# Atualizar sonda após git push
Stop-Service CorujaProbe
cd "C:\Program Files\CorujaMonitor\Probe"
git pull
Start-Service CorujaProbe

# Verificar logs
Get-Content "C:\Program Files\CorujaMonitor\Probe\logs\probe.log" -Tail 50
```

---

## Verificação Pós-Deploy

```bash
# API health
curl http://localhost:8000/health

# Observability health score
curl http://localhost:8000/api/v1/observability/health-score

# Alertas inteligentes
curl http://localhost:8000/api/v1/alerts/intelligent

# Logs dos containers
docker-compose logs -f api
docker-compose logs -f worker
```

---

## Rollback

```bash
# Reverter para commit anterior
git revert HEAD
git push origin master

# No Linux
git pull
docker-compose up -d --build api worker frontend
```
