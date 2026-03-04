# Problema: Probe Não Subiu - URL Incorreta

## Problema Identificado

A probe foi configurada com a URL **http://localhost:3000** (frontend), mas precisa se conectar à **http://localhost:8000** (API/backend).

## Por Que Não Funciona?

```
❌ ERRADO: http://localhost:3000
   └─> Esta é a interface web (React)
   └─> A probe não consegue se comunicar com o frontend

✅ CORRETO: http://localhost:8000
   └─> Esta é a API (FastAPI)
   └─> A probe envia métricas para a API
```

## Arquitetura do Sistema

```
┌─────────────────┐
│  Probe (Coleta) │
│   porta: N/A    │
└────────┬────────┘
         │ Envia métricas
         ↓
┌─────────────────┐
│   API (Backend) │
│   porta: 8000   │ ← A probe se conecta AQUI
└────────┬────────┘
         │ Fornece dados
         ↓
┌─────────────────┐
│ Frontend (React)│
│   porta: 3000   │ ← Você acessa AQUI no navegador
└─────────────────┘
```

## Solução Rápida

### Opção 1: Script Automático (RECOMENDADO)

Execute como Administrador:
```batch
cd probe
corrigir_url.bat
```

Este script vai:
1. Parar o serviço
2. Corrigir a URL para http://localhost:8000
3. Testar a conexão
4. Reiniciar o serviço

### Opção 2: Correção Manual

1. Abra o arquivo `probe/probe_config.json`

2. Altere a linha `"api_url"`:
```json
{
  "api_url": "http://localhost:8000",  ← Mude de 3000 para 8000
  "probe_token": "seu_token_aqui",
  ...
}
```

3. Reinicie o serviço:
```batch
net stop CorujaProbe
net start CorujaProbe
```

## Verificar Se Funcionou

### 1. Verificar Serviço
```batch
sc query CorujaProbe
```
Deve mostrar: `STATE: 4 RUNNING`

### 2. Verificar Logs
```batch
cd probe
type probe.log
```
Deve mostrar mensagens de sucesso, não erros de conexão

### 3. Verificar Dashboard
1. Abra http://localhost:3000
2. Vá em "Servidores"
3. Seu computador deve aparecer com status "Online"
4. Métricas devem começar a aparecer em 1-2 minutos

## Diagnóstico Completo

Se ainda não funcionar, execute:
```batch
cd probe
diagnostico_probe.bat
```

Este script mostra:
- Configuração atual
- Status do serviço
- Logs recentes
- Teste de conectividade

## Erros Comuns

### Erro: "Connection refused"
**Causa**: API não está rodando
**Solução**: 
```batch
docker-compose up -d
```

### Erro: "Invalid token"
**Causa**: Token incorreto ou expirado
**Solução**: 
1. Acesse http://localhost:3000
2. Vá em Configurações → Probes
3. Copie o token correto
4. Execute `corrigir_url.bat` e cole o novo token

### Erro: "Timeout"
**Causa**: Firewall bloqueando
**Solução**: 
- Adicione exceção no firewall para Python
- Ou desative temporariamente para testar

## Portas do Sistema

| Serviço | Porta | Acesso |
|---------|-------|--------|
| Frontend | 3000 | Navegador (você) |
| API | 8000 | Probe + Frontend |
| PostgreSQL | 5432 | Apenas API |
| Redis | 6379 | Apenas API |
| AI Agent | 8001 | Apenas API |

## Próximos Passos

Após corrigir:
1. Aguarde 1-2 minutos
2. Acesse o dashboard
3. Verifique se o servidor aparece
4. Confirme que as métricas estão sendo coletadas

## Suporte

Se o problema persistir:
1. Execute `diagnostico_probe.bat`
2. Copie a saída completa
3. Verifique os logs: `docker-compose logs api`
