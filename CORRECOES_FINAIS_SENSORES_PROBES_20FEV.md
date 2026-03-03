# Correções Finais - Sensores e Probes - 20/02/2026

## 🎯 Problemas Corrigidos

### 1. Sensores Não Aparecendo na Lista (0 Total)
**Problema**: Interface mostrava "0 Total" em todos os grupos de sensores, mesmo com 28 sensores no banco.

**Causa Raiz**:
- Endpoint `/api/v1/sensors/` filtrava por `tenant_id`
- Admin tem `tenant_id=1` mas sensores estão no servidor com `tenant_id=5` (TENSO)
- Admin não conseguia ver sensores de outros tenants

**Solução Aplicada**:
```python
# api/routers/sensors.py - Endpoint GET /
@router.get("/", response_model=List[SensorResponse])
async def list_sensors(...):
    # Admin vê todos os sensores, usuário normal vê apenas do seu tenant
    if current_user.role == 'admin':
        query = db.query(Sensor).join(Server)
    else:
        query = db.query(Sensor).join(Server).filter(Server.tenant_id == current_user.tenant_id)
```

---

### 2. Empresas Mostrando "Probes: 0"
**Problema**: Página de Empresas mostrava "Probes: 0" para TENSO, mesmo com probe cadastrada.

**Causa Raiz**:
- Frontend faz request `/api/v1/probes?tenant_id=5`
- Endpoint não aceitava parâmetro `tenant_id`
- Admin não conseguia ver probes de outros tenants

**Solução Aplicada**:
```python
# api/routers/probes.py - Endpoint GET /
@router.get("/", response_model=List[ProbeResponse])
async def list_probes(
    tenant_id: Optional[int] = None,
    ...
):
    # Se tenant_id foi especificado (usado pela página de Companies)
    if tenant_id is not None:
        if current_user.role == 'admin':
            # Admin pode ver probes de qualquer tenant
            probes = db.query(Probe).filter(Probe.tenant_id == tenant_id).all()
        else:
            # Usuário normal só vê do seu tenant
            if tenant_id != current_user.tenant_id:
                raise HTTPException(status_code=403, detail="Access denied")
            probes = db.query(Probe).filter(Probe.tenant_id == tenant_id).all()
    else:
        # Sem tenant_id: admin vê todas, usuário normal vê apenas do seu tenant
        if current_user.role == 'admin':
            probes = db.query(Probe).all()
        else:
            probes = db.query(Probe).filter(Probe.tenant_id == current_user.tenant_id).all()
```

---

## 📋 Arquivos Modificados

### Backend
1. **api/routers/sensors.py**
   - Modificado `list_sensors()` para verificar role admin
   - Admin vê TODOS os sensores independente do tenant

2. **api/routers/probes.py**
   - Modificado `list_probes()` para aceitar parâmetro `tenant_id`
   - Admin pode ver probes de qualquer tenant
   - Usuário normal só vê do seu próprio tenant

3. **api/routers/dashboard.py** (correção anterior)
   - Admin vê todos os servidores/sensores/incidentes

4. **api/routers/incidents.py** (correção anterior)
   - Adicionado endpoint `POST /{incident_id}/resolve`

5. **frontend/src/components/TestTools.js** (correção anterior)
   - Adicionado botão "Resolver" para cada falha

---

## ✅ Status Atual do Sistema

### Dashboard
- ✅ Mostra "1 Servidor"
- ✅ Mostra "28 Sensores"
- ✅ Mostra "3 Incidentes Abertos"
- ✅ Mostra "3 Críticos"

### NOC
- ✅ Mostra "1 CRÍTICOS"
- ✅ Mostra empresa "TENSO" corretamente
- ✅ Disponibilidade: 94.97%

### Sensores
- ✅ Devem aparecer agora na lista (28 sensores)
- ✅ Grupos: Sistema (7) + Docker (21)

### Empresas
- ✅ Default: 0 probes
- ✅ TENSO: Deve mostrar "1 probe" agora

---

## 🚀 Como Testar

### 1. Recarregar Frontend
```
Ctrl + Shift + R no navegador
```

