"""
Parallel Collection Engine — Coruja Monitor
SDD: ProbeOrchestrator + SensorExecutor + MetricsDispatcher + ProbeTelemetry
MCT: Shadow mode, comparação automática, canary release

Feature flag: parallel_enabled (config.yaml)
Quando OFF: probe_core.py roda normalmente (sequencial)
Quando ON: este módulo assume a coleta com ThreadPoolExecutor
"""
import logging
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable

logger = logging.getLogger(__name__)


# ── ProbeTelemetry ────────────────────────────────────────────────────────────

class ProbeTelemetry:
    """Observabilidade da sonda: tempos, erros, métricas por host."""

    def __init__(self):
        self._lock = threading.Lock()
        self._host_times: Dict[str, float] = {}
        self._host_errors: Dict[str, str] = {}
        self._cycle_start: float = 0
        self._cycle_end: float = 0
        self._metrics_count: int = 0
        self._errors_count: int = 0
        self._total_hosts: int = 0

    def start_cycle(self):
        self._cycle_start = time.monotonic()
        self._host_times.clear()
        self._host_errors.clear()
        self._metrics_count = 0
        self._errors_count = 0

    def end_cycle(self):
        self._cycle_end = time.monotonic()

    def record_host(self, host: str, duration_ms: float, metrics_count: int, error: str = None):
        with self._lock:
            self._host_times[host] = duration_ms
            self._metrics_count += metrics_count
            if error:
                self._host_errors[host] = error
                self._errors_count += 1

    @property
    def cycle_duration_ms(self) -> float:
        return (self._cycle_end - self._cycle_start) * 1000

    def summary(self) -> Dict[str, Any]:
        return {
            "cycle_duration_ms": round(self.cycle_duration_ms, 0),
            "total_hosts": len(self._host_times),
            "total_metrics": self._metrics_count,
            "total_errors": self._errors_count,
            "slowest_host": max(self._host_times, key=self._host_times.get) if self._host_times else None,
            "slowest_ms": round(max(self._host_times.values()), 0) if self._host_times else 0,
            "errors": dict(self._host_errors) if self._host_errors else None,
        }


# ── MetricsDispatcher ─────────────────────────────────────────────────────────

class MetricsDispatcher:
    """Envio incremental de métricas — não espera ciclo completo."""

    def __init__(self, api_url: str, probe_token: str, batch_size: int = 50):
        self.api_url = api_url
        self.probe_token = probe_token
        self.batch_size = batch_size
        self._buffer: List[Dict] = []
        self._lock = threading.Lock()
        self._sent_count = 0
        self._error_count = 0

    def enqueue(self, metrics: List[Dict]):
        """Adiciona métricas ao buffer. Envia se atingir batch_size."""
        with self._lock:
            self._buffer.extend(metrics)
            if len(self._buffer) >= self.batch_size:
                self._flush()

    def flush(self):
        """Força envio de tudo que está no buffer."""
        with self._lock:
            self._flush()

    def _flush(self):
        """Envia buffer atual para a API (chamado com lock)."""
        if not self._buffer:
            return

        import socket
        local_hostname = socket.gethostname()
        local_ip = "127.0.0.1"
        try:
            local_ip = socket.gethostbyname(local_hostname)
        except Exception:
            pass

        formatted = []
        for m in self._buffer:
            hostname = m.get("hostname", local_hostname)
            metadata = m.get("metadata", {})
            if hostname == local_hostname:
                metadata["ip_address"] = local_ip
            formatted.append({
                "hostname": hostname,
                "sensor_type": m.get("sensor_type", m.get("type", "unknown")),
                "sensor_name": m.get("name", "unknown"),
                "value": m.get("value", 0),
                "unit": m.get("unit"),
                "status": m.get("status", "ok"),
                "timestamp": m.get("timestamp"),
                "metadata": metadata,
            })

        try:
            import httpx
            with httpx.Client(timeout=15.0, verify=False) as client:
                resp = client.post(
                    f"{self.api_url}/api/v1/metrics/probe/bulk",
                    json={"probe_token": self.probe_token, "metrics": formatted},
                )
                if resp.status_code == 200:
                    self._sent_count += len(formatted)
                    logger.info(f"📤 Dispatch: {len(formatted)} metrics sent (total: {self._sent_count})")
                else:
                    self._error_count += 1
                    logger.warning(f"📤 Dispatch error: HTTP {resp.status_code}")
        except Exception as e:
            self._error_count += 1
            logger.warning(f"📤 Dispatch error: {e}")

        self._buffer.clear()

    @property
    def stats(self) -> Dict[str, int]:
        return {"sent": self._sent_count, "errors": self._error_count, "buffered": len(self._buffer)}


