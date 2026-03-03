import axios from 'axios';
import { API_URL } from '../config';

const api = axios.create({
  baseURL: API_URL,
  timeout: 30000,
});

// Log para verificar baseURL
console.log('🔗 [API v2.0] Axios baseURL configurado:', API_URL);
console.log('🕐 [API v2.0] Timestamp:', new Date().toISOString());

// Request interceptor to always include token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
      console.log('🚀 [REQUEST v2.0] URL completa:', config.baseURL + config.url);
      console.log('🚀 [REQUEST v2.0] baseURL:', config.baseURL);
      console.log('🚀 [REQUEST v2.0] url relativa:', config.url);
    } else {
      console.warn('Request to:', config.url, 'WITHOUT token');
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for better error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Log error for debugging
    if (error.response) {
      // Server responded with error
      console.error('API Error Response:', {
        status: error.response.status,
        data: error.response.data,
        url: error.config?.url
      });
      
      // If 401, token is invalid
      if (error.response.status === 401) {
        console.error('Unauthorized! Token may be invalid or expired');
      }
    } else if (error.request) {
      // Request made but no response
      console.error('API No Response:', error.request);
      console.error('Possible causes: API not running, CORS issue, network problem');
    } else {
      // Error setting up request
      console.error('API Request Setup Error:', error.message);
    }
    
    // Return a rejected promise with the error
    return Promise.reject(error);
  }
);

export default api;
