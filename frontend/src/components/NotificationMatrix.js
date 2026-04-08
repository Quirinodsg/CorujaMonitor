import React, { useState, useEffect } from 'react';
import api from '../services/api';
import './NotificationMatrix.css';

const SENSOR_TYPES = [
  { key: 'ping', label: 'PING (Servidor Offline)' },
  { key: 'cpu', label: 'CPU' },
  { key: 'memory', label: 'Memória' },
  { key: 'disk', label: 'Disco' },
  { key: 'service', label: 'Serviço' },
  { key: 'http', label: 'HTTP (Sites)' },
  { key: 'printer', label: 'Impressora' },
  { key: 'equallogic', label: 'Storage (EqualLogic)' },
  { key: 'conflex', label: 'Ar-condicionado (Conflex)' },
  { key: 'engetron', label: 'Nobreak (Engetron)' },
  { key: 'snmp', label: 'Ativos de Rede (SNMP)' },
  { key: 'docker', label: 'Docker' },
  { key: 'kubernetes', label: 'Kubernetes' },
  { key: 'hyperv', label: 'Hyper-V' },
  { key: 'network_in', label: 'Link Internet (IN)' },
  { key: 'network_out', label: 'Link Internet (OUT)' },
  { key: 'system', label: 'Reboot (Informativo)' },
];

const CHANNELS = [
  { key: 'email', label: '📧 Email' },
  { key: 'teams', label: '💬 Teams' },
  { key: 'ticket', label: '🎫 Chamado' },
  { key: 'sms', label: '📱 SMS' },
  { key: 'whatsapp', label: '📲 WhatsApp' },
  { key: 'phone_call', label: '📞 Ligação' },
];

function NotificationMatrix() {
  const [matrix, setMatrix] = useState({});
  const [isDefault, setIsDefault] = useState(true);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saveMsg, setSaveMsg] = useState({ text: '', type: '' });

  useEffect(() => {
    loadMatrix();
  }, []);

  const loadMatrix = async () => {
    try {
      const response = await api.get('/notifications/matrix');
      setMatrix(response.data.matrix || {});
      setIsDefault(response.data.is_default ?? true);
    } catch (error) {
      console.error('Erro ao carregar matriz de notificação:', error);
    } finally {
      setLoading(false);
    }
  };

  const isChannelEnabled = (sensorType, channel) => {
    const channels = matrix[sensorType] || [];
    return channels.includes(channel);
  };

  const toggleChannel = (sensorType, channel) => {
    setMatrix(prev => {
      const current = prev[sensorType] || [];
      const updated = current.includes(channel)
        ? current.filter(c => c !== channel)
        : [...current, channel];
      return { ...prev, [sensorType]: updated };
    });
  };

  const handleSave = async () => {
    setSaving(true);
    setSaveMsg({ text: '', type: '' });
    try {
      await api.put('/notifications/matrix', { matrix });
      setIsDefault(false);
      setSaveMsg({ text: 'Matriz salva com sucesso!', type: 'success' });
      setTimeout(() => setSaveMsg({ text: '', type: '' }), 3000);
    } catch (error) {
      setSaveMsg({
        text: 'Erro ao salvar: ' + (error.response?.data?.detail || error.message),
        type: 'error'
      });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="nm-loading">
        <div className="nm-spinner"></div>
        <span>Carregando matriz...</span>
      </div>
    );
  }

  return (
    <div className="nm-container">
      <div className="nm-header">
        <div className="nm-title-row">
          <h3>📋 Matriz de Notificação</h3>
          {isDefault && (
            <span className="nm-badge-default">Usando configuração padrão</span>
          )}
        </div>
        <p className="nm-description">
          Defina quais canais de notificação serão acionados para cada tipo de sensor.
        </p>
      </div>

      <div className="nm-table-wrapper">
        <table className="nm-table">
          <thead>
            <tr>
              <th className="nm-th-sensor">Tipo de Sensor</th>
              {CHANNELS.map(ch => (
                <th key={ch.key} className="nm-th-channel">{ch.label}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {SENSOR_TYPES.map(sensor => (
              <tr key={sensor.key}>
                <td className="nm-td-sensor">{sensor.label}</td>
                {CHANNELS.map(ch => (
                  <td key={ch.key} className="nm-td-check">
                    <label className="nm-checkbox-label">
                      <input
                        type="checkbox"
                        checked={isChannelEnabled(sensor.key, ch.key)}
                        onChange={() => toggleChannel(sensor.key, ch.key)}
                      />
                      <span className="nm-checkmark"></span>
                    </label>
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="nm-actions">
        {saveMsg.text && (
          <span className={`nm-msg nm-msg-${saveMsg.type}`}>{saveMsg.text}</span>
        )}
        <button className="nm-btn-save" onClick={handleSave} disabled={saving}>
          {saving ? 'Salvando...' : '💾 Salvar Matriz'}
        </button>
      </div>
    </div>
  );
}

export default NotificationMatrix;
