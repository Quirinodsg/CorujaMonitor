import React, { useState, useEffect } from 'react';
import './SystemUpdates.css';

const SystemUpdates = () => {
  const [updateInfo, setUpdateInfo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [applying, setApplying] = useState(false);
  const [error, setError] = useState(null);
  const [history, setHistory] = useState([]);
  const [autoCheck, setAutoCheck] = useState(true);

  useEffect(() => {
    // Verificar atualizações ao carregar
    if (autoCheck) {
      checkForUpdates();
    }
    loadHistory();
  }, []);

  const checkForUpdates = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/updates/check');
      if (!response.ok) throw new Error('Erro ao verificar atualizações');
      
      const data = await response.json();
      setUpdateInfo(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const downloadUpdate = async () => {
    if (!updateInfo?.download_url) {
      setError('URL de download não disponível');
      return;
    }

    setDownloading(true);
    setError(null);

    try {
      const response = await fetch('/api/updates/download', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          download_url: updateInfo.download_url,
          version: updateInfo.latest_version
        })
      });

      if (!response.ok) throw new Error('Erro ao baixar atualização');
      
      const data = await response.json();
      alert(`Download concluído! Tamanho: ${(data.size / 1024 / 1024).toFixed(2)} MB`);
      
      // Perguntar se deseja aplicar agora
      if (window.confirm('Deseja aplicar a atualização agora? O sistema será reiniciado.')) {
        applyUpdate(data.version);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setDownloading(false);
    }
  };

  const applyUpdate = async (version) => {
    setApplying(true);
    setError(null);

    try {
      const response = await fetch(`/api/updates/apply?version=${version}`, {
        method: 'POST'
      });

      if (!response.ok) throw new Error('Erro ao aplicar atualização');
      
      const data = await response.json();
      alert(data.message);
      
      // Sistema será reiniciado automaticamente
      setTimeout(() => {
        window.location.reload();
      }, 5000);
    } catch (err) {
      setError(err.message);
      setApplying(false);
    }
  };

  const loadHistory = async () => {
    try {
      const response = await fetch('/api/updates/history');
      if (!response.ok) throw new Error('Erro ao carregar histórico');
      
      const data = await response.json();
      setHistory(data.backups || []);
    } catch (err) {
      console.error('Erro ao carregar histórico:', err);
    }
  };

  const rollbackToBackup = async (backupName) => {
    if (!window.confirm(`Deseja reverter para o backup: ${backupName}?`)) {
      return;
    }

    try {
      const response = await fetch(`/api/updates/rollback?backup_name=${backupName}`, {
        method: 'POST'
      });

      if (!response.ok) throw new Error('Erro ao reverter');
      
      const data = await response.json();
      alert(data.message);
      window.location.reload();
    } catch (err) {
      setError(err.message);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('pt-BR');
  };

  const formatSize = (bytes) => {
    return (bytes / 1024 / 1024).toFixed(2) + ' MB';
  };

  return (
    <div className="system-updates">
      <div className="updates-header">
        <h2>Atualizações do Sistema</h2>
        <div className="header-actions">
          <label className="auto-check-toggle">
            <input
              type="checkbox"
              checked={autoCheck}
              onChange={(e) => setAutoCheck(e.target.checked)}
            />
            <span>Verificar automaticamente</span>
          </label>
          <button
            className="btn btn-primary"
            onClick={checkForUpdates}
            disabled={loading}
          >
            {loading ? 'Verificando...' : 'Verificar Atualizações'}
          </button>
        </div>
      </div>

      {error && (
        <div className="alert alert-error">
          <span className="alert-icon">⚠️</span>
          <span>{error}</span>
        </div>
      )}

      {updateInfo && (
        <div className="glass-card update-status-card">
          <div className="glass-card-header">
            <h3>Status da Atualização</h3>
          </div>
          <div className="glass-card-body">
            <div className="version-info">
              <div className="version-item">
                <span className="version-label">Versão Atual</span>
                <span className="version-value">{updateInfo.current_version}</span>
              </div>
              
              {updateInfo.update_available && (
                <>
                  <div className="version-arrow">→</div>
                  <div className="version-item">
                    <span className="version-label">Nova Versão</span>
                    <span className="version-value version-new">
                      {updateInfo.latest_version}
                    </span>
                  </div>
                </>
              )}
            </div>

            {updateInfo.update_available ? (
              <div className="update-available">
                <div className="status-badge status-processing">
                  Atualização Disponível
                </div>
                
                {updateInfo.release_name && (
                  <h4 className="release-name">{updateInfo.release_name}</h4>
                )}
                
                {updateInfo.published_at && (
                  <p className="release-date">
                    Publicado em: {formatDate(updateInfo.published_at)}
                  </p>
                )}

                {updateInfo.changelog && (
                  <div className="changelog">
                    <h4>Novidades:</h4>
                    <div className="changelog-content">
                      {updateInfo.changelog}
                    </div>
                  </div>
                )}

                <div className="update-actions">
                  <button
                    className="btn btn-primary"
                    onClick={downloadUpdate}
                    disabled={downloading || applying}
                  >
                    {downloading ? 'Baixando...' : 'Baixar e Instalar'}
                  </button>
                </div>
              </div>
            ) : (
              <div className="update-current">
                <div className="status-badge status-online">
                  Sistema Atualizado
                </div>
                <p>Você está usando a versão mais recente do sistema.</p>
              </div>
            )}
          </div>
        </div>
      )}

      {applying && (
        <div className="glass-card applying-update">
          <div className="glass-card-body">
            <div className="loading-spinner"></div>
            <h3>Aplicando Atualização...</h3>
            <p>O sistema será reiniciado automaticamente em alguns segundos.</p>
            <p className="warning-text">⚠️ Não feche esta janela</p>
          </div>
        </div>
      )}

      {history.length > 0 && (
        <div className="glass-card backup-history">
          <div className="glass-card-header">
            <h3>Histórico de Backups</h3>
          </div>
          <div className="glass-card-body">
            <div className="backup-list">
              {history.map((backup) => (
                <div key={backup.name} className="backup-item">
                  <div className="backup-info">
                    <span className="backup-name">{backup.name}</span>
                    <span className="backup-date">{formatDate(backup.created_at)}</span>
                    <span className="backup-size">{formatSize(backup.size)}</span>
                  </div>
                  <button
                    className="btn btn-secondary btn-sm"
                    onClick={() => rollbackToBackup(backup.name)}
                  >
                    Reverter
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SystemUpdates;
