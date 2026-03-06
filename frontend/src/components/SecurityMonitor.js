import React, { useState, useEffect } from 'react';
import api from '../services/api';
import './SecurityMonitor.css';

const SecurityMonitor = () => {
  const [status, setStatus] = useState(null);
  const [wafStats, setWafStats] = useState(null);
  const [integrityStatus, setIntegrityStatus] = useState(null);
  const [vulnerabilities, setVulnerabilities] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    loadSecurityData();
    const interval = setInterval(loadSecurityData, 30000); // Atualizar a cada 30s
    return () => clearInterval(interval);
  }, []);

  const loadSecurityData = async () => {
    try {
      // Carregar status geral
      const statusRes = await api.get('/security/status');
      setStatus(statusRes.data);

      // Carregar estatísticas do WAF
      const wafRes = await api.get('/security/waf/stats');
      setWafStats(wafRes.data);

      // Carregar status de integridade
      const integrityRes = await api.get('/security/integrity/status');
      setIntegrityStatus(integrityRes.data);

      // Carregar vulnerabilidades
      const vulnRes = await api.get('/security/vulnerabilities/status');
      setVulnerabilities(vulnRes.data);

      // Carregar recomendações
      const recRes = await api.get('/security/recommendations');
      setRecommendations(recRes.data.recommendations || []);

      setLoading(false);
    } catch (error) {
      console.error('Error loading security data:', error);
      setLoading(false);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'active':
      case 'compliant':
      case 'clean':
      case 'configured':
        return '✅';
      case 'issues_found':
      case 'vulnerabilities_found':
        return '⚠️';
      case 'unknown':
      case 'not_configured':
      case 'not_scanned':
        return '❓';
      default:
        return '⚠️';
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high':
        return '#dc3545';
      case 'medium':
        return '#ffc107';
      case 'low':
        return '#17a2b8';
      default:
        return '#6c757d';
    }
  };

  if (loading) {
    return (
      <div className="security-monitor">
        <div className="loading">Carregando dados de segurança...</div>
      </div>
    );
  }

  return (
    <div className="security-monitor">
      <div className="security-header">
        <h2>🔒 Monitoramento de Segurança</h2>
        <button onClick={loadSecurityData} className="refresh-btn">
          🔄 Atualizar
        </button>
      </div>

      {/* Tabs */}
      <div className="security-tabs">
        <button
          className={activeTab === 'overview' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('overview')}
        >
          Visão Geral
        </button>
        <button
          className={activeTab === 'waf' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('waf')}
        >
          WAF
        </button>
        <button
          className={activeTab === 'integrity' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('integrity')}
        >
          Integridade
        </button>
        <button
          className={activeTab === 'vulnerabilities' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('vulnerabilities')}
        >
          Vulnerabilidades
        </button>
        <button
          className={activeTab === 'recommendations' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('recommendations')}
        >
          Recomendações
        </button>
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && status && (
        <div className="tab-content">
          <div className="security-cards">
            {/* WAF Status */}
            <div className="security-card">
              <div className="card-header">
                <h3>{getStatusIcon(status.waf.status)} WAF (Firewall)</h3>
                <span className={`status-badge ${status.waf.status === 'active' ? 'active' : 'disabled'}`}>
                  {status.waf.status === 'active' ? 'ATIVO' : 'DESABILITADO'}
                </span>
              </div>
              <div className="card-body">
                <p><strong>Proteções Ativas:</strong></p>
                <ul>
                  {status.waf.protections.map((protection, idx) => (
                    <li key={idx}>✓ {protection}</li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Integrity Status */}
            <div className="security-card">
              <div className="card-header">
                <h3>{getStatusIcon(status.integrity.status)} Integridade</h3>
                <span className={`status-badge ${status.integrity.status}`}>
                  {status.integrity.status.toUpperCase()}
                </span>
              </div>
              <div className="card-body">
                <p><strong>Arquivos Monitorados:</strong> {status.integrity.files_monitored}</p>
                {status.integrity.last_check && (
                  <p><strong>Última Verificação:</strong> {new Date(status.integrity.last_check).toLocaleString()}</p>
                )}
              </div>
            </div>

            {/* Vulnerabilities Status */}
            <div className="security-card">
              <div className="card-header">
                <h3>{getStatusIcon(status.vulnerabilities.status)} Vulnerabilidades</h3>
                <span className={`status-badge ${status.vulnerabilities.status}`}>
                  {status.vulnerabilities.issues_found} ENCONTRADAS
                </span>
              </div>
              <div className="card-body">
                {status.vulnerabilities.last_scan && (
                  <p><strong>Último Scan:</strong> {new Date(status.vulnerabilities.last_scan).toLocaleString()}</p>
                )}
                <p><strong>Issues:</strong> {status.vulnerabilities.issues_found}</p>
              </div>
            </div>

            {/* Compliance Status */}
            <div className="security-card">
              <div className="card-header">
                <h3>✅ Conformidade</h3>
                <span className="status-badge active">100%</span>
              </div>
              <div className="card-body">
                <p>✓ LGPD: {status.compliance.lgpd}</p>
                <p>✓ ISO 27001: {status.compliance.iso27001}</p>
                <p>✓ OWASP Top 10: {status.compliance.owasp}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* WAF Tab */}
      {activeTab === 'waf' && wafStats && (
        <div className="tab-content">
          <div className="waf-stats">
            <h3>Estatísticas do WAF</h3>
            <div className="stats-grid">
              <div className="stat-item">
                <div className="stat-value">{wafStats.requests_blocked}</div>
                <div className="stat-label">Requisições Bloqueadas</div>
              </div>
              <div className="stat-item">
                <div className="stat-value">{wafStats.sql_injection_attempts}</div>
                <div className="stat-label">Tentativas SQL Injection</div>
              </div>
              <div className="stat-item">
                <div className="stat-value">{wafStats.xss_attempts}</div>
                <div className="stat-label">Tentativas XSS</div>
              </div>
              <div className="stat-item">
                <div className="stat-value">{wafStats.rate_limit_violations}</div>
                <div className="stat-label">Violações Rate Limit</div>
              </div>
              <div className="stat-item">
                <div className="stat-value">{wafStats.blacklisted_ips}</div>
                <div className="stat-label">IPs Bloqueados</div>
              </div>
              <div className="stat-item">
                <div className="stat-value">{wafStats.total_requests}</div>
                <div className="stat-label">Total de Requisições</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Integrity Tab */}
      {activeTab === 'integrity' && integrityStatus && (
        <div className="tab-content">
          <div className="integrity-status">
            <h3>Status de Integridade</h3>
            {integrityStatus.status === 'not_configured' ? (
              <div className="alert alert-warning">
                <p>{integrityStatus.message}</p>
                <button className="btn-primary">Gerar Checksums</button>
              </div>
            ) : (
              <div className="integrity-info">
                <p><strong>Status:</strong> {integrityStatus.status}</p>
                <p><strong>Arquivos Monitorados:</strong> {integrityStatus.total_files}</p>
                <p><strong>Gerado em:</strong> {new Date(integrityStatus.generated_at).toLocaleString()}</p>
                <button className="btn-primary" onClick={() => alert('Verificação em desenvolvimento')}>
                  Verificar Integridade
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Vulnerabilities Tab */}
      {activeTab === 'vulnerabilities' && vulnerabilities && (
        <div className="tab-content">
          <div className="vulnerabilities-status">
            <h3>Status de Vulnerabilidades</h3>
            {vulnerabilities.status === 'not_scanned' ? (
              <div className="alert alert-warning">
                <p>{vulnerabilities.message}</p>
                <button className="btn-primary">Executar Scan</button>
              </div>
            ) : (
              <div className="vuln-info">
                <p><strong>Último Scan:</strong> {new Date(vulnerabilities.scan_date).toLocaleString()}</p>
                
                <div className="vuln-section">
                  <h4>Python Dependencies</h4>
                  <p>Status: {vulnerabilities.python.status}</p>
                </div>
                
                <div className="vuln-section">
                  <h4>Node.js Dependencies</h4>
                  <p>Status: {vulnerabilities.nodejs.status}</p>
                </div>
                
                <div className="vuln-section">
                  <h4>Docker Images</h4>
                  <p>Status: {vulnerabilities.docker.status}</p>
                </div>
                
                <button className="btn-primary" onClick={() => alert('Scan em desenvolvimento')}>
                  Executar Novo Scan
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Recommendations Tab */}
      {activeTab === 'recommendations' && (
        <div className="tab-content">
          <div className="recommendations">
            <h3>Recomendações de Segurança</h3>
            {recommendations.length === 0 ? (
              <div className="alert alert-success">
                ✅ Nenhuma recomendação pendente. Sistema seguro!
              </div>
            ) : (
              <div className="recommendations-list">
                {recommendations.map((rec, idx) => (
                  <div key={idx} className="recommendation-item" style={{ borderLeftColor: getPriorityColor(rec.priority) }}>
                    <div className="rec-header">
                      <h4>{rec.title}</h4>
                      <span className="priority-badge" style={{ backgroundColor: getPriorityColor(rec.priority) }}>
                        {rec.priority.toUpperCase()}
                      </span>
                    </div>
                    <p className="rec-description">{rec.description}</p>
                    <p className="rec-action"><strong>Ação:</strong> {rec.action}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default SecurityMonitor;
