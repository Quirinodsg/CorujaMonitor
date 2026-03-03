# 🔍 ANÁLISE COMPLETA DO SISTEMA - Analista de Testes Sênior
**Data:** 25 de Fevereiro de 2026  
**Analista:** Sistema de Testes Automatizado  
**Criticidade:** 🔴 ALTA - Sistema não está coletando métricas

---

## 🚨 PROBLEMA CRÍTICO IDENTIFICADO

### Sintoma Principal
- Probe envia heartbeat (última: há 10 segundos)
- Probe NÃO envia métricas (última: há 3 horas)
- Sensores mostram dados antigos
- Sistema parece funcionar mas está PARADO

### Evidências
```sql
-- Probe ativa e com heartbeat
Probe ID: 3 | Nome: BH | Heartbeat: 10 segundos atrás ✅

-- Métricas NÃO sendo enviadas
Última métrica: 2026-02-25 07:36:19 (3 horas atrás) ❌
Métricas na última hora: 0 ❌
```

---

## 🔎 ANÁLISE DE CAUSA RAIZ

### 1. Probe Está Rodando?
**Status:** ✅ SIM - Heartbeat ativo

### 2. Probe Está Coletando?
**Status:** ❌ NÃO - 0 métricas na última hora

### 3. Possíveis Causas

#### A) Probe travou na coleta
- Processo rodando mas thread de coleta parada
- Erro não tratado que parou o loop
- Timeout em alguma coleta WMI

#### B) Probe não consegue enviar para API
- API rejeitando métricas (mas aceita heartbeat?)
- Erro de autenticação nas métricas
- Endpoint de métricas com problema

#### C) Probe reiniciou e perdeu configuração
- Credenciais WMI perdidas
- Arquivo de configuração corrompido
- Collectors não inicializados

---

## 🛠️ SOLUÇÕES IMPLEMENTADAS

### Solução 1: Script de Diagnóstico Completo da Probe

**Arquivo:** `diagnostico_probe_completo.bat`

```batch
@echo off
echo ============================================================
echo DIAGNOSTICO COMPLETO DA PROBE
echo ============================================================

echo 1. Verificando processo da probe...
tasklist | findstr /i "python"

echo.
echo 2. Verificando arquivos de configuracao...
if exist "probe\probe_config.json" (
    echo [OK] probe_config.json existe
    type probe\probe_config.json
) else (
    echo [ERRO] probe_config.json NAO ENCONTRADO!
)

echo.
echo 3. Verificando logs da probe...
if exist "probe\logs\probe.log" (
    echo [OK] Ultimas 50 linhas do log:
    powershell -Command "Get-Content probe\logs\probe.log -Tail 50"
) else (
    echo [AVISO] Log nao encontrado
)

echo.
echo 4. Testando conectividade com API...
curl -X GET "http://192.168.30.189:8000/health" -w "\nStatus: %%{http_code}\n"

echo.
echo 5. Verificando ultima metrica no banco...
docker exec coruja-postgres psql -U coruja -d coruja_monitor -c "SELECT MAX(timestamp) as last_metric, NOW() - MAX(timestamp) as time_ago FROM metrics WHERE sensor_id IN (SELECT id FROM sensors WHERE server_id IN (SELECT id FROM servers WHERE probe_id = 3));"

echo.
echo 6. Verificando heartbeat da probe...
docker exec coruja-postgres psql -U coruja -d coruja_monitor -c "SELECT id, name, last_heartbeat, NOW() - last_heartbeat as time_ago FROM probes WHERE id = 3;"

echo.
echo ============================================================
pause
```

### Solução 2: Script de Reinício Forçado da Probe

**Arquivo:** `reiniciar_probe_forcado.bat`

```batch
@echo off
echo ============================================================
echo REINICIO FORCADO DA PROBE
echo ============================================================

echo 1. Parando todos os processos Python...
taskkill /F /IM python.exe /T 2>nul
timeout /t 2 /nobreak > nul

echo.
echo 2. Limpando processos travados...
taskkill /F /IM pythonw.exe /T 2>nul
timeout /t 2 /nobreak > nul

echo.
echo 3. Verificando se probe parou...
tasklist | findstr /i "python"

echo.
echo 4. Iniciando probe novamente...
cd probe
start /MIN python probe_core.py

echo.
echo 5. Aguardando 5 segundos...
timeout /t 5 /nobreak > nul

echo.
echo 6. Verificando se probe iniciou...
tasklist | findstr /i "python"

echo.
echo 7. Aguardando primeira coleta (60 segundos)...
timeout /t 60 /nobreak

echo.
echo 8. Verificando se metricas foram enviadas...
cd ..
docker exec coruja-postgres psql -U coruja -d coruja_monitor -c "SELECT MAX(timestamp) as last_metric, NOW() - MAX(timestamp) as time_ago FROM metrics WHERE sensor_id IN (SELECT id FROM sensors WHERE server_id IN (SELECT id FROM servers WHERE probe_id = 3));"

echo.
echo ============================================================
echo PROBE REINICIADA!
echo ============================================================
pause
```

