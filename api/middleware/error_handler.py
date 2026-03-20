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

logger = logging.getLogger("coruja.error_handler")


class GlobalErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Captura qualquer exceção não tratada e retorna JSON estruturado.
    Nunca deixa um 500 sem corpo ou sem CORS.
    """

    async def dispatch(self, request: Request, call_next):
        start = time.monotonic()
        try:
            response = await call_next(request)
            return response
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
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Internal server error",
                    "error": type(exc).__name__,
                    "path": request.url.path,
                    "duration_ms": duration_ms,
                },
                headers={"Access-Control-Allow-Origin": "*"},
            )
