import React, { useState, useEffect } from 'react';
import api from '../services/api';
import './Management.css';

function TestTools() {
  const [servers, setServers] = useState([]);
  const [sensors, setSensors] = useState([]);
  const [selectedServer, setSelectedServer] = useState('');
  const [selectedSensor, setSelectedSensor] = useState('');
  const [failureType, setFailureType] = useState('critical');
  const [customValue, setCustomValue] = useState('');
  const [duration, setDuration] = useState(5);
  const [activeFailures, setActiveFailures] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadServers();
    loadActiveFailures();
    
    // Atualizar falhas ativas a cada 5 segundos
    const interval = setInterval(() => {
      loadActiveFailures();
    }, 5000);
    
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (selectedServer) {
      loadSensors(selectedServer);
    }
  }, [selectedServer]);

  const loadServers = async () => {
    try {
      const response = await api.get('/servers');
      setServers(response.data);
    } catch (error) {
      console.error('Erro ao carregar servidores:', error);
    }
  };

  const loadSensors = async (serverId) => {
    try {
      const response = await api.get(`/sensors?server_id=${serverId}`);
      setSensors(response.data);
    } catch (error) {
      console.error('Erro ao carregar sensores:', error);
    }
  };

  const loadActiveFailures = async () => {
    try {
      console.log('🔍 Carregando falhas ativas...');
      const response = await api.get('/test-tools/simulated-failures');
      console.log('📊 Resposta do servidor:', response.data);
      console.log('📋 Falhas encontradas:', response.data.failures);
      setActiveFailures(response.data.failures || []);
    } catch (error) {
      console.error('❌ Erro ao carregar falhas ativas:', error);
      console.error('Detalhes:', error.response?.data);
    }
  };

  const handleSimulateFailure = async (e) => {
    e.preventDefault();
    if (!selectedSensor) {
      alert('Selecione um sensor');
      return;
    }

    setLoading(true);
    try {
      const payload = {
        sensor_id: parseInt(selectedSensor),
        failure_type: failureType,
        duration_minutes: duration
      };

      if (customValue) {
        payload.value = parseFloat(customValue);
      }

      console.log('⚡ Simulando falha com payload:', payload);
      const response = await api.post('/test-tools/simulate-failure', payload);
      console.log('✅ Resposta:', response.data);
      
      alert('Falha simulada com sucesso! Verifique os alertas e notificações.');
      
      // Recarregar falhas ativas
      await loadActiveFailures();
      
      // Reset form
      setSelectedServer('');
      setSelectedSensor('');
      setCustomValue('');
    } catch (error) {
      console.error('❌ Erro ao simular falha:', error);
      alert('Erro ao simular falha: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleClearAll = async () => {
    if (!window.confirm('Tem certeza que deseja limpar todas as falhas simuladas?')) {
      return;
    }

    setLoading(true);
    try {
      console.log('🧹 Limpando todas as falhas...');
      const response = await api.post('/test-tools/clear-simulated-failures');
      console.log('✅ Resposta:', response.data);
      
      alert(`Limpeza concluída!\n${response.data.metrics_deleted} métricas removidas\n${response.data.incidents_resolved} incidentes resolvidos`);
      
      // Recarregar falhas ativas
      await loadActiveFailures();
    } catch (error) {
      console.error('❌ Erro ao limpar falhas:', error);
      alert('Erro ao limpar falhas: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleResolveFailure = async (incidentId, sensorName) => {
    if (!window.confirm(`Deseja resolver a falha simulada do sensor "${sensorName}"?`)) {
      return;
    }

    try {
      console.log(`🔧 Resolvendo incidente ${incidentId}...`);
      await api.post(`/incidents/${incidentId}/resolve`, {
        resolution_notes: 'Falha simulada resolvida manualmente pelo administrador'
      });
      alert('Falha resolvida com sucesso!');
      await loadActiveFailures();
    } catch (error) {
      console.error('❌ Erro ao resolver falha:', error);
      alert('Erro ao resolver falha: ' + (error.response?.data?.detail || error.message));
    }
  };

  return (
    <div className="management-page">
      <div className="page-header">
        <h1>🧪 Ferramentas de Teste</h1>
        <p style={{ color: '#64748b', fontSize: '14px', marginTop: '8px' }}>
          Simule falhas em sensores para testar alertas e notificações
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '24px' }}>
        {/* Formulário de Simulação */}
        <div className="card">
          <div className="card-header">
            <h2>⚡ Simular Falha</h2>
          </div>
          <div className="card-body">
            <form onSubmit={handleSimulateFailure}>
              <div className="form-group">
                <label>Servidor</label>
                <select
                  value={selectedServer}
                  onChange={(e) => setSelectedServer(e.target.value)}
                  required
                  style={{
                    width: '100%',
                    padding: '10px',
                    borderRadius: '6px',
                    border: '1px solid #e5e7eb',
                    fontSize: '14px'
                  }}
                >
                  <option value="">Selecione um servidor</option>
                  {servers.map(server => (
                    <option key={server.id} value={server.id}>
                      {server.hostname}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>Sensor</label>
                <select
                  value={selectedSensor}
                  onChange={(e) => setSelectedSensor(e.target.value)}
                  required
                  disabled={!selectedServer}
                  style={{
                    width: '100%',
                    padding: '10px',
                    borderRadius: '6px',
                    border: '1px solid #e5e7eb',
                    fontSize: '14px'
                  }}
                >
                  <option value="">Selecione um sensor</option>
                  {sensors.map(sensor => (
                    <option key={sensor.id} value={sensor.id}>
                      {sensor.name} ({sensor.sensor_type})
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>Tipo de Falha</label>
                <div style={{ display: 'flex', gap: '12px' }}>
                  <label style={{ display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer' }}>
                    <input
                      type="radio"
                      value="warning"
                      checked={failureType === 'warning'}
                      onChange={(e) => setFailureType(e.target.value)}
                    />
                    <span style={{ color: '#f59e0b', fontWeight: '600' }}>⚠️ Warning</span>
                  </label>
                  <label style={{ display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer' }}>
                    <input
                      type="radio"
                      value="critical"
                      checked={failureType === 'critical'}
                      onChange={(e) => setFailureType(e.target.value)}
                    />
                    <span style={{ color: '#ef4444', fontWeight: '600' }}>🔥 Critical</span>
                  </label>
                </div>
              </div>

              <div className="form-group">
                <label>Valor Customizado (opcional)</label>
                <input
                  type="number"
                  step="0.1"
                  value={customValue}
                  onChange={(e) => setCustomValue(e.target.value)}
                  placeholder="Deixe vazio para usar valor padrão"
                  style={{
                    width: '100%',
                    padding: '10px',
                    borderRadius: '6px',
                    border: '1px solid #e5e7eb',
                    fontSize: '14px'
                  }}
                />
                <small style={{ color: '#64748b', fontSize: '12px' }}>
                  Padrão: 85% (warning) ou 98% (critical)
                </small>
              </div>

              <div className="form-group">
                <label>Duração (minutos)</label>
                <input
                  type="number"
                  min="1"
                  max="60"
                  value={duration}
                  onChange={(e) => setDuration(parseInt(e.target.value))}
                  required
                  style={{
                    width: '100%',
                    padding: '10px',
                    borderRadius: '6px',
                    border: '1px solid #e5e7eb',
                    fontSize: '14px'
                  }}
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                style={{
                  width: '100%',
                  padding: '12px',
                  background: loading ? '#94a3b8' : 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  fontSize: '16px',
                  fontWeight: '600',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  transition: 'all 0.3s ease'
                }}
              >
                {loading ? '⏳ Simulando...' : '⚡ Simular Falha'}
              </button>
            </form>
          </div>
        </div>

        {/* Falhas Ativas */}
        <div className="card">
          <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h2>🔴 Falhas Ativas ({activeFailures.length})</h2>
            {activeFailures.length > 0 && (
              <button
                onClick={handleClearAll}
                disabled={loading}
                style={{
                  padding: '8px 16px',
                  background: '#10b981',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  fontSize: '14px',
                  fontWeight: '600',
                  cursor: loading ? 'not-allowed' : 'pointer'
                }}
              >
                🧹 Limpar Todas
              </button>
            )}
          </div>
          <div className="card-body">
            {activeFailures.length === 0 ? (
              <div style={{
                textAlign: 'center',
                padding: '40px 20px',
                color: '#64748b'
              }}>
                <div style={{ fontSize: '48px', marginBottom: '16px' }}>✅</div>
                <p>Nenhuma falha simulada ativa</p>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {activeFailures.map(failure => (
                  <div
                    key={failure.id}
                    style={{
                      padding: '16px',
                      background: failure.severity === 'critical' ? '#fef2f2' : '#fffbeb',
                      border: `2px solid ${failure.severity === 'critical' ? '#ef4444' : '#f59e0b'}`,
                      borderRadius: '8px'
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', alignItems: 'center' }}>
                      <strong style={{ color: '#1e293b' }}>{failure.sensor_name}</strong>
                      <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                        <span style={{
                          padding: '4px 12px',
                          borderRadius: '12px',
                          fontSize: '12px',
                          fontWeight: '600',
                          background: failure.severity === 'critical' ? '#ef4444' : '#f59e0b',
                          color: 'white'
                        }}>
                          {failure.severity === 'critical' ? '🔥 CRITICAL' : '⚠️ WARNING'}
                        </span>
                        <button
                          onClick={() => handleResolveFailure(failure.id, failure.sensor_name)}
                          style={{
                            padding: '4px 12px',
                            background: '#10b981',
                            color: 'white',
                            border: 'none',
                            borderRadius: '6px',
                            fontSize: '12px',
                            fontWeight: '600',
                            cursor: 'pointer',
                            transition: 'all 0.2s ease'
                          }}
                          onMouseEnter={(e) => e.target.style.background = '#059669'}
                          onMouseLeave={(e) => e.target.style.background = '#10b981'}
                        >
                          ✓ Resolver
                        </button>
                      </div>
                    </div>
                    <div style={{ fontSize: '14px', color: '#475569' }}>
                      <div>🖥️ Servidor: {failure.server_name}</div>
                      <div>⏱️ Duração: {failure.duration_minutes} minutos</div>
                      <div>📅 Criado: {new Date(failure.created_at).toLocaleString('pt-BR')}</div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Informações */}
      <div className="card">
        <div className="card-header">
          <h2>ℹ️ Como Usar</h2>
        </div>
        <div className="card-body">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px' }}>
            <div>
              <h3 style={{ fontSize: '16px', color: '#1e293b', marginBottom: '8px' }}>1️⃣ Selecione</h3>
              <p style={{ fontSize: '14px', color: '#64748b', lineHeight: '1.6' }}>
                Escolha o servidor e o sensor que deseja testar
              </p>
            </div>
            <div>
              <h3 style={{ fontSize: '16px', color: '#1e293b', marginBottom: '8px' }}>2️⃣ Configure</h3>
              <p style={{ fontSize: '14px', color: '#64748b', lineHeight: '1.6' }}>
                Defina o tipo de falha (Warning ou Critical) e a duração
              </p>
            </div>
            <div>
              <h3 style={{ fontSize: '16px', color: '#1e293b', marginBottom: '8px' }}>3️⃣ Teste</h3>
              <p style={{ fontSize: '14px', color: '#64748b', lineHeight: '1.6' }}>
                Verifique se os alertas e notificações foram disparados corretamente
              </p>
            </div>
          </div>
          <div style={{
            marginTop: '20px',
            padding: '16px',
            background: '#f1f5f9',
            borderRadius: '8px',
            borderLeft: '4px solid #3b82f6'
          }}>
            <strong style={{ color: '#1e293b' }}>💡 Dica:</strong>
            <span style={{ color: '#475569', marginLeft: '8px' }}>
              As falhas simuladas são marcadas como teste e podem ser limpas a qualquer momento sem afetar dados reais.
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default TestTools;
