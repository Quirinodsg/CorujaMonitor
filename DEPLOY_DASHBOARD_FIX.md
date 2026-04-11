# Deploy da Correção - Dashboard Incidentes

## Arquitetura
- **Desenvolvimento (Kiro)**: Windows - onde as alterações são feitas
- **Sonda**: Windows Server - deploy via RDP
- **Produção (Linux)**: srvcmonitor001 - deploy via Git

## Arquivos Alterados

### Backend
- `api/routers/dashboard.py` (linhas 30-32, 35-38, 66-68, 73-76, 106-108)

### Frontend  
- `frontend/src/components/Incidents.js` (linha 142)

## Deploy para Linux (Produção)

### 1. Commit e Push das Alterações

No ambiente Kiro (desenvolvimento):

```bash
git add api/routers/dashboard.py
git add frontend/src/components/Incidents.js
git add DASHBOARD_INCIDENT_FIX.md
git commit -m "fix: corrige discrepância na contagem de incidentes entre dashboard e página de incidentes

- Dashboard agora conta incidentes 'open' + 'acknowledged'
- Frontend alinhado com mesma lógica
- Resolve inconsistência onde dashboard mostrava 4 e página mostrava 2"

git push origin main
```

### 2. Deploy no Servidor Linux

Conectar no servidor:
```bash
ssh root@srvcmonitor001
cd /home/administrador/CorujaMonitor
```

Atualizar o código:
```bash
# Fazer backup antes
cp api/routers/dashboard.py api/routers/dashboard.py.bak.$(date +%Y%m%d_%H%M%S)

# Puxar as alterações
git pull origin main

# Verificar as alterações
git log -1 --stat
```

### 3. Reiniciar Serviços Backend

```bash
# Reiniciar API
sudo systemctl restart coruja-api

# Verificar se subiu corretamente
sudo systemctl status coruja-api

# Verificar logs
sudo journalctl -u coruja-api -f --lines=50
```

### 4. Rebuild e Deploy do Frontend

```bash
cd frontend

# Instalar dependências (se necessário)
npm install

# Build de produção
npm run build

# Copiar para nginx (ajustar caminho conforme sua configuração)
sudo cp -r build/* /var/www/coruja-monitor/

# Reiniciar nginx
sudo systemctl restart nginx
```

### 5. Verificação

```bash
# Testar endpoint do dashboard
curl -H "Authorization: Bearer SEU_TOKEN" http://localhost:8000/api/v1/dashboard/overview

# Verificar contagem de incidentes no banco
sudo -u postgres psql coruja_monitor -c "
SELECT 
    status, 
    COUNT(*) as total 
FROM incidents 
WHERE status IN ('open', 'acknowledged') 
GROUP BY status;
"
```

## Deploy para Sonda (Windows Server)

Via RDP, copiar os arquivos:
1. `api/routers/dashboard.py`
2. `frontend/src/components/Incidents.js`

Depois:
```powershell
# Reiniciar serviços
Restart-Service CorujaAPI
Restart-Service CorujaWorker

# Rebuild frontend
cd frontend
npm run build
```

## Rollback (se necessário)

No Linux:
```bash
cd /home/administrador/CorujaMonitor

# Restaurar backup
cp api/routers/dashboard.py.bak.TIMESTAMP api/routers/dashboard.py

# Ou reverter commit
git revert HEAD
git push origin main

# Reiniciar serviços
sudo systemctl restart coruja-api
```

## Validação Pós-Deploy

1. Acessar o dashboard e verificar contagem de incidentes
2. Acessar página de incidentes e verificar se os números batem
3. Verificar logs de erro:
   ```bash
   sudo journalctl -u coruja-api -f | grep -i error
   ```

## Notas Importantes

- ✅ Alterações são apenas em lógica de contagem (baixo risco)
- ✅ Não há mudanças no schema do banco de dados
- ✅ Compatível com versão atual
- ⚠️ Fazer backup antes do deploy
- ⚠️ Testar em ambiente de desenvolvimento primeiro