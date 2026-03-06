import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './KnowledgeBase.css';
import { API_URL } from '../config';

function KnowledgeBase() {
  const [entries, setEntries] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedEntry, setSelectedEntry] = useState(null);
  const [filterType, setFilterType] = useState('all');

  useEffect(() => {
    loadData();
  }, [filterType]);

  const loadData = async () => {
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };

      const [entriesRes, statsRes] = await Promise.all([
        axios.get(`${API_URL}/knowledge-base/`, {
          headers,
          params: filterType !== 'all' ? { sensor_type: filterType } : {}
        }),
        axios.get(`${API_URL}/knowledge-base/stats`, { headers })
      ]);

      setEntries(entriesRes.data);
      setStats(statsRes.data);
    } catch (error) {
      console.error('Error loading knowledge base:', error);
    } finally {
      setLoading(false);
    }
  };

  const viewDetails = async (entryId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_URL}/knowledge-base/${entryId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSelectedEntry(response.data);
    } catch (error) {
      console.error('Error loading entry details:', error);
    }
  };

  const toggleAutoResolution = async (entryId, currentValue) => {
    try {
      const token = localStorage.getItem('token');
      await axios.put(
        `${API_URL}/knowledge-base/${entryId}`,
        { auto_resolution_enabled: !currentValue },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      loadData();
    } catch (error) {
      console.error('Error updating entry:', error);
      alert('Erro ao atualizar entrada');
    }
  };

  const getRiskColor = (risk) => {
    switch (risk) {
      case 'low': return '#4caf50';
      case 'medium': return '#ff9800';
      case 'high': return '#f44336';
      default: return '#999';
    }
  };

  const getRiskLabel = (risk) => {
    switch (risk) {
      case 'low': return '🟢 Baixo';
      case 'medium': return '🟡 Médio';
      case 'high': return '🔴 Alto';
      default: return '⚪ Desconhecido';
    }
  };

  const filteredEntries = entries.filter(entry =>
    entry.problem_title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    entry.problem_signature.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return <div className="kb-loading">Carregando base de conhecimento...</div>;
  }

  if (selectedEntry) {
    return (
      <div className="kb-container">
        <div className="kb-header">
          <button className="kb-back-btn" onClick={() => setSelectedEntry(null)}>
            ← Voltar
          </button>
          <h2>🧠 Detalhes do Problema</h2>
        </div>

        <div className="kb-detail">
          <div className="kb-detail-header">
            <h3>{selectedEntry.entry.problem_title}</h3>
            <span className="kb-risk-badge" style={{ backgroundColor: getRiskColor(selectedEntry.entry.risk_level) }}>
              {getRiskLabel(selectedEntry.entry.risk_level)}
            </span>
          </div>

          <div className="kb-detail-section">
            <h4>📝 Descrição</h4>
            <p>{selectedEntry.entry.problem_description}</p>
          </div>

          <div className="kb-detail-section">
            <h4>🔍 Causa Raiz</h4>
            <p>{selectedEntry.entry.root_cause}</p>
          </div>

          <div className="kb-detail-section">
            <h4>✅ Solução</h4>
            <p>{selectedEntry.entry.solution_description}</p>
            {selectedEntry.entry.solution_steps && (
              <ol>
                {selectedEntry.entry.solution_steps.map((step, idx) => (
                  <li key={idx}>{step}</li>
                ))}
              </ol>
            )}
          </div>

          {selectedEntry.entry.solution_commands && selectedEntry.entry.solution_commands.length > 0 && (
            <div className="kb-detail-section">
              <h4>💻 Comandos</h4>
              <pre className="kb-commands">
                {selectedEntry.entry.solution_commands.join('\n')}
              </pre>
            </div>
          )}

          <div className="kb-detail-section">
            <h4>📊 Estatísticas</h4>
            <div className="kb-stats-grid">
              <div className="kb-stat-item">
                <span className="kb-stat-label">Identificado</span>
                <span className="kb-stat-value">{selectedEntry.entry.times_matched}x</span>
              </div>
              <div className="kb-stat-item">
                <span className="kb-stat-label">Resolvido com sucesso</span>
                <span className="kb-stat-value">{selectedEntry.entry.times_successful}x</span>
              </div>
              <div className="kb-stat-item">
                <span className="kb-stat-label">Taxa de sucesso</span>
                <span className="kb-stat-value">{(selectedEntry.entry.success_rate * 100).toFixed(0)}%</span>
              </div>
            </div>
          </div>

          {selectedEntry.recent_resolutions && selectedEntry.recent_resolutions.length > 0 && (
            <div className="kb-detail-section">
              <h4>📅 Histórico Recente</h4>
              <div className="kb-history">
                {selectedEntry.recent_resolutions.map((res) => (
                  <div key={res.id} className="kb-history-item">
                    <span className={`kb-history-status ${res.success ? 'success' : 'failed'}`}>
                      {res.success ? '✅' : '❌'}
                    </span>
                    <span className="kb-history-date">
                      {new Date(res.created_at).toLocaleString('pt-BR')}
                    </span>
                    <span className="kb-history-time">
                      {res.execution_time_seconds ? `${res.execution_time_seconds.toFixed(1)}s` : '-'}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="kb-detail-actions">
            <button
              className={`kb-btn ${selectedEntry.entry.auto_resolution_enabled ? 'kb-btn-danger' : 'kb-btn-success'}`}
              onClick={() => toggleAutoResolution(selectedEntry.entry.id, selectedEntry.entry.auto_resolution_enabled)}
            >
              {selectedEntry.entry.auto_resolution_enabled ? 'Desativar Auto-Resolução' : 'Ativar Auto-Resolução'}
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="kb-container">
      <div className="kb-header">
        <h2>🧠 Base de Conhecimento</h2>
      </div>

      <div className="kb-search-bar">
        <input
          type="text"
          placeholder="🔍 Buscar problema..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="kb-search-input"
        />
        <select
          value={filterType}
          onChange={(e) => setFilterType(e.target.value)}
          className="kb-filter-select"
        >
          <option value="all">Todos os tipos</option>
          <option value="cpu">CPU</option>
          <option value="memory">Memória</option>
          <option value="disk">Disco</option>
          <option value="service">Serviço</option>
          <option value="network">Rede</option>
        </select>
      </div>

      {stats && (
        <div className="kb-stats-overview">
          <div className="kb-stat-card">
            <div className="kb-stat-icon">📚</div>
            <div className="kb-stat-content">
              <div className="kb-stat-number">{stats.total_entries}</div>
              <div className="kb-stat-text">Problemas Conhecidos</div>
            </div>
          </div>
          <div className="kb-stat-card">
            <div className="kb-stat-icon">🤖</div>
            <div className="kb-stat-content">
              <div className="kb-stat-number">{stats.auto_resolution_enabled}</div>
              <div className="kb-stat-text">Com Auto-Resolução</div>
            </div>
          </div>
          <div className="kb-stat-card">
            <div className="kb-stat-icon">✅</div>
            <div className="kb-stat-content">
              <div className="kb-stat-number">{(stats.average_success_rate * 100).toFixed(0)}%</div>
              <div className="kb-stat-text">Taxa de Sucesso Média</div>
            </div>
          </div>
          <div className="kb-stat-card">
            <div className="kb-stat-icon">🚀</div>
            <div className="kb-stat-content">
              <div className="kb-stat-number">{stats.total_resolutions_this_month}</div>
              <div className="kb-stat-text">Resoluções Este Mês</div>
            </div>
          </div>
        </div>
      )}

      <div className="kb-entries">
        <h3>📋 Problemas Conhecidos</h3>
        {filteredEntries.length === 0 ? (
          <div className="kb-empty">
            <p>Nenhum problema encontrado.</p>
            <p className="kb-empty-hint">A IA aprenderá com as resoluções dos técnicos.</p>
          </div>
        ) : (
          filteredEntries.map((entry) => (
            <div key={entry.id} className="kb-entry-card">
              <div className="kb-entry-header">
                <div className="kb-entry-title">
                  <span className="kb-entry-icon">
                    {entry.sensor_type === 'cpu' && '🔥'}
                    {entry.sensor_type === 'memory' && '💾'}
                    {entry.sensor_type === 'disk' && '💿'}
                    {entry.sensor_type === 'service' && '⚙️'}
                    {entry.sensor_type === 'network' && '🌐'}
                  </span>
                  <h4>{entry.problem_title}</h4>
                </div>
                <span className="kb-risk-badge" style={{ backgroundColor: getRiskColor(entry.risk_level) }}>
                  {getRiskLabel(entry.risk_level)}
                </span>
              </div>

              <div className="kb-entry-stats">
                <span className="kb-entry-stat">
                  Taxa de sucesso: <strong>{(entry.success_rate * 100).toFixed(0)}%</strong> ({entry.times_successful}/{entry.times_matched})
                </span>
                <span className={`kb-entry-auto ${entry.auto_resolution_enabled ? 'enabled' : 'disabled'}`}>
                  Auto-resolução: {entry.auto_resolution_enabled ? '✅ Ativa' : '⚠️ Desativada'}
                </span>
              </div>

              {entry.last_matched_at && (
                <div className="kb-entry-last">
                  Última execução: {new Date(entry.last_matched_at).toLocaleString('pt-BR')}
                </div>
              )}

              <div className="kb-entry-actions">
                <button className="kb-btn kb-btn-primary" onClick={() => viewDetails(entry.id)}>
                  Ver Detalhes
                </button>
                <button
                  className={`kb-btn ${entry.auto_resolution_enabled ? 'kb-btn-warning' : 'kb-btn-success'}`}
                  onClick={() => toggleAutoResolution(entry.id, entry.auto_resolution_enabled)}
                >
                  {entry.auto_resolution_enabled ? 'Desativar' : 'Ativar'}
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default KnowledgeBase;
