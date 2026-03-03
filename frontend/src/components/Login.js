import React, { useState } from 'react';
import api from '../services/api';
import './Login.css';

function Login({ onLogin }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    console.log('Attempting login with:', email);

    try {
      const response = await api.post('/api/v1/auth/login', {
        email,
        password
      });

      console.log('Login response received:', response.data);

      if (response.data.access_token && response.data.user) {
        console.log('Calling onLogin callback...');
        onLogin(response.data.access_token, response.data.user);
      } else {
        console.error('Invalid response format:', response.data);
        setError('Resposta inválida do servidor');
      }
    } catch (err) {
      console.error('Login error:', err);
      
      // Handle different error formats
      let errorMessage = 'Erro ao fazer login';
      
      if (err.response?.data) {
        const errorData = err.response.data;
        
        // Check if it's a validation error (array of errors)
        if (Array.isArray(errorData.detail)) {
          errorMessage = errorData.detail.map(e => e.msg).join(', ');
        } 
        // Check if it's a simple string detail
        else if (typeof errorData.detail === 'string') {
          errorMessage = errorData.detail;
        }
        // Check if there's a message field
        else if (errorData.message) {
          errorMessage = errorData.message;
        }
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <div className="login-header">
          <img src="/coruja-logo.png" alt="Coruja Monitor" className="login-logo" />
          <h1>Coruja Monitor</h1>
          <p>Plataforma de Monitoramento Empresarial</p>
        </div>
        
        <form onSubmit={handleSubmit} className="login-form">
          {error && <div className="error-message">{error}</div>}
          
          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder="seu@email.com"
            />
          </div>

          <div className="form-group">
            <label>Senha</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder="••••••••"
            />
          </div>

          <button type="submit" disabled={loading} className="login-button">
            {loading ? 'Entrando...' : 'Entrar'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default Login;
