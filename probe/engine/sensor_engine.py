"""
Sensor Engine - Arquitetura baseada em sensores (como PRTG)

Cada sensor é uma unidade independente com:
  id, type, target, interval, timeout, retries, query

Tipos suportados:
  icmp_ping, tcp_port, wmi_cpu, wmi_memory, wmi_disk,
  wmi_service, wmi_process, registry_perf
"""
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class SensorType(str, Enum):
    ICMP_PING = "icmp_ping"
    TCP_PORT = "tcp_port"
    WMI_CPU = "wmi_cpu"
    WMI_MEMORY = "wmi_memory"
    WMI_DISK = "wmi_disk"
    WMI_SERVICE = "wmi_service"
    WMI_PROCESS = "wmi_process"
    REGISTRY_PERF = "registry_perf"


class SensorStatus(str, Enum):
    OK = "ok"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"
    PAUSED = "paused"


@dataclass
class SensorDefinition:
    """Define um sensor - o que coletar, de onde e como"""
    id: str
    type: SensorType
    target: str                          # hostname ou IP
    interval: int = 60                   # segundos entre coletas
    timeout: int = 10                    # timeout por coleta
    retries: int = 2                     # tentativas em caso de falha
    query: Optional[str] = None          # WQL query customizada (opcional)
    port: Optional[int] = None           # para tcp_port
    service_name: Optional[str] = None   # para wmi_service
    credentials: Optional[Dict] = None  # {username, password, domain}
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class SensorResult:
    """Resultado de uma execução de sensor"""
    sensor_id: str
    sensor_type: str
    target: str
    status: SensorStatus
    value: float
    unit: str
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    execution_ms: float = 0.0


