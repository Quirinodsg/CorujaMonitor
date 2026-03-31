import React, { useState, useEffect } from 'react';
import './App.css';
import './styles/design-system.css';
import './styles/global-dark-override.css';
import MainLayout from './components/MainLayout';
import Login from './components/Login';
import api from './services/api';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Force dark mode always
    document.body.classList.add('dark-mode');
    document.documentElement.style.background = '#0B0F14';
    document.documentElement.style.colorScheme = 'dark';
  }, []);

  useEffect(() => {
    console.log('App mounted, checking authentication...');
    
    // Check for Azure AD callback token in URL
    const urlParams = new URLSearchParams(window.location.search);
    const azureToken = urlParams.get('azure_token');
    const azureUser = urlParams.get('azure_user');
    const azureName = urlParams.get('azure_name');
    const azureRole = urlParams.get('azure_role');
    const azureError = urlParams.get('azure_error');
    
    if (azureError) {
      console.error('Azure AD error:', azureError);
      window.history.replaceState({}, '', '/');
    } else if (azureToken && azureUser) {
      console.log('Azure AD login detected:', azureUser);
      const userData = {
        email: azureUser,
        full_name: decodeURIComponent(azureName || azureUser.split('@')[0]),
        username: decodeURIComponent(azureName || azureUser.split('@')[0]),
        role: azureRole || 'viewer',
      };
      localStorage.setItem('token', azureToken);
      localStorage.setItem('user', JSON.stringify(userData));
      api.defaults.headers.common['Authorization'] = `Bearer ${azureToken}`;
      setUser(userData);
      setIsAuthenticated(true);
      setLoading(false);
      window.history.replaceState({}, '', '/');
      return;
    }
    
    const token = localStorage.getItem('token');
    const userData = localStorage.getItem('user');
    
    console.log('Token exists:', !!token);
    console.log('User data exists:', !!userData);
    
    if (token && userData) {
      try {
        const parsedUser = JSON.parse(userData);
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        setUser(parsedUser);
        setIsAuthenticated(true);
        console.log('✓ User authenticated from localStorage:', parsedUser.email);
      } catch (error) {
        console.error('✗ Error parsing user data:', error);
        localStorage.removeItem('token');
        localStorage.removeItem('user');
      }
    } else {
      console.log('No existing session found');
    }
    
    setLoading(false);
  }, []);

  const handleLogin = (token, userData) => {
    console.log('=== LOGIN CALLBACK TRIGGERED ===');
    console.log('Token received:', token ? token.substring(0, 30) + '...' : 'NULL');
    console.log('User data:', userData);
    
    if (!token || !userData) {
      console.error('✗ Invalid login data!');
      return;
    }
    
    try {
      localStorage.setItem('token', token);
      localStorage.setItem('user', JSON.stringify(userData));
      console.log('✓ Saved to localStorage');
      
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      console.log('✓ Axios header configured');
      
      console.log('Setting isAuthenticated to TRUE');
      setIsAuthenticated(true);
      
      console.log('Setting user state');
      setUser(userData);
      
      console.log('=== LOGIN COMPLETE ===');
      
    } catch (error) {
      console.error('✗ Error in handleLogin:', error);
    }
  };

  const handleLogout = () => {
    console.log('Logging out...');
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    delete api.defaults.headers.common['Authorization'];
    setIsAuthenticated(false);
    setUser(null);
  };

  console.log('App render - isAuthenticated:', isAuthenticated, 'loading:', loading);

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        fontSize: '24px',
        color: '#666'
      }}>
        Carregando...
      </div>
    );
  }

  return (
    <div className="App">
      {isAuthenticated && user ? (
        <MainLayout user={user} onLogout={handleLogout} />
      ) : (
        <Login onLogin={handleLogin} />
      )}
    </div>
  );
}

export default App;
