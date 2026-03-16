"""
WMI Batch Collector — coleta CPU, RAM e Disco em consulta combinada.
Cache interno por host com TTL 5s para evitar queries redundantes.

Em vez de 3 queries separadas (CPU, RAM, Disco), executa as 3 em paralelo
e cacheia o resultado por 5s — igual ao comportamento do PRTG WMI sensor.
"""
import logging
import threading
import time
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

CACHE_TTL_SEC = 5  # TTL do cache WMI por host


class _CacheEntry:
    __slots__ = ("data", "expires_at")

    def __init__(self, data: dict, ttl: float = CACHE_TTL_SEC):
        self.data = data
        self.expires_at = time.monotonic() + ttl

    def is_valid(self) -> bool:
        return time.monotonic() < self.expires_at


class WMIBatchCollector:
    """
    Coleta CPU + RAM + Disco em batch (paralelo) com cache TTL 5s.

    Uso:
        collector = WMIBatchCollector()
        metrics = collector.collect(wmi_connection, host="SRVHVSPRD010")
        # Retorna lista de métricas: cpu, memory, disk(s)
        # Segunda chamada dentro de 5s retorna do cache.
    """

    def __init__(self, cache_ttl: float = CACHE_TTL_SEC):
        self._cache: Dict[str, _CacheEntry] = {}
        self._lock = threading.Lock()
        self._cache_ttl = cache_ttl
        self._hits = 0
        self._misses = 0

    def collect(self, connection, host: str) -> List[Dict[str, Any]]:
        """
        Coleta métricas do host. Usa cache se disponível.
        connection: objeto wmi.WMI já conectado.
        """
        with self._lock:
            entry = self._cache.get(host)
            if entry and entry.is_valid():
                self._hits += 1
                logger.debug(f"WMIBatch cache HIT para {host}")
                return entry.data["metrics"]

        # Cache miss — executar queries em paralelo
        self._misses += 1
        logger.debug(f"WMIBatch cache MISS para {host}, executando queries")
        metrics = self._collect_batch(connection, host)

        with self._lock:
            self._cache[host] = _CacheEntry({"metrics": metrics}, self._cache_ttl)

        return metrics

    def _collect_batch(self, connection, host: str) -> List[Dict[str, Any]]:
        """Executa CPU, RAM e Disco em threads paralelas."""
        results = {}
        errors = {}

        def run(name, fn):
            try:
                results[name] = fn()
            except Exception as e:
                errors[name] = str(e)
                logger.warning(f"WMIBatch {name} error para {host}: {e}")

        threads = [
            threading.Thread(target=run, args=("cpu", lambda: self._query_cpu(connection))),
            threading.Thread(target=run, args=("memory", lambda: self._query_memory(connection))),
            threading.Thread(target=run, args=("disk", lambda: self._query_disk(connection))),
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=10)

        metrics = []
        if "cpu" in results:
            metrics.extend(results["cpu"])
        if "memory" in results:
            metrics.extend(results["memory"])
        if "disk" in results:
            metrics.extend(results["disk"])

        logger.debug(f"WMIBatch coletou {len(metrics)} métricas de {host} ({len(errors)} erros)")
        return metrics

    def _query_cpu(self, conn) -> List[Dict]:
        rows = conn.query(
            "SELECT Name,LoadPercentage,NumberOfLogicalProcessors FROM Win32_Processor"
        )
        loads = [r.LoadPercentage for r in rows if r.LoadPercentage is not None]
        avg = sum(loads) / len(loads) if loads else 0.0
        return [{
            "type": "cpu",
            "name": "CPU Usage",
            "value": round(float(avg), 2),
            "unit": "percent",
            "status": _status(avg, 80, 95),
            "metadata": {"logical_cpus": rows[0].NumberOfLogicalProcessors if rows else 0},
        }]

    def _query_memory(self, conn) -> List[Dict]:
        rows = conn.query(
            "SELECT FreePhysicalMemory,TotalVisibleMemorySize FROM Win32_OperatingSystem"
        )
        if not rows:
            return []
        total = int(rows[0].TotalVisibleMemorySize)
        free = int(rows[0].FreePhysicalMemory)
        used = total - free
        pct = (used / total * 100) if total > 0 else 0.0
        return [{
            "type": "memory",
            "name": "Memory Usage",
            "value": round(pct, 2),
            "unit": "percent",
            "status": _status(pct, 80, 95),
            "metadata": {
                "total_gb": round(total / 1024 / 1024, 2),
                "free_gb": round(free / 1024 / 1024, 2),
            },
        }]

    def _query_disk(self, conn) -> List[Dict]:
        rows = conn.query(
            "SELECT DeviceID,FreeSpace,Size,VolumeName FROM Win32_LogicalDisk WHERE DriveType=3"
        )
        metrics = []
        for row in rows:
            if not row.Size:
                continue
            total = int(row.Size)
            free = int(row.FreeSpace)
            pct = ((total - free) / total * 100) if total > 0 else 0.0
            metrics.append({
                "type": "disk",
                "name": f"Disk {row.DeviceID}",
                "value": round(pct, 2),
                "unit": "percent",
                "status": _status(pct, 80, 95),
                "metadata": {
                    "device": row.DeviceID,
                    "total_gb": round(total / 1024 ** 3, 2),
                    "free_gb": round(free / 1024 ** 3, 2),
                },
            })
        return metrics

    def invalidate(self, host: str):
        """Remove cache de um host específico."""
        with self._lock:
            self._cache.pop(host, None)

    def stats(self) -> dict:
        with self._lock:
            return {
                "cache_size": len(self._cache),
                "cache_ttl_sec": self._cache_ttl,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate_pct": round(
                    self._hits / max(self._hits + self._misses, 1) * 100, 1
                ),
            }


def _status(value: float, warn: float, crit: float) -> str:
    if value >= crit:
        return "critical"
    if value >= warn:
        return "warning"
    return "ok"


# Singleton global
_collector: Optional[WMIBatchCollector] = None


def get_batch_collector() -> WMIBatchCollector:
    global _collector
    if _collector is None:
        _collector = WMIBatchCollector()
    return _collector