class SensorEngine:
    """
    Motor de execução de sensores.
    Recebe definições de sensores e executa cada um usando o coletor correto.
    """

    def __init__(self, wmi_pool=None):
        self.wmi_pool = wmi_pool
        self._sensors: Dict[str, SensorDefinition] = {}

    def register(self, sensor: SensorDefinition):
        """Registra um sensor no engine"""
        self._sensors[sensor.id] = sensor
        logger.debug(f"Sensor registrado: {sensor.id} ({sensor.type}) → {sensor.target}")

    def register_many(self, sensors: List[SensorDefinition]):
        for s in sensors:
            self.register(s)

    def execute(self, sensor: SensorDefinition) -> SensorResult:
        """Executa um sensor e retorna o resultado"""
        start = time.monotonic()
        try:
            result = self._dispatch(sensor)
            result.execution_ms = (time.monotonic() - start) * 1000
            logger.debug(
                f"Sensor {sensor.id} [{sensor.type}] → {result.status} "
                f"({result.value} {result.unit}) [{result.execution_ms:.1f}ms]"
            )
            return result
        except Exception as e:
            elapsed = (time.monotonic() - start) * 1000
            logger.error(f"Sensor {sensor.id} falhou: {e}")
            return SensorResult(
                sensor_id=sensor.id,
                sensor_type=sensor.type,
                target=sensor.target,
                status=SensorStatus.UNKNOWN,
                value=0.0,
                unit="",
                error=str(e),
                execution_ms=elapsed,
            )

    def execute_all(self) -> List[SensorResult]:
        """Executa todos os sensores registrados"""
        return [self.execute(s) for s in self._sensors.values()]

    def _dispatch(self, sensor: SensorDefinition) -> SensorResult:
        """Despacha para o coletor correto baseado no tipo"""
        if sensor.type == SensorType.ICMP_PING:
            return self._run_icmp(sensor)
        elif sensor.type == SensorType.TCP_PORT:
            return self._run_tcp_port(sensor)
        elif sensor.type in (SensorType.WMI_CPU, SensorType.WMI_MEMORY,
                              SensorType.WMI_DISK, SensorType.WMI_SERVICE,
                              SensorType.WMI_PROCESS):
            return self._run_wmi(sensor)
        elif sensor.type == SensorType.REGISTRY_PERF:
            return self._run_registry(sensor)
        else:
            raise ValueError(f"Tipo de sensor desconhecido: {sensor.type}")

    def _run_icmp(self, sensor: SensorDefinition) -> SensorResult:
        from collectors.icmp_sensor import ICMPSensor
        s = ICMPSensor(host=sensor.target, timeout=sensor.timeout, retries=sensor.retries)
        r = s.collect()
        return SensorResult(
            sensor_id=sensor.id,
            sensor_type=sensor.type,
            target=sensor.target,
            status=SensorStatus(r["status"]),
            value=r["latency_ms"],
            unit="ms",
            metadata=r.get("metadata", {}),
        )

    def _run_tcp_port(self, sensor: SensorDefinition) -> SensorResult:
        from collectors.tcp_port_sensor import TCPPortSensor
        port = sensor.port or 80
        s = TCPPortSensor(host=sensor.target, port=port, timeout=sensor.timeout, retries=sensor.retries)
        r = s.collect()
        return SensorResult(
            sensor_id=sensor.id,
            sensor_type=sensor.type,
            target=sensor.target,
            status=SensorStatus(r["status"]),
            value=r["latency_ms"],
            unit="ms",
            metadata=r.get("metadata", {}),
        )

    def _run_wmi(self, sensor: SensorDefinition) -> SensorResult:
        """Executa sensor WMI usando SmartCollector via pool"""
        from engine.smart_collector import SmartCollector

        creds = sensor.credentials or {}
        conn = None

        if self.wmi_pool:
            conn = self.wmi_pool.acquire(
                sensor.target,
                creds.get("username", ""),
                creds.get("password", ""),
                creds.get("domain", ""),
            )

        try:
            sc = SmartCollector(wmi_connection=conn)

            if sensor.type == SensorType.WMI_CPU:
                metrics = sc.collect_cpu()
            elif sensor.type == SensorType.WMI_MEMORY:
                metrics = sc.collect_memory()
            elif sensor.type == SensorType.WMI_DISK:
                metrics = sc.collect_disk()
            elif sensor.type == SensorType.WMI_SERVICE:
                from engine.wmi_engine import WMIEngine
                engine = WMIEngine(conn)
                svc = sensor.service_name or ""
                wql = f"SELECT Name,State,StartMode FROM Win32_Service WHERE Name='{svc}'"
                metrics = engine.collect_services(filter_auto_only=False) if not svc else []
            elif sensor.type == SensorType.WMI_PROCESS:
                from engine.wmi_engine import WMIEngine
                engine = WMIEngine(conn)
                metrics = engine.collect_processes()
            else:
                metrics = []

            if not metrics:
                return SensorResult(
                    sensor_id=sensor.id,
                    sensor_type=sensor.type,
                    target=sensor.target,
                    status=SensorStatus.UNKNOWN,
                    value=0.0,
                    unit="",
                    error="no_data",
                )

            m = metrics[0]
            return SensorResult(
                sensor_id=sensor.id,
                sensor_type=sensor.type,
                target=sensor.target,
                status=SensorStatus(m.get("status", "unknown")),
                value=float(m.get("value", 0)),
                unit=m.get("unit", ""),
                metadata=m.get("metadata", {}),
            )

        finally:
            if self.wmi_pool and conn:
                self.wmi_pool.release(sensor.target, conn)

    def _run_registry(self, sensor: SensorDefinition) -> SensorResult:
        from collectors.registry_collector import RemoteRegistryCollector
        creds = sensor.credentials or {}
        rc = RemoteRegistryCollector(
            hostname=sensor.target,
            username=creds.get("username"),
            password=creds.get("password"),
            domain=creds.get("domain"),
        )
        info = rc.collect_os_info()
        rc.close()

        return SensorResult(
            sensor_id=sensor.id,
            sensor_type=sensor.type,
            target=sensor.target,
            status=SensorStatus.OK if info else SensorStatus.UNKNOWN,
            value=1.0 if info else 0.0,
            unit="state",
            metadata=info,
        )

    def get_sensor(self, sensor_id: str) -> Optional[SensorDefinition]:
        return self._sensors.get(sensor_id)

    def list_sensors(self) -> List[SensorDefinition]:
        return list(self._sensors.values())
