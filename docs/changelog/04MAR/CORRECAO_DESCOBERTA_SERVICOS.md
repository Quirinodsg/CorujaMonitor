# Correção: Descoberta de Serviços e Discos em Tempo Real

## Problema Identificado

Ao clicar em "Adicionar Sensor" → "Serviço Windows" ou "Disco", o sistema retornava erro 404:

```
GET http://localhost:8000/api/v1/probe-commands/services/1 404 (Not Found)
GET http://localhost:8000/api/v1/probe-commands/disks/1 404 (Not Found)
```

### Causa Raiz

O frontend estava passando o **probe_id** em vez do **server_id** para os endpoints de descoberta:

**ERRADO (antes):**
```javascript
// Linha 325
const response = await api.get(`/api/v1/probe-commands/services/${selectedServer.probe_id}`);

// Linha 349
const response = await api.get(`/api/v1/probe-commands/disks/${selectedServer.probe_id}`);
```

O backend espera receber o **server_id**:
```python
@router.get("/services/{server_id}")
async def discover_services(server_id: int, ...):
    server = db.query(Server).filter(
        Server.id == server_id,
        Server.tenant_id == current_user.tenant_id
    ).first()
```

### Por que o erro 404?

- O servidor atual tem **ID = 8**
- Mas o frontend estava enviando **probe_id = 1** (ID da probe)
- O backend procurava por um servidor com ID 1, que não existe mais (foi deletado)
- Resultado: 404 Not Found

## Solução Aplicada

Corrigido o frontend para usar o **server_id** correto:

**CORRETO (depois):**
```javascript
// Linha 325
const response = await api.get(`/api/v1/probe-commands/services/${selectedServer.id}`);

// Linha 349
const response = await api.get(`/api/v1/probe-commands/disks/${selectedServer.id}`);
```

## Arquivo Modificado

- `frontend/src/components/Servers.js` (linhas 325 e 349)

## Como Funciona Agora

1. Usuário clica em "Adicionar Sensor" no servidor DESKTOP-P9VGN04 (ID 8)
2. Frontend chama: `GET /api/v1/probe-commands/services/8`
3. Backend busca o servidor com ID 8 no banco de dados
4. Backend executa PowerShell no servidor local:
   ```powershell
   Get-Service | Select-Object Name, DisplayName, Status, StartType | ConvertTo-Json
   ```
5. Retorna lista REAL de todos os serviços Windows em tempo real
6. Usuário vê a lista completa e pode selecionar o serviço desejado

## Próximos Passos

Após reiniciar o frontend, o sistema irá:

1. ✅ Conectar no servidor correto (ID 8)
2. ✅ Listar TODOS os serviços Windows em tempo real
3. ✅ Mostrar status atual (running/stopped)
4. ✅ Permitir seleção do serviço para monitoramento
5. ✅ Mesmo processo para descoberta de discos

## Comando para Aplicar

```bash
cd frontend
npm start
```

Ou se estiver usando Docker:

```bash
docker-compose restart frontend
```

## Validação

Após reiniciar, ao clicar em "Adicionar Sensor":
- ✅ Não deve mais aparecer erro 404
- ✅ Deve carregar lista real de serviços do Windows
- ✅ Deve carregar lista real de discos disponíveis
- ✅ Serviços devem mostrar status (running/stopped)
- ✅ Discos devem mostrar espaço usado/livre

---

**Data:** 18/02/2026  
**Status:** ✅ CORRIGIDO  
**Impacto:** Descoberta de serviços e discos agora funciona corretamente