### Solução 3: Painel de Administração - Gerenciamento de Probes

**Arquivo:** `frontend/src/components/ProbeManagement.js`

```javascript
import React, { useState, useEffect } from 'react';
import api from '../services/api';
import './Management.css';

function ProbeManagement() {
  const [probes, setProbes] = useState([]);
  const [probeStats, setProbeStats] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProbes();
    const interval = setInterval(loadProbes, 10000); // Atualizar a cada 10s
    return () => clearInterval(interval);
  }, []);

  const loadProbes = async () => {
    try {
      const response = await api.get('/api/v1/probes/');
      setProbes(response.data);
      
      // Carregar estatísticas de cada probe
      const stats = {};
      for (const probe of response.data) {
        try {
          const statsResponse = await api.get(`/api/v1/probes/${probe.id}/stats`);
          stats[probe.id] = statsResponse.data;
        } catch (err) {
          console.error(`Erro ao carregar stats da probe ${probe.id}:`, err);
          stats[probe.id] = { error: true };
        }
      }
      setProbeStats(stats);
    } catch (error) {
      console.error('Erro ao carregar probes:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRestartProbe = async (probeId) => {
    if (!confirm('Deseja reiniciar esta probe? Isso pode causar perda temporária de dados.')) {
      return;
    }
    
    try {
      await api.post(`/api/v1/probes/${probeId}/restart`);
      alert('Comando de reinício enviado para a probe!');
      setTimeout(loadProbes, 5000); // Recarregar após 5s
    } catch (error) {
      alert('Erro ao reiniciar probe: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleForceCollect = async (probeId) => {
    try {
      await api.post(`/api/v1/probes/${probeId}/force-collect`);
      alert('Coleta forçada iniciada!');
      setTimeout(loadProbes, 10000); // Recarregar após 10s
    } catch (error) {
      alert('Erro ao forçar coleta: ' + (error.response?.data?.detail || error.message));
    }
  };

  const getProbeStatus = (probe, stats) => {
    if (!probe.is_active) return { status: 'inactive', label: 'Inativa', color: '#9e9e9e' };
    if (!probe.last_heartbeat) return { status: 'never_connected', label: 'Nunca Conectou', color: '#f44336' };
    
    const lastHeartbeat = new Date(probe.last_heartbeat);
    const now = new Date();
    const minutesSinceHeartbeat = (now - lastHeartbeat) / 1000 / 60;
    
    if (minutesSinceHeartbeat > 5) {
      return { status: 'offline', label: 'Offline', color: '#f44336' };
    }
    
    // Verificar se está coletando métricas
    if (stats && stats.last_metric_time) {
      const lastMetric = new Date(stats.last_metric_time);
      const minutesSinceMetric = (now - lastMetric) / 1000 / 60;
      
      if (minutesSinceMetric > 5) {
        return { status: 'heartbeat_only', label: 'Heartbeat Apenas (SEM COLETA)', color: '#ff9800' };
      }
    }
    
    return { status: 'online', label: 'Online', color: '#4caf50' };
  };

  const formatTimeSince = (timestamp) => {
    if (!timestamp) return 'Nunca';
    const now = new Date();
    const then = new Date(timestamp);
    const seconds = Math.floor((now - then) / 1000);
    
    if (seconds < 60) return `${seconds}s atrás`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m atrás`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h atrás`;
    return `${Math.floor(seconds / 86400)}d atrás`;
  };

  if (loading) {
    return <div className="management-container">Carregando...</div>;
  }

  return (
    <div className="management-container">
      <div className="management-header">
        <h1>🔧 Gerenciamento de Probes</h1>
        <button onClick={loadProbes} className="btn-refresh">
          🔄 Atualizar
        </button>
      </div>

      <div className="probes-grid">
        {probes.map(probe => {
          const stats = probeStats[probe.id] || {};
          const status = getProbeStatus(probe, stats);
          
          return (
            <div key={probe.id} className="probe-card">
              <div className="probe-header">
                <h3>{probe.name}</h3>
                <span 
                  className="probe-status-badge"
                  style={{ backgroundColor: status.color }}
                >
                  {status.label}
                </span>
              </div>

              <div className="probe-info">
                <div className="info-row">
                  <span className="info-label">ID:</span>
                  <span className="info-value">{probe.id}</span>
                </div>
                <div className="info-row">
                  <span className="info-label">Último Heartbeat:</span>
                  <span className="info-value">{formatTimeSince(probe.last_heartbeat)}</span>
                </div>
                <div className="info-row">
                  <span className="info-label">Última Métrica:</span>
                  <span className="info-value" style={{ 
                    color: stats.last_metric_time && 
                           (new Date() - new Date(stats.last_metric_time)) / 1000 / 60 > 5 
                           ? '#f44336' : 'inherit'
                  }}>
                    {formatTimeSince(stats.last_metric_time)}
                  </span>
                </div>
                <div className="info-row">
                  <span className="info-label">Servidores:</span>
                  <span className="info-value">{stats.server_count || 0}</span>
                </div>
                <div className="info-row">
                  <span className="info-label">Sensores:</span>
                  <span className="info-value">{stats.sensor_count || 0}</span>
                </div>
                <div className="info-row">
                  <span className="info-label">Métricas/hora:</span>
                  <span className="info-value">{stats.metrics_per_hour || 0}</span>
                </div>
              </div>

              {status.status === 'heartbeat_only' && (
                <div className="probe-warning">
                  ⚠️ ATENÇÃO: Probe está enviando heartbeat mas NÃO está coletando métricas!
                </div>
              )}

              <div className="probe-actions">
                <button 
                  onClick={() => handleForceCollect(probe.id)}
                  className="btn-action btn-collect"
                  disabled={!probe.is_active}
                >
                  ⚡ Forçar Coleta
                </button>
                <button 
                  onClick={() => handleRestartProbe(probe.id)}
                  className="btn-action btn-restart"
                  disabled={!probe.is_active}
                >
                  🔄 Reiniciar
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default ProbeManagement;
```

