# SOLUÇÃO DEFINITIVA - DISCO D (CD-ROM)

## 🔍 DIAGNÓSTICO COMPLETO

### Problema Atual
- Sensor "Disco D" aparece com 100% de uso (CRITICAL)
- Tentativa de excluir via web retorna erro: "Sem resposta do servidor"
- Disco D é uma unidade de CD-ROM que não deveria ser monitorada

### Causa Raiz
As correções que fizemos estão APENAS no Windows (máquina de desenvolvimento).
O servidor Linux NÃO TEM as correções porque não foram enviadas para o Git.

## ✅ CORREÇÕES NECESSÁRIAS

### 1. Filtro de CD-ROM (probe/collectors/disk_collector.py)
```python
# Skip CD-ROM, DVD, and removable drives
if 'cdrom' in partition.opts.lower() or partition.fstype == '':
    continue

# Skip drives with 0 total space (empty CD/DVD drives)
if usage.total == 0:
    continue
```

### 2. Exclusão via Web (api/routers/sensors.py)
```python
class SensorUpdate(BaseModel):
    is_active: Optional[bool] = None  # Para ativar/desativar sensor
```

### 3. Fallback no Frontend (frontend/src/components/Servers.js)
```javascript
// Se DELETE falhar, tentar desativar o sensor
if (error.response && error.response.status === 404) {
    await api.put(`/sensors/${sensorId}`, { is_active: false });
}
```

## 📋 PLANO DE AÇÃO

### PASSO 1: Enviar Correções para o Git (Windows)

No Git Bash:
```bash
cd "/c/Users/andre.quirino/Coruja Monitor"

git add api/routers/sensors.py
git add frontend/src/components/Servers.js  
git add probe/collectors/disk_collector.py
git add probe/config.yaml

git commit -m "fix: Adiciona filtro CD-ROM e suporte para desativar sensores"

git push origin master
```

### PASSO 2: Atualizar Servidor Linux

No PuTTY (servidor Linux):
```bash
cd /home/administrador/CorujaMonitor
git pull origin master
docker-compose restart api frontend
```

### PASSO 3: Deletar Sensor do Banco

No PuTTY (servidor Linux):
```bash
docker-compose exec postgres psql -U coruja -d coruja_monitor -c "
DELETE FROM metrics WHERE sensor_id IN (SELECT id FROM sensors WHERE name LIKE '%DISCO D%');
DELETE FROM incidents WHERE sensor_id IN (SELECT id FROM sensors WHERE name LIKE '%DISCO D%');
DELETE FROM sensor_notes WHERE sensor_id IN (SELECT id FROM sensors WHERE name LIKE '%DISCO D%');
DELETE FROM sensors WHERE name LIKE '%DISCO D%';
"
```

### PASSO 4: Atualizar Probe na Máquina de Produção

Na máquina Windows de produção (C:\Program Files\CorujaMonitor\Probe):

1. Copiar arquivo atualizado:
   ```
   Origem: C:\Users\andre.quirino\Coruja Monitor\probe\collectors\disk_collector.py
   Destino: C:\Program Files\CorujaMonitor\Probe\collectors\disk_collector.py
   ```

2. Reiniciar serviço:
   ```
   Execute: REINICIAR_PROBE_AGORA.bat
   ```

## 🎯 RESULTADO ESPERADO

Após seguir todos os passos:

✅ Sensor Disco D será deletado do banco
✅ Probe NÃO vai recriar o sensor (filtro impede)
✅ Interface web permite excluir sensores sem erro
✅ CD-ROM não aparece mais no monitoramento

## ⚠️ OBSERVAÇÕES IMPORTANTES

1. **Ordem é importante**: Primeiro envie para Git, depois atualize servidor, depois delete do banco
2. **Probe precisa ser atualizada**: Copiar arquivo manualmente na máquina de produção
3. **Reiniciar serviço**: Após copiar arquivo, reiniciar probe para aplicar filtro
4. **Teste final**: Verificar se Disco D não reaparece após alguns minutos

## 🔧 TESTE FINAL

1. Acesse: http://192.168.31.161:3000
2. Vá em: Servidores → SRVSONDA001
3. Verifique que Disco D NÃO está na lista
4. Aguarde 2-3 minutos (intervalo de coleta)
5. Recarregue a página
6. Confirme que Disco D NÃO reapareceu

## 📝 ARQUIVOS MODIFICADOS

- `api/routers/sensors.py` - Campo is_active no SensorUpdate
- `frontend/src/components/Servers.js` - Fallback para desativar sensor
- `probe/collectors/disk_collector.py` - Filtros para CD-ROM
- `probe/config.yaml` - Porta 8000 (já estava correto)