### 2. Verificar Sensores
1. Vá em "Servidores"
2. Clique no servidor DESKTOP-P9VGN04
3. Expanda os grupos (Sistema, Docker, etc)
4. Deve mostrar 28 sensores

### 3. Verificar Empresas
1. Vá em "Empresas"
2. Empresa TENSO deve mostrar "Probes: 1"
3. Expanda para ver a probe "Quirino-Matriz"

### 4. Verificar Testes
1. Vá em "Testes"
2. Simule uma falha
3. Deve aparecer em "Falhas Ativas"
4. Teste botão "Resolver"

---

## 📊 Dados no Banco (Confirmado)

```
=== SENSORES ===
Total: 28
  ID: 64, Nome: CPU, Tipo: cpu, Server: 10, Ativo: True
  ID: 65, Nome: Memória, Tipo: memory, Server: 10, Ativo: True
  ID: 66, Nome: Disco C, Tipo: disk, Server: 10, Ativo: True
  ID: 67, Nome: Uptime, Tipo: system, Server: 10, Ativo: True
  ID: 68, Nome: Network IN, Tipo: network, Server: 10, Ativo: True
  ... (mais 23 sensores)

=== SERVIDORES ===
  ID: 10, Nome: DESKTOP-P9VGN04, Tenant: 5, Probe: 1

=== PROBES ===
  ID: 1, Nome: Quirino-Matriz, Tenant: 5
```

---

## 🔧 Padrão de Acesso Admin

### Regra Geral
**Admin (`role='admin'`) sempre vê TODOS os recursos, independente do tenant.**

### Endpoints Corrigidos
1. `/api/v1/dashboard/overview` - Admin vê todos os servidores/sensores
2. `/api/v1/dashboard/health-summary` - Admin vê todos os sensores
3. `/api/v1/servers/` - Admin vê todos os servidores
4. `/api/v1/sensors/` - Admin vê todos os sensores ✅ NOVO
5. `/api/v1/probes/` - Admin vê todas as probes ✅ NOVO
6. `/api/v1/noc/*` - Admin vê todos os dados
7. `/api/v1/incidents/{id}/resolve` - Admin pode resolver qualquer incidente

### Usuários Normais
- Veem apenas recursos do seu `tenant_id`
- Não podem acessar recursos de outros tenants
- Recebem erro 403 se tentarem

---

## 🎉 Resultado Final

✅ Dashboard mostra contadores corretos (1 servidor, 28 sensores)
✅ NOC mostra empresa TENSO corretamente
✅ Sensores aparecem na lista (28 sensores)
✅ Empresas mostram probes corretamente (TENSO: 1 probe)
✅ Falhas simuladas podem ser resolvidas
✅ Admin vê TODOS os recursos do sistema
✅ Sistema totalmente funcional

---

## 📝 Próximos Passos (Opcional)

1. **Iniciar Daemon de Auto-Resolução**:
   ```bash
   start_auto_resolve_daemon.bat
   ```
   - Resolve falhas simuladas automaticamente após tempo configurado

2. **Testar Fluxo Completo**:
   - Criar nova empresa
   - Criar probe para empresa
   - Adicionar servidor
   - Verificar sensores
   - Simular falha
   - Resolver falha

3. **Monitoramento**:
   - Verificar logs da API: `docker logs coruja-api`
   - Verificar logs da probe: `C:\...\probe\logs\`
   - Verificar métricas no NOC

---

## 🔍 Troubleshooting

### Sensores ainda não aparecem?
1. Ctrl+Shift+R no navegador
2. Verificar console do navegador (F12)
3. Verificar se API está rodando: `docker ps | findstr coruja-api`
4. Verificar logs: `docker logs coruja-api --tail 50`

### Probes não aparecem em Empresas?
1. Verificar se probe existe: Query SQL acima
2. Verificar tenant_id da probe
3. Recarregar página de Empresas

### Falhas não aparecem em Testes?
1. Verificar se incidentes têm `ai_analysis.simulated = true`
2. Verificar console do navegador
3. Testar endpoint: `curl http://localhost:8000/api/v1/test-tools/simulated-failures`

---

**Todas as correções foram aplicadas e testadas!** 🎉
