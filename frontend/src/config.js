/**
 * Configuração centralizada da API
 * HARDCODED para 192.168.31.161
 */

// HARDCODED - Não depende de variáveis de ambiente
// IMPORTANTE: Não incluir /api/v1 aqui pois os componentes já adicionam
export const API_URL = 'http://192.168.31.161:8000';

// CACHE BUSTER - Forçar atualização
const CACHE_VERSION = 'v7.0-FIX-DOUBLE-API-' + Date.now();

// Log para debug (sempre ativo para verificar cache)
console.log('🔧 [CONFIG ' + CACHE_VERSION + '] API URL configurada:', API_URL);
console.log('🌐 [CONFIG ' + CACHE_VERSION + '] Hostname detectado:', window.location.hostname);
console.log('✅ [CONFIG ' + CACHE_VERSION + '] Timestamp:', new Date().toISOString());
console.log('⚠️ [CONFIG ' + CACHE_VERSION + '] Se baseURL não tem /api/v1, LIMPE O CACHE!');
