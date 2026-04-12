import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom';
import axios from 'axios';
import './AIActivities.css';
import { API_URL } from '../config';

function AIActivities() {
  const [activities, setActivities] = useState([]);
  const [stats, setStats] = useState(null);
  const [pending, setPending] = useState([]);
  const [ollamaStatus, setOllamaStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('recent');
  const [autoRemediationConfig, setAutoRemediationConfig] = useState(null);
  const [selectedActivity, setSelectedActivity] = useState(null);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };

      const [activitiesRes, statsRes, pendingRes, ollamaRes, configRes] = await Promise.all([
        axios.get(`${API_URL}/ai-activities/`, { headers }),
        axios.get(`${API_URL}/ai-activities/stats`, { headers }),
        axios.get(`${API_URL}/ai-activities/pending`, { headers }),
        axios.get(`${API_URL}/ai/status`, { headers }),
        axios.get(`${API_URL}/ai/auto-resolution/config`, { headers })
      ]);

      setActivities(activitiesRes.data);
      setStats(statsRes.data);
      setPending(pendingRes.data);
      setOllamaStatus(ollamaRes.data);
      setAutoRemediationConfig(configRes.data);
    } catch (error) {
      console.error('Error loading AI activities:', error);
    } finally {
      setLoading(false);
    }
  };

  const approveResolution = async (attemptId) => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `${API_URL}/ai-activities/${attemptId}/approve`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      alert('Resolução aprovada!');
      loadData();
    } catch (error) {
      console.error('Error approving resolution:', error);
      alert('Erro ao aprovar resolução');
    }
  };

  const rejectResolution = async (attemptId) => {
    const reason = prompt('Motivo da rejeição:');
    if (!reason) return;

    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `${API_URL}/ai-activities/${attemptId}/reject`,
        { reason },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      alert('Resolução rejeitada');
      loadData();
    } catch (error) {
      console.error('Error rejecting resolution:', error);
      alert('Erro ao rejeitar resolução');
    }
  };

  const testOllama = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API_URL}/ai/test`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      if (response.data.success) {
        alert('Ollama está funcionando!\n\nResposta: ' + response.data.response);
      } else {
        alert('Erro ao testar Ollama:\n' + response.data.error);
      }
    } catch (error) {
      console.error('Error testing Ollama:', error);
      alert('Erro ao testar Ollama');
    }
  };

  if (loading) {
    return <div className="ai-activities-loading">Carregando atividades da IA...</div>;
  }

  return (
    <>
    <div className="ai-activities-container">
      <div className="ai-activities-header">
        <h2>🤖 Atividades da IA</h2>
      </div>

      {/* Ollama Status */}
      {ollamaStatus && (
        <div className={`ollama-status ${ollamaStatus.online ? 'online' : 'offline'}`}>
          <div className="ollama-status-icon">
            {ollamaStatus.online ? '✅' : '❌'}
          </div>
          <div className="ollama-status-content">
            <div className="ollama-status-title">
              Ollama: {ollamaStatus.online ? 'Online' : 'Offline'}
            </div>
            <div className="ollama-status-details">
              {ollamaStatus.online ? (
                <>
                  <span>URL: {ollamaStatus.url}</span>
                  <span>Modelo: {ollamaStatus.model}</span>
                  {ollamaStatus.version && <span>Versão: {ollamaStatus.version}</span>}
                </>
              ) : (
                <span className="ollama-error">{ollamaStatus.error}</span>
              )}
            </div>
          </div>
          {ollamaStatus.online && (
            <button className="ollama-test-btn" onClick={testOllama}>
              Testar Conexão
            </button>
          )}
        </div>
      )}

      {/* Stats Overview */}
      {stats && (
        <div className="ai-stats-overview">
          <div className="ai-stat-card">
            <div className="ai-stat-icon">🔍</div>
            <div className="ai-stat-content">
              <div className="ai-stat-number">{stats.today_analyses}</div>
              <div className="ai-stat-text">Análises Hoje</div>
            </div>
          </div>
          <div className="ai-stat-card">
            <div className="ai-stat-icon">🚀</div>
            <div className="ai-stat-content">
              <div className="ai-stat-number">{stats.today_resolutions}</div>
              <div className="ai-stat-text">Auto-Resoluções Hoje</div>
            </div>
          </div>
          <div className="ai-stat-card">
            <div className="ai-stat-icon">⏳</div>
            <div className="ai-stat-content">
              <div className="ai-stat-number">{stats.pending_approvals}</div>
              <div className="ai-stat-text">Aguardando Aprovação</div>
            </div>
          </div>
          <div className="ai-stat-card">
            <div className="ai-stat-icon">✅</div>
            <div className="ai-stat-content">
              <div className="ai-stat-number">{stats.success_rate_today.toFixed(0)}%</div>
              <div className="ai-stat-text">Taxa de Sucesso Hoje</div>
            </div>
          </div>
          <div className="ai-stat-card highlight">
            <div className="ai-stat-icon">⏱️</div>
            <div className="ai-stat-content">
              <div className="ai-stat-number">{stats.total_time_saved_minutes}</div>
              <div className="ai-stat-text">Minutos Economizados</div>
            </div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="ai-tabs">
        <button
          className={`ai-tab ${activeTab === 'recent' ? 'active' : ''}`}
          onClick={() => setActiveTab('recent')}
        >
          🔄 Atividades Recentes
        </button>
        <button
          className={`ai-tab ${activeTab === 'pending' ? 'active' : ''}`}
          onClick={() => setActiveTab('pending')}
        >
          ⏳ Aguardando Aprovação ({pending.length})
        </button>
        <button
          className={`ai-tab ${activeTab === 'remediation' ? 'active' : ''}`}
          onClick={() => setActiveTab('remediation')}
        >
          🤖 Auto-Remediação
        </button>
      </div>

      {/* Content */}
      <div className="ai-content">
        {activeTab === 'recent' && (
          <div className="ai-activities-list">
            {activities.length === 0 ? (
              <div className="ai-empty">
                <p>Nenhuma atividade recente.</p>
                <p className="ai-empty-hint">A IA começará a trabalhar quando houver incidentes.</p>
              </div>
            ) : (
              activities.map((activity) => (
                <div key={`${activity.type}-${activity.id}`} className={`ai-activity-card ${activity.type}`} onClick={() => setSelectedActivity(activity)} style={{ cursor: 'pointer' }}>
                  <div className="ai-activity-header">
                    <div className="ai-activity-title">
                      <span className="ai-activity-icon">
                        {activity.type === 'resolution' && '🚀'}
                        {activity.type === 'learning' && '🎓'}
                        {activity.type === 'analysis' && '🔍'}
                      </span>
                      <div>
                        <h4>{activity.title}</h4>
                        <p className="ai-activity-description">{activity.description}</p>
                      </div>
                    </div>
                    <span className={`ai-activity-status ${activity.status}`}>
                      {activity.status === 'success' && '✅ Sucesso'}
                      {activity.status === 'failed' && '❌ Falhou'}
                      {activity.status === 'pending' && '⏳ Pendente'}
                      {activity.status === 'learned' && '🎓 Aprendido'}
                      {activity.status === 'captured' && '📝 Capturado'}
                    </span>
                  </div>

                  <div className="ai-activity-meta">
                    {activity.server_name && (
                      <span className="ai-activity-meta-item">
                        🖥️ {activity.server_name}
                      </span>
                    )}
                    {activity.sensor_name && (
                      <span className="ai-activity-meta-item">
                        📡 {activity.sensor_name}
                      </span>
                    )}
                    <span className="ai-activity-meta-item">
                      🕐 {new Date(activity.created_at).toLocaleString('pt-BR')}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === 'pending' && (
          <div className="ai-pending-list">
            {pending.length === 0 ? (
              <div className="ai-empty">
                <p>✅ Nenhuma resolução aguardando aprovação.</p>
              </div>
            ) : (
              pending.map((item) => (
                <div key={item.id} className="ai-pending-card">
                  <div className="ai-pending-header">
                    <h4>⏳ Aguardando Aprovação</h4>
                    <span className="ai-pending-time">
                      {new Date(item.created_at).toLocaleString('pt-BR')}
                    </span>
                  </div>

                  <div className="ai-pending-info">
                    <div className="ai-pending-row">
                      <span className="ai-pending-label">Servidor:</span>
                      <span className="ai-pending-value">{item.server}</span>
                    </div>
                    <div className="ai-pending-row">
                      <span className="ai-pending-label">Sensor:</span>
                      <span className="ai-pending-value">{item.sensor}</span>
                    </div>
                    <div className="ai-pending-row">
                      <span className="ai-pending-label">Problema:</span>
                      <span className="ai-pending-value">{item.problem}</span>
                    </div>
                  </div>

                  <div className="ai-pending-solution">
                    <h5>💡 Solução Proposta:</h5>
                    <p>{item.solution}</p>
                    {item.commands && item.commands.length > 0 && (
                      <pre className="ai-pending-commands">
                        {item.commands.join('\n')}
                      </pre>
                    )}
                  </div>

                  <div className="ai-pending-metrics">
                    <div className="ai-pending-metric">
                      <span className="ai-pending-metric-label">Confiança:</span>
                      <span className="ai-pending-metric-value">
                        {(item.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div className="ai-pending-metric">
                      <span className="ai-pending-metric-label">Taxa de Sucesso:</span>
                      <span className="ai-pending-metric-value">
                        {(item.success_rate * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div className="ai-pending-metric">
                      <span className="ai-pending-metric-label">Risco:</span>
                      <span className={`ai-pending-risk ${item.risk_level}`}>
                        {item.risk_level === 'low' && '🟢 Baixo'}
                        {item.risk_level === 'medium' && '🟡 Médio'}
                        {item.risk_level === 'high' && '🔴 Alto'}
                      </span>
                    </div>
                  </div>

                  <div className="ai-pending-actions">
                    <button
                      className="ai-btn ai-btn-success"
                      onClick={() => approveResolution(item.id)}
                    >
                      ✅ Aprovar
                    </button>
                    <button
                      className="ai-btn ai-btn-danger"
                      onClick={() => rejectResolution(item.id)}
                    >
                      ❌ Rejeitar
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === 'remediation' && autoRemediationConfig && (
          <div className="auto-remediation-config">
            <div className="remediation-intro">
              <h3>🤖 Auto-Remediação Inteligente</h3>
              <p>Configure quais problemas o sistema pode resolver automaticamente e quais requerem aprovação manual.</p>
            </div>

            {/* Serviços Windows */}
            <div className="remediation-section">
              <div className="remediation-header">
                <div className="remediation-title">
                  <span className="remediation-icon">⚙️</span>
                  <div>
                    <h4>Serviços Windows</h4>
                    <span className={`remediation-badge ${autoRemediationConfig.service_auto_resolve ? 'active' : 'inactive'}`}>
                      {autoRemediationConfig.service_auto_resolve ? '✅ ATIVO' : '⚠️ INATIVO'}
                    </span>
                  </div>
                </div>
              </div>
              
              <div className="remediation-content">
                <div className="remediation-description">
                  <h5>O que faz:</h5>
                  <ul>
                    <li>Detecta quando um serviço Windows para</li>
                    <li>Tenta reiniciar o serviço automaticamente via probe</li>
                    <li>Registra todas as tentativas no log</li>
                    <li>Notifica a equipe sobre a ação</li>
                  </ul>
                </div>

                <div className="remediation-examples">
                  <h5>Exemplos de serviços:</h5>
                  <div className="remediation-tags">
                    <span className="remediation-tag">IIS (W3SVC)</span>
                    <span className="remediation-tag">SQL Server</span>
                    <span className="remediation-tag">Apache</span>
                    <span className="remediation-tag">Tomcat</span>
                    <span className="remediation-tag">Print Spooler</span>
                  </div>
                </div>

                <div className="remediation-config-box">
                  <div className="config-row">
                    <span className="config-label">Máximo de tentativas:</span>
                    <span className="config-value">{autoRemediationConfig.max_executions_per_hour || 3} por hora</span>
                  </div>
                  <div className="config-row">
                    <span className="config-label">Cooldown:</span>
                    <span className="config-value">{autoRemediationConfig.cooldown_minutes || 5} minutos</span>
                  </div>
                  <div className="config-row">
                    <span className="config-label">Requer aprovação críticos:</span>
                    <span className="config-value">{autoRemediationConfig.require_approval_for_critical ? 'Sim' : 'Não'}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Limpeza de Disco */}
            <div className="remediation-section">
              <div className="remediation-header">
                <div className="remediation-title">
                  <span className="remediation-icon">💾</span>
                  <div>
                    <h4>Limpeza de Disco</h4>
                    <span className={`remediation-badge ${autoRemediationConfig.disk_auto_resolve ? 'manual' : 'inactive'}`}>
                      {autoRemediationConfig.disk_auto_resolve ? '⚠️ MANUAL' : '⚠️ INATIVO'}
                    </span>
                  </div>
                </div>
              </div>
              
              <div className="remediation-content">
                <div className="remediation-description">
                  <h5>O que faz:</h5>
                  <ul>
                    <li>Detecta quando disco está cheio (&gt;90%)</li>
                    <li>IA analisa uso de disco e identifica arquivos grandes</li>
                    <li>Sugere ações de limpeza (temp, logs, cache)</li>
                    <li><strong>⚠️ REQUER APROVAÇÃO MANUAL</strong> antes de executar</li>
                  </ul>
                </div>

                <div className="remediation-examples">
                  <h5>Ações possíveis:</h5>
                  <div className="remediation-tags">
                    <span className="remediation-tag">Limpar C:\Windows\Temp</span>
                    <span className="remediation-tag">Limpar logs antigos</span>
                    <span className="remediation-tag">Limpar cache</span>
                    <span className="remediation-tag">Esvaziar lixeira</span>
                  </div>
                </div>

                <div className="remediation-warning">
                  <span className="warning-icon">⚠️</span>
                  <div>
                    <strong>Importante:</strong> Todas as ações de limpeza de disco requerem aprovação manual para garantir segurança dos dados.
                  </div>
                </div>
              </div>
            </div>

            {/* Memória */}
            <div className="remediation-section">
              <div className="remediation-header">
                <div className="remediation-title">
                  <span className="remediation-icon">🧠</span>
                  <div>
                    <h4>Limpeza de Memória</h4>
                    <span className={`remediation-badge ${autoRemediationConfig.memory_auto_resolve ? 'manual' : 'inactive'}`}>
                      {autoRemediationConfig.memory_auto_resolve ? '⚠️ MANUAL' : '⚠️ INATIVO'}
                    </span>
                  </div>
                </div>
              </div>
              
              <div className="remediation-content">
                <div className="remediation-description">
                  <h5>O que faz:</h5>
                  <ul>
                    <li>Detecta uso alto de memória (&gt;95%)</li>
                    <li>Identifica processos consumindo mais memória</li>
                    <li>Analisa se processos são críticos ou não-críticos</li>
                    <li>Sugere reiniciar processos não-críticos</li>
                    <li><strong>⚠️ REQUER APROVAÇÃO MANUAL</strong> antes de executar</li>
                  </ul>
                </div>

                <div className="remediation-examples">
                  <h5>Ações possíveis:</h5>
                  <div className="remediation-tags">
                    <span className="remediation-tag">Identificar memory leaks</span>
                    <span className="remediation-tag">Reiniciar processos não-críticos</span>
                    <span className="remediation-tag">Limpar cache de aplicações</span>
                    <span className="remediation-tag">Liberar memória standby</span>
                    <span className="remediation-tag">Analisar dumps de memória</span>
                  </div>
                </div>

                <div className="remediation-config-box">
                  <div className="config-row">
                    <span className="config-label">Threshold de detecção:</span>
                    <span className="config-value">95% de uso</span>
                  </div>
                  <div className="config-row">
                    <span className="config-label">Tempo de observação:</span>
                    <span className="config-value">5 minutos contínuos</span>
                  </div>
                  <div className="config-row">
                    <span className="config-label">Requer aprovação:</span>
                    <span className="config-value">Sim (sempre)</span>
                  </div>
                </div>

                <div className="remediation-warning">
                  <span className="warning-icon">⚠️</span>
                  <div>
                    <strong>Importante:</strong> Reiniciar processos pode causar perda de dados não salvos. Todas as ações requerem aprovação manual e análise do contexto.
                  </div>
                </div>
              </div>
            </div>

            {/* CPU */}
            <div className="remediation-section">
              <div className="remediation-header">
                <div className="remediation-title">
                  <span className="remediation-icon">💻</span>
                  <div>
                    <h4>CPU Alta</h4>
                    <span className={`remediation-badge ${autoRemediationConfig.cpu_auto_resolve ? 'manual' : 'inactive'}`}>
                      {autoRemediationConfig.cpu_auto_resolve ? '⚠️ MANUAL' : '⚠️ INATIVO'}
                    </span>
                  </div>
                </div>
              </div>
              
              <div className="remediation-content">
                <div className="remediation-description">
                  <h5>O que faz:</h5>
                  <ul>
                    <li>Detecta CPU alta (&gt;95%) por tempo prolongado</li>
                    <li>Identifica processos consumindo mais CPU</li>
                    <li>Analisa padrões de uso e comportamento anormal</li>
                    <li>Verifica possível malware ou processos suspeitos</li>
                    <li>Sugere ações corretivas baseadas no contexto</li>
                    <li><strong>⚠️ REQUER APROVAÇÃO MANUAL</strong> antes de executar</li>
                  </ul>
                </div>

                <div className="remediation-examples">
                  <h5>Ações possíveis:</h5>
                  <div className="remediation-tags">
                    <span className="remediation-tag">Identificar processos problemáticos</span>
                    <span className="remediation-tag">Ajustar prioridade de processos</span>
                    <span className="remediation-tag">Reiniciar serviços travados</span>
                    <span className="remediation-tag">Verificar malware/vírus</span>
                    <span className="remediation-tag">Analisar threads em loop</span>
                    <span className="remediation-tag">Otimizar agendamentos</span>
                  </div>
                </div>

                <div className="remediation-config-box">
                  <div className="config-row">
                    <span className="config-label">Threshold de detecção:</span>
                    <span className="config-value">95% de uso</span>
                  </div>
                  <div className="config-row">
                    <span className="config-label">Tempo de observação:</span>
                    <span className="config-value">10 minutos contínuos</span>
                  </div>
                  <div className="config-row">
                    <span className="config-label">Análise de malware:</span>
                    <span className="config-value">Habilitada</span>
                  </div>
                  <div className="config-row">
                    <span className="config-label">Requer aprovação:</span>
                    <span className="config-value">Sim (sempre)</span>
                  </div>
                </div>

                <div className="remediation-warning">
                  <span className="warning-icon">⚠️</span>
                  <div>
                    <strong>Importante:</strong> CPU alta pode indicar problemas sérios como malware ou loops infinitos. A IA analisa o contexto antes de sugerir ações.
                  </div>
                </div>
              </div>
            </div>

            {/* Rede */}
            <div className="remediation-section">
              <div className="remediation-header">
                <div className="remediation-title">
                  <span className="remediation-icon">📡</span>
                  <div>
                    <h4>Conectividade</h4>
                    <span className={`remediation-badge ${autoRemediationConfig.network_auto_resolve ? 'active' : 'inactive'}`}>
                      {autoRemediationConfig.network_auto_resolve ? '✅ ATIVO' : '⚠️ INATIVO'}
                    </span>
                  </div>
                </div>
              </div>
              
              <div className="remediation-content">
                <div className="remediation-description">
                  <h5>O que faz:</h5>
                  <ul>
                    <li>Detecta quando servidor não responde ao ping</li>
                    <li>Executa diagnóstico completo de rede</li>
                    <li>Verifica se é problema local, remoto ou de rota</li>
                    <li>Testa conectividade com gateway e DNS</li>
                    <li>Tenta reiniciar interface de rede automaticamente</li>
                    <li>Registra todas as tentativas e resultados</li>
                  </ul>
                </div>

                <div className="remediation-examples">
                  <h5>Diagnósticos executados:</h5>
                  <div className="remediation-tags">
                    <span className="remediation-tag">Ping para gateway</span>
                    <span className="remediation-tag">Teste de DNS</span>
                    <span className="remediation-tag">Traceroute</span>
                    <span className="remediation-tag">Status de interfaces</span>
                    <span className="remediation-tag">Verificar firewall</span>
                    <span className="remediation-tag">Reiniciar adaptador</span>
                  </div>
                </div>

                <div className="remediation-config-box">
                  <div className="config-row">
                    <span className="config-label">Tentativas de ping:</span>
                    <span className="config-value">4 pacotes</span>
                  </div>
                  <div className="config-row">
                    <span className="config-label">Timeout por tentativa:</span>
                    <span className="config-value">3 segundos</span>
                  </div>
                  <div className="config-row">
                    <span className="config-label">Reinício automático:</span>
                    <span className="config-value">{autoRemediationConfig.network_auto_resolve ? 'Habilitado' : 'Desabilitado'}</span>
                  </div>
                  <div className="config-row">
                    <span className="config-label">Cooldown entre tentativas:</span>
                    <span className="config-value">{autoRemediationConfig.cooldown_minutes || 5} minutos</span>
                  </div>
                </div>

                <div className="remediation-note">
                  <span className="note-icon">💡</span>
                  <div>
                    <strong>Nota:</strong> Problemas de conectividade são críticos. O sistema tenta diagnóstico e correção automática, mas notifica a equipe imediatamente.
                  </div>
                </div>
              </div>
            </div>

            {/* Configurações Globais */}
            <div className="remediation-section global-config">
              <div className="remediation-header">
                <div className="remediation-title">
                  <span className="remediation-icon">⚙️</span>
                  <h4>Configurações Globais</h4>
                </div>
              </div>
              
              <div className="remediation-content">
                <div className="remediation-config-box">
                  <div className="config-row">
                    <span className="config-label">Auto-remediação habilitada:</span>
                    <span className={`config-value ${autoRemediationConfig.auto_resolution_enabled ? 'enabled' : 'disabled'}`}>
                      {autoRemediationConfig.auto_resolution_enabled ? '✅ Sim' : '❌ Não'}
                    </span>
                  </div>
                  <div className="config-row">
                    <span className="config-label">Confiança mínima:</span>
                    <span className="config-value">{(autoRemediationConfig.min_confidence_threshold * 100).toFixed(0)}%</span>
                  </div>
                  <div className="config-row">
                    <span className="config-label">Taxa de sucesso mínima:</span>
                    <span className="config-value">{(autoRemediationConfig.min_success_rate_threshold * 100).toFixed(0)}%</span>
                  </div>
                  <div className="config-row">
                    <span className="config-label">Máximo por hora:</span>
                    <span className="config-value">{autoRemediationConfig.max_executions_per_hour}</span>
                  </div>
                  <div className="config-row">
                    <span className="config-label">Máximo por dia:</span>
                    <span className="config-value">{autoRemediationConfig.max_executions_per_day}</span>
                  </div>
                </div>

                <div className="remediation-note">
                  <span className="note-icon">💡</span>
                  <div>
                    <strong>Nota:</strong> Para alterar essas configurações, acesse <strong>Configurações → Avançado</strong> ou entre em contato com o administrador do sistema.
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>

      {selectedActivity && ReactDOM.createPortal(
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.75)', zIndex: 99999, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 16 }}
          onClick={() => setSelectedActivity(null)}>
          <div style={{ background: '#1e293b', borderRadius: 16, padding: 24, width: '100%', maxWidth: 640, maxHeight: '80vh', overflowY: 'auto', border: '1px solid #334155', boxShadow: '0 25px 50px rgba(0,0,0,0.5)' }}
            onClick={e => e.stopPropagation()}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
              <div style={{ fontSize: 16, fontWeight: 700, color: '#e2e8f0' }}>{selectedActivity.title}</div>
              <button onClick={() => setSelectedActivity(null)} style={{ background: 'none', border: 'none', color: '#64748b', fontSize: 24, cursor: 'pointer', padding: '0 4px' }}>✕</button>
            </div>
            <div style={{ display: 'flex', gap: 8, marginBottom: 16, flexWrap: 'wrap' }}>
              <span style={{ background: selectedActivity.success ? '#065f46' : '#7f1d1d', color: selectedActivity.success ? '#22c55e' : '#ef4444', padding: '3px 10px', borderRadius: 20, fontSize: 12, fontWeight: 600 }}>
                {selectedActivity.success ? '✅ Sucesso' : selectedActivity.status}
              </span>
              <span style={{ background: '#1e3a5f', color: '#60a5fa', padding: '3px 10px', borderRadius: 20, fontSize: 12 }}>
                {selectedActivity.type}
              </span>
              <span style={{ color: '#64748b', fontSize: 12 }}>
                🕐 {new Date(selectedActivity.created_at).toLocaleString('pt-BR')}
              </span>
            </div>
            <div style={{ background: '#0f172a', borderRadius: 10, padding: 16, fontSize: 13, color: '#cbd5e1', lineHeight: 1.7, whiteSpace: 'pre-wrap' }}>
              {selectedActivity.description || 'Sem detalhes disponíveis.'}
            </div>
          </div>
        </div>,
        document.body
      )}
    </>
  );
}

export default AIActivities;
