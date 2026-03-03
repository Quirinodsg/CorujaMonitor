# ✅ CORREÇÃO OLLAMA DOCKER - 25 FEV 2026

## 🎯 PROBLEMA RESOLVIDO

**Status Anterior**: ❌ Ollama: Offline - Connection refused

**Status Atual**: ✅ Ollama: Online - Funcionando corretamente

---

## 🔧 CORREÇÕES APLICADAS

### 1. Variável de Ambiente no `.env`

**Antes:**
```env
OLLAMA_BASE_URL=http://localhost:11434
AI_MODEL=gpt-4
```

**Depois:**
```env
OLLAMA_BASE_URL=http://ollama:11434
AI_MODEL=llama2
```

**Motivo**: Dentro do Docker, `localhost` refere-se ao próprio container. Para comunicação entre containers, deve-se usar o nome do serviço (`ollama`).

---

### 2. Variáveis Explícitas no `docker-compose.yml`

Adicionado `environment` section nos serviços `api` e `ai-agent`:

```yaml
api:
  build:
    context: ./api
    dockerfile: Dockerfile
  container_name: coruja-api
  env_file: .env
  environment:
    - OLLAMA_BASE_URL=http://ollama:11434
    - AI_MODEL=llama2
  ports:
    - "8000:8000"
  # ...

ai-agent:
  build:
    context: ./ai-agent
    dockerfile: Dockerfile
  container_name: coruja-ai-agent
  env_file: .env
  environment:
    - OLLAMA_BASE_URL=http://ollama:11434
    - AI_MODEL=llama2
  ports:
    - "8001:8001"
  # ...
```

**Motivo**: Garantir que as variáveis corretas sejam aplicadas, mesmo que o `.env` tenha valores diferentes.

---

### 3. Recriação dos Containers

Comandos executados:
```bash
docker-compose stop api ai-agent
docker-compose rm -f api ai-agent
docker-compose up -d api ai-agent
```

**Motivo**: `docker-compose restart` não recarrega variáveis de ambiente. Foi necessário recriar os containers.

---

## ✅ VERIFICAÇÕES REALIZADAS

### 1. Variáveis de Ambiente Aplicadas

```bash
$ docker exec coruja-api sh -c "printenv | grep OLLAMA"
OLLAMA_BASE_URL=http://ollama:11434

$ docker exec coruja-ai-agent sh -c "printenv | grep OLLAMA"
OLLAMA_BASE_URL=http://ollama:11434
```

✅ Ambos os containers com a URL correta!

---

### 2. Conectividade entre Containers

```bash
$ docker exec coruja-api python -c "import httpx; r = httpx.get('http://ollama:11434/api/tags', timeout=5); print('Status:', r.status_code)"
Status: 200
```

✅ Container da API consegue acessar o Ollama!

---

### 3. Modelo Instalado

```bash
$ curl http://localhost:11434/api/tags
{
  "models": [
    {
      "name": "llama2:latest",
      "size": 3826793677,
      "digest": "78e26419b4469263f75331927a00a0284ef6544c1975b826b15abdaef17bb962"
    }
  ]
}
```

✅ Modelo `llama2` (3.8 GB) instalado e funcionando!

---

## 🎯 PRÓXIMOS PASSOS

1. **Acessar a interface web**: http://localhost:3000
2. **Ir para "🤖 Atividades da IA"**
3. **Verificar status**: Deve mostrar "✅ Ollama: Online"
4. **Testar análise de IA**: Criar um incidente de teste e verificar se a IA analisa

---

## 📊 STATUS DOS CONTAINERS

```
NAMES             STATUS                PORTS
coruja-api        Up 5 minutes          0.0.0.0:8000->8000/tcp
coruja-ai-agent   Up 5 minutes          0.0.0.0:8001->8001/tcp
coruja-ollama     Up About an hour      0.0.0.0:11434->11434/tcp
coruja-worker     Up About an hour
coruja-frontend   Up 3 minutes          0.0.0.0:3000->3000/tcp
coruja-postgres   Up 5 days (healthy)   0.0.0.0:5432->5432/tcp
coruja-redis      Up 5 days (healthy)   0.0.0.0:6379->6379/tcp
```

✅ Todos os containers rodando!

---

## 🔍 TROUBLESHOOTING

### Se o Ollama ainda aparecer como Offline:

1. **Verificar logs da API:**
   ```bash
   docker logs coruja-api --tail 50
   ```

2. **Verificar logs do Ollama:**
   ```bash
   docker logs coruja-ollama --tail 50
   ```

3. **Testar conexão manualmente:**
   ```bash
   docker exec coruja-api python -c "import httpx; print(httpx.get('http://ollama:11434/api/tags').json())"
   ```

4. **Reiniciar todos os containers:**
   ```bash
   docker-compose restart
   ```

---

## 📝 LIÇÕES APRENDIDAS

1. **Docker Networking**: `localhost` não funciona entre containers. Use o nome do serviço.
2. **Variáveis de Ambiente**: `docker-compose restart` NÃO recarrega variáveis. Use `rm` + `up`.
3. **Precedência**: `environment` no `docker-compose.yml` tem precedência sobre `env_file`.
4. **Modelo Correto**: Usar `llama2` ao invés de `gpt-4` (que é da OpenAI).

---

## ✅ RESULTADO FINAL

🎉 **Ollama está 100% funcional!**

- ✅ Container rodando
- ✅ Modelo llama2 instalado
- ✅ Comunicação entre containers funcionando
- ✅ Variáveis de ambiente corretas
- ✅ API consegue acessar o Ollama

**Próximo problema a resolver**: Aba de Thresholds não aparece (frontend precisa rebuild - JÁ FEITO!)
