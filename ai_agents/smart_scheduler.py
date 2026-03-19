"""
Smart Scheduler Agent — Coruja Monitor v3.0
Ajusta dinamicamente os intervalos de coleta por sensor.
"""
import logging
from ai_agents.base_agent import BaseAgent, AgentContext, AgentResult

logger = logging.getLogger(__name__)

DEFAULT_INTERVAL = 60       # segundos
ANOMALY_INTERVAL = 30       # segundos — reduz quando anomalia detectada
RECOVERY_CYCLES = 5         # ciclos normais para restaurar intervalo padrão


class SmartSchedulerAgent(BaseAgent):
    """
    Ajusta intervalos de coleta:
    - Anomalia detectada → reduz para 30s
    - 5 ciclos normais consecutivos → restaura para padrão
    """

    def __init__(self):
        # {sensor_id: normal_cycles_count}
        self._normal_cycles: dict[str, int] = {}
        # {sensor_id: current_interval}
        self._intervals: dict[str, int] = {}

    def process(self, context: AgentContext) -> AgentResult:
        try:
            adjustments = {}
            anomaly_sensor_ids = set()

            # Coletar sensores com anomalia dos eventos
            for event in context.events:
                if event.type == "anomaly":
                    # source_metric_id é o sensor_id
                    if event.source_metric_id:
                        anomaly_sensor_ids.add(str(event.source_metric_id))

            # Ajustar intervalos
            for sensor_id in anomaly_sensor_ids:
                self._intervals[sensor_id] = ANOMALY_INTERVAL
                self._normal_cycles[sensor_id] = 0
                adjustments[sensor_id] = ANOMALY_INTERVAL
                logger.info("SmartScheduler: sensor %s → %ds (anomalia)", sensor_id, ANOMALY_INTERVAL)

            # Verificar sensores em recuperação (sem anomalia neste ciclo)
            for sensor_id, interval in list(self._intervals.items()):
                if sensor_id not in anomaly_sensor_ids and interval == ANOMALY_INTERVAL:
                    self._normal_cycles[sensor_id] = self._normal_cycles.get(sensor_id, 0) + 1
                    if self._normal_cycles[sensor_id] >= RECOVERY_CYCLES:
                        self._intervals[sensor_id] = DEFAULT_INTERVAL
                        adjustments[sensor_id] = DEFAULT_INTERVAL
                        logger.info("SmartScheduler: sensor %s → %ds (recuperado)", sensor_id, DEFAULT_INTERVAL)

            return AgentResult(
                agent_name=self.name,
                success=True,
                output={"interval_adjustments": adjustments},
            )
        except Exception as e:
            logger.error("SmartSchedulerAgent error: %s", e)
            return AgentResult(agent_name=self.name, success=False, error=str(e))

    def get_interval(self, sensor_id: str) -> int:
        return self._intervals.get(sensor_id, DEFAULT_INTERVAL)
