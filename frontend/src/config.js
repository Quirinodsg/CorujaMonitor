/**
 * Configuração centralizada da API
 * Usa o hostname atual para funcionar em qualquer ambiente
 * - Porta 80/443 (nginx): usa URL relativa, sem porta explícita
 * - Porta 3000 (dev direto): usa hostname:8000
 */

const hostname = window.location.hostname;
const port = window.location.port;

let API_URL;

if (port === '3000') {
  // Acesso direto ao frontend dev (sem nginx)
  API_URL = `http://${hostname}:8000/api/v1`;
} else {
  // Acesso via nginx (porta 80 ou 443) — usa URL relativa
  API_URL = `/api/v1`;
}

export { API_URL };

console.log('[CONFIG] API URL:', API_URL);
