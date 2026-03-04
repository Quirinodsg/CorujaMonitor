import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Login.css';

function Login({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [terminalText, setTerminalText] = useState('');
  const [showOwl, setShowOwl] = useState(false);

  const terminalLines = [
    '> Inicializando Coruja Monitor...',
    '> Carregando módulos de segurança...',
    '> Estabelecendo conexão criptografada...',
    '> Sistema de monitoramento ativo',
    '> Aguardando autenticação...'
  ];

  useEffect(() => {
    // Animação do terminal
    let currentLine = 0;
    let currentChar = 0;
    let text = '';

    const typeWriter = setInterval(() => {
      if (currentLine < terminalLines.length) {
        if (currentChar < terminalLines[currentLine].length) {
          text += terminalLines[currentLine][currentChar];
          setTerminalText(text);
          currentChar++;
        } else {
          text += '\n';
          setTerminalText(text);
          currentLine++;
          currentChar = 0;
          
          if (currentLine === 2) {
            // Mostrar coruja no meio da animação
            setShowOwl(true);
          }
        }
      } else {
        clearInterval(typeWriter);
        // Mostrar formulário após animação
        setTimeout(() => setShowForm(true), 500);
      }
    }, 50);

    return () => clearInterval(typeWriter);
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await axios.post('http://localhost:8000/api/v1/auth/login', {
        username,
        password
      });

      // Chamar onLogin com token e user data
      onLogin(response.data.access_token, response.data.user);
    } catch (err) {
      setError(err.response?.data?.detail || 'Erro ao fazer login');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      {/* Fundo com efeito Matrix */}
      <div className="matrix-bg"></div>
      
      {/* Partículas flutuantes */}
      <div className="particles">
        {[...Array(20)].map((_, i) => (
          <div key={i} className="particle" style={{
            left: `${Math.random() * 100}%`,
            animationDelay: `${Math.random() * 5}s`,
            animationDuration: `${5 + Math.random() * 10}s`
          }}></div>
        ))}
      </div>

      {/* Terminal de inicialização */}
      <div className={`terminal-boot ${showForm ? 'fade-out' : ''}`}>
        <div className="terminal-header">
          <span className="terminal-dot red"></span>
          <span className="terminal-dot yellow"></span>
          <span className="terminal-dot green"></span>
          <span className="terminal-title">CORUJA MONITOR SYSTEM</span>
        </div>
        <div className="terminal-body">
          <pre className="terminal-text">{terminalText}</pre>
          <span className="terminal-cursor">_</span>
        </div>
      </div>

      {/* Coruja surgindo no topo */}
      <div className={`owl-container-top ${showOwl ? 'show' : ''}`}>
        <div className="owl-glow"></div>
        <div className="owl-logo">
          <img src="/coruja-logo.png" alt="Coruja Monitor" className="owl-image" />
        </div>
        <div className="owl-pulse"></div>
      </div>

      {/* Formulário de login */}
      <div className={`login-box ${showForm ? 'show' : ''}`}>
        <div className="login-header">
          <h1 className="login-title">
            <span className="glitch" data-text="CORUJA MONITOR">CORUJA MONITOR</span>
          </h1>
          <p className="login-subtitle">Sistema de Monitoramento Inteligente</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label className="input-label">Usuário</label>
            <div className="input-wrapper">
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Digite seu usuário"
                required
                className="login-input"
                autoComplete="username"
              />
              <span className="input-icon-right">👤</span>
              <div className="input-line"></div>
            </div>
          </div>

          <div className="form-group">
            <label className="input-label">Senha</label>
            <div className="input-wrapper">
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Digite sua senha"
                required
                className="login-input"
                autoComplete="current-password"
              />
              <span className="input-icon-right">🔒</span>
              <div className="input-line"></div>
            </div>
          </div>

          {error && (
            <div className="error-message">
              <span className="error-icon">⚠️</span>
              {error}
            </div>
          )}

          <button 
            type="submit" 
            disabled={loading}
            className="login-button"
          >
            {loading ? (
              <>
                <span className="spinner"></span>
                Autenticando...
              </>
            ) : (
              <>
                <span className="button-icon">🚀</span>
                ACESSAR SISTEMA
              </>
            )}
          </button>
        </form>

        <div className="login-footer">
          <p className="version">v1.0.0 | Sistema Seguro</p>
          <div className="security-badges">
            <span className="badge">🔐 Criptografado</span>
            <span className="badge">🛡️ Protegido</span>
          </div>
        </div>
      </div>

      {/* Efeito de scan */}
      <div className="scan-line"></div>
    </div>
  );
}

export default Login;
