/**
 * Configuração centralizada da API
 * Sempre usa URL relativa — funciona via nginx (porta 80 ou 443)
 * O nginx faz proxy de /api/v1 → container api:8000
 */

const API_URL = '/api/v1';

export { API_URL };

console.log('[CONFIG] API URL:', API_URL);