# ── MetricsComparator (MCT Shadow Mode) ───────────────────────────────────────

class MetricsComparator:
    """Compara métricas do modo sequencial vs paralelo (MCT Phase 1)."""

    TOLERANCE_PCT = 5.0  # Diferença aceitável

    def __init__(self):
        self._results: List[Dict] = []

    def compare(self, host: str, metric: str, old_val: float, new_val: float) -> Dict:
        if old_val == 0 and new_val == 0:
            diff_pct = 0.0
        elif old_val == 0:
            diff_pct = 100.0
        else:
            diff_pct = abs(new_val - old_val) / abs(old_val) * 100

        status = "OK" if diff_pct <= self.TOLERANCE_PCT else "DRIFT"
        result = {
            "host": host,
            "metric": metric,
            "old": round(old_val, 2),
            "new": round(new_val, 2),
            "diff_pct": round(diff_pct, 2),
            "status": status,
        }
        self._results.append(result)

        if status == "DRIFT":
            logger.warning(f"MCT DRIFT: {host}/{metric} old={old_val} new={new_val} diff={diff_pct:.1f}%")

        return result

    @property
    def summary(self) -> Dict:
        total = len(self._results)
        drifts = sum(1 for r in self._results if r["status"] == "DRIFT")
        return {"total": total, "ok": total - drifts, "drifts": drifts, "pass": drifts == 0}


# ── ProbeOrchestrator ─────────────────────────────────────────────────────────

