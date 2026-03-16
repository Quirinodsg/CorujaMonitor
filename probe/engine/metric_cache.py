"""
Metric Cache - Cache de métricas com suporte a Redis e fallback local
TTL: CPU/Memory=5s, Disk/Services=10s
"""
import hashlib
import json
import time
import threading
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class MetricCache:
    TTL_CPU_MEMORY    = 5   # segundos
    TTL_DISK_SERVICES = 10  # segundos

    def __init__(self, redis_url: Optional[str] = None):
        self._use_redis = False
        self._redis = None
        self._local: Dict[str, tuple] = {}  # key -> (value, expires_at)
        self._lock = threading.Lock()
        self._hits = 0
        self._misses = 0

        if redis_url:
            try:
                import redis
                self._redis = redis.from_url(redis_url, socket_connect_timeout=2)
                self._redis.ping()
                self._use_redis = True
                logger.info(f"MetricCache: usando Redis em {redis_url}")
            except Exception as e:
                logger.warning(f"MetricCache: Redis indisponivel ({e}), usando cache local")
        else:
            try:
                import redis
                self._redis = redis.Redis(host="localhost", port=6379, db=1, socket_connect_timeout=2)
                self._redis.ping()
                self._use_redis = True
                logger.info("MetricCache: usando Redis local")
            except Exception:
                logger.info("MetricCache: usando cache em memoria local")

    @staticmethod
    def make_key(host: str, sensor_type: str, query: str = "") -> str:
        query_hash = hashlib.md5(query.encode()).hexdigest()[:8]
        return f"{host}:{sensor_type}:{query_hash}"

    def get(self, host: str, sensor_type: str, query: str = "") -> Optional[Any]:
        key = self.make_key(host, sensor_type, query)
        if self._use_redis:
            try:
                val = self._redis.get(key)
                if val:
                    with self._lock:
                        self._hits += 1
                    return json.loads(val)
            except Exception:
                pass
        else:
            with self._lock:
                entry = self._local.get(key)
                if entry and time.monotonic() < entry[1]:
                    self._hits += 1
                    return entry[0]
        with self._lock:
            self._misses += 1
        return None

    def set(self, host: str, sensor_type: str, query: str, value: Any, ttl: Optional[int] = None):
        if ttl is None:
            ttl = self.TTL_CPU_MEMORY if sensor_type in ("cpu", "memory") else self.TTL_DISK_SERVICES
        key = self.make_key(host, sensor_type, query)
        if self._use_redis:
            try:
                self._redis.setex(key, ttl, json.dumps(value))
                return
            except Exception:
                pass
        with self._lock:
            self._local[key] = (value, time.monotonic() + ttl)

    def invalidate(self, host: str):
        prefix = f"{host}:"
        if self._use_redis:
            try:
                keys = self._redis.keys(f"{prefix}*")
                if keys:
                    self._redis.delete(*keys)
                return
            except Exception:
                pass
        with self._lock:
            self._local = {k: v for k, v in self._local.items() if not k.startswith(prefix)}

    @property
    def stats(self) -> Dict:
        with self._lock:
            total = self._hits + self._misses
            return {
                "hits": self._hits,
                "misses": self._misses,
                "hit_ratio": round(self._hits / max(1, total), 3),
                "backend": "redis" if self._use_redis else "local",
                "local_entries": len(self._local),
            }

    def cleanup_expired(self):
        now = time.monotonic()
        with self._lock:
            self._local = {k: v for k, v in self._local.items() if v[1] > now}