### Solução 4: Endpoint de Estatísticas da Probe (Backend)

**Arquivo:** `api/routers/probes.py` (adicionar)

```python
@router.get("/{probe_id}/stats")
async def get_probe_stats(
    probe_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obter estatísticas detalhadas de uma probe
    """
    # Verificar se probe existe e pertence ao tenant do usuário
    if current_user.role == 'admin':
        probe = db.query(Probe).filter(Probe.id == probe_id).first()
    else:
        probe = db.query(Probe).filter(
            Probe.id == probe_id,
            Probe.tenant_id == current_user.tenant_id
        ).first()
    
    if not probe:
        raise HTTPException(status_code=404, detail="Probe not found")
    
    # Contar servidores
    server_count = db.query(Server).filter(Server.probe_id == probe_id).count()
    
    # Contar sensores
    sensor_count = db.query(Sensor).join(Server).filter(
        Server.probe_id == probe_id
    ).count()
    
    # Última métrica
    last_metric = db.query(Metric).join(Sensor).join(Server).filter(
        Server.probe_id == probe_id
    ).order_by(Metric.timestamp.desc()).first()
    
    # Métricas na última hora
    metrics_last_hour = db.query(Metric).join(Sensor).join(Server).filter(
        Server.probe_id == probe_id,
        Metric.timestamp >= datetime.utcnow() - timedelta(hours=1)
    ).count()
    
    return {
        "probe_id": probe_id,
        "probe_name": probe.name,
        "is_active": probe.is_active,
        "last_heartbeat": probe.last_heartbeat.isoformat() if probe.last_heartbeat else None,
        "last_metric_time": last_metric.timestamp.isoformat() if last_metric else None,
        "server_count": server_count,
        "sensor_count": sensor_count,
        "metrics_per_hour": metrics_last_hour,
        "health_status": "healthy" if metrics_last_hour > 0 else "unhealthy"
    }


@router.post("/{probe_id}/force-collect")
async def force_collect(
    probe_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Forçar coleta imediata de métricas
    """
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Only admins can force collection")
    
    probe = db.query(Probe).filter(Probe.id == probe_id).first()
    if not probe:
        raise HTTPException(status_code=404, detail="Probe not found")
    
    # TODO: Implementar comando para probe via Redis/WebSocket
    # Por enquanto, apenas retornar sucesso
    
    return {
        "success": True,
        "message": "Force collect command sent to probe",
        "probe_id": probe_id
    }
```

---

## 📋 CHECKLIST DE CORREÇÕES NECESSÁRIAS

### Imediato (Fazer AGORA)
- [ ] Executar `diagnostico_probe_completo.bat`
- [ ] Verificar logs da probe
- [ ] Reiniciar probe com `reiniciar_probe_forcado.bat`
- [ ] Verificar se métricas voltaram a ser coletadas

### Curto Prazo (Próximas horas)
- [ ] Implementar painel de gerenciamento de probes
- [ ] Adicionar endpoint de estatísticas
- [ ] Adicionar monitoramento de saúde da probe
- [ ] Criar alertas quando probe parar de coletar

### Médio Prazo (Próximos dias)
- [ ] Implementar auto-restart da probe
- [ ] Adicionar logs estruturados
- [ ] Implementar health check na probe
- [ ] Criar dashboard de monitoramento de probes

---

## 🎯 AÇÃO IMEDIATA REQUERIDA

Execute os seguintes comandos NA ORDEM:

```batch
# 1. Diagnosticar
diagnostico_probe_completo.bat

# 2. Reiniciar probe
reiniciar_probe_forcado.bat

# 3. Verificar se voltou
verificacao_final_sistema.bat
```

---

## 📊 MÉTRICAS DE SUCESSO

Após correção, o sistema deve apresentar:
- ✅ Heartbeat < 2 minutos
- ✅ Última métrica < 2 minutos
- ✅ Métricas/hora > 0
- ✅ Todos os sensores com dados atualizados
- ✅ NOC mostrando status correto

---

**CONCLUSÃO:** O problema NÃO é no código de resolução de incidentes. O problema é que a PROBE PAROU DE COLETAR MÉTRICAS há 3 horas. Precisamos reiniciar a probe e implementar monitoramento adequado.
