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

        # Round before comparison to avoid floating-point boundary issues
        diff_pct = round(diff_pct, 2)
        status = "OK" if diff_pct <= self.TOLERANCE_PCT else "DRIFT"
        result = {
            "host": host,
            "metric": metric,
            "old": round(old_val, 2),
            "new": round(new_val, 2),
            "diff_pct": diff_pct,
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


# ── SensorExecutor ─────────────────────────────────────────────────────────────

class SensorExecutor:
    """
    Execução isolada de sensores por tipo.
    Encapsula a lógica de roteamento existente no ProbeCore,
    garantindo que falha em um coletor não propague para outros.
    """

    def __init__(self, probe_core, buffer_lock: threading.Lock = None):
        """Recebe referência ao ProbeCore para acessar métodos de coleta existentes."""
        self.probe = probe_core
        self._buffer_lock = buffer_lock or threading.Lock()

    def collect_server(self, server: Dict) -> List[Dict]:
        """
        Coleta métricas de um servidor remoto.
        Roteia para WMI ou SNMP baseado em monitoring_protocol.
        Retorna lista de métricas coletadas (isolada do buffer global).
        Thread-safe: usa _buffer_lock para proteger acesso ao ProbeCore.buffer.
        Nota: COM init é feito pelo caller (_collect_one_server_safe) para WMI.
        """
        hostname = server.get("hostname", "unknown")
        metrics: List[Dict] = []

        try:
            with self._buffer_lock:
                # Snapshot do buffer antes da coleta para capturar apenas as novas métricas
                buffer_before = len(self.probe.buffer)

            protocol = server.get("monitoring_protocol", "wmi")
            if protocol == "snmp":
                logger.info(f"SensorExecutor: SNMP collection for {hostname}")
                self.probe._collect_snmp_remote(server)
            elif protocol == "wmi" or server.get("wmi_enabled"):
                logger.info(f"SensorExecutor: WMI collection for {hostname}")
                self.probe._collect_wmi_remote(server)
            else:
                logger.info(f"SensorExecutor: WMI fallback for {hostname}")
                self.probe._collect_wmi_remote(server)

            with self._buffer_lock:
                # Extrair métricas adicionadas ao buffer por esta coleta
                if len(self.probe.buffer) > buffer_before:
                    metrics = list(self.probe.buffer[buffer_before:])

        except Exception as e:
            logger.error(f"SensorExecutor collect_server {hostname}: {e}")
            # Isolamento de falhas: exceção não propaga, retorna lista vazia

        return metrics

    def collect_standalone(self, sensor: Dict, timestamp: datetime) -> List[Dict]:
        """
        Coleta métrica de um sensor standalone.
        Preserva lógica de roteamento: HTTP → ICMP → Printer → Engetron → Conflex → EqualLogic → SNMP → fallback.
        Retorna lista de métricas coletadas (isolada do buffer global).
        Thread-safe: usa _buffer_lock para proteger acesso ao ProbeCore.buffer.
        """
        name = sensor.get("name", "unknown")
        metrics: List[Dict] = []

        try:
            with self._buffer_lock:
                # Snapshot do buffer antes da coleta
                buffer_before = len(self.probe.buffer)

            # ── HTTP sensors ──
            if (sensor.get("sensor_type") == "http" or sensor.get("http_url")) and sensor.get("http_url"):
                self._collect_http(sensor, timestamp)

            # ── ICMP/Ping standalone — PRIORIDADE por sensor_type/category ──
            elif sensor.get("ip_address") and (
                sensor.get("sensor_type") in ("icmp", "ping")
                or sensor.get("category") == "icmp"
            ):
                try:
                    self.probe._collect_icmp_standalone(sensor, timestamp)
                except Exception as e:
                    logger.warning(f"ICMP {name} error: {e}")

            # ── Engetron UPS (HTTP scraping) — detecta pelo nome ──
            elif sensor.get("ip_address") and sensor.get("name", "").lower().find("engetron") >= 0:
                try:
                    self.probe._collect_engetron(sensor, timestamp)
                except Exception as e:
                    logger.warning(f"Engetron {name} error: {e}")

            # ── Conflex HVAC (SNMP proprietário) — detecta pelo nome ──
            elif sensor.get("ip_address") and (
                sensor.get("name", "").lower().find("conflex") >= 0
                or sensor.get("name", "").lower().find("ar-condicionado") >= 0
                or sensor.get("name", "").lower().find("ar condicionado") >= 0
            ):
                try:
                    self.probe._collect_conflex(sensor, timestamp)
                except Exception as e:
                    logger.warning(f"Conflex {name} error: {e}")

            # ── Impressora SNMP (Printer MIB) — detecta pelo nome ──
            elif sensor.get("ip_address") and any(
                kw in (sensor.get("name", "") or "").lower()
                for kw in ["impressora", "printer", "samsung", "hp laserjet", "canon"]
            ):
                try:
                    self.probe._collect_printer(sensor, timestamp)
                except Exception as e:
                    logger.warning(f"Printer {name} error: {e}")

            # ── Dell EqualLogic Storage (SNMP proprietário) — detecta pelo nome ──
            elif sensor.get("ip_address") and any(
                kw in (sensor.get("name", "") or "").lower()
                for kw in ["equallogic", "storage", "dell storage", "san", "iscsi storage"]
            ):
                try:
                    self.probe._collect_equallogic(sensor, timestamp)
                except Exception as e:
                    logger.warning(f"EqualLogic {name} error: {e}")

            # ── SNMP sensors (switches, APs, etc.) ──
            elif sensor.get("ip_address") and (
                sensor.get("sensor_type") == "snmp"
                or sensor.get("snmp_community")
            ):
                try:
                    self.probe._collect_snmp_standalone(sensor, timestamp)
                except Exception as e:
                    logger.warning(f"SNMP {name} error: {e}")

            # ── Fallback: qualquer sensor com IP que não foi tratado acima ──
            elif sensor.get("ip_address") and sensor.get("sensor_type") not in ("http", "https"):
                try:
                    self.probe._collect_snmp_standalone(sensor, timestamp)
                except Exception as e:
                    logger.warning(f"Fallback {name} error: {e}")

            with self._buffer_lock:
                # Extrair métricas adicionadas ao buffer por esta coleta
                if len(self.probe.buffer) > buffer_before:
                    metrics = list(self.probe.buffer[buffer_before:])

        except Exception as e:
            logger.error(f"SensorExecutor collect_standalone {name}: {e}")
            # Isolamento de falhas: exceção não propaga, retorna lista vazia

        # Garantir formato padrão em todas as métricas retornadas
        for m in metrics:
            m.setdefault("hostname", "__standalone__")
            m.setdefault("sensor_type", sensor.get("sensor_type", "unknown"))
            m.setdefault("sensor_name", m.get("name", name))
            m.setdefault("value", 0)
            m.setdefault("unit", None)
            m.setdefault("status", "ok")
            m.setdefault("timestamp", timestamp.isoformat())
            m.setdefault("metadata", {})

        return metrics

    def _collect_http(self, sensor: Dict, timestamp: datetime):
        """Coleta sensor HTTP standalone — isolado para reuso."""
        import httpx as _httpx
        name = sensor.get("name", "HTTP")
        try:
            start = time.time()
            with _httpx.Client(timeout=15.0, verify=False, follow_redirects=True) as http_client:
                resp = http_client.request(
                    method=sensor.get("http_method", "GET"),
                    url=sensor["http_url"],
                )
            elapsed_ms = (time.time() - start) * 1000
            status = "ok" if resp.status_code < 400 else "critical"
            logger.info(f"HTTP {name}: {resp.status_code} in {elapsed_ms:.0f}ms")
        except Exception as e:
            elapsed_ms = 0
            status = "critical"
            logger.warning(f"HTTP {name} unreachable: {e}")

        self.probe.buffer.append({
            "sensor_id": sensor["id"],
            "sensor_type": "http",
            "name": name,
            "value": round(elapsed_ms, 2),
            "unit": "ms",
            "status": status,
            "timestamp": timestamp.isoformat(),
            "hostname": "__standalone__",
            "metadata": {"sensor_id": sensor["id"]},
        })


# ── ProbeOrchestrator ─────────────────────────────────────────────────────────

class ProbeOrchestrator:
    """
    Orquestrador de coleta paralela.
    Substitui o loop sequencial do probe_core._collect_metrics().

    Fases de coleta (ordem preservada, paralelismo interno):
    1. LOCAL: sensores locais (CPU, RAM, Disco, Rede) — síncrono
    2. REMOTO: servidores WMI/SNMP — paralelo via ThreadPoolExecutor
    3. STANDALONE: sensores standalone (Engetron, Conflex, Printer, EqualLogic) — paralelo
    4. HYPER-V: hosts Hyper-V
    """

    def __init__(self, probe_core, config: Dict[str, Any]):
        self.probe = probe_core
        self.config = config
        self.max_workers = config.get("max_workers", 8)
        self.timeout_seconds = config.get("timeout_seconds", 30)
        self.dispatch_mode = config.get("dispatch_mode", "bulk")  # bulk ou incremental
        self.canary_hosts: List[str] = config.get("canary_hosts", [])
        self.telemetry = ProbeTelemetry()
        self._buffer_lock = threading.Lock()
        self.executor = SensorExecutor(probe_core, buffer_lock=self._buffer_lock)
        self._pool = ThreadPoolExecutor(
            max_workers=self.max_workers,
            thread_name_prefix="probe",
        )
        self.dispatcher = MetricsDispatcher(
            api_url=probe_core.config.api_url,
            probe_token=probe_core.config.probe_token,
            batch_size=50 if self.dispatch_mode == "incremental" else 9999,
        )
        logger.info(
            f"ProbeOrchestrator initialized: workers={self.max_workers}, "
            f"timeout={self.timeout_seconds}s, dispatch={self.dispatch_mode}, "
            f"canary_hosts={len(self.canary_hosts)}"
        )

    def collect_all(self) -> Dict[str, Any]:
        """Executa ciclo completo de coleta paralela. Retorna summary da telemetria."""
        self.telemetry.start_cycle()
        timestamp = datetime.now()

        # Recarregar canary_hosts do config a cada ciclo (hot-reload)
        self._reload_canary_hosts()

        # Fase 1: LOCAL (síncrono — rápido, não precisa de thread)
        self._collect_local(timestamp)

        # Fase 2: REMOTO (paralelo via ThreadPoolExecutor)
        servers = self._fetch_servers()
        if servers:
            self._collect_servers_parallel(servers, timestamp)

        # Fase 3: STANDALONE (paralelo via ThreadPoolExecutor)
        self._collect_standalone_parallel(timestamp)

        # Fase 4: HYPER-V
        self._collect_hyperv()

        # Flush final — enviar métricas restantes
        if self.dispatch_mode == "bulk":
            with self._buffer_lock:
                if self.probe.buffer:
                    self.dispatcher.enqueue(list(self.probe.buffer))
                    self.probe.buffer.clear()
        self.dispatcher.flush()

        self.telemetry.end_cycle()
        summary = self.telemetry.summary()

        # Logging estruturado do ciclo
        logger.info(
            f"⚡ Parallel cycle complete: {summary['cycle_duration_ms']:.0f}ms | "
            f"{summary['total_hosts']} hosts | {summary['total_metrics']} metrics | "
            f"{summary['total_errors']} errors"
        )
        if summary.get("slowest_host"):
            logger.info(f"   Slowest host: {summary['slowest_host']} ({summary['slowest_ms']:.0f}ms)")
        if summary.get("errors"):
            for host, err in summary["errors"].items():
                logger.warning(f"   Host error: {host} — {err}")

        return summary

    def _reload_canary_hosts(self):
        """Recarrega canary_hosts do config.yaml a cada ciclo (hot-reload sem restart)."""
        try:
            from probe.probe_core import ProbeCore
            fresh = ProbeCore._load_parallel_config(self.probe)
            self.canary_hosts = fresh.get("canary_hosts", [])
        except Exception:
            # Manter valor atual se falhar a releitura
            pass

    def _collect_local(self, timestamp: datetime) -> None:
        """Coleta síncrona de sensores locais (CPU, RAM, Disco, Rede) via collectors do ProbeCore."""
        t0 = time.monotonic()
        count = 0
        try:
            for collector in self.probe.collectors:
                try:
                    metrics = collector.collect()
                    for m in metrics:
                        m["timestamp"] = timestamp.isoformat()
                        with self._buffer_lock:
                            self.probe.buffer.append(m)
                        count += 1
                except Exception as e:
                    logger.error(f"Local collector {collector.__class__.__name__}: {e}")
        except Exception as e:
            logger.error(f"Local collection error: {e}")
        elapsed = (time.monotonic() - t0) * 1000
        self.telemetry.record_host("__local__", elapsed, count)
        logger.debug(f"Local collection: {count} metrics in {elapsed:.0f}ms")

    def _fetch_servers(self) -> List[Dict]:
        """Busca servidores da API e filtra servidor local para evitar duplicação."""
        try:
            import httpx
            import socket
            with httpx.Client(timeout=10.0, verify=False) as client:
                resp = client.get(
                    f"{self.probe.config.api_url}/api/v1/probes/servers",
                    params={"probe_token": self.probe.config.probe_token},
                )
                if resp.status_code != 200:
                    logger.warning(f"Failed to fetch servers: HTTP {resp.status_code}")
                    return []

                servers = resp.json()

            # Filtrar servidor local para evitar coleta duplicada (Req 2.7)
            local_hostname = socket.gethostname().lower()
            try:
                local_ip = socket.gethostbyname(socket.gethostname())
            except Exception:
                local_ip = "127.0.0.1"

            remote = [
                s for s in servers
                if s.get("hostname", "").lower() != local_hostname
                and s.get("ip_address", "") != local_ip
            ]

            filtered_count = len(servers) - len(remote)
            if filtered_count > 0:
                logger.debug(f"Filtered {filtered_count} local server(s) from remote list")
            logger.info(f"Found {len(remote)} remote servers to monitor (total from API: {len(servers)})")
            return remote

        except Exception as e:
            logger.error(f"Failed to fetch servers: {e}")
        return []

    def _collect_servers_parallel(self, servers: List[Dict], timestamp: datetime) -> None:
        """Submete coleta de cada servidor remoto ao ThreadPoolExecutor.
        Trata timeout e exceções por servidor sem afetar os demais."""

        # Aplicar filtro canary_hosts (Req 7)
        if self.canary_hosts:
            canary_set = {h.lower() for h in self.canary_hosts}
            parallel_servers = [s for s in servers if s.get("hostname", "").lower() in canary_set]
            sequential_servers = [s for s in servers if s.get("hostname", "").lower() not in canary_set]
            logger.info(
                f"Canary mode: {len(parallel_servers)} parallel, "
                f"{len(sequential_servers)} sequential"
            )
            # Coleta sequencial dos servidores fora do canary
            for server in sequential_servers:
                self._collect_one_server_safe(server, timestamp)
        else:
            parallel_servers = servers

        if not parallel_servers:
            return

        # Submeter coleta paralela
        futures = {
            self._pool.submit(self._collect_one_server_safe, s, timestamp): s
            for s in parallel_servers
        }

        try:
            for future in as_completed(futures, timeout=self.timeout_seconds * 2):
                server = futures[future]
                hostname = server.get("hostname", "?")
                try:
                    future.result(timeout=self.timeout_seconds)
                except TimeoutError:
                    logger.warning(
                        f"⏱️ Timeout collecting {hostname} "
                        f"(exceeded {self.timeout_seconds}s)"
                    )
                    self.telemetry.record_host(
                        hostname, self.timeout_seconds * 1000, 0, "timeout"
                    )
                except Exception as e:
                    logger.error(f"Parallel error {hostname}: {e}")
                    self.telemetry.record_host(hostname, 0, 0, str(e))
        except TimeoutError:
            # Global timeout for as_completed — log remaining servers
            for future, server in futures.items():
                if not future.done():
                    hostname = server.get("hostname", "?")
                    logger.warning(f"⏱️ Global timeout: {hostname} still pending")
                    self.telemetry.record_host(
                        hostname, self.timeout_seconds * 2 * 1000, 0, "global_timeout"
                    )
                    future.cancel()

    def _collect_one_server_safe(self, server: Dict, timestamp: datetime) -> None:
        """Coleta um servidor individual com isolamento de falhas e telemetria.
        Inicializa COM apartment para WMI funcionar em worker threads."""
        hostname = server.get("hostname", "unknown")
        t0 = time.monotonic()
        count = 0
        error = None
        com_initialized = False
        try:
            # COM init necessário para WMI em worker threads do ThreadPoolExecutor
            try:
                import pythoncom
                pythoncom.CoInitialize()
                com_initialized = True
            except ImportError:
                pass  # Linux ou pythoncom não disponível — OK, não usa WMI
            except Exception:
                pass

            metrics = self.executor.collect_server(server)
            count = len(metrics)

            # Despacho incremental: enviar métricas imediatamente
            if self.dispatch_mode == "incremental" and metrics:
                self.dispatcher.enqueue(metrics)
        except Exception as e:
            error = str(e)
            logger.error(f"Collection failed for {hostname}: {e}")
        finally:
            if com_initialized:
                try:
                    pythoncom.CoUninitialize()
                except Exception:
                    pass

        elapsed = (time.monotonic() - t0) * 1000
        self.telemetry.record_host(hostname, elapsed, count, error)

    def _collect_standalone_parallel(self, timestamp: datetime) -> None:
        """Coleta sensores standalone em paralelo via SensorExecutor."""
        t0 = time.monotonic()
        total_metrics = 0
        try:
            # Buscar sensores standalone da API
            sensors = self._fetch_standalone_sensors()
            if not sensors:
                elapsed = (time.monotonic() - t0) * 1000
                self.telemetry.record_host("__standalone__", elapsed, 0)
                return

            logger.info(f"Collecting {len(sensors)} standalone sensors in parallel")

            # Submeter cada sensor ao pool
            futures = {
                self._pool.submit(self.executor.collect_standalone, sensor, timestamp): sensor
                for sensor in sensors
            }

            for future in as_completed(futures, timeout=self.timeout_seconds * 2):
                sensor = futures[future]
                sensor_name = sensor.get("name", "unknown")
                try:
                    metrics = future.result(timeout=self.timeout_seconds)
                    total_metrics += len(metrics)
                except TimeoutError:
                    logger.warning(f"⏱️ Standalone timeout: {sensor_name}")
                except Exception as e:
                    logger.warning(f"Standalone error {sensor_name}: {e}")

        except Exception as e:
            logger.error(f"Standalone collection error: {e}")

        elapsed = (time.monotonic() - t0) * 1000
        self.telemetry.record_host("__standalone__", elapsed, total_metrics)

    def _fetch_standalone_sensors(self) -> List[Dict]:
        """Busca sensores standalone da API."""
        try:
            import httpx
            with httpx.Client(timeout=10.0, verify=False) as client:
                resp = client.get(
                    f"{self.probe.config.api_url}/api/v1/sensors/standalone/by-probe",
                    params={"probe_token": self.probe.config.probe_token},
                )
                if resp.status_code == 200:
                    sensors = resp.json()
                    return sensors if sensors else []
                else:
                    logger.warning(f"Failed to fetch standalone sensors: HTTP {resp.status_code}")
        except Exception as e:
            logger.error(f"Failed to fetch standalone sensors: {e}")
        return []

    def _collect_hyperv(self) -> None:
        """Coleta Hyper-V via método existente do ProbeCore."""
        t0 = time.monotonic()
        try:
            self.probe._collect_hyperv_hosts()
        except Exception as e:
            logger.error(f"HyperV collection error: {e}")
        elapsed = (time.monotonic() - t0) * 1000
        self.telemetry.record_host("__hyperv__", elapsed, 0)
