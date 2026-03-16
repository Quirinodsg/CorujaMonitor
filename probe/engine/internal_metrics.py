"""
Internal Metrics Collector - Coleta métricas de saúde da própria probe
Envia para API com sensor_type=probe_internal a cada 60s
"""
import logging
import threading
import time
from collections import deque
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

COLLECT_INTERVAL = 60       # segundos
MAX_LOG_ENTRIES  = 1000
MEMORY_WARN_MB   = 512
QUEUE_WARN_PCT   = 0.80


class InternalMetricsCollector:
    def __init__(self, api_url: str, probe_token: str, thread_pool=None, metric_cache=None):
        self.api_url = api_url
        self.probe_token = probe_token
        self._pool = thread_pool
        self._cache = metric_cache
        self._health_log: deque = deque(maxlen=MAX_LOG_ENTRIES)
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True, name="InternalMetrics")
        self._thread.start()
        logger.info("InternalMetricsCollector iniciado")

    def stop(self):
        self._running = False

    def _loop(self):
        while self._running:
            try:
                metrics = self._collect()
                self._health_log.append(metrics)
                self._check_alerts(metrics)
                self._send(metrics)
            except Exception as e:
                logger.error(f"InternalMetrics erro: {e}")
            time.sleep(COLLECT_INTERVAL)

    def _collect(self) -> Dict[str, Any]:
        import psutil
        proc = psutil.Process()

        cpu_pct = proc.cpu_percent(interval=1)
        mem_mb  = proc.memory_info().rss / (1024 * 1024)

        pool_stats = self._pool.stats() if self._pool else {}
        cache_stats = self._cache.stats if self._cache else {}

        return {
            "timestamp": time.time(),
            "probe_cpu_percent": cpu_pct,
            "probe_memory_mb": round(mem_mb, 2),
            "worker_queue_size": pool_stats.get("active_workers", 0),
            "active_workers": pool_stats.get("active_workers", 0),
            "max_workers": pool_stats.get("max_workers", 0),
            "completed_tasks": pool_stats.get("completed", 0),
            "failed_tasks": pool_stats.get("failed", 0),
            "cache_hit_ratio": cache_stats.get("hit_ratio", 0),
        }

    def _check_alerts(self, m: Dict):
        max_workers = m.get("max_workers", 1) or 1
        queue_pct = m.get("worker_queue_size", 0) / max_workers
        if queue_pct >= QUEUE_WARN_PCT:
            logger.warning(
                f"InternalMetrics: fila em {queue_pct*100:.0f}% da capacidade "
                f"({m['worker_queue_size']}/{max_workers})"
            )

        if m.get("probe_memory_mb", 0) > MEMORY_WARN_MB:
            logger.warning(
                f"InternalMetrics: memória da probe em {m['probe_memory_mb']:.0f}MB "
                f"(limite={MEMORY_WARN_MB}MB) — reduzindo workers para 10"
            )
            if self._pool and hasattr(self._pool, "resize"):
                self._pool.resize(10)

    def _send(self, m: Dict):
        try:
            import httpx
            payload = {
                "probe_token": self.probe_token,
                "metrics": [{
                    "hostname": "probe_internal",
                    "sensor_type": "probe_internal",
                    "sensor_name": k,
                    "value": v,
                    "unit": "",
                    "status": "ok",
                    "timestamp": None,
                    "metadata": {},
                } for k, v in m.items() if k != "timestamp"]
            }
            with httpx.Client(timeout=10.0, verify=False) as client:
                client.post(f"{self.api_url}/api/v1/metrics/probe/bulk", json=payload)
        except Exception as e:
            logger.debug(f"InternalMetrics: falha ao enviar ({e})")

    def get_health_log(self):
        return list(self._health_log)