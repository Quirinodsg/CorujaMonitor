"""
Anomaly Detection Agent — Coruja Monitor v3.0
Detecta anomalias usando baseline Z-score com janela deslizante de 7 dias.
Encapsula ai-agent/anomaly_detector.py existente sem modificá-lo.
"""
import logging
import math
from collections import deque
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from core.spec.models import Metric, Event
from core.spec.enums import EventSeverity
from ai_agents.base_agent import BaseAgent, AgentContext, AgentResult

logger = logging.getLogger(__name__)

# Desvio padrão mínimo para evitar divisão por zero
MIN_STD = 0.001
# Janela de baseline: 7 dias × 24h × 60min / intervalo_médio (60s) ≈ 10080 amostras
BASELINE_WINDOW = 10_080
# Threshold de anomalia: 3 desvios padrão
ANOMALY_THRESHOLD_SIGMA = 3.0


class SensorBaseline:
    """Mantém baseline estatístico (média + desvio padrão) para um sensor."""

    def __init__(self, window: int = BASELINE_WINDOW):
        self._values: deque[float] = deque(maxlen=window)

    def add(self, value: float) -> None:
        self._values.append(value)

    def mean(self) -> Optional[float]:
        if not self._values:
            return None
        return sum(self._values) / len(self._values)

    def std(self) -> Optional[float]:
        if len(self._values) < 2:
            return None
        mu = self.mean()
        variance = sum((v - mu) ** 2 for v in self._values) / len(self._values)
        return math.sqrt(variance)

    def z_score(self, value: float) -> Optional[float]:
        mu = self.mean()
        sigma = self.std()
        if mu is None or sigma is None:
            return None
        sigma = max(sigma, MIN_STD)
        return abs(value - mu) / sigma

    def is_anomaly(self, value: float) -> tuple[bool, float]:
        """
        Retorna (is_anomaly, confidence_score).
        Requer desvio padrão real > MIN_STD para evitar falsos positivos
        quando todos os valores são idênticos.
        """
        mu = self.mean()
        sigma = self.std()
        if mu is None or sigma is None:
            return False, 0.0
        # Se std real é muito baixo (dados constantes), não há baseline confiável
        if sigma < MIN_STD:
            return False, 0.0
        z = abs(value - mu) / sigma
        is_anom = z > ANOMALY_THRESHOLD_SIGMA
        confidence = min(z / 10.0, 1.0)
        return is_anom, confidence

    def sample_count(self) -> int:
        return len(self._values)


class AnomalyDetectionAgent(BaseAgent):
    """
    Detecta anomalias por Z-score.
    Property 8: desvio > 3σ gera Event(type="anomaly") com confidence_score.
    """

    def __init__(self):
        # {sensor_id: SensorBaseline}
        self._baselines: dict[str, SensorBaseline] = {}

    def _get_baseline(self, sensor_id: str) -> SensorBaseline:
        if sensor_id not in self._baselines:
            self._baselines[sensor_id] = SensorBaseline()
        return self._baselines[sensor_id]

    def process(self, context: AgentContext) -> AgentResult:
        try:
            anomaly_events = []

            for metric in context.metrics:
                sensor_id = str(metric.sensor_id)
                baseline = self._get_baseline(sensor_id)

                is_anom, confidence = baseline.is_anomaly(metric.value)

                # Adicionar ao baseline APÓS verificar (evita contaminar com o próprio valor)
                baseline.add(metric.value)

                if is_anom:
                    event = Event(
                        host_id=metric.host_id,
                        type="anomaly",
                        severity=EventSeverity.WARNING,
                        timestamp=datetime.now(timezone.utc),
                        source_metric_id=metric.sensor_id,
                        description=(
                            f"Anomalia detectada: valor={metric.value}{metric.unit}, "
                            f"confidence={confidence:.2f}"
                        ),
                    )
                    anomaly_events.append({
                        "event": event,
                        "sensor_id": sensor_id,
                        "confidence": confidence,
                        "value": metric.value,
                    })
                    logger.warning(
                        "AnomalyDetection: anomalia em sensor %s valor=%.2f confidence=%.2f",
                        sensor_id, metric.value, confidence,
                    )

            return AgentResult(
                agent_name=self.name,
                success=True,
                output={
                    "anomalies_detected": len(anomaly_events),
                    "anomaly_events": anomaly_events,
                },
            )
        except Exception as e:
            logger.error("AnomalyDetectionAgent error: %s", e)
            return AgentResult(agent_name=self.name, success=False, error=str(e))

    def get_baseline(self, sensor_id: str) -> SensorBaseline:
        """Expõe baseline para testes."""
        return self._get_baseline(sensor_id)
