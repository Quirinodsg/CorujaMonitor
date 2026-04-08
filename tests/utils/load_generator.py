"""
LoadGenerator — Coruja Monitor v3.0.
Simula carga de 1000 hosts × 50 sensores (50.000 métricas/ciclo).
"""
import random
import time
from datetime import datetime, timezone
from uuid import uuid4

from core.spec.enums import HostType, Protocol, SensorStatus
from core.spec.models import Host, Metric, Sensor

# Tipos de sensor com protocolos associados
_SENSOR_TEMPLATES = [
    ("cpu", Protocol.WMI, "%"),
    ("memory", Protocol.WMI, "%"),
    ("disk_c", Protocol.WMI, "%"),
    ("disk_d", Protocol.WMI, "%"),
    ("network_in", Protocol.SNMP, "bytes/s"),
    ("network_out", Protocol.SNMP, "bytes/s"),
    ("ping", Protocol.ICMP, "ms"),
    ("http_response", Protocol.HTTP, "ms"),
    ("tcp_port_80", Protocol.TCP, "ms"),
    ("tcp_port_443", Protocol.TCP, "ms"),
]


class LoadGenerator:
    """Gerador de carga para testes de performance."""

    def generate_hosts(self, count: int = 1000) -> list[Host]:
        """Gera lista de hosts simulados."""
        hosts = []
        for i in range(count):
            hosts.append(
                Host(
                    hostname=f"srv-{i:04d}",
                    ip_address=f"10.{(i >> 16) & 0xFF}.{(i >> 8) & 0xFF}.{i & 0xFF}",
                    type=random.choice(list(HostType)),
                    tags=[f"rack-{i % 20}", f"dc-{i % 3}"],
                )
            )
        return hosts

    def generate_sensors(
        self, hosts: list[Host], sensors_per_host: int = 50
    ) -> list[Sensor]:
        """
        Gera sensores para cada host.
        Cicla pelos templates de sensor para preencher até sensors_per_host.
        """
        sensors = []
        for host in hosts:
            for i in range(sensors_per_host):
                tmpl = _SENSOR_TEMPLATES[i % len(_SENSOR_TEMPLATES)]
                sensor_type, protocol, _ = tmpl
                sensors.append(
                    Sensor(
                        host_id=host.id,
                        type=f"{sensor_type}_{i}",
                        protocol=protocol,
                        interval=60,
                        timeout=30,
                        retries=3,
                        thresholds={"warning": 80.0, "critical": 95.0},
                    )
                )
        return sensors

    def generate_metrics_batch(
        self,
        sensors: list[Sensor],
        timestamp: datetime | None = None,
    ) -> list[Metric]:
        """
        Gera uma métrica por sensor (um ciclo de coleta completo).
        Valores aleatórios entre 0-100 com distribuição normal centrada em 50.
        """
        ts = timestamp or datetime.now(timezone.utc)
        metrics = []
        for sensor in sensors:
            value = max(0.0, min(100.0, random.gauss(50.0, 20.0)))
            # Determinar status baseado em thresholds
            warn = sensor.thresholds.get("warning", 80.0)
            crit = sensor.thresholds.get("critical", 95.0)
            if value >= crit:
                status = SensorStatus.CRITICAL
            elif value >= warn:
                status = SensorStatus.WARNING
            else:
                status = SensorStatus.OK

            tmpl_idx = int(sensor.type.rsplit("_", 1)[-1]) % len(_SENSOR_TEMPLATES)
            unit = _SENSOR_TEMPLATES[tmpl_idx][2]

            metrics.append(
                Metric(
                    sensor_id=sensor.id,
                    host_id=sensor.host_id,
                    value=round(value, 2),
                    unit=unit,
                    timestamp=ts,
                    status=status,
                )
            )
        return metrics

    def simulate_collection_cycle(
        self,
        hosts: list[Host] | None = None,
        sensors: list[Sensor] | None = None,
        host_count: int = 1000,
        sensors_per_host: int = 50,
    ) -> dict:
        """
        Simula um ciclo completo de coleta e retorna estatísticas.
        Retorna: {hosts, sensors, metrics, elapsed_ms, throughput_per_sec}
        """
        if hosts is None:
            hosts = self.generate_hosts(host_count)
        if sensors is None:
            sensors = self.generate_sensors(hosts, sensors_per_host)

        start = time.monotonic()
        metrics = self.generate_metrics_batch(sensors)
        elapsed = time.monotonic() - start

        elapsed_ms = elapsed * 1000
        throughput = len(metrics) / elapsed if elapsed > 0 else float("inf")

        return {
            "hosts": len(hosts),
            "sensors": len(sensors),
            "metrics": len(metrics),
            "elapsed_ms": round(elapsed_ms, 2),
            "throughput_per_sec": round(throughput, 0),
        }