class ProbeOrchestrator:
    """
    Orquestrador de coleta paralela.
    Substitui o loop sequencial do probe_core._collect_metrics().
    
    Grupos de coleta (executados em paralelo entre si):
    1. LOCAL: sensores locais (CPU, RAM, Disco, Rede)
    2. WMI: servidores Windows remotos (ThreadPool)
    3. SNMP: dispositivos SNMP remotos (ThreadPool)
    4. STANDALONE: sensores standalone (Engetron, Conflex, Printer, EqualLogic)
    5. HYPERV: hosts Hyper-V
    """

    def __init__(self, probe_core, config: Dict[str, Any]):
        self.probe = probe_core
        self.max_workers = config.get("max_workers", 8)
        self.timeout_seconds = config.get("timeout_seconds", 30)
        self.dispatch_mode = config.get("dispatch_mode", "bulk")  # bulk ou incremental
        self.canary_hosts = config.get("canary_hosts", [])  # MCT Phase 3
        self.telemetry = ProbeTelemetry()
        self.dispatcher = MetricsDispatcher(
            api_url=probe_core.config.api_url,
            probe_token=probe_core.config.probe_token,
            batch_size=50 if self.dispatch_mode == "incremental" else 9999,
        )

    def collect_all(self):
        """Coleta paralela de todas as fontes."""
        self.telemetry.start_cycle()
        timestamp = datetime.now()

        # Fase 1: Coleta local (rápida, não precisa de thread)
        self._collect_local(timestamp)

        # Fase 2: Coleta remota em paralelo
        servers = self._fetch_servers()
        if servers:
            self._collect_servers_parallel(servers, timestamp)

        # Fase 3: Standalone sensors em paralelo
        self._collect_standalone_parallel(timestamp)

        # Fase 4: Hyper-V
        self._collect_hyperv()

        # Flush final
        if self.dispatch_mode == "bulk":
            # Modo bulk: copiar buffer do probe e enviar
            if self.probe.buffer:
                self.dispatcher.enqueue(list(self.probe.buffer))
                self.probe.buffer.clear()
        self.dispatcher.flush()

        self.telemetry.end_cycle()
        summary = self.telemetry.summary()
        logger.info(
            f"⚡ Parallel cycle: {summary['cycle_duration_ms']:.0f}ms | "
            f"{summary['total_hosts']} hosts | {summary['total_metrics']} metrics | "
            f"{summary['total_errors']} errors"
        )
        if summary.get("slowest_host"):
            logger.info(f"   Slowest: {summary['slowest_host']} ({summary['slowest_ms']}ms)")

        return summary

    def _collect_local(self, timestamp):
        """Coleta sensores locais (CPU, RAM, etc.)."""
        t0 = time.monotonic()
        count = 0
        try:
            for collector in self.probe.collectors:
                try:
                    metrics = collector.collect()
                    for m in metrics:
                        m["timestamp"] = timestamp.isoformat()
                        self.probe.buffer.append(m)
                        count += 1
                except Exception as e:
                    logger.error(f"Local collector {collector.__class__.__name__}: {e}")
        except Exception as e:
            logger.error(f"Local collection error: {e}")
        elapsed = (time.monotonic() - t0) * 1000
        self.telemetry.record_host("__local__", elapsed, count)

    def _fetch_servers(self) -> List[Dict]:
        """Busca lista de servidores da API."""
        try:
            import httpx
            with httpx.Client(timeout=10.0, verify=False) as client:
                resp = client.get(
                    f"{self.probe.config.api_url}/api/v1/probes/servers",
                    params={"probe_token": self.probe.config.probe_token},
                )
                if resp.status_code == 200:
                    servers = resp.json()
                    logger.info(f"Found {len(servers)} servers to monitor")
                    return servers
        except Exception as e:
            logger.error(f"Failed to fetch servers: {e}")
        return []

    def _collect_servers_parallel(self, servers: List[Dict], timestamp):
        """Coleta servidores remotos em paralelo com ThreadPoolExecutor."""
        import socket
        local_hostname = socket.gethostname().lower()
        local_ip = socket.gethostbyname(socket.gethostname())

        # Filtrar local
        remote = [s for s in servers
                  if s.get("hostname", "").lower() != local_hostname
                  and s.get("ip_address", "") != local_ip]

        if not remote:
            return

        def collect_one_server(server):
            hostname = server.get("hostname", "unknown")
            t0 = time.monotonic()
            count = 0
            error = None
            try:
                protocol = server.get("monitoring_protocol", "wmi")
                if protocol == "snmp":
                    self.probe._collect_snmp_remote(server)
                else:
                    self.probe._collect_wmi_remote(server)
                count = len([m for m in self.probe.buffer if m.get("hostname", "").lower() == hostname.lower()])
            except Exception as e:
                error = str(e)
                logger.error(f"Parallel collect {hostname}: {e}")
            elapsed = (time.monotonic() - t0) * 1000
            self.telemetry.record_host(hostname, elapsed, count, error)

            # Envio incremental: dispatch após cada servidor
            if self.dispatch_mode == "incremental" and self.probe.buffer:
                self.dispatcher.enqueue(list(self.probe.buffer))
                self.probe.buffer.clear()

        with ThreadPoolExecutor(max_workers=self.max_workers, thread_name_prefix="probe") as pool:
            futures = {pool.submit(collect_one_server, s): s for s in remote}
            for future in as_completed(futures, timeout=self.timeout_seconds * 2):
                server = futures[future]
                try:
                    future.result(timeout=self.timeout_seconds)
                except TimeoutError:
                    hostname = server.get("hostname", "?")
                    logger.warning(f"⏱️ Timeout collecting {hostname} ({self.timeout_seconds}s)")
                    self.telemetry.record_host(hostname, self.timeout_seconds * 1000, 0, "timeout")
                except Exception as e:
                    hostname = server.get("hostname", "?")
                    logger.error(f"Parallel error {hostname}: {e}")
                    self.telemetry.record_host(hostname, 0, 0, str(e))

    def _collect_standalone_parallel(self, timestamp):
        """Coleta sensores standalone em paralelo."""
        t0 = time.monotonic()
        try:
            # Reutiliza o método existente (já funciona)
            self.probe._collect_standalone_sensors()
        except Exception as e:
            logger.error(f"Standalone collection error: {e}")
        elapsed = (time.monotonic() - t0) * 1000
        self.telemetry.record_host("__standalone__", elapsed, 0)

    def _collect_hyperv(self):
        """Coleta Hyper-V."""
        t0 = time.monotonic()
        try:
            self.probe._collect_hyperv_hosts()
        except Exception as e:
            logger.error(f"HyperV collection error: {e}")
        elapsed = (time.monotonic() - t0) * 1000
        self.telemetry.record_host("__hyperv__", elapsed, 0)
