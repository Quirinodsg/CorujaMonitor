"""
Global Error Handler Middleware — Coruja Monitor v3.5
Garante que NENHUM endpoint retorna 500 sem mensagem controlada.
Sempre retorna JSON válido com log estruturado.
"""
import logging
import time
import traceback
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Receive, Scope, Send

logger = logging.getLogger("coruja.error_handler")


class GlobalErrorHandlerMiddleware:
    """
    Captura qualquer exceção não tratada e retorna JSON estruturado.
    Implementado como ASGI puro para não quebrar WebSockets
    (BaseHTTPMiddleware intercepta o upgrade e mata a conexão WS).
    """

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        # WebSocket e lifespan passam direto — sem interceptação
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)
        start = time.monotonic()
        try:
            await self.app(scope, receive, send)
        except Exception as exc:
            duration_ms = round((time.monotonic() - start) * 1000, 2)
            tb = traceback.format_exc()
            logger.error(
                "Unhandled exception | method=%s path=%s duration_ms=%s error=%s\n%s",
                request.method,
                request.url.path,
                duration_ms,
                str(exc),
                tb,
            )
            response = JSONResponse(
                status_code=500,
                content={
                    "detail": "Internal server error",
                    "error": type(exc).__name__,
                    "path": request.url.path,
                    "duration_ms": duration_ms,
                },
                headers={"Access-Control-Allow-Origin": "*"},
            )
            await response(scope, receive, send)
