import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './ThresholdConfig.css';
import { API_URL } from '../config';

function ThresholdConfig() {
  const [config, setConfig] = useState(null);
  const [presets, setPresets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [appliedPreset, setAppliedPreset] = useState(null);

  useEffect(() => {
    loadConfig();
    loadPresets();
  }, []);

  useEffect(() => {
    if (config && presets.length > 0) {
      detectAppliedPreset();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [config, presets]);

  const loadConfig = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_URL}/thresholds/config`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setConfig(response.data);
    } catch (error) {
      console.error('Erro ao carregar configuração:', error);
      alert('Erro ao carregar configuração de thresholds');
    } finally {
      setLoading(false);
    }
  };

  const loadPresets = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_URL}/thresholds/presets`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setPresets(response.data.presets);
    } catch (error) {
      console.error('Erro ao carregar presets:', error);
    }
  };

  const detectAppliedPreset = () => {
    if (!config) return;

    // Verificar qual preset está aplicado comparando valores
    for (const preset of presets) {
      const matches = 
        config.cpu_breach_duration === preset.config.cpu_breach_duration &&
        config.memory_breach_duration === preset.config.memory_breach_duration &&
        config.disk_breach_duration === preset.config.disk_breach_duration &&
        config.ping_breach_duration === preset.config.ping_breach_duration;
      
      if (matches) {
        setAppliedPreset(preset.name);
        return;
      }
    }
    
    // Se não corresponde a nenhum preset, é customizado
    setAppliedPreset('Customizado');
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const token = localStorage.getItem('token');
      await axios.put(`${API_URL}/thresholds/config`, config, {
        headers: { Authorization: `Bearer ${token}` }
      });
      alert('✅ Configuração salva com sucesso!');
    } catch (error) {
      console.error('Erro ao salvar:', error);
      alert('❌ Erro ao salvar configuração');
    } finally {
      setSaving(false);
    }
  };

  const applyPreset = async (presetName) => {
    if (!window.confirm(`Aplicar preset "${presetName}"? Isso substituirá as configurações atuais.`)) {
      return;
    }

    setSaving(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API_URL}/thresholds/apply-preset/${presetName.toLowerCase().replace(/\s+/g, '-')}`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setConfig(response.data.config);
      setAppliedPreset(presetName);
      alert(`✅ Preset "${presetName}" aplicado com sucesso!`);
    } catch (error) {
      console.error('Erro ao aplicar preset:', error);
      alert('❌ Erro ao aplicar preset');
    } finally {
      setSaving(false);
    }
  };

  const formatDuration = (seconds) => {
    if (seconds < 60) return `${seconds}s`;
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return secs > 0 ? `${minutes}m ${secs}s` : `${minutes}m`;
  };

  if (loading) {
    return <div className="threshold-loading">Carregando configurações...</div>;
  }

  if (!config) {
    return <div className="threshold-error">Erro ao carregar configurações</div>;
  }

  return (
    <div className="threshold-config-container">
      <div className="threshold-header">
        <h2>⏱️ Configuração de Thresholds Temporais</h2>
        <p className="threshold-subtitle">
          Baseado em melhores práticas ITIL para evitar falsos positivos
        </p>
      </div>

      {/* Presets Section */}
      <div className="threshold-section">
        <h3>📋 Presets Recomendados</h3>
        <div className="presets-grid">
          {presets.map((preset) => {
            const isApplied = appliedPreset === preset.name;
            return (
              <div 
                key={preset.name} 
                className={`preset-card ${isApplied ? 'preset-card-active' : ''}`}
              >
                <div className="preset-header">
                  <h4>
                    {preset.name}
                    {isApplied && <span className="preset-badge">✅ APLICADO</span>}
                  </h4>
                  <button
                    className="preset-apply-btn"
                    onClick={() => applyPreset(preset.name)}
                    disabled={saving || isApplied}
                  >
                    {isApplied ? 'Aplicado' : 'Aplicar'}
                  </button>
                </div>
              <p className="preset-description">{preset.description}</p>
              <div className="preset-details">
                <div className="preset-detail">
                  <span>CPU:</span>
                  <strong>{formatDuration(preset.config.cpu_breach_duration)}</strong>
                </div>
                <div className="preset-detail">
                  <span>Memória:</span>
                  <strong>{formatDuration(preset.config.memory_breach_duration)}</strong>
                </div>
                <div className="preset-detail">
                  <span>Disco:</span>
                  <strong>{formatDuration(preset.config.disk_breach_duration)}</strong>
                </div>
                <div className="preset-detail">
                  <span>Ping:</span>
                  <strong>{formatDuration(preset.config.ping_breach_duration)}</strong>
                </div>
              </div>
              </div>
            );
          })}
        </div>
        {appliedPreset && (
          <div className="applied-preset-info">
            <strong>Preset Atual:</strong> {appliedPreset}
          </div>
        )}
      </div>

      {/* Sensor-Specific Durations */}
      <div className="threshold-section">
        <h3>🎯 Duração de Breach por Tipo de Sensor</h3>
        <p className="section-help">
          Tempo que o sensor deve estar em breach antes de criar um incidente
        </p>
        
        <div className="threshold-grid">
          <div className="threshold-item">
            <label>
              <span className="threshold-icon">💻</span>
              CPU
            </label>
            <div className="threshold-input-group">
              <input
                type="number"
                min="60"
                max="3600"
                value={config.cpu_breach_duration}
                onChange={(e) => setConfig({...config, cpu_breach_duration: parseInt(e.target.value)})}
              />
              <span className="threshold-unit">segundos ({formatDuration(config.cpu_breach_duration)})</span>
            </div>
          </div>

          <div className="threshold-item">
            <label>
              <span className="threshold-icon">🧠</span>
              Memória
            </label>
            <div className="threshold-input-group">
              <input
                type="number"
                min="60"
                max="3600"
                value={config.memory_breach_duration}
                onChange={(e) => setConfig({...config, memory_breach_duration: parseInt(e.target.value)})}
              />
              <span className="threshold-unit">segundos ({formatDuration(config.memory_breach_duration)})</span>
            </div>
          </div>

          <div className="threshold-item">
            <label>
              <span className="threshold-icon">💾</span>
              Disco
            </label>
            <div className="threshold-input-group">
              <input
                type="number"
                min="300"
                max="7200"
                value={config.disk_breach_duration}
                onChange={(e) => setConfig({...config, disk_breach_duration: parseInt(e.target.value)})}
              />
              <span className="threshold-unit">segundos ({formatDuration(config.disk_breach_duration)})</span>
            </div>
          </div>

          <div className="threshold-item">
            <label>
              <span className="threshold-icon">📡</span>
              Ping
            </label>
            <div className="threshold-input-group">
              <input
                type="number"
                min="30"
                max="600"
                value={config.ping_breach_duration}
                onChange={(e) => setConfig({...config, ping_breach_duration: parseInt(e.target.value)})}
              />
              <span className="threshold-unit">segundos ({formatDuration(config.ping_breach_duration)})</span>
            </div>
            <span className="threshold-hint">🏓 Ping alerta apenas se offline (sem resposta). Latência alta é só métrica.</span>
          </div>

          <div className="threshold-item">
            <label>
              <span className="threshold-icon">⏱️</span>
              Uptime
            </label>
            <div className="threshold-input-group">
              <span className="threshold-unit">🔄 Uptime cria incidente informativo (já resolvido) apenas em reboot. Sem threshold configurável.</span>
            </div>
          </div>

          <div className="threshold-item">
            <label>
              <span className="threshold-icon">⚙️</span>
              Serviços
            </label>
            <div className="threshold-input-group">
              <input
                type="number"
                min="30"
                max="600"
                value={config.service_breach_duration}
                onChange={(e) => setConfig({...config, service_breach_duration: parseInt(e.target.value)})}
              />
              <span className="threshold-unit">segundos ({formatDuration(config.service_breach_duration)})</span>
            </div>
          </div>

          <div className="threshold-item">
            <label>
              <span className="threshold-icon">🌐</span>
              Rede
            </label>
            <div className="threshold-input-group">
              <input
                type="number"
                min="60"
                max="3600"
                value={config.network_breach_duration}
                onChange={(e) => setConfig({...config, network_breach_duration: parseInt(e.target.value)})}
              />
              <span className="threshold-unit">segundos ({formatDuration(config.network_breach_duration)})</span>
            </div>
          </div>
        </div>
      </div>

      {/* Flapping Detection */}
      <div className="threshold-section">
        <h3>🔄 Detecção de Flapping</h3>
        <p className="section-help">
          Detecta quando um sensor oscila rapidamente entre estados (evita spam de alertas)
        </p>
        
        <div className="threshold-grid">
          <div className="threshold-item">
            <label>Janela de Tempo</label>
            <div className="threshold-input-group">
              <input
                type="number"
                min="60"
                max="1800"
                value={config.flapping_window_seconds}
                onChange={(e) => setConfig({...config, flapping_window_seconds: parseInt(e.target.value)})}
              />
              <span className="threshold-unit">segundos ({formatDuration(config.flapping_window_seconds)})</span>
            </div>
          </div>

          <div className="threshold-item">
            <label>Número de Mudanças</label>
            <div className="threshold-input-group">
              <input
                type="number"
                min="2"
                max="10"
                value={config.flapping_threshold}
                onChange={(e) => setConfig({...config, flapping_threshold: parseInt(e.target.value)})}
              />
              <span className="threshold-unit">mudanças para considerar flapping</span>
            </div>
          </div>
        </div>
      </div>

      {/* Suppression Settings */}
      <div className="threshold-section">
        <h3>🔕 Supressão de Alertas</h3>
        
        <div className="threshold-toggles">
          <label className="threshold-toggle">
            <input
              type="checkbox"
              checked={config.suppress_during_maintenance}
              onChange={(e) => setConfig({...config, suppress_during_maintenance: e.target.checked})}
            />
            <span>Suprimir durante janelas de manutenção</span>
          </label>

          <label className="threshold-toggle">
            <input
              type="checkbox"
              checked={config.suppress_acknowledged}
              onChange={(e) => setConfig({...config, suppress_acknowledged: e.target.checked})}
            />
            <span>Suprimir sensores reconhecidos por técnicos</span>
          </label>

          <label className="threshold-toggle">
            <input
              type="checkbox"
              checked={config.suppress_flapping}
              onChange={(e) => setConfig({...config, suppress_flapping: e.target.checked})}
            />
            <span>Suprimir sensores com flapping detectado</span>
          </label>
        </div>
      </div>

      {/* Escalation Settings */}
      <div className="threshold-section">
        <h3>📈 Escalação Automática</h3>
        
        <div className="threshold-toggles">
          <label className="threshold-toggle">
            <input
              type="checkbox"
              checked={config.escalation_enabled}
              onChange={(e) => setConfig({...config, escalation_enabled: e.target.checked})}
            />
            <span>Habilitar escalação automática de incidentes</span>
          </label>
        </div>

        {config.escalation_enabled && (
          <div className="threshold-grid">
            <div className="threshold-item">
              <label>Tempo para Escalar</label>
              <div className="threshold-input-group">
                <input
                  type="number"
                  min="5"
                  max="240"
                  value={config.escalation_time_minutes}
                  onChange={(e) => setConfig({...config, escalation_time_minutes: parseInt(e.target.value)})}
                />
                <span className="threshold-unit">minutos</span>
              </div>
            </div>

            <div className="threshold-item">
              <label>Severidade para Escalar</label>
              <select
                value={config.escalation_severity}
                onChange={(e) => setConfig({...config, escalation_severity: e.target.value})}
              >
                <option value="warning">Warning → Critical</option>
                <option value="critical">Apenas Critical</option>
              </select>
            </div>
          </div>
        )}
      </div>

      {/* Save Button */}
      <div className="threshold-actions">
        <button
          className="threshold-save-btn"
          onClick={handleSave}
          disabled={saving}
        >
          {saving ? 'Salvando...' : '💾 Salvar Configurações'}
        </button>
      </div>

      {/* Info Box */}
      <div className="threshold-info-box">
        <h4>ℹ️ Sobre Thresholds Temporais</h4>
        <p>
          Os thresholds temporais seguem as melhores práticas do ITIL para gerenciamento de eventos.
          Ao invés de criar um incidente imediatamente quando um limite é ultrapassado, o sistema
          aguarda um período configurável para confirmar que o problema é persistente.
        </p>
        <p>
          <strong>Exemplo:</strong> Se a CPU ultrapassar 95% por apenas 30 segundos e depois voltar
          ao normal, não faz sentido abrir um chamado. Com threshold temporal de 10 minutos, o sistema
          só abrirá o incidente se a CPU permanecer acima de 95% por 10 minutos consecutivos.
        </p>
      </div>
    </div>
  );
}

export default ThresholdConfig;
