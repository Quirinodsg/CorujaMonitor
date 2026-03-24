import React, { useState, useEffect } from 'react';
import api from '../services/api';
import './Management.css';
import './AIOps.css';

function AIOps() {
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(false);
  const [anomalies, setAnomalies] = useState([]);
  const [correlations, setCorrelations] = useState([]);
  const [actionPlans, setActionPlans] = useState([]);
  const [sensors, setSensors] = useState([]);
  const [selectedSensor, setSelectedSensor] = useState(null);
  const [selectedIncident, setSelectedIncident] = useState(null);
  const [rcaResult, setRcaResult] = useState(null);
  const [stats, setStats] = useState({
    total_anomalies: 0,
    total_correlations: 0,
    total_action_plans: 0,
    automated_actions: 0
  });
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [detailsType, setDetailsType] = useState(null);

  useEffect(() => {
    loadSensors();
    loadStats();
  }, []);

  const loadSensors = async () => {
    try {
      const response = await api.get('/sensors');
      setSensors(response.data);
    } catch (error) {
      console.error('Erro ao carregar sensores:', error);
    }
  };

  const loadStats = async () => {
    // Simular estatísticas (em produção, criar endpoint específico)
    setStats({
      total_anomalies: 12,
      total_correlations: 5,
      total_action_plans: 8,
      automated_actions: 15
    });
  };

  const detectAnomalies = async (sensorId) => {
    setLoading(true);
    try {
      const response = await api.post('/aiops/anomaly-detection', {
        sensor_id: sensorId,
        lookback_hours: 24
      });
      
      setAnomalies(prev => [...prev, {
        ...response.data,
        timestamp: new Date().toISOString()
      }]);
      
      alert(`Análise concluída!\n\nAnomalias detectadas: ${response.data.anomaly_detected ? 'SIM' : 'NÃO'}\nConfiança: ${(response.data.confidence * 100).toFixed(1)}%`);
    } catch (error) {
      console.error('Erro ao detectar anomalias:', error);
      alert('Erro ao detectar anomalias: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const correlateEvents = async () => {
    setLoading(true);
    try {
      const response = await api.post('/aiops/event-correlation', {
        time_window_minutes: 30,
        severity_filter: ['critical', 'warning']
      });
      
      setCorrelations(prev => [...prev, {
        ...response.data,
        timestamp: new Date().toISOString()
      }]);
      
      alert(`Correlação concluída!\n\nGrupos encontrados: ${response.data.total_groups}\nPadrão: ${response.data.analysis?.pattern || 'N/A'}`);
    } catch (error) {
      console.error('Erro ao correlacionar eventos:', error);
      alert('Erro ao correlacionar eventos: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const analyzeRootCause = async (incidentId) => {
    setLoading(true);
    try {
      const response = await api.post('/aiops/root-cause-analysis', {
        incident_id: incidentId
      });
      
      setRcaResult(response.data);
      setActiveTab('rca');
    } catch (error) {
      console.error('Erro ao analisar causa raiz:', error);
      alert('Erro ao analisar causa raiz: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const createActionPlan = async (incidentId) => {
    setLoading(true);
    try {
      const response = await api.post(`/aiops/action-plan/${incidentId}?include_correlation=true`);
      
      setActionPlans(prev => [...prev, {
        ...response.data,
        timestamp: new Date().toISOString()
      }]);
      
      setActiveTab('action-plans');
      alert('Plano de ação criado com sucesso!');
    } catch (error) {
      console.error('Erro ao criar plano de ação:', error);
      alert('Erro ao criar plano de ação: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const renderOverview = () => (
    <div className="aiops-overview">
      <h2>🤖 AIOps Dashboard</h2>
      <p className="overview-description">
        Inteligência Artificial para Operações de TI - Monitoramento proativo e análise automatizada
      </p>

      <div className="stats-grid">
        <div 
          className="stat-card anomalies clickable" 
          onClick={() => {
            if (anomalies.length > 0) {
              setActiveTab('anomaly-detection');
            } else {
              alert('Nenhuma anomalia detectada ainda.\n\nPara começar:\n1. Vá para a aba "Detecção de Anomalias"\n2. Selecione um sensor\n3. Clique em "Detectar Anomalias"');
            }
          }}
          title="Clique para ver detalhes"
        >
          <div className="stat-icon">🔍</div>
          <div className="stat-content">
            <h3>Anomalias Detectadas</h3>
            <p className="stat-number">{anomalies.filter(a => a.anomaly_detected).length}</p>
            <small>Últimas 24 horas • {anomalies.length} análises realizadas</small>
          </div>
          {anomalies.length > 0 && <div className="click-hint">👆 Ver detalhes</div>}
        </div>

        <div 
          className="stat-card correlations clickable"
          onClick={() => {
            if (correlations.length > 0) {
              setActiveTab('correlations');
            } else {
              alert('Nenhuma correlação realizada ainda.\n\nPara começar:\n1. Vá para a aba "Correlação de Eventos"\n2. Clique em "Correlacionar Eventos"');
            }
          }}
          title="Clique para ver detalhes"
        >
          <div className="stat-icon">🔗</div>
          <div className="stat-content">
            <h3>Eventos Correlacionados</h3>
            <p className="stat-number">{correlations.reduce((sum, c) => sum + c.total_groups, 0)}</p>
            <small>Grupos identificados • {correlations.length} análises</small>
          </div>
          {correlations.length > 0 && <div className="click-hint">👆 Ver detalhes</div>}
        </div>

        <div 
          className="stat-card action-plans clickable"
          onClick={() => {
            if (actionPlans.length > 0) {
              setActiveTab('action-plans');
            } else {
              alert('Nenhum plano de ação criado ainda.\n\nPara começar:\n1. Vá para a aba "Análise de Causa Raiz"\n2. Digite o ID de um incidente\n3. Clique em "Analisar Causa Raiz"\n4. Depois clique em "Criar Plano de Ação"');
            }
          }}
          title="Clique para ver detalhes"
        >
          <div className="stat-icon">📋</div>
          <div className="stat-content">
            <h3>Planos de Ação</h3>
            <p className="stat-number">{actionPlans.length}</p>
            <small>Criados automaticamente</small>
          </div>
          {actionPlans.length > 0 && <div className="click-hint">👆 Ver detalhes</div>}
        </div>

        <div 
          className="stat-card automated clickable"
          onClick={() => {
            const automatedCount = actionPlans.reduce((sum, plan) => {
              return sum + (plan.immediate_actions?.filter(a => a.automated).length || 0);
            }, 0);
            if (automatedCount > 0) {
              setActiveTab('action-plans');
            } else {
              alert('Nenhuma ação automatizada disponível ainda.\n\nAções automatizadas aparecem nos planos de ação quando você:\n1. Cria um plano de ação a partir de uma análise RCA\n2. O sistema identifica ações que podem ser executadas automaticamente');
            }
          }}
          title="Clique para ver detalhes"
        >
          <div className="stat-icon">⚡</div>
          <div className="stat-content">
            <h3>Ações Automatizadas</h3>
            <p className="stat-number">
              {actionPlans.reduce((sum, plan) => {
                return sum + (plan.immediate_actions?.filter(a => a.automated).length || 0) +
                             (plan.short_term_actions?.filter(a => a.automated).length || 0);
              }, 0)}
            </p>
            <small>Disponíveis nos planos</small>
          </div>
          {actionPlans.length > 0 && <div className="click-hint">👆 Ver detalhes</div>}
        </div>
      </div>

      <div className="quick-actions">
        <h3>🚀 Ações Rápidas</h3>
        <div className="action-buttons">
          <button 
            className="action-btn primary"
            onClick={() => setActiveTab('anomaly-detection')}
          >
            🔍 Detectar Anomalias
          </button>
          <button 
            className="action-btn secondary"
            onClick={correlateEvents}
            disabled={loading}
          >
            🔗 Correlacionar Eventos
          </button>
          <button 
            className="action-btn tertiary"
            onClick={() => setActiveTab('rca')}
          >
            🎯 Análise de Causa Raiz
          </button>
        </div>
      </div>

      <div className="recent-activity">
        <div className="activity-header">
          <h3>📊 Atividade Recente</h3>
          <div className="activity-summary">
            <span className="summary-badge anomaly">
              {anomalies.length} Análises de Anomalias
            </span>
            <span className="summary-badge correlation">
              {correlations.length} Correlações
            </span>
            <span className="summary-badge plan">
              {actionPlans.length} Planos de Ação
            </span>
          </div>
        </div>
        
        <div className="activity-list">
          {anomalies.slice(-5).reverse().map((anomaly, idx) => (
            <div 
              key={`anomaly-${idx}`}
              className="activity-item clickable"
              onClick={() => setActiveTab('anomaly-detection')}
              title="Clique para ver todas as anomalias"
            >
              <span className="activity-icon">🔍</span>
              <div className="activity-content">
                <div className="activity-title">
                  <strong>{anomaly.sensor_name}</strong>
                  <span className={`activity-badge ${anomaly.anomaly_detected ? 'danger' : 'success'}`}>
                    {anomaly.anomaly_detected ? 'ANOMALIA' : 'NORMAL'}
                  </span>
                </div>
                <p>
                  {anomaly.anomaly_detected ? 
                    `Detectadas ${anomaly.anomalies?.length || 0} anomalias com ${(anomaly.confidence * 100).toFixed(0)}% de confiança` : 
                    'Comportamento normal detectado'
                  }
                </p>
                {anomaly.recommendation && (
                  <p className="activity-recommendation">
                    💡 {anomaly.recommendation}
                  </p>
                )}
                <small>🕐 {new Date(anomaly.timestamp).toLocaleString('pt-BR')}</small>
              </div>
              <div className="activity-arrow">→</div>
            </div>
          ))}
          
          {correlations.slice(-3).reverse().map((corr, idx) => (
            <div 
              key={`corr-${idx}`}
              className="activity-item clickable"
              onClick={() => setActiveTab('correlations')}
              title="Clique para ver todas as correlações"
            >
              <span className="activity-icon">🔗</span>
              <div className="activity-content">
                <div className="activity-title">
                  <strong>Correlação de Eventos</strong>
                  <span className={`activity-badge ${corr.correlated ? 'warning' : 'info'}`}>
                    {corr.correlated ? `${corr.total_groups} GRUPOS` : 'SEM CORRELAÇÃO'}
                  </span>
                </div>
                <p>
                  {corr.correlated ? 
                    `Padrão identificado: ${corr.analysis?.pattern || 'N/A'} • ${corr.analysis?.total_correlated_incidents || 0} incidentes • ${corr.analysis?.total_affected_servers || 0} servidores` :
                    'Nenhuma correlação encontrada entre os incidentes'
                  }
                </p>
                <small>🕐 {new Date(corr.timestamp).toLocaleString('pt-BR')}</small>
              </div>
              <div className="activity-arrow">→</div>
            </div>
          ))}
          
          {actionPlans.slice(-3).reverse().map((plan, idx) => (
            <div 
              key={`plan-${idx}`}
              className="activity-item clickable"
              onClick={() => setActiveTab('action-plans')}
              title="Clique para ver todos os planos"
            >
              <span className="activity-icon">📋</span>
              <div className="activity-content">
                <div className="activity-title">
                  <strong>Plano de Ação: {plan.plan_id}</strong>
                  <span className={`activity-badge ${plan.severity}`}>
                    {plan.severity.toUpperCase()}
                  </span>
                </div>
                <p>
                  ⏱️ Tempo estimado: {plan.estimated_resolution_time} • 
                  {plan.immediate_actions?.length || 0} ações imediatas • 
                  {plan.short_term_actions?.length || 0} curto prazo • 
                  {plan.long_term_actions?.length || 0} longo prazo
                </p>
                {plan.automation_available && (
                  <p className="activity-automation">
                    ⚡ Automação disponível para algumas ações
                  </p>
                )}
                <small>🕐 {new Date(plan.timestamp).toLocaleString('pt-BR')}</small>
              </div>
              <div className="activity-arrow">→</div>
            </div>
          ))}
          
          {anomalies.length === 0 && correlations.length === 0 && actionPlans.length === 0 && (
            <div className="no-activity">
              <div className="no-activity-icon">🤖</div>
              <p>Nenhuma atividade recente</p>
              <small>Execute análises para ver resultados aqui</small>
              <div className="quick-start-tips">
                <h4>Como começar:</h4>
                <ol>
                  <li>Vá para "Detecção de Anomalias" e selecione um sensor</li>
                  <li>Ou clique em "Correlacionar Eventos" para analisar incidentes</li>
                  <li>Para análise profunda, use "Análise de Causa Raiz"</li>
                </ol>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );


  const renderAnomalyDetection = () => (
    <div className="aiops-section">
      <h2>🔍 Detecção de Anomalias</h2>
      <p>Detecte comportamentos anormais em métricas usando análise estatística, média móvel e taxa de mudança.</p>

      <div className="sensor-selector">
        <label>Selecione um Sensor:</label>
        <select 
          value={selectedSensor || ''} 
          onChange={(e) => setSelectedSensor(e.target.value)}
        >
          <option value="">-- Selecione --</option>
          {sensors.map(sensor => (
            <option key={sensor.id} value={sensor.id}>
              {sensor.name} ({sensor.sensor_type}) - {sensor.server?.hostname}
            </option>
          ))}
        </select>
        
        <button 
          className="btn-detect"
          onClick={() => selectedSensor && detectAnomalies(parseInt(selectedSensor))}
          disabled={!selectedSensor || loading}
        >
          {loading ? 'Analisando...' : '🔍 Detectar Anomalias'}
        </button>
      </div>

      <div className="anomalies-results">
        <h3>Resultados</h3>
        {anomalies.length === 0 ? (
          <div className="no-results">
            <p>Nenhuma análise realizada ainda</p>
            <small>Selecione um sensor e clique em "Detectar Anomalias"</small>
          </div>
        ) : (
          <div className="results-list">
            {anomalies.map((anomaly, idx) => (
              <div key={idx} className={`result-card ${anomaly.anomaly_detected ? 'anomaly-found' : 'no-anomaly'}`}>
                <div className="result-header">
                  <h4>{anomaly.sensor_name}</h4>
                  <span className={`badge ${anomaly.anomaly_detected ? 'danger' : 'success'}`}>
                    {anomaly.anomaly_detected ? 'ANOMALIA DETECTADA' : 'NORMAL'}
                  </span>
                </div>
                
                <div className="result-details">
                  <div className="detail-item">
                    <strong>Confiança:</strong>
                    <span>{(anomaly.confidence * 100).toFixed(1)}%</span>
                  </div>
                  
                  {anomaly.anomaly_detected && (
                    <>
                      <div className="detail-item">
                        <strong>Total de Anomalias:</strong>
                        <span>{anomaly.anomalies?.length || 0}</span>
                      </div>
                      
                      <div className="detail-item full-width">
                        <strong>Recomendação:</strong>
                        <p>{anomaly.recommendation}</p>
                      </div>
                      
                      {anomaly.anomalies && anomaly.anomalies.length > 0 && (
                        <div className="anomalies-list">
                          <strong>Detalhes das Anomalias:</strong>
                          {anomaly.anomalies.slice(0, 3).map((a, i) => (
                            <div key={i} className="anomaly-detail">
                              <span>Valor: {a.value?.toFixed(2)}</span>
                              <span>Método: {a.method}</span>
                              {a.z_score && <span>Z-score: {a.z_score.toFixed(2)}</span>}
                            </div>
                          ))}
                        </div>
                      )}
                    </>
                  )}
                </div>
                
                <div className="result-footer">
                  <small>{new Date(anomaly.timestamp).toLocaleString('pt-BR')}</small>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );

  const renderCorrelations = () => (
    <div className="aiops-section">
      <h2>🔗 Correlação de Eventos</h2>
      <p>Identifique relações entre incidentes usando análise temporal e espacial.</p>

      <button 
        className="btn-correlate"
        onClick={correlateEvents}
        disabled={loading}
      >
        {loading ? 'Analisando...' : '🔗 Correlacionar Eventos (Últimos 30 min)'}
      </button>

      <div className="correlations-results">
        <h3>Resultados</h3>
        {correlations.length === 0 ? (
          <div className="no-results">
            <p>Nenhuma correlação realizada ainda</p>
            <small>Clique em "Correlacionar Eventos" para analisar</small>
          </div>
        ) : (
          <div className="results-list">
            {correlations.map((corr, idx) => (
              <div key={idx} className="result-card correlation">
                <div className="result-header">
                  <h4>Correlação #{idx + 1}</h4>
                  <span className={`badge ${corr.correlated ? 'warning' : 'info'}`}>
                    {corr.correlated ? `${corr.total_groups} GRUPOS` : 'SEM CORRELAÇÃO'}
                  </span>
                </div>
                
                {corr.correlated && (
                  <div className="result-details">
                    <div className="detail-item">
                      <strong>Padrão Identificado:</strong>
                      <span className="pattern-badge">{corr.analysis?.pattern || 'N/A'}</span>
                    </div>
                    
                    <div className="detail-item">
                      <strong>Total de Incidentes:</strong>
                      <span>{corr.analysis?.total_correlated_incidents || 0}</span>
                    </div>
                    
                    <div className="detail-item">
                      <strong>Servidores Afetados:</strong>
                      <span>{corr.analysis?.total_affected_servers || 0}</span>
                    </div>
                    
                    {corr.groups && corr.groups.length > 0 && (
                      <div className="groups-list">
                        <strong>Grupos de Incidentes:</strong>
                        {corr.groups.map((group, i) => (
                          <div key={i} className="group-card">
                            <div className="group-header">
                              <span>Grupo {i + 1}</span>
                              <span className={`severity-badge ${group.severity}`}>
                                {group.severity}
                              </span>
                            </div>
                            <div className="group-details">
                              <p>Incidentes: {group.incident_count}</p>
                              <p>Tipo: {group.correlation_type}</p>
                              <p>Duração: {group.time_span_seconds}s</p>
                              <p>Servidores: {group.affected_servers?.join(', ')}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
                
                <div className="result-footer">
                  <small>{new Date(corr.timestamp).toLocaleString('pt-BR')}</small>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );


  const renderRCA = () => (
    <div className="aiops-section">
      <h2>🎯 Análise de Causa Raiz (RCA)</h2>
      <p>Determine a causa raiz de incidentes usando análise multi-dimensional.</p>

      <div className="incident-selector">
        <label>ID do Incidente:</label>
        <input 
          type="number" 
          value={selectedIncident || ''} 
          onChange={(e) => setSelectedIncident(e.target.value)}
          placeholder="Digite o ID do incidente"
        />
        
        <button 
          className="btn-analyze"
          onClick={() => selectedIncident && analyzeRootCause(parseInt(selectedIncident))}
          disabled={!selectedIncident || loading}
        >
          {loading ? 'Analisando...' : '🎯 Analisar Causa Raiz'}
        </button>
      </div>

      {rcaResult && (
        <div className="rca-result">
          <div className="rca-header">
            <h3>Resultado da Análise</h3>
            <span className="confidence-badge">
              Confiança: {(rcaResult.confidence * 100).toFixed(0)}%
            </span>
          </div>

          <div className="rca-root-cause">
            <h4>🎯 Causa Raiz Identificada</h4>
            <p className="root-cause-text">{rcaResult.root_cause}</p>
          </div>

          <div className="rca-sections">
            <div className="rca-section">
              <h4>🔍 Sintomas Detectados</h4>
              <div className="symptoms-list">
                {rcaResult.symptoms?.map((symptom, idx) => (
                  <div key={idx} className={`symptom-item ${symptom.type}`}>
                    <span className="symptom-type">{symptom.type}</span>
                    <p>{symptom.description}</p>
                    <span className={`severity-badge ${symptom.severity}`}>
                      {symptom.severity}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <div className="rca-section">
              <h4>⏱️ Timeline de Eventos</h4>
              <div className="timeline">
                {rcaResult.timeline?.map((event, idx) => (
                  <div key={idx} className="timeline-item">
                    <div className="timeline-marker"></div>
                    <div className="timeline-content">
                      <strong>{event.event}</strong>
                      <p>{event.description}</p>
                      <small>{new Date(event.timestamp).toLocaleString('pt-BR')}</small>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="rca-section">
              <h4>🔗 Fatores Contribuintes</h4>
              <ul className="contributing-factors">
                {rcaResult.contributing_factors?.map((factor, idx) => (
                  <li key={idx}>{factor}</li>
                ))}
              </ul>
            </div>
          </div>

          <div className="rca-actions">
            <button 
              className="btn-create-plan"
              onClick={() => createActionPlan(rcaResult.incident_id)}
              disabled={loading}
            >
              📋 Criar Plano de Ação
            </button>
          </div>
        </div>
      )}
    </div>
  );

  const renderActionPlans = () => (
    <div className="aiops-section">
      <h2>📋 Planos de Ação</h2>
      <p>Planos estruturados para resolução de incidentes com ações imediatas, curto e longo prazo.</p>

      {actionPlans.length === 0 ? (
        <div className="no-results">
          <p>Nenhum plano de ação criado ainda</p>
          <small>Execute uma análise RCA e crie um plano de ação</small>
        </div>
      ) : (
        <div className="action-plans-list">
          {actionPlans.map((plan, idx) => (
            <div key={idx} className="action-plan-card">
              <div className="plan-header">
                <div>
                  <h3>{plan.plan_id}</h3>
                  <p>Incidente #{plan.incident_id}</p>
                </div>
                <div className="plan-meta">
                  <span className={`severity-badge ${plan.severity}`}>
                    {plan.severity}
                  </span>
                  <span className="time-estimate">
                    ⏱️ {plan.estimated_resolution_time}
                  </span>
                  {plan.automation_available && (
                    <span className="automation-badge">⚡ Automação Disponível</span>
                  )}
                </div>
              </div>

              <div className="plan-sections">
                <div className="plan-section immediate">
                  <h4>🚨 Ações Imediatas</h4>
                  <p className="section-description">Parar o sangramento (1-5 min)</p>
                  <div className="actions-list">
                    {plan.immediate_actions?.map((action, i) => (
                      <div key={i} className="action-item">
                        <div className="action-header">
                          <span className="priority">P{action.priority}</span>
                          <strong>{action.action}</strong>
                          <span className={`risk-badge ${action.risk_level}`}>
                            {action.risk_level}
                          </span>
                        </div>
                        {action.command && (
                          <div className="action-command">
                            <code>{action.command}</code>
                          </div>
                        )}
                        <div className="action-meta">
                          <span>⏱️ {action.estimated_time}</span>
                          {action.automated && <span>⚡ Automatizado</span>}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="plan-section short-term">
                  <h4>🔧 Ações de Curto Prazo</h4>
                  <p className="section-description">Corrigir o problema (5-30 min)</p>
                  <div className="actions-list">
                    {plan.short_term_actions?.map((action, i) => (
                      <div key={i} className="action-item">
                        <div className="action-header">
                          <span className="priority">P{action.priority}</span>
                          <strong>{action.action}</strong>
                          <span className={`risk-badge ${action.risk_level}`}>
                            {action.risk_level}
                          </span>
                        </div>
                        {action.command && (
                          <div className="action-command">
                            <code>{action.command}</code>
                          </div>
                        )}
                        <div className="action-meta">
                          <span>⏱️ {action.estimated_time}</span>
                          {action.automated && <span>⚡ Automatizado</span>}
                          {action.requires_approval && <span>⚠️ Requer Aprovação</span>}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="plan-section long-term">
                  <h4>📈 Ações de Longo Prazo</h4>
                  <p className="section-description">Prevenir recorrência (horas/dias)</p>
                  <div className="actions-list">
                    {plan.long_term_actions?.map((action, i) => (
                      <div key={i} className="action-item">
                        <div className="action-header">
                          <span className="priority">P{action.priority}</span>
                          <strong>{action.action}</strong>
                          <span className={`risk-badge ${action.risk_level}`}>
                            {action.risk_level}
                          </span>
                        </div>
                        <div className="action-meta">
                          <span>⏱️ {action.estimated_time}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div className="plan-footer">
                <small>Criado em: {new Date(plan.timestamp).toLocaleString('pt-BR')}</small>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  return (
    <div className="management-container aiops-container">
      <div className="management-header">
        <h1>🤖 AIOps - Inteligência Artificial para Operações</h1>
      </div>

      <div className="aiops-tabs">
        <button 
          className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          📊 Overview
        </button>
        <button 
          className={`tab ${activeTab === 'anomaly-detection' ? 'active' : ''}`}
          onClick={() => setActiveTab('anomaly-detection')}
        >
          🔍 Detecção de Anomalias
        </button>
        <button 
          className={`tab ${activeTab === 'correlations' ? 'active' : ''}`}
          onClick={() => setActiveTab('correlations')}
        >
          🔗 Correlação de Eventos
        </button>
        <button 
          className={`tab ${activeTab === 'rca' ? 'active' : ''}`}
          onClick={() => setActiveTab('rca')}
        >
          🎯 Análise de Causa Raiz
        </button>
        <button 
          className={`tab ${activeTab === 'action-plans' ? 'active' : ''}`}
          onClick={() => setActiveTab('action-plans')}
        >
          📋 Planos de Ação
        </button>
      </div>

      <div className="aiops-content">
        {activeTab === 'overview' && renderOverview()}
        {activeTab === 'anomaly-detection' && renderAnomalyDetection()}
        {activeTab === 'correlations' && renderCorrelations()}
        {activeTab === 'rca' && renderRCA()}
        {activeTab === 'action-plans' && renderActionPlans()}
      </div>
    </div>
  );
}

export default AIOps;
