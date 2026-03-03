# 🔧 Comandos Úteis - TOPdesk

## 🚀 Reiniciar API

### Windows (Recomendado)
```bash
reiniciar_api_topdesk.bat
```

### Docker Direto
```bash
docker restart coruja-api
```

### Verificar Status
```bash
docker ps | findstr coruja-api
```

## 📋 Ver Logs

### Últimas 50 linhas
```bash
docker logs coruja-api --tail 50
```

### Últimas 100 linhas
```bash
docker logs coruja-api --tail 100
```

### Seguir logs em tempo real
```bash
docker logs coruja-api -f
```

### Procurar por TOPdesk nos logs
```bash
docker logs coruja-api --tail 200 | findstr TOPdesk
```

### Procurar por erros
```bash
docker logs coruja-api --tail 200 | findstr "error\|Error\|ERROR"
```

## 🔍 Debug

### Ver configuração do container
```bash
docker inspect coruja-api
```

### Entrar no container
```bash
docker exec -it coruja-api bash
```

### Ver variáveis de ambiente
```bash
docker exec coruja-api env | findstr TOPDESK
```

## 🔄 Reiniciar Tudo

### Reiniciar todos os containers
```bash
docker-compose restart
```

### Parar tudo
```bash
docker-compose down
```

### Iniciar tudo
```bash
docker-compose up -d
```

### Rebuild completo
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## 📊 Status do Sistema

### Ver todos os containers
```bash
docker ps
```

### Ver uso de recursos
```bash
docker stats --no-stream
```

### Ver logs de todos os serviços
```bash
docker-compose logs --tail 50
```

## 🧪 Testar Conexão

### Testar se API está respondendo
```bash
curl http://localhost:8000/health
```

### Testar endpoint de notificações
```bash
curl http://localhost:8000/api/v1/notifications/config
```

## 📁 Arquivos Importantes

### Ver configuração do TOPdesk no banco
```bash
docker exec -it coruja-db psql -U coruja -d coruja -c "SELECT name, notification_config FROM tenants;"
```

### Backup do banco antes de testar
```bash
docker exec coruja-db pg_dump -U coruja coruja > backup_antes_topdesk.sql
```

## 🔐 Verificar Credenciais

### Testar login no TOPdesk (PowerShell)
```powershell
$url = "https://grupotechbiz.topdesk.net/tas/api/incidents"
$user = "coruja.monitor"
$pass = "SUA_SENHA_AQUI"
$base64 = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("${user}:${pass}"))
$headers = @{
    "Authorization" = "Basic $base64"
    "Content-Type" = "application/json"
}
Invoke-RestMethod -Uri $url -Method Get -Headers $headers
```

### Testar login no TOPdesk (curl)
```bash
curl -u coruja.monitor:SUA_SENHA https://grupotechbiz.topdesk.net/tas/api/incidents
```

## 📝 Logs Específicos

### Ver apenas erros de TOPdesk
```bash
docker logs coruja-api 2>&1 | findstr "topdesk\|TOPdesk"
```

### Ver tentativas de autenticação
```bash
docker logs coruja-api 2>&1 | findstr "authentication\|auth\|login"
```

### Ver chamadas à API
```bash
docker logs coruja-api 2>&1 | findstr "POST.*notifications"
```

## 🛠️ Troubleshooting

### API não inicia
```bash
# Ver erro completo
docker logs coruja-api

# Verificar se porta está em uso
netstat -ano | findstr :8000

# Reiniciar forçado
docker rm -f coruja-api
docker-compose up -d coruja-api
```

### Banco de dados com problema
```bash
# Verificar conexão
docker exec coruja-api python -c "from database import engine; print(engine.connect())"

# Reiniciar banco
docker restart coruja-db
timeout /t 5
docker restart coruja-api
```

### Frontend não atualiza
```bash
# Limpar cache do navegador
# Ctrl + Shift + Delete

# Ou forçar reload
# Ctrl + Shift + R

# Ou rebuild do frontend
cd frontend
npm run build
```

## 📞 Suporte Rápido

### Coletar informações para debug
```bash
echo "=== Status dos Containers ===" > debug_topdesk.txt
docker ps >> debug_topdesk.txt
echo "" >> debug_topdesk.txt
echo "=== Logs da API ===" >> debug_topdesk.txt
docker logs coruja-api --tail 100 >> debug_topdesk.txt
echo "" >> debug_topdesk.txt
echo "=== Configuracao do Tenant ===" >> debug_topdesk.txt
docker exec -it coruja-db psql -U coruja -d coruja -c "SELECT name, notification_config FROM tenants;" >> debug_topdesk.txt
```

### Resetar configuração do TOPdesk
```bash
docker exec -it coruja-db psql -U coruja -d coruja -c "UPDATE tenants SET notification_config = jsonb_set(notification_config, '{topdesk}', '{\"enabled\": false}'::jsonb);"
```

## 🎯 Comandos Mais Usados

```bash
# 1. Reiniciar API
docker restart coruja-api

# 2. Ver logs
docker logs coruja-api --tail 50

# 3. Ver status
docker ps

# 4. Reiniciar tudo
docker-compose restart

# 5. Ver erros
docker logs coruja-api 2>&1 | findstr "error"
```

---

**Dica**: Salve este arquivo para referência rápida!
