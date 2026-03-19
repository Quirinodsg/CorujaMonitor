"""
Alert Prioritizer — Coruja Monitor v3.0
Calcula score de prioridade ponderado para alertas.
Property 15: score = severidade×0.40 + hosts×0.30 + impacto_critico×0.20 + horario×0.10
"""
from datetime import datetime, timezone

from core.spec.models import Alert
from core.spec.enums import EventSeverity

BUSINESS_HOURS = (8, 18)

# Pesos da fórmula
W_SEVERITY = 0.40
W_HOSTS = 0.30
W_CRITICAL_SERVICES = 0.20
W_BUSINESS_HOURS = 0.10

# Mapeamento de severidade para score [0, 1]
SEVERITY_SCORES = {
    EventSeverity.INFO.value: 0.2,
    EventSeverity.WARNING.value: 0.6,
    EventSeverity.CRITICAL.value: 1.0,
    "info": 0.2,
    "warning": 0.6,
    "critical": 1.0,
}

# Capacidade máxima de hosts para normalização
MAX_HOSTS_REFERENCE = 100


class AlertPrioritizer:
    """
    Score ponderado:
      severidade × 0.40
      + hosts_afetados_normalizado × 0.30
      + impacto_critico × 0.20
      + horario_negocio × 0.10

    Todos os fatores no intervalo [0, 1].
    Score final no intervalo [0, 1].
    """

    def score(self, alert: Alert, context: dict = None) -> float:
        """
        Calcula score de prioridade.
        context pode conter: critical_services_count, max_hosts_reference.
        """
        context = context or {}

        severity_val = alert.severity if isinstance(alert.severity, str) else alert.severity.value
        severity_score = SEVERITY_SCORES.get(severity_val, 0.5)

        # Hosts afetados normalizado [0, 1]
        max_hosts = context.get("max_hosts_reference", MAX_HOSTS_REFERENCE)
        hosts_count = len(alert.affected_hosts)
        hosts_score = min(hosts_count / max_hosts, 1.0) if max_hosts > 0 else 0.0

        # Impacto em serviços críticos [0, 1]
        critical_services = context.get("critical_services_count", 0)
        max_critical = context.get("max_critical_services", 10)
        critical_score = min(critical_services / max_critical, 1.0) if max_critical > 0 else 0.0

        # Horário de negócio [0, 1]
        now = datetime.now(timezone.utc)
        business_hours_score = 1.0 if BUSINESS_HOURS[0] <= now.hour < BUSINESS_HOURS[1] else 0.3

        score = (
            severity_score * W_SEVERITY
            + hosts_score * W_HOSTS
            + critical_score * W_CRITICAL_SERVICES
            + business_hours_score * W_BUSINESS_HOURS
        )

        # Garantir intervalo [0, 1]
        return max(0.0, min(score, 1.0))
