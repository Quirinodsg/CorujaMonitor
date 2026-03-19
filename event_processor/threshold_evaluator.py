"""
Threshold Evaluator — Coruja Monitor v3.0
Avalia métricas contra thresholds e retorna SensorStatus.
"""
from core.spec.models import Metric
from core.spec.enums import SensorStatus


class ThresholdEvaluator:
    """
    Avalia o status de uma métrica com base nos thresholds do sensor.

    Thresholds esperados: {"warning": float, "critical": float}
    Suporta thresholds "lower" (ex: memória livre — abaixo é ruim).
    """

    def evaluate(self, metric: Metric, thresholds: dict) -> SensorStatus:
        """
        Retorna SensorStatus baseado nos thresholds.

        Lógica padrão (higher = worse):
          value >= critical → CRITICAL
          value >= warning  → WARNING
          else              → OK

        Se thresholds contiver "lower": True, inverte a lógica
        (ex: memória livre — valor baixo é ruim).
        """
        if not thresholds:
            return SensorStatus.OK

        value = metric.value
        warning = thresholds.get("warning")
        critical = thresholds.get("critical")
        lower_is_worse = thresholds.get("lower", False)

        if lower_is_worse:
            # Valor baixo é ruim (ex: memória livre)
            if critical is not None and value <= critical:
                return SensorStatus.CRITICAL
            if warning is not None and value <= warning:
                return SensorStatus.WARNING
            return SensorStatus.OK
        else:
            # Valor alto é ruim (ex: CPU %)
            if critical is not None and value >= critical:
                return SensorStatus.CRITICAL
            if warning is not None and value >= warning:
                return SensorStatus.WARNING
            return SensorStatus.OK

    def get_event_type(self, metric_type: str, status: SensorStatus) -> str:
        """Mapeia tipo de sensor + status para tipo de evento."""
        mapping = {
            ("cpu", SensorStatus.CRITICAL): "high_cpu",
            ("cpu", SensorStatus.WARNING): "high_cpu",
            ("memory", SensorStatus.CRITICAL): "low_memory",
            ("memory", SensorStatus.WARNING): "low_memory",
            ("disk", SensorStatus.CRITICAL): "disk_full",
            ("disk", SensorStatus.WARNING): "disk_full",
            ("ping", SensorStatus.CRITICAL): "host_unreachable",
            ("service", SensorStatus.CRITICAL): "service_down",
        }
        key = (metric_type.lower(), status)
        return mapping.get(key, f"{metric_type}_{status.value}")
