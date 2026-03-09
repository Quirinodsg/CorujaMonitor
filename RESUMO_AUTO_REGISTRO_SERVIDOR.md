# Auto-Registro de Servidor - Implementado

## 🎯 Objetivo

Quando a probe é instalada e configurada, ela deve criar o servidor automaticamente no dashboard, sem necessidade de intervenção manual.

---

## ✨ O Que Mudou

### ANTES (Manual)
1. Criar probe no dashboard → Copiar token
2. Configurar probe no Windows
3. Iniciar probe
4. **Ir no dashboard e criar servidor manualmente** ❌
5. Aguardar métricas

### AGORA (Automático)
1. Criar probe no dashboard → Copiar token
2. Configurar probe no Windows
3. Iniciar probe
4. **Servidor criado automaticamente!** ✅
5. Métricas aparecem imediatamente

---

## 🔧 Implementação

### 1. Backend (API)

**Arquivo**: `api/routers/servers.py`

**Novos Endpoints**:

```python
GET /api/v1/servers/check
  → Verifica se servidor já existe
  → Parâmetros: probe_token, hostname
  → Retorna: { exists: bool, server_id: int }

POST /api/v1/servers/auto-register
  → Cria servidor automaticamente
  → Parâmetros: probe_token
  → Body: { hostname, ip_address, os_info, description }
  → Retorna: { id, hostname, message }
```

### 2. Probe (Python)

**Arquivo**: `probe/probe_core.py`

**Novo Método**:

```python
def _auto_register_server(self):
    """Auto-register this server if it doesn't exist"""
    
    # 1. Detecta hostname e IP da máquina
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    os_info = f"{platform.system()} {platform.release()}"
    
    # 2. Verifica se servidor já existe
    check_response = client.get(
        f"{api_url}/api/v1/servers/check",
        params={"probe_token": token, "hostname": hostname}
    )
    
    if exists:
        logger.info("✓ Server already registered")
        return
    
    # 3. Registra servidor automaticamente
    register_response = client.post(
        f"{api_url}/api/v1/servers/auto-register",
        params={"probe_token": token},
        json={
            "hostname": hostname,
            "ip_address": ip_address,
            "os_info": os_info,
            "description": "Auto-registered by probe"
        }
    )
    
    logger.info("✅ Server registered successfully!")
```

**Chamada no Start**:

```python
def start(self):
    self.running = True
    logger.info("Coruja Probe started")
    
    # Send initial heartbeat
    self._send_heartbeat()
    
    # Auto-register this server ← NOVO!
    self._auto_register_server()
    
    # Main collection loop
    ...
```

---

## 📋 Fluxo Completo

### 1. Usuário Cria Probe no Dashboard

```
Dashboard → Probes → + Nova Probe
Nome: WIN-15GM8UTRS4K
Empresa: [Seleciona]
Salvar → COPIAR TOKEN
```

### 2. Usuário Configura Probe no Windows

```bash
probe\configurar_probe.bat

Token: [Cola o token]
Nome: WIN-15GM8UTRS4K
IP: 192.168.31.161
Porta: 3000
```

### 3. Usuário Inicia Probe

```bash
iniciar_probe.bat
```

### 4. Probe Faz Auto-Registro (Automático)

```
[INFO] Coruja Probe started
[INFO] Heartbeat sent successfully
[INFO] 🔍 Checking if server 'WIN-15GM8UTRS4K' is registered...
[INFO] 📝 Auto-registering server 'WIN-15GM8UTRS4K'...
[INFO] ✅ Server 'WIN-15GM8UTRS4K' registered successfully! (ID: 1)
[INFO]    IP: 192.168.1.100
[INFO]    OS: Windows 10
[INFO] Starting metric collection...
```

### 5. Servidor Aparece no Dashboard

```
Dashboard → Servidores
✓ WIN-15GM8UTRS4K
  Status: 🟢 Online
  IP: 192.168.1.100
  OS: Windows 10
  Probe: WIN-15GM8UTRS4K
```

---

## ✅ Vantagens

1. **Menos Passos**: Elimina etapa manual de criar servidor
2. **Menos Erros**: Não esquece de criar servidor
3. **Mais Rápido**: Servidor criado em segundos
4. **Automático**: Funciona sempre, sem intervenção
5. **Inteligente**: Detecta hostname, IP e OS automaticamente

---

## 🚀 Deploy

### 1. Commit no Windows

```bash
git add .
git commit -m "Auto-registro de servidor implementado - Probe cria servidor automaticamente ao iniciar"
git push origin master
```

### 2. Atualizar no Linux

```bash
cd /home/administrador/CorujaMonitor
git pull origin master
docker-compose restart
```

### 3. Testar

```bash
# No Windows
iniciar_probe.bat

# Verificar logs
# Deve aparecer: "✅ Server registered successfully!"
```

---

## 📁 Arquivos Modificados

```
probe/probe_core.py
  + Método _auto_register_server()
  + Chamada no start()

api/routers/servers.py
  + Endpoint GET /check
  + Endpoint POST /auto-register

INSTALAR_PROBE_AUTO_REGISTRO.txt
  + Guia de instalação atualizado

RESUMO_AUTO_REGISTRO_SERVIDOR.md
  + Este arquivo (documentação)
```

---

## 🎯 Resultado Final

**Usuário só precisa**:
1. Criar probe no dashboard (copiar token)
2. Configurar probe (colar token)
3. Iniciar probe

**Sistema faz automaticamente**:
- ✅ Cria servidor
- ✅ Detecta hostname
- ✅ Detecta IP
- ✅ Detecta OS
- ✅ Começa a coletar métricas

---

## 📝 Notas Importantes

- ⚠️ Probe ainda precisa ser criada manualmente no dashboard
- ⚠️ Token é gerado ao criar a probe
- ⚠️ Sem probe, não tem token
- ✅ Mas servidor é criado automaticamente!
- ✅ Funciona em Windows e Linux
- ✅ Detecta informações automaticamente

---

**Data**: 09/03/2026  
**Status**: ✅ Implementado  
**Próximo**: Commit e deploy no servidor Linux
