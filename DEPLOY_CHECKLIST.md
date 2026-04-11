# ✅ Checklist de Deploy - Correção Dashboard

## Pré-Deploy (Kiro - Windows)

- [ ] Testar alterações localmente
- [ ] Verificar se não há erros de sintaxe
- [ ] Commit das alterações
- [ ] Push para GitHub

```bash
git add api/routers/dashboard.py frontend/src/components/Incidents.js
git commit -m "fix: corrige contagem de incidentes no dashboard"
git push origin main
```

## Deploy Linux (srvcmonitor001)

### 1. Conectar e Preparar
```bash
ssh root@srvcmonitor001
cd /home/administrador/CorujaMonitor
```

- [ ] Conectado no servidor
- [ ] No diretório correto

### 2. Backup
```bash
mkdir -p backups/dashboard-fix-$(date +%Y%m%d_%H%M%S)
cp api/routers/dashboard.py backups/dashboard-fix-$(date +%Y%m%d_%H%M%S)/
```

- [ ] Backup criado

### 3. Atualizar Código
```bash
git pull origin main
```

- [ ] Código atualizado
- [ ] Verificar arquivos alterados: `git log -1 --stat`

### 4. Reiniciar Backend
```bash
sudo systemctl restart coruja-api
sudo systemctl status coruja-api
```

- [ ] API reiniciada
- [ ] API rodando sem erros

### 5. Rebuild Frontend
```bash
cd frontend
npm run build
sudo cp -r build/* /var/www/coruja-monitor/
sudo systemctl reload nginx
cd ..
```

- [ ] Frontend buildado
- [ ] Arquivos copiados
- [ ] Nginx recarregado

### 6. Verificação
```bash
# Ver logs
sudo journalctl -u coruja-api -f --lines=20

# Verificar incidentes no banco
sudo -u postgres psql coruja_monitor -c "
SELECT status, COUNT(*) 
FROM incidents 
WHERE status IN ('open', 'acknowledged') 
GROUP BY status;"
```

- [ ] Logs sem erros
- [ ] Contagem no banco verificada

## Testes Pós-Deploy

- [ ] Acessar dashboard - verificar número de incidentes
- [ ] Acessar página de incidentes - verificar se números batem
- [ ] Clicar em "Incidentes Abertos" no dashboard
- [ ] Verificar se mostra mesma quantidade na página
- [ ] Testar com usuário admin
- [ ] Testar com usuário normal (tenant)

## Rollback (se necessário)

```bash
cd /home/administrador/CorujaMonitor
cp backups/dashboard-fix-TIMESTAMP/dashboard.py api/routers/dashboard.py
sudo systemctl restart coruja-api
```

## Deploy Sonda (Windows Server) - Via RDP

- [ ] Copiar `api/routers/dashboard.py`
- [ ] Copiar `frontend/src/components/Incidents.js`
- [ ] Reiniciar serviços Windows
- [ ] Rebuild frontend: `cd frontend && npm run build`

## Notas

**Tempo estimado**: 10-15 minutos
**Risco**: Baixo (apenas lógica de contagem)
**Downtime**: ~30 segundos (restart da API)

**Contato em caso de problemas**: 
- Verificar logs: `sudo journalctl -u coruja-api -f`
- Rollback disponível via backup