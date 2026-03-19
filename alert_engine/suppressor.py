"""
Duplicate Suppressor — Coruja Monitor v3.0
Suprime alertas duplicados usando cache com TTL de 5 minutos.
Property 14: mesmo (host_id, type, severity) → não cria novo alerta.
"""
import hashlib
import time
import logging
from typing import Optional

from core.spec.models import Event

logger = logging.getLogger(__name__)

SUPPRESSION_TTL_SECONDS = 300  # 5 minutos


class DuplicateSuppressor:
    """
    Cache em memória com TTL 5 minutos.
    Chave: hash(host_id + type + severity).
    Fallback para Redis quando disponível.
    """

    def __init__(self, redis_client=None, ttl: int = SUPPRESSION_TTL_SECONDS):
        self._redis = redis_client
        self._ttl = ttl
        # Fallback em memória: {key: expires_at}
        self._cache: dict[str, float] = {}

    def _make_key(self, event: Event) -> str:
        host_id = str(event.host_id)
        event_type = event.type
        severity = event.severity if isinstance(event.severity, str) else event.severity.value
        raw = f"{host_id}:{event_type}:{severity}"
        return hashlib.md5(raw.encode()).hexdigest()

    def is_duplicate(self, event: Event) -> bool:
        """Retorna True se evento já foi visto recentemente."""
        key = self._make_key(event)

        if self._redis:
            try:
                return bool(self._redis.exists(f"suppress:{key}"))
            except Exception:
                pass

        # Fallback em memória
        entry = self._cache.get(key)
        if entry and time.monotonic() < entry:
            return True
        # Limpar expirado
        if key in self._cache:
            del self._cache[key]
        return False

    def mark_seen(self, event: Event) -> None:
        """Marca evento como visto (TTL 5 minutos)."""
        key = self._make_key(event)

        if self._redis:
            try:
                self._redis.setex(f"suppress:{key}", self._ttl, "1")
                return
            except Exception:
                pass

        # Fallback em memória
        self._cache[key] = time.monotonic() + self._ttl

    def clear(self) -> None:
        """Limpa cache (para testes)."""
        self._cache.clear()
