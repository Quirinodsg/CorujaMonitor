"""
WAF Middleware - Web Application Firewall
Implementado como middleware ASGI puro (não BaseHTTPMiddleware).
Evita o bug do Starlette onde BaseHTTPMiddleware intercepta exceções
antes que o CORSMiddleware possa adicionar os headers.
"""

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send
from collections import defaultdict
from datetime import datetime, timedelta
import re
import logging

logger = logging.getLogger(__name__)


class WAFMiddleware:
    """
    WAF implementado como middleware ASGI puro.
    Não herda de BaseHTTPMiddleware — evita interceptação de exceções
    que impede o CORSMiddleware de adicionar Access-Control-Allow-Origin.
    """

    def __init__(self, app: ASGIApp):
        self.app = app

        # Rate limiting: IP -> lista de timestamps
        self.rate_limits = defaultdict(list)

        # Blacklist de IPs bloqueados
        self.blacklist = set()
        self._blacklist_expiry = {}

        # Cache de padrões compilados
        self._compiled_sql_patterns = None
        self._compiled_xss_patterns = None

        # Configurações
        self.max_requests_per_minute = 500
        self.max_requests_per_hour = 5000
        self.blacklist_duration = timedelta(hours=1)

        # Whitelist de IPs internos (Docker, localhost, redes privadas)
        self.whitelist_ips = {"127.0.0.1", "::1", "172.18.0.1", "localhost"}
        self.whitelist_prefixes = (
            "172.16.", "172.17.", "172.18.", "172.19.", "172.20.", "172.21.",
            "172.22.", "172.23.", "172.24.", "172.25.", "172.26.", "172.27.",
            "172.28.", "172.29.", "172.30.", "172.31.",
            "192.168.",
            "10.",
        )

        # Paths que não precisam de verificação
        self.whitelist_paths = [
            "/health", "/", "/api/v1/auth/login", "/api/v1/auth/refresh"
        ]

        self.sql_injection_patterns = [
            r"(\bunion\b.*\bselect\b)", r"(\bselect\b.*\bfrom\b)",
            r"(\binsert\b.*\binto\b)", r"(\bdelete\b.*\bfrom\b)",
            r"(\bdrop\b.*\btable\b)", r"(\bexec\b.*\()",
            r"(\bexecute\b.*\()", r"(;.*--)",
            r"('.*or.*'.*=.*')", r"(\".*or.*\".*=.*\")",
        ]

        self.xss_patterns = [
            r"<script[^>]*>.*?</script>", r"javascript:",
            r"onerror\s*=", r"onload\s*=", r"onclick\s*=",
            r"<iframe[^>]*>", r"<embed[^>]*>", r"<object[^>]*>",
        ]

        logger.info("WAF Middleware (ASGI pure) initialized")

    @property
    def compiled_sql_patterns(self):
        if self._compiled_sql_patterns is None:
            self._compiled_sql_patterns = [
                re.compile(p, re.IGNORECASE) for p in self.sql_injection_patterns
            ]
        return self._compiled_sql_patterns

    @property
    def compiled_xss_patterns(self):
        if self._compiled_xss_patterns is None:
            self._compiled_xss_patterns = [
                re.compile(p, re.IGNORECASE) for p in self.xss_patterns
            ]
        return self._compiled_xss_patterns

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        """Ponto de entrada ASGI puro."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)
        blocked_response = await self._check(request)
        if blocked_response is not None:
            await blocked_response(scope, receive, send)
        else:
            await self.app(scope, receive, send)

    async def _check(self, request: Request):
        """Retorna JSONResponse se bloqueado, None se deve continuar."""
        client_ip = request.client.host if request.client else "unknown"
        path = request.url.path
        origin = request.headers.get("origin", "*")

        def cors_block(status_code: int, detail: str):
            return JSONResponse(
                status_code=status_code,
                content={"detail": detail},
                headers={
                    "Access-Control-Allow-Origin": origin,
                    "Access-Control-Allow-Credentials": "true",
                    "Access-Control-Allow-Methods": "*",
                    "Access-Control-Allow-Headers": "*",
                }
            )

        # IPs internos/Docker — passa direto
        if client_ip in self.whitelist_ips or any(client_ip.startswith(p) for p in self.whitelist_prefixes):
            return None

        # WebSocket upgrade — passa direto
        if request.headers.get("upgrade", "").lower() == "websocket":
            return None

        # Preflight CORS — passa direto
        if request.method == "OPTIONS":
            return None

        # Paths whitelisted — passa direto
        if path in self.whitelist_paths:
            return None

        # Blacklist
        if client_ip in self.blacklist:
            self._cleanup_blacklist()
            if client_ip in self.blacklist:
                logger.warning(f"WAF: blocked blacklisted IP {client_ip}")
                return cors_block(403, "Access denied")

        # Rate limiting
        if not self._check_rate_limit(client_ip):
            logger.warning(f"WAF: rate limit exceeded for {client_ip}")
            return cors_block(429, "Too many requests. Please try again later.")

        # SQL Injection (query params apenas)
        query_string = str(request.url.query).lower()
        if query_string:
            for pattern in self.compiled_sql_patterns:
                if pattern.search(query_string):
                    logger.error(f"WAF: SQL injection attempt from {client_ip}")
                    self._add_to_blacklist(client_ip)
                    return cors_block(400, "Invalid request")

        # XSS (query params apenas)
        if query_string:
            for pattern in self.compiled_xss_patterns:
                if pattern.search(query_string):
                    logger.error(f"WAF: XSS attempt from {client_ip}")
                    return cors_block(400, "Invalid request")

        # Content-Type para métodos com body
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("content-type", "")
            if content_type and not self._valid_content_type(content_type):
                logger.warning(f"WAF: invalid content-type from {client_ip}: {content_type}")
                return cors_block(415, "Unsupported media type")

        return None  # tudo ok

    def _check_rate_limit(self, ip: str) -> bool:
        now = datetime.now()
        self.rate_limits[ip] = [
            ts for ts in self.rate_limits[ip] if now - ts < timedelta(hours=1)
        ]
        recent = [ts for ts in self.rate_limits[ip] if now - ts < timedelta(minutes=1)]
        if len(recent) >= self.max_requests_per_minute:
            return False
        if len(self.rate_limits[ip]) >= self.max_requests_per_hour:
            return False
        self.rate_limits[ip].append(now)
        return True

    def _valid_content_type(self, content_type: str) -> bool:
        allowed = [
            "application/json", "application/x-www-form-urlencoded",
            "multipart/form-data", "text/plain",
            "application/octet-stream", "application/xml", "text/xml",
        ]
        return any(content_type.startswith(a) for a in allowed)

    def _add_to_blacklist(self, ip: str):
        self.blacklist.add(ip)
        self._blacklist_expiry[ip] = datetime.now() + self.blacklist_duration
        logger.warning(f"WAF: IP {ip} blacklisted for {self.blacklist_duration}")

    def _cleanup_blacklist(self):
        now = datetime.now()
        expired = [ip for ip, exp in self._blacklist_expiry.items() if now >= exp]
        for ip in expired:
            self.blacklist.discard(ip)
            del self._blacklist_expiry[ip]
