/**
 * Configuração centralizada da API
 * Detecta automaticamente o IP do host
 */

// Função para detectar o IP automaticamente
const getApiUrl = () => {
  // Se REACT_APP_API_URL está definido, usa ele
  if (process.env.REACT_APP_API_URL) {
    return process.env.REACT_APP_API_URL;
  }
  
  // Detecta automaticamente o IP do host atual
  const hostname = window.location.hostname;
  
  // Se estiver em localhost, usa localhost
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return 'http://localhost:8000/api/v1';
  }
  
  // Caso contrário, usa o IP do host atual na porta 8000
  return `http://${hostname}:8000/api/v1`;
};

export const API_URL = getApiUrl();

// CACHE BUSTER - Forçar atualização
const CACHE_VERSION = 'v3.0-' + Date.now();

// Log para debug (sempre ativo para verificar cache)
console.log('🔧 [CONFIG ' + CACHE_VERSION + '] API URL configurada:', API_URL);
console.log('🌐 [CONFIG ' + CACHE_VERSION + '] Hostname detectado:', window.location.hostname);
console.log('✅ [CONFIG ' + CACHE_VERSION + '] Timestamp:', new Date().toISOString());
console.log('⚠️ [CONFIG ' + CACHE_VERSION + '] Se baseURL não tem /api/v1, LIMPE O CACHE!');
