import React, { useState, useEffect } from 'react';
import api from '../services/api';
import './SystemReset.css';

function SystemReset() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [confirmText, setConfirmText] = useState('');
  const [showConfirm, setShowConfirm] = useState(false);
  const [message, setMessage] = useState(null);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const res = await api.get('/system/stats');
      if (res.data) setStats(res.data);
    } catch (error) {
      console.error('Erro ao carregar estatísticas:', error);
    }
  };

  const handleResetClick = () => {
    setShowConfirm(true);
    setMessage(null);
  };

  const handleConfirmReset = async () => {
    if (confirmText !== 'RESETAR') {
      setMessage({ type: 'error', text: 'Digite RESETAR para confirmar' });
      return;
    }

    setLoading(true);
    setMessage(null);

    try {
      const res = await api.post('/system/reset');
      const data = res.data;
      setMessage({
        type: 'success',
        text: `Sistema resetado com sucesso! Apagados: ${data.deleted.metrics} métricas, ${data.deleted.sensors} sensores, ${data.deleted.servers} servidores, ${data.deleted.probes} probes, ${data.deleted.tenants} empresas`
      });
      setShowConfirm(false);
      setConfirmText('');
      loadStats();
    } catch (error) {
      setMessage({ type: 'error', text: error.response?.data?.detail || 'Erro ao resetar sistema' });
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    setShowConfirm(false);
    setConfirmText('');
    setMessage(null);
  };

  return (
    <div className="system-reset">
      <div className="system-reset-header">
        <h2>🔄 Reset do Sistema</h2>
        <p>Apague todos os dados e reinicie o sistema do zero</p>
      </div>

      {stats && (
        <div className="system-stats">
          <h3>Estatísticas Atuais</h3>
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-value">{stats.metrics}</div>
              <div className="stat-label">Métricas</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{stats.incidents}</div>
              <div className="stat-label">Incidentes</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{stats.sensors}</div>
              <div className="stat-label">Sensores</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{stats.servers}</div>
              <div className="stat-label">Servidores</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{stats.probes}</div>
              <div className="stat-label">Probes</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{stats.tenants}</div>
              <div className="stat-label">Empresas</div>
            </div>
          </div>
        </div>
      )}

      <div className="reset-warning">
        <h3>⚠️ ATENÇÃO</h3>
        <p>Esta ação irá:</p>
        <ul>
          <li>✗ Apagar TODAS as métricas</li>
          <li>✗ Apagar TODOS os incidentes</li>
          <li>✗ Apagar TODOS os sensores</li>
          <li>✗ Apagar TODOS os servidores</li>
          <li>✗ Apagar TODAS as probes</li>
          <li>✗ Apagar TODAS as empresas (exceto Admin)</li>
          <li>✓ Manter usuário admin</li>
        </ul>
        <p className="warning-text">
          <strong>Esta ação NÃO pode ser desfeita!</strong>
        </p>
      </div>

      {message && (
        <div className={`message ${message.type}`}>
          {message.text}
        </div>
      )}

      {!showConfirm ? (
        <button 
          className="btn-reset-danger"
          onClick={handleResetClick}
          disabled={loading}
        >
          🗑️ Resetar Sistema
        </button>
      ) : (
        <div className="confirm-box">
          <h3>Confirmar Reset</h3>
          <p>Digite <strong>RESETAR</strong> para confirmar:</p>
          <input
            type="text"
            value={confirmText}
            onChange={(e) => setConfirmText(e.target.value)}
            placeholder="Digite RESETAR"
            className="confirm-input"
            autoFocus
          />
          <div className="confirm-buttons">
            <button
              className="btn-confirm-reset"
              onClick={handleConfirmReset}
              disabled={loading || confirmText !== 'RESETAR'}
            >
              {loading ? 'Resetando...' : 'Confirmar Reset'}
            </button>
            <button
              className="btn-cancel"
              onClick={handleCancel}
              disabled={loading}
            >
              Cancelar
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default SystemReset;
