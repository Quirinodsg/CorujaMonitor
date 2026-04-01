# Guia: Qual URL Usar na Probe?

## Seu Cenário Atual

Você está na máquina **192.168.0.37** e o Docker também está rodando nela.

```
┌─────────────────────────────────────────────────────┐
│  Máquina: 192.168.0.37 (Windows)                    │
│                                                      │
│  ┌──────────────────┐                               │
│  │  Probe           │                               │
│  │  (setup_wizard)  │                               │
│  └────────┬─────────┘                               │
│           │                                          │
│           │ Conecta via localhost                   │
│           ↓                                          │
│  ┌──────────────────────────────────────┐           │
│  │  Docker Compose                      │           │
│  │  ├─ API (porta 8000)      ←─────────┼─ USE ESTA │
│  │  ├─ Frontend (porta 3000)            │           │
│  │  ├─ PostgreSQL (porta 5432)          │           │
│  │  ├─ Redis (porta 6379)               │           │
│  │  └─ AI Agent (porta 8001)            │           │
│  └──────────────────────────────────────┘           │
└─────────────────────────────────────────────────────┘
```

### ✅ URL Correta para Seu Caso

```
http://localhost:8000
```

**Por quê?** Porque a probe e o Docker estão na **mesma máquina**, então você usa `localhost`.

## Outros Cenários (Para Referência)

### Cenário 2: Probe em Outra Máquina

Se você fosse instalar a probe em **outra máquina** (ex: 192.168.0.50):

```
┌─────────────────────┐          ┌─────────────────────┐
│  Máquina: 192.168.0.50         │  Máquina: 192.168.0.37
│                     │          │                     │
│  ┌──────────────┐   │          │  ┌──────────────┐  │
│  │   Probe      │───┼──────────┼─→│  Docker      │  │
│  └──────────────┘   │  Rede    │  │  API:8000    │  │
│                     │          │  └──────────────┘  │
└─────────────────────┘          └─────────────────────┘
```

**URL neste caso:** `http://192.168.0.37:8000`

### Cenário 3: Probe em Servidor Remoto

Se você fosse monitorar um servidor remoto (ex: 192.168.0.100):

```
┌─────────────────────┐          ┌─────────────────────┐
│  Servidor Central   │          │  Servidor Remoto    │
│  192.168.0.37       │          │  192.168.0.100      │
│                     │          │                     │
│  ┌──────────────┐   │          │  ┌──────────────┐  │
│  │  Docker      │   │          │  │   Probe      │  │
│  │  API:8000    │←──┼──────────┼──│  (instalada) │  │
│  └──────────────┘   │  Rede    │  └──────────────┘  │
└─────────────────────┘          └─────────────────────┘
```

**URL neste caso:** `http://192.168.0.37:8000`

## Regra Simples

```
┌─────────────────────────────────────────────────────┐
│  Onde está a Probe?  │  Onde está o Docker?  │ URL  │
├──────────────────────┼───────────────────────┼──────┤
│  Mesma máquina       │  Mesma máquina        │ localhost:8000 │
│  Máquina diferente   │  Outra máquina        │ IP_DO_DOCKER:8000 │
└─────────────────────────────────────────────────────┘
```

## Verificar Se Está Correto

### 1. Teste a Conexão

No CMD da máquina onde a probe está instalada:

```batch
curl http://localhost:8000/health
```

Deve retornar: `{"status":"healthy"}`

### 2. Verifique o Docker

Na máquina onde o Docker está rodando:

```batch
docker-compose ps
```

Deve mostrar os containers rodando, incluindo `api` na porta 8000.

### 3. Teste do Navegador

De qualquer máquina na rede, acesse:
- Frontend: `http://192.168.0.37:3000` (interface web)
- API: `http://192.168.0.37:8000/docs` (documentação da API)

## Portas do Sistema

| Serviço | Porta | Acesso Externo | Descrição |
|---------|-------|----------------|-----------|
| Frontend | 3000 | ✅ Sim | Interface web (React) |
| API | 8000 | ✅ Sim | Backend (FastAPI) - Probe conecta aqui |
| PostgreSQL | 5432 | ❌ Não | Banco de dados (apenas interno) |
| Redis | 6379 | ❌ Não | Cache (apenas interno) |
| AI Agent | 8001 | ❌ Não | Motor de IA (apenas interno) |

## Configuração do Docker

O `docker-compose.yml` já expõe as portas corretas:

```yaml
api:
  ports:
    - "8000:8000"  # Acessível de fora do container

frontend:
  ports:
    - "3000:3000"  # Acessível de fora do container
```

## Firewall

Se a probe estiver em outra máquina, certifique-se de que o firewall permite:
- Porta 8000 (API) - Para a probe enviar dados
- Porta 3000 (Frontend) - Para você acessar a interface

## Resumo para Seu Caso

✅ **Você está na máquina 192.168.0.37**
✅ **Docker está na mesma máquina (192.168.0.37)**
✅ **Use: `http://localhost:8000`**

Execute agora:
```batch
cd C:\Users\user\OneDrive - EmpresaXPTO Ltda\Desktop\probe
corrigir_url.bat
```

E cole o token quando solicitado!
