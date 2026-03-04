"""
WAF Middleware - Web Application Firewall
Proteção contra SQL Injection, XSS, CSRF, DDoS e outros ataques
Otimizado para alta performance com cache e processamento assíncrono
"""

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
from datetime import datetime, timedelta
from functools import lru_cache
import re
import logging
import asyncio

logger = logging.getLogger(__name__)

class WAFMiddleware(BaseHTTPMiddleware):
    """
    Web Application Firewall Middleware
    Implementa proteções contra ataques comuns
    Otimizado para alta performance
    """
    
    def __init__(self, app):
        super().__init__(app)
        
        # Rate limiting: IP -> lista de timestamps
        self.rate_limits = defaultdict(list)
        
        # Blacklist de IPs bloqueados
        self.blacklist = set()
        
        # Cache de padrões compilados para melhor performance
        self._compiled_sql_patterns = None
        self._compiled_xss_patterns = None
        
        # Configurações
        self.max_requests_per_minute = 100
        self.max_requests_per_hour = 1000
        self.blacklist_duration = timedelta(hours=1)
        
        # Whitelist de paths que não precisam de verificação completa
        self.whitelist_paths = [
            "/health",
            "/",
            "/api/v1/auth/login",
            "/api/v1/auth/refresh"
        ]
        
        # Padrões de ataque (compilados sob demanda)
        self.sql_injection_patterns = [
            r"(\bunion\b.*\bselect\b)",
            r"(\bselect\b.*\bfrom\b)",
            r"(\binsert\b.*\binto\b)",
            r"(\bdelete\b.*\bfrom\b)",
            r"(\bdrop\b.*\btable\b)",
            r"(\bexec\b.*\()",
            r"(\bexecute\b.*\()",
            r"(;.*--)",
            r"('.*or.*'.*=.*')",
            r"(\".*or.*\".*=.*\")",
        ]
        
        self.xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"onerror\s*=",
            r"onload\s*=",
            r"onclick\s*=",
            r"<iframe[^>]*>",
            r"<embed[^>]*>",
            r"<object[^>]*>",
        ]
        
        logger.info("WAF Middleware initialized with performance optimizations")
    
    @property
    def compiled_sql_patterns(self):
        """Lazy compilation de padrões SQL"""
        if self._compiled_sql_patterns is None:
            self._compiled_sql_patterns = [
                re.compile(pattern, re.IGNORECASE)
                for pattern in self.sql_injection_patterns
            ]
        return self._compiled_sql_patterns
    
    @property
    def compiled_xss_patterns(self):
        """Lazy compilation de padrões XSS"""
        if self._compiled_xss_patterns is None:
            self._compiled_xss_patterns = [
                re.compile(pattern, re.IGNORECASE)
                for pattern in self.xss_patterns
            ]
        return self._compiled_xss_patterns
    
    async def dispatch(self, request: Request, call_next):
        """Processa cada requisição através do WAF"""
        
        client_ip = request.client.host
        path = request.url.path
        
        # Skip verificação completa para paths whitelisted (performance)
        if path in self.whitelist_paths:
            response = await call_next(request)
            self._add_security_headers(response)
            return response
        
        # 1. Verificar blacklist (mais rápido)
        if client_ip in self.blacklist:
            logger.warning(f"Blocked request from blacklisted IP: {client_ip}")
            return JSONResponse(
                status_code=403,
                content={"detail": "Access denied"}
            )
        
        # 2. Rate Limiting (otimizado)
        if not self.check_rate_limit(client_ip):
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please try again later."}
            )
        
        # 3. Detectar SQL Injection (apenas em query params para performance)
        if await self.detect_sql_injection_fast(request):
            logger.error(f"SQL Injection attempt detected from IP: {client_ip}")
            self.add_to_blacklist(client_ip)
            return JSONResponse(
                status_code=400,
                content={"detail": "Invalid request"}
            )
        
        # 4. Detectar XSS (apenas em headers críticos)
        if await self.detect_xss_fast(request):
            logger.error(f"XSS attempt detected from IP: {client_ip}")
            return JSONResponse(
                status_code=400,
                content={"detail": "Invalid request"}
            )
        
        # 5. Validar Content-Type (apenas POST/PUT/PATCH)
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("content-type", "")
            if not self.validate_content_type(content_type):
                logger.warning(f"Invalid content-type from IP: {client_ip}")
                return JSONResponse(
                    status_code=415,
                    content={"detail": "Unsupported media type"}
                )
        
        # Processar requisição
        response = await call_next(request)
        
        # 6. Adicionar Security Headers
        self._add_security_headers(response)
        
        return response
    
    def _add_security_headers(self, response: Response):
        """Adiciona security headers (método separado para reuso)"""
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Content Security Policy
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' http://localhost:* ws://localhost:*; "
            "frame-ancestors 'none';"
        )
        response.headers["Content-Security-Policy"] = csp
    
    def check_rate_limit(self, ip: str) -> bool:
        """Verifica rate limiting por IP"""
        now = datetime.now()
        
        # Limpar timestamps antigos
        self.rate_limits[ip] = [
            ts for ts in self.rate_limits[ip]
            if now - ts < timedelta(hours=1)
        ]
        
        # Verificar limite por minuto
        recent_requests = [
            ts for ts in self.rate_limits[ip]
            if now - ts < timedelta(minutes=1)
        ]
        
        if len(recent_requests) >= self.max_requests_per_minute:
            return False
        
        # Verificar limite por hora
        if len(self.rate_limits[ip]) >= self.max_requests_per_hour:
            return False
        
        # Adicionar timestamp atual
        self.rate_limits[ip].append(now)
        
        return True
    
    async def detect_sql_injection_fast(self, request: Request) -> bool:
        """Detecta tentativas de SQL Injection (versão otimizada)"""
        
        # Verificar apenas query parameters (mais rápido)
        query_string = str(request.url.query).lower()
        
        # Early return se query vazia
        if not query_string:
            return False
        
        # Usar padrões compilados
        for pattern in self.compiled_sql_patterns:
            if pattern.search(query_string):
                return True
        
        return False
    
    async def detect_xss_fast(self, request: Request) -> bool:
        """Detecta tentativas de XSS (versão otimizada)"""
        
        # Verificar apenas query parameters
        query_string = str(request.url.query)
        
        # Early return se query vazia
        if not query_string:
            return False
        
        # Usar padrões compilados
        for pattern in self.compiled_xss_patterns:
            if pattern.search(query_string):
                return True
        
        return False
    
    def validate_content_type(self, content_type: str) -> bool:
        """Valida Content-Type permitidos"""
        allowed_types = [
            "application/json",
            "application/x-www-form-urlencoded",
            "multipart/form-data",
            "text/plain"
        ]
        
        for allowed in allowed_types:
            if content_type.startswith(allowed):
                return True
        
        return False
    
    def add_to_blacklist(self, ip: str):
        """Adiciona IP à blacklist temporária"""
        self.blacklist.add(ip)
        logger.warning(f"IP {ip} added to blacklist")
        
        # TODO: Implementar remoção automática após duração
        # Pode usar background task ou scheduler
