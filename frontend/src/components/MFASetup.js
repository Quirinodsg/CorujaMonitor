import React, { useState, useEffect } from 'react';
import api from '../services/api';
import './MFASetup.css';

const MFASetup = () => {
  const [mfaStatus, setMfaStatus] = useState(null);
  const [setupData, setSetupData] = useState(null);
  const [password, setPassword] = useState('');
  const [code, setCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [step, setStep] = useState('status'); // status, setup, verify, disable

  useEffect(() => {
    loadMFAStatus();
  }, []);

  const loadMFAStatus = async () => {
    try {
      const response = await api.get('/mfa/status');
      setMfaStatus(response.data);
    } catch (err) {
      console.error('Error loading MFA status:', err);
    }
  };

  const startSetup = async () => {
    setLoading(true);
    setError('');
    
    try {
      const response = await api.post('/mfa/setup');
      setSetupData(response.data);
      setStep('setup');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to setup MFA');
    } finally {
      setLoading(false);
    }
  };

  const enableMFA = async () => {
    if (!password || !code) {
      setError('Please enter password and verification code');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const response = await api.post('/mfa/enable', { password, code });
      setSuccess('MFA enabled successfully!');
      setPassword('');
      setCode('');
      setStep('status');
      loadMFAStatus();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to enable MFA');
    } finally {
      setLoading(false);
    }
  };

  const disableMFA = async () => {
    if (!password || !code) {
      setError('Please enter password and verification code');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const response = await api.post('/mfa/disable', { password, code });
      setSuccess('MFA disabled successfully!');
      setPassword('');
      setCode('');
      setStep('status');
      loadMFAStatus();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to disable MFA');
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    setSuccess('Copied to clipboard!');
    setTimeout(() => setSuccess(''), 2000);
  };

  return (
    <div className="mfa-setup">
      <div className="mfa-header">
        <h2>🔐 Autenticação de Dois Fatores (MFA)</h2>
        <p>Adicione uma camada extra de segurança à sua conta</p>
      </div>

      {error && (
        <div className="alert alert-error">
          {error}
          <button onClick={() => setError('')}>×</button>
        </div>
      )}

      {success && (
        <div className="alert alert-success">
          {success}
          <button onClick={() => setSuccess('')}>×</button>
        </div>
      )}

      {/* Status View */}
      {step === 'status' && mfaStatus && (
        <div className="mfa-status">
          <div className="status-card">
            <div className="status-icon">
              {mfaStatus.enabled ? '✅' : '⚠️'}
            </div>
            <div className="status-info">
              <h3>Status: {mfaStatus.enabled ? 'Habilitado' : 'Desabilitado'}</h3>
              {mfaStatus.enabled && (
                <p>Códigos de backup restantes: {mfaStatus.backup_codes_remaining}</p>
              )}
            </div>
          </div>

          {!mfaStatus.enabled ? (
            <div className="mfa-actions">
              <button 
                className="btn-primary" 
                onClick={startSetup}
                disabled={loading}
              >
                {loading ? 'Carregando...' : 'Habilitar MFA'}
              </button>
              
              <div className="mfa-info">
                <h4>Por que usar MFA?</h4>
                <ul>
                  <li>✓ Protege sua conta mesmo se sua senha for comprometida</li>
                  <li>✓ Compatível com Google Authenticator, Authy, Microsoft Authenticator</li>
                  <li>✓ Códigos de backup para emergências</li>
                  <li>✓ Recomendado para contas administrativas</li>
                </ul>
              </div>
            </div>
          ) : (
            <div className="mfa-actions">
              <button 
                className="btn-danger" 
                onClick={() => setStep('disable')}
              >
                Desabilitar MFA
              </button>
              
              <button 
                className="btn-secondary" 
                onClick={() => alert('Regenerar códigos em desenvolvimento')}
              >
                Regenerar Códigos de Backup
              </button>
            </div>
          )}
        </div>
      )}

      {/* Setup View */}
      {step === 'setup' && setupData && (
        <div className="mfa-setup-view">
          <h3>Configurar Autenticação de Dois Fatores</h3>
          
          <div className="setup-steps">
            <div className="setup-step">
              <div className="step-number">1</div>
              <div className="step-content">
                <h4>Instale um aplicativo autenticador</h4>
                <p>Baixe um dos seguintes aplicativos no seu smartphone:</p>
                <ul>
                  <li>Google Authenticator (iOS/Android)</li>
                  <li>Microsoft Authenticator (iOS/Android)</li>
                  <li>Authy (iOS/Android/Desktop)</li>
                </ul>
              </div>
            </div>

            <div className="setup-step">
              <div className="step-number">2</div>
              <div className="step-content">
                <h4>Escaneie o QR Code</h4>
                <div className="qr-code-container">
                  <img src={setupData.qr_code} alt="QR Code" />
                </div>
                <p className="text-center">
                  <small>Ou insira manualmente o código:</small>
                </p>
                <div className="secret-code">
                  <code>{setupData.secret}</code>
                  <button 
                    className="btn-copy" 
                    onClick={() => copyToClipboard(setupData.secret)}
                  >
                    📋 Copiar
                  </button>
                </div>
              </div>
            </div>

            <div className="setup-step">
              <div className="step-number">3</div>
              <div className="step-content">
                <h4>Salve os códigos de backup</h4>
                <p>Guarde estes códigos em um local seguro. Você pode usá-los se perder acesso ao seu dispositivo.</p>
                <div className="backup-codes">
                  {setupData.backup_codes.map((code, idx) => (
                    <div key={idx} className="backup-code">{code}</div>
                  ))}
                </div>
                <button 
                  className="btn-secondary" 
                  onClick={() => copyToClipboard(setupData.backup_codes.join('\n'))}
                >
                  📋 Copiar Todos os Códigos
                </button>
              </div>
            </div>

            <div className="setup-step">
              <div className="step-number">4</div>
              <div className="step-content">
                <h4>Verificar e Ativar</h4>
                <div className="form-group">
                  <label>Senha da Conta</label>
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Digite sua senha"
                  />
                </div>
                <div className="form-group">
                  <label>Código do Aplicativo</label>
                  <input
                    type="text"
                    value={code}
                    onChange={(e) => setCode(e.target.value)}
                    placeholder="Digite o código de 6 dígitos"
                    maxLength="6"
                  />
                </div>
                <div className="button-group">
                  <button 
                    className="btn-primary" 
                    onClick={enableMFA}
                    disabled={loading}
                  >
                    {loading ? 'Verificando...' : 'Ativar MFA'}
                  </button>
                  <button 
                    className="btn-secondary" 
                    onClick={() => {
                      setStep('status');
                      setPassword('');
                      setCode('');
                    }}
                  >
                    Cancelar
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Disable View */}
      {step === 'disable' && (
        <div className="mfa-disable-view">
          <h3>Desabilitar Autenticação de Dois Fatores</h3>
          
          <div className="alert alert-warning">
            ⚠️ Desabilitar MFA tornará sua conta menos segura. Certifique-se de que realmente deseja fazer isso.
          </div>

          <div className="form-group">
            <label>Senha da Conta</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Digite sua senha"
            />
          </div>

          <div className="form-group">
            <label>Código de Verificação</label>
            <input
              type="text"
              value={code}
              onChange={(e) => setCode(e.target.value)}
              placeholder="Digite o código de 6 dígitos"
              maxLength="6"
            />
          </div>

          <div className="button-group">
            <button 
              className="btn-danger" 
              onClick={disableMFA}
              disabled={loading}
            >
              {loading ? 'Desabilitando...' : 'Desabilitar MFA'}
            </button>
            <button 
              className="btn-secondary" 
              onClick={() => {
                setStep('status');
                setPassword('');
                setCode('');
              }}
            >
              Cancelar
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default MFASetup;
