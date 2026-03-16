"""
Prometheus Exporter - Expõe métricas da probe no formato Prometheus
Endpoint: http://0.0.0.0:9090/metrics
Atualiza a cada 15 segundos
"""
import logging
import threading
import time
from typing import Optional

logger = logging.getLogger(__name__)

UPDATE_INTERVAL = 15  # segundos
DEFAULT_PORT    = 9090


class PrometheusExporter:
    def __init__(self, port: int = DEFAULT_PORT, probe_name: str = "coruja_probe",
                 thread_pool=None, metric_cache=None, scheduler=None):
        self.port = port
        self.probe_name = probe_name
        self._pool = thread_pool
        self._cache = metric_cache
        self._scheduler = scheduler
        self._running = False
        self._server_thread: Optional[threading.Thread] = None
        self._update_thread: Optional[threading.Thread] = None
        self._registry = None
        self._metrics = {}

    def start(self):
        try:
            from prometheus_client import (
                Counter, Gauge, Histogram, CollectorRegistry, start_http_server
            )
            self._registry = CollectorRegistry()
            labels = ["probe_name", "sensor_type", "target_host", "status"]

            self._metrics = {
                "sensors_total": Gauge(
                    "coruja_probe_sensors_total", "Total de sensores registrados",
                    ["probe_name"], registry=self._registry
                ),
                "execution_seconds": Histogram(
                    "coruja_probe_sensor_execution_seconds", "Tempo de execução dos sensores",
                    ["probe_name", "sensor_type", "target_host"],
                    registry=self._registry
                ),
                "wmi_queries_total": Counter(
                    "coruja_probe_wmi_queries_total", "Total de queries WMI executadas",
                    ["probe_name", "target_host"], registry=self._registry
                ),
                "cache_hits_total": Counter(
                    "coruja_probe_cache_hits_total", "Total de cache hits",
                    ["probe_name"], registry=self._registry
                ),
                "cache_misses_total": Counter(
                    "coruja_probe_cache_misses_total", "Total de cache misses",
                    ["probe_name"], registry=self._registry
                ),
                "worker_queue_size": Gauge(
                    "coruja_probe_worker_queue_size", "Tamanho atual da fila de workers",
                    ["probe_name"], registry=self._registry
                ),
                "errors_total": Counter(
                    "coruja_probe_errors_total", "Total de erros",
                    ["probe_name", "sensor_type", "target_host", "status"],
                    registry=self._registry
                ),
            }

            start_http_server(self.port, registry=self._registry)
            logger.info(f"PrometheusExporter: endpoint /metrics na porta {self.port}")

            self._running = True
            self._update_thread = threading.Thread(
                target=self._update_loop, daemon=True, name="PrometheusUpdater"
            )
            self._update_thread.start()

        except ImportError:
            logger.warning("prometheus_client não instalado — PrometheusExporter desabilitado")
        except Exception as e:
            logger.error(f"PrometheusExporter erro ao iniciar: {e}")

    def stop(self):
        self._running = False

    def _update_loop(self):
        while self._running:
            try:
                self._update_metrics()
            except Exception as e:
                logger.debug(f"PrometheusExporter update erro: {e}")
            time.sleep(UPDATE_INTERVAL)

    def _update_metrics(self):
        if not self._metrics:
            return

        if self._scheduler:
            status = self._scheduler.status()
            self._metrics["sensors_total"].labels(
                probe_name=self.probe_name
            ).set(status.get("total_sensors", 0))

        if self._pool:
            stats = self._pool.stats()
            self._metrics["worker_queue_size"].labels(
                probe_name=self.probe_name
            ).set(stats.get("active_workers", 0))

    def record_execution(self, sensor_type: str, target_host: str, duration_s: float):
        if "execution_seconds" in self._metrics:
            self._metrics["execution_seconds"].labels(
                probe_name=self.probe_name,
                sensor_type=sensor_type,
                target_host=target_host,
            ).observe(duration_s)

    def record_error(self, sensor_type: str, target_host: str, status: str):
        if "errors_total" in self._metrics:
            self._metrics["errors_total"].labels(
                probe_name=self.probe_name,
                sensor_type=sensor_type,
                target_host=target_host,
                status=status,
            ).inc()
