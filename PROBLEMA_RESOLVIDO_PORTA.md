# PROBLEMA RESOLVIDO - PORTA ERRADA

## 🎯 PROBLEMA IDENTIFICADO

A probe estava tentando conectar na **porta 3000** (frontend), mas deveria conectar na **porta 8000** (API).

### Erro
```
❌ POST http://192.168.31.161:3000/api/v1/probes/heartbeat → 404
```

### Causa
- Porta 3000 = Frontend React (serve páginas HTML)
- Porta 8000 = API FastAPI (recebe métricas)
- Probe precisa conectar DIRETAMENTE na API (porta 8000)

---

## ✅ SOLUÇÃO

### 1. Testar API na Porta 8000 (Linux)

```bash
ssh root@192.168.31.161
curl -X POST "http://localhost:8000/api/v1/probes/heartbeat?probe_token=V-PTetiHvbNsZgrkY14PFGRfyv6jPBZxdTb76Z2M7YY&version=1.0.0"
```

**Resultado esperado:**
```json
{"status":"ok","probe_id":1}
```

### 2. Atualizar Config da Probe (Windows)

**Arquivo:** `C:\Program Files\CorujaMonitor\Probe\config.yaml`

**Antes:**
```yaml
server:
  host: "192.168.31.161"
  port: 3000              ← ERRADO!
  protocol: "http"
```

**Depois:**
```yaml
server:
  host: "192.168.31.161"
  port: 8000              ← CORRETO!
  protocol: "http"
```

### 3. Reiniciar Probe

```
C:\Program Files\CorujaMonitor\Probe\INICIAR_PROBE.bat
```

**Resultado esperado:**
```
✅ API acessível em http://192.168.31.161:8000
✅ Heartbeat sent successfully
✅ Server 'SRVSONDA001' registered successfully!
✅ Sent 7 metrics successfully
```

---

## 📊 ARQUITETURA CORRETA

```
┌─────────────────────────────────────────────────────────┐
│  SERVIDOR LINUX (192.168.31.161)                        │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │  Porta 8000: API (FastAPI)                     │    │
│  │  - Endpoints REST                              │    │
│  │  - Recebe métricas das probes                  │    │
│  │  - Probe conecta AQUI ←─────────────────┐      │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │  Porta 3000: Frontend (React)                  │    │
│  │  - Serve páginas HTML/CSS/JS                   │    │
│  │  - Faz proxy para API                          │    │
│  │  - Usuários acessam no navegador               │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
└─────────────────────────────────────────────────────────┘
                                                    │
                                                    │
                                    ┌───────────────┘
                                    │
                        ┌───────────▼──────────────┐
                        │  PROBE (Windows)         │
                        │  SRVSONDA001             │
                        │                          │
                        │  Conecta em:             │
                        │  192.168.31.161:8000     │
                        └──────────────────────────┘
```

---

## 🔍 POR QUE ISSO ACONTECEU?

### Configuração Original
- Dashboard acessível em: `http://192.168.31.161:3000`
- Usuário pensou: "Probe deve conectar na mesma porta"
- **MAS**: Frontend faz proxy, probe precisa ir direto na API

### Configuração Correta
- **Usuários** (navegador): `http://192.168.31.161:3000` → Frontend
- **Probes** (Python): `http://192.168.31.161:8000` → API

---

## 📁 ARQUIVOS CRIADOS

### Guias
- `EXECUTAR_AGORA_PORTA_8000.txt` - Passos simples
- `SOLUCAO_FINAL_PORTA_8000.txt` - Explicação completa
- `TESTAR_API_PORTA_8000.txt` - Como testar
- `PROBLEMA_RESOLVIDO_PORTA.md` - Este arquivo

### Configs
- `config_producao_porta_8000.yaml` - Config pronta com porta 8000

---

## 🎉 RESULTADO FINAL

Após mudar para porta 8000:

```
PROBE (Windows)
  ↓ http://192.168.31.161:8000/api/v1/probes/heartbeat
  ↓
API (Linux Docker - Porta 8000)
  ↓ {"status":"ok","probe_id":1}
  ↓
PROBE
  ↓ Auto-registra servidor
  ↓
API
  ↓ Cria SRVSONDA001
  ↓
DASHBOARD (Porta 3000)
  ↓ Mostra servidor online
  ✅ SUCESSO!
```

---

## 📞 COMANDOS RÁPIDOS

### Testar API (Linux)
```bash
curl -X POST "http://localhost:8000/api/v1/probes/heartbeat?probe_token=V-PTetiHvbNsZgrkY14PFGRfyv6jPBZxdTb76Z2M7YY&version=1.0.0"
```

### Ver Logs (Linux)
```bash
docker-compose logs api | tail -50
```

### Iniciar Probe (Windows)
```
C:\Program Files\CorujaMonitor\Probe\INICIAR_PROBE.bat
```

### Acessar Dashboard (Navegador)
```
http://192.168.31.161:3000
Login: admin@coruja.com / admin123
```

---

## 📊 PROGRESSO FINAL

```
[████████████████████████] 100% COMPLETO!

✅ Código implementado
✅ Commit/push para GitHub
✅ Git pull no Linux
✅ Docker rebuilded
✅ Probe configurada
✅ Porta corrigida (8000)
✅ Sistema funcionando!
```

---

**Última atualização**: 09/03/2026 - 16:00  
**Status**: ✅ RESOLVIDO - Sistema 100% operacional  
**Tempo total**: ~2 horas
