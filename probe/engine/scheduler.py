"""
Scheduler Central - Controla execução de sensores por intervalo
Intervalos suportados: 30s, 60s, 300s

Controla:
  - Fila de execução
  - Max sensores concorrentes
  - Retry com backoff
  - Proteção contra overload (limite por host)
  - DependencyEngine: bloqueia filhos quando pai está CRITICAL
"""
import logging
import time
import threading
from collections import defaultdict
from typing import Callable, Dict, List, Optional
from dataclasses import dataclass, field

from engine.sensor_engine import SensorDefinition, SensorResult, SensorStatus

logger = logging.getLogger(__name__)

# Intervalos válidos (segundos)
VALID_INTERVALS = {30, 60, 300}

# Proteção contra overload
MAX_SENSORS_PER_HOST = 10
MAX_CONCURRENT_SENSORS = 20
MAX_WMI_QUERIES_PER_HOST = 5
MAX_RPC_CONNECTIONS_PER_HOST = 3


@dataclass
class ScheduledSensor:
    sensor: SensorDefinition
    next_run: float = field(default_factory=time.monotonic)
    last_run: Optional[float] = None
    last_result: Optional[SensorResult] = None
    consecutive_errors: int = 0
    retry_backoff: float = 0.0


class Scheduler:
    """
    Scheduler central de sensores.
    
    Uso:
        scheduler = Scheduler(sensor_engine, thread_pool)
        scheduler.add(sensor_def)
        scheduler.start()
    """

    def __init__(self, sensor_engine, thread_pool, result_callback: Optional[Callable] = None,
                 dependency_engine=None):
        self.engine = sensor_engine
        self.pool = thread_pool
        self.result_callback = result_callback
        self._scheduled: Dict[str, ScheduledSensor] = {}
        self._lock = threading.Lock()
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._host_active_count: Dict[str, int] = defaultdict(int)
        self._host_wmi_count: Dict[str, int] = defaultdict(int)

        # DependencyEngine — opcional, injetado externamente
        self._dep_engine = dependency_engine
        if dependency_engine:
            logger.info("Scheduler: DependencyEngine integrado — dependências ativas")

    def set_dependency_engine(self, dep_engine) -> None:
        """Injeta DependencyEngine após construção."""
        self._dep_engine = dep_engine
        logger.info("Scheduler: DependencyEngine configurado")

    def add(self, sensor: SensorDefinition, delay: float = 0.0):
        """Adiciona sensor ao scheduler"""
        # Validar intervalo
        if sensor.interval not in VALID_INTERVALS:
            # Arredondar para o intervalo válido mais próximo
            sensor.interval = min(VALID_INTERVALS, key=lambda x: abs(x - sensor.interval))
            logger.warning(f"Intervalo ajustado para {sensor.interval}s para sensor {sensor.id}")

        # Verificar limite por host
        host_sensors = sum(
            1 for ss in self._scheduled.values()
            if ss.sensor.target == sensor.target
        )
        if host_sensors >= MAX_SENSORS_PER_HOST:
            logger.warning(
                f"Limite de {MAX_SENSORS_PER_HOST} sensores por host atingido para {sensor.target}"
            )
            return False

        with self._lock:
            self._scheduled[sensor.id] = ScheduledSensor(
                sensor=sensor,
                next_run=time.monotonic() + delay,
            )
            self.engine.register(sensor)

        logger.info(f"Sensor agendado: {sensor.id} ({sensor.type}) → {sensor.target} a cada {sensor.interval}s")
        return True

    def add_many(self, sensors: List[SensorDefinition]):
        """Adiciona múltiplos sensores com delay escalonado para evitar burst"""
        for i, sensor in enumerate(sensors):
            delay = (i % 10) * 3.0  # Escalonar em grupos de 10, 3s entre cada
            self.add(sensor, delay=delay)

    def start(self):
        """Inicia o loop do scheduler"""
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True, name="SchedulerLoop")
        self._thread.start()
        logger.info(f"Scheduler iniciado com {len(self._scheduled)} sensores")

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("Scheduler parado")

    def _loop(self):
        """Loop principal do scheduler"""
        while self._running:
            now = time.monotonic()
            due = []

            with self._lock:
                for sensor_id, ss in self._scheduled.items():
                    if now >= ss.next_run:
                        due.append(ss)

            # Limitar concorrência total
            active = self.pool.active_count()
            available_slots = MAX_CONCURRENT_SENSORS - active

            for ss in due[:available_slots]:
                self._submit(ss)

            if len(due) > available_slots:
                logger.warning(
                    f"Scheduler: {len(due) - available_slots} sensores aguardando slot "
                    f"(max_concurrent={MAX_CONCURRENT_SENSORS})"
                )

            time.sleep(1)

    def _submit(self, ss: ScheduledSensor):
        """Submete sensor para execução no thread pool"""
        sensor = ss.sensor
        host = sensor.target

        # ── DEPENDENCY ENGINE: verificar se sensor pode executar ──────────
        if self._dep_engine is not None:
            try:
                if not self._dep_engine.should_execute(sensor.id, host):
                    logger.debug(
                        "Scheduler: sensor %s (%s) SUSPENSO por dependência em host %s",
                        sensor.id, sensor.type, host,
                    )
                    # Reagendar normalmente — não consome slot
                    with self._lock:
                        ss.next_run = time.monotonic() + sensor.interval
                    return
            except Exception as dep_err:
                logger.warning("Scheduler: erro no DependencyEngine para %s: %s", sensor.id, dep_err)
        # ─────────────────────────────────────────────────────────────────

        # ── PAUSE / ENABLED: verificar campos do sensor ──────────────────
        sensor_enabled = getattr(sensor, 'enabled', True)
        sensor_paused_until = getattr(sensor, 'paused_until', None)
        if not sensor_enabled:
            logger.debug("Scheduler: sensor %s desabilitado (enabled=False)", sensor.id)
            with self._lock:
                ss.next_run = time.monotonic() + sensor.interval
            return
        if sensor_paused_until is not None:
            import datetime as _dt
            now_dt = _dt.datetime.utcnow()
            if isinstance(sensor_paused_until, _dt.datetime) and sensor_paused_until > now_dt:
                logger.debug(
                    "Scheduler: sensor %s pausado até %s", sensor.id, sensor_paused_until
                )
                with self._lock:
                    ss.next_run = time.monotonic() + sensor.interval
                return
        # ─────────────────────────────────────────────────────────────────

        # Proteção: limite de queries WMI por host
        is_wmi = sensor.type.startswith("wmi_")
        if is_wmi and self._host_wmi_count[host] >= MAX_WMI_QUERIES_PER_HOST:
            logger.warning(f"Limite WMI atingido para {host}, adiando sensor {sensor.id}")
            ss.next_run = time.monotonic() + 10  # Tentar em 10s
            return

        # Marcar como em execução
        with self._lock:
            ss.next_run = time.monotonic() + sensor.interval
            ss.last_run = time.monotonic()

        self._host_active_count[host] += 1
        if is_wmi:
            self._host_wmi_count[host] += 1

        def run():
            try:
                result = self.engine.execute(sensor)
                self._on_result(ss, result)
            except Exception as e:
                logger.error(f"Erro ao executar sensor {sensor.id}: {e}")
            finally:
                self._host_active_count[host] -= 1
                if is_wmi:
                    self._host_wmi_count[host] -= 1

        self.pool.submit(run)

    def _on_result(self, ss: ScheduledSensor, result: SensorResult):
        """Processa resultado do sensor"""
        ss.last_result = result

        # ── Alimentar DependencyEngine com o novo status ──────────────────
        if self._dep_engine is not None:
            try:
                # Mapear SensorStatus → SensorStatus do DependencyEngine
                # Ambos usam os mesmos valores de string: 'ok', 'warning', 'critical'
                from engine.dependency_engine import DependencyEngine as _DE
                # Importar enum do core
                try:
                    from core.spec.enums import SensorStatus as CoreStatus
                    status_val = result.status if isinstance(result.status, str) else result.status.value
                    core_status = CoreStatus(status_val)
                    self._dep_engine.update_state(ss.sensor.id, ss.sensor.target, core_status)
                except Exception:
                    pass  # Se enum não mapear, não bloquear execução
            except Exception as dep_err:
                logger.debug("Scheduler: erro ao atualizar DependencyEngine: %s", dep_err)
        # ─────────────────────────────────────────────────────────────────

        if result.status in (SensorStatus.UNKNOWN, SensorStatus.CRITICAL):
            ss.consecutive_errors += 1
            # Backoff exponencial: 30s, 60s, 120s, max 300s
            ss.retry_backoff = min(30 * (2 ** (ss.consecutive_errors - 1)), 300)
            logger.warning(
                f"Sensor {ss.sensor.id} falhou ({ss.consecutive_errors}x), "
                f"próxima tentativa em {ss.retry_backoff}s"
            )
            ss.next_run = time.monotonic() + ss.retry_backoff
        else:
            ss.consecutive_errors = 0
            ss.retry_backoff = 0.0

        if self.result_callback:
            try:
                self.result_callback(result)
            except Exception as e:
                logger.error(f"Erro no result_callback: {e}")

    def status(self) -> Dict:
        """Retorna status do scheduler"""
        with self._lock:
            dep_status = None
            if self._dep_engine is not None:
                try:
                    dep_status = self._dep_engine.get_graph_status()
                except Exception:
                    dep_status = {"error": "unavailable"}

            return {
                "total_sensors": len(self._scheduled),
                "running": self._running,
                "active_per_host": dict(self._host_active_count),
                "wmi_queries_per_host": dict(self._host_wmi_count),
                "dependency_engine": dep_status,
                "sensors": [
                    {
                        "id": ss.sensor.id,
                        "type": ss.sensor.type,
                        "target": ss.sensor.target,
                        "interval": ss.sensor.interval,
                        "last_status": ss.last_result.status if ss.last_result else "never_run",
                        "consecutive_errors": ss.consecutive_errors,
                        "next_run_in": max(0, ss.next_run - time.monotonic()),
                        "enabled": getattr(ss.sensor, 'enabled', True),
                        "paused_until": str(getattr(ss.sensor, 'paused_until', None)),
                        "priority": getattr(ss.sensor, 'priority', 3),
                    }
                    for ss in self._scheduled.values()
                ],
            }
