"""
Auto Remediation Agent — Coruja Monitor v3.0
Executa ações de remediação quando confiança >= 85% e DecisionAgent aprovou.
Property 10: só executa com confidence >= 0.85.
"""
import logging
from datetime import datetime, timezone

from ai_agents.base_agent import BaseAgent, AgentContext, AgentResult

logger = logging.getLogger(__name__)

CONFIDENCE_THRESHOLD = 0.85

# Ações de remediação pré-configuradas
REMEDIATION_ACTIONS = {
    "high_cpu": "restart_service",
    "low_memory": "clear_cache",
    "disk_full": "cleanup_logs",
    "host_unreachable": "check_network",
    "service_down": "restart_service",
    "anomaly": "increase_monitoring",
}


class AutoRemediationAgent(BaseAgent):
    """
    Executa remediação automática.
    Property 10: confidence < 0.85 → não executa nenhuma ação.
    """

    def __init__(self):
        self._executed_actions: list[dict] = []

    def process(self, context: AgentContext) -> AgentResult:
        try:
            # Verificar se DecisionAgent aprovou
            should_alert = context.pipeline_data.get("should_alert", False)
            confidence = context.pipeline_data.get("decision_confidence", 0.0)

            # Property 10: só executa com confiança >= 85%
            if not should_alert or confidence < CONFIDENCE_THRESHOLD:
                logger.debug(
                    "AutoRemediation: pulando (should_alert=%s, confidence=%.2f < %.2f)",
                    should_alert, confidence, CONFIDENCE_THRESHOLD,
                )
                return AgentResult(
                    agent_name=self.name,
                    success=True,
                    output={"actions_executed": [], "skipped": True, "reason": "confidence_below_threshold"},
                )

            # Determinar ações baseadas nos tipos de evento
            actions_executed = []
            for event in context.events:
                event_type = event.type if isinstance(event.type, str) else str(event.type)
                action = REMEDIATION_ACTIONS.get(event_type)
                if action:
                    result = self._execute_action(action, str(event.host_id), event_type)
                    actions_executed.append(result)

            return AgentResult(
                agent_name=self.name,
                success=True,
                output={"actions_executed": actions_executed, "skipped": False},
            )
        except Exception as e:
            logger.error("AutoRemediationAgent error: %s", e)
            return AgentResult(agent_name=self.name, success=False, error=str(e))

    def _execute_action(self, action: str, host_id: str, event_type: str) -> dict:
        """Executa ação de remediação e registra resultado."""
        start = datetime.now(timezone.utc)
        # Simulação de execução (em produção: chamar API/script real)
        success = True
        logger.info("AutoRemediation: executando '%s' em host %s (evento: %s)", action, host_id, event_type)

        record = {
            "action": action,
            "host_id": host_id,
            "event_type": event_type,
            "timestamp": start.isoformat(),
            "result": "success" if success else "failure",
            "duration_ms": 0,
        }
        self._executed_actions.append(record)
        return record
