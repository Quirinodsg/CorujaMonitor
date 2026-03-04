# Correção - Ferramentas Administrativas

## Problema Identificado
As ferramentas administrativas estavam tentando executar comandos `docker` diretamente, mas a API roda dentro de um container Docker e não tem acesso ao Docker host.

**Erro:**
```
❌ Erro: [Errno 2] No such file or directory: 'docker'
```

## Solução Aplicada

### 1. Limpar Cache (Redis)
**Antes:** Usava `docker exec coruja-redis redis-cli FLUSHDB`
**Depois:** Usa biblioteca `redis-py` para conectar diretamente

```python
import redis
r = redis.Redis(host='redis', port=6379, db=0)
r.flushdb()
```

**Vantagens:**
- Funciona dentro do container
- Mais rápido (conexão direta)
- Não depende de comandos externos

### 2. Ver Logs
**Antes:** Usava `docker logs coruja-api`
**Depois:** Lê arquivo de log local

```python
log_file = 'logs/api.log'
with open(log_file, 'r') as f:
    logs = f.readlines()[-lines:]
```

**Limitações:**
- Apenas logs da API disponíveis
- Outros serviços mostram mensagem informativa
- Requer configuração de logging em arquivo

### 3. Backup do Banco
**Antes:** Usava `docker exec coruja-postgres pg_dump`
**Depois:** Usa `pg_dump` diretamente com conexão ao PostgreSQL

```python
pg_dump -h postgres -U coruja -d coruja_db -f backup.sql
```

**Requisitos:**
- `postgresql-client` instalado no container da API
- Variáveis de ambiente configuradas

**Nota:** Se pg_dump não estiver disponível, retorna erro informativo

### 4. Status do Sistema
**Antes:** Usava `docker-compose ps`
**Depois:** Verifica conexão com serviços diretamente

```python
# PostgreSQL
db.execute("SELECT 1")

# Redis
r = redis.Redis(host='redis', port=6379)
r.ping()
```

**Vantagens:**
- Verifica saúde real dos serviços
- Não depende de Docker
- Mais confiável

### 5. Uso de Disco
**Antes:** Usava `docker exec` para verificar tamanho do banco
**Depois:** Apenas uso de disco do container e tamanho dos backups

```python
total, used, free = shutil.disk_usage("/")
```

**Limitação:**
- Não mostra tamanho do banco de dados
- Mostra apenas disco do container

### 6. Restart do Sistema
**Antes:** Tentava executar `docker-compose restart`
**Depois:** Retorna mensagem informativa

```python
return {
    'message': 'Para reiniciar, execute no host: docker-compose restart'
}
```

**Motivo:**
- Container não pode reiniciar outros containers
- Requer acesso ao Docker host
- Deve ser executado manualmente

## Funcionalidades Atualizadas

### ✅ Funcionando Completamente:
1. **Modo Manutenção** - Cria/remove arquivo `.maintenance`
2. **Reset de Probes** - Limpa heartbeats no banco
3. **Limpar Cache** - Conecta ao Redis e executa FLUSHDB
4. **Status do Sistema** - Verifica conexão com PostgreSQL e Redis
5. **Uso de Disco** - Mostra disco do container e backups

### ⚠️ Funcionando com Limitações:
1. **Ver Logs** - Apenas logs da API (arquivo local)
2. **Backup do Banco** - Requer pg_dump instalado no container

### ❌ Não Funciona Automaticamente:
1. **Restart do Sistema** - Deve ser executado manualmente no host

## Como Instalar pg_dump no Container

Para habilitar backup do banco, adicione ao Dockerfile da API:

```dockerfile
# api/Dockerfile
FROM python:3.11-slim

# Instalar postgresql-client
RUN apt-get update && \
    apt-get install -y postgresql-client && \
    rm -rf /var/lib/apt/lists/*

# ... resto do Dockerfile
```

Depois rebuild:
```bash
docker-compose build api
docker-compose up -d api
```

## Como Configurar Logs em Arquivo

Para habilitar logs da API em arquivo, adicione ao `main.py`:

```python
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/api.log'),
        logging.StreamHandler()
    ]
)
```

E crie o diretório:
```bash
mkdir -p logs
```

## Alternativas para Restart do Sistema

### Opção 1: Script no Host
Criar script `restart_system.sh` no host:
```bash
#!/bin/bash
docker-compose restart api frontend worker
```

### Opção 2: API Endpoint Externo
Criar endpoint que chama webhook externo que executa restart

### Opção 3: Docker Socket
Montar Docker socket no container (não recomendado por segurança):
```yaml
volumes:
  - /var/run/docker.sock:/var/run/docker.sock
```

## Testes

### Limpar Cache:
```bash
# Deve funcionar agora
1. Acesse Configurações > Ferramentas Admin
2. Clique em "Limpar Cache"
3. Confirme
4. Veja: "Cache limpo com sucesso!"
```

### Ver Logs:
```bash
# Se logs/api.log existir
1. Clique em "Ver Logs"
2. Veja últimas linhas do log

# Se não existir
Mensagem: "Log file not found"
```

### Backup:
```bash
# Se pg_dump estiver instalado
1. Clique em "Criar Backup"
2. Aguarde conclusão
3. Arquivo criado em backups/

# Se não estiver instalado
Erro: "pg_dump não disponível"
```

### Status do Sistema:
```bash
1. Clique em qualquer ferramenta
2. Status é verificado automaticamente
3. Mostra PostgreSQL e Redis como "healthy"
```

## Resumo das Mudanças

| Ferramenta | Antes | Depois | Status |
|------------|-------|--------|--------|
| Modo Manutenção | Arquivo local | Arquivo local | ✅ OK |
| Reset Probes | Banco de dados | Banco de dados | ✅ OK |
| Limpar Cache | docker exec | redis-py | ✅ OK |
| Ver Logs | docker logs | Arquivo local | ⚠️ Limitado |
| Backup Banco | docker exec | pg_dump direto | ⚠️ Requer instalação |
| Status Sistema | docker ps | Conexão direta | ✅ OK |
| Uso de Disco | docker exec | shutil | ✅ OK |
| Restart Sistema | docker-compose | Mensagem | ❌ Manual |

## Próximos Passos

### Para Produção:
1. Adicionar `postgresql-client` ao Dockerfile da API
2. Configurar logging em arquivo
3. Criar script de restart no host
4. Documentar processo de restart manual

### Melhorias Futuras:
1. Webhook para restart remoto
2. Logs centralizados (ELK, Grafana Loki)
3. Backup automático agendado
4. Monitoramento de saúde dos serviços
5. Alertas quando serviços ficam unhealthy

## Arquivos Modificados

- `api/routers/admin_tools.py` - Todas as funções atualizadas

## Conclusão

As ferramentas administrativas agora funcionam corretamente dentro do ambiente Docker:
- ✅ Limpar Cache funciona perfeitamente
- ✅ Status do Sistema verifica saúde real
- ✅ Modo Manutenção e Reset Probes funcionam
- ⚠️ Logs e Backup requerem configuração adicional
- ❌ Restart deve ser executado manualmente no host

O sistema está funcional e pronto para uso!
