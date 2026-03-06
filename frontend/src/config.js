/**
 * Configuração centralizada da API
 * HARDCODED para 192.168.31.161
 */

// HARDCODED - Não depende de variáveis de ambiente
export const API_URL = 'http://192.168.31.161:8000/api/v1';

// CACHE BUSTER - Forçar atualização
const CACHE_VERSION = 'v11.0-SEGURANCA-MFA-' + Date.now();

// Log para debug (sempre ativo para verificar cache)
console.log('🔧 [CONFIG ' + CACHE_VERSION + '] API URL configurada:', API_URL);
console.log('🌐 [CONFIG ' + CACHE_VERSION + '] Hostname detectado:', window.location.hostname);
console.log('✅ [CONFIG ' + CACHE_VERSION + '] Timestamp:', new Date().toISOString());
console.log('⚠️ [CONFIG ' + CACHE_VERSION + '] Se baseURL não tem /api/v1, LIMPE O CACHE!');
