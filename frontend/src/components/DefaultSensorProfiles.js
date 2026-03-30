import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import './DefaultSensorProfiles.css';

const ASSET_TYPES = [
  { key: 'VM', label: 'VM (Máquina Virtual)' },
  { key: 'physical_server', label: 'Servidor Físico' },
  { key: 'network_device', label: 'Dispositivo de Rede' },
];

const ALERT_MODE_OPTIONS = [
  { value: 'normal', label: 'Normal (com alertas)' },
  { value: 'silent', label: 'Silencioso (sem alertas)' },
  { value: 'metric_only', label: 'Apenas Métrica (sem incidentes)' },
];

export default function DefaultSensorProfiles() {
  const [profiles, setProfiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState({});
  const [message, setMessage] = useState(null);

  const fetchProfiles = useCallback(async () => {
    try {
      const token = localStorage.getItem('token');
      const res = await axios.get('/api/v1/default-sensor-profiles', {
        headers: { Authorization: `Bearer ${token}` },
      });
      setProfiles(res.data);
    } catch (err) {
      setMessage({ type: 'error', text: 'Erro ao carregar perfis: ' + (err.response?.data?.detail || err.message) });
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchProfiles(); }, [fetchProfiles]);

  const handleChange = (id, field, value) => {
    setProfiles(prev => prev.map(p => p.id === id ? { ...p, [field]: value } : p));
  };

  const handleSave = async (assetType) => {
    setSaving(prev => ({ ...prev, [assetType]: true }));
    setMessage(null);
    try {
      const token = localStorage.getItem('token');
      const toSave = profiles.filter(p => p.asset_type === assetType);
      await axios.put(`/api/v1/default-sensor-profiles/${assetType}`, toSave, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setMessage({ type: 'success', text: `Perfis de "${assetType}" salvos com sucesso.` });
      fetchProfiles();
    } catch (err) {
      setMessage({ type: 'error', text: 'Erro ao salvar: ' + (err.response?.data?.detail || err.message) });
    } finally {
      setSaving(prev => ({ ...prev, [assetType]: false }));
    }
  };

  if (loading) return <div className="dsp-loading">Carregando perfis...</div>;

  return (
    <div className="dsp-container">
      <h2 className="dsp-title">Sensores Padrão por Tipo de Ativo</h2>
      <p className="dsp-subtitle">
        Configure quais sensores são criados automaticamente ao adicionar um novo servidor.
      </p>

      {message && (
        <div className={`dsp-message dsp-message--${message.type}`}>{message.text}</div>
      )}

      {ASSET_TYPES.map(({ key, label }) => {
        const assetProfiles = profiles.filter(p => p.asset_type === key);
        return (
          <div key={key} className="dsp-card">
            <div className="dsp-card-header">
              <h3>{label}</h3>
              <button
                className="dsp-btn-save"
                onClick={() => handleSave(key)}
                disabled={saving[key]}
              >
                {saving[key] ? 'Salvando...' : 'Salvar'}
              </button>
            </div>

            <table className="dsp-table">
              <thead>
                <tr>
                  <th>Sensor</th>
                  <th>Habilitado</th>
                  <th>Modo de Alerta</th>
                  <th>Aviso (%)</th>
                  <th>Crítico (%)</th>
                </tr>
              </thead>
              <tbody>
                {assetProfiles.length === 0 && (
                  <tr><td colSpan={5} className="dsp-empty">Nenhum perfil configurado</td></tr>
                )}
                {assetProfiles.map(p => (
                  <tr key={p.id}>
                    <td className="dsp-sensor-type">{p.sensor_type}</td>
                    <td>
                      <input
                        type="checkbox"
                        checked={p.enabled}
                        onChange={e => handleChange(p.id, 'enabled', e.target.checked)}
                      />
                    </td>
                    <td>
                      <select
                        value={p.alert_mode}
                        onChange={e => handleChange(p.id, 'alert_mode', e.target.value)}
                        className="dsp-select"
                      >
                        {ALERT_MODE_OPTIONS.map(o => (
                          <option key={o.value} value={o.value}>{o.label}</option>
                        ))}
                      </select>
                    </td>
                    <td>
                      {(p.sensor_type === 'ping' || p.sensor_type === 'system' || p.sensor_type === 'uptime') ? (
                        <span className="dsp-na" title={p.sensor_type === 'ping' ? 'Ping alerta apenas se offline' : 'Uptime alerta apenas em reboot'}>—</span>
                      ) : (
                        <input
                          type="number"
                          value={p.threshold_warning ?? ''}
                          onChange={e => handleChange(p.id, 'threshold_warning', e.target.value ? Number(e.target.value) : null)}
                          className="dsp-input-num"
                          min={0} max={100}
                        />
                      )}
                    </td>
                    <td>
                      {(p.sensor_type === 'ping' || p.sensor_type === 'system' || p.sensor_type === 'uptime') ? (
                        <span className="dsp-na" title={p.sensor_type === 'ping' ? 'Ping alerta apenas se offline' : 'Uptime alerta apenas em reboot'}>—</span>
                      ) : (
                        <input
                          type="number"
                          value={p.threshold_critical ?? ''}
                          onChange={e => handleChange(p.id, 'threshold_critical', e.target.value ? Number(e.target.value) : null)}
                          className="dsp-input-num"
                          min={0} max={100}
                        />
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        );
      })}
    </div>
  );
}
