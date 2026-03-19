/**
 * Configuração centralizada da API
 * Usa o hostname atual para funcionar em qualquer ambiente
 */

const hostname = window.location.hostname;
const port = '8000';
const protocol = window.location.protocol;

export const API_URL = `${protocol}//${hostname}:${port}/api/v1`;

console.log('[CONFIG] API URL:', API_URL);
