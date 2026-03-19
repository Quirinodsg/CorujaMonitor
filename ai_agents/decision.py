"""
Decision Agent — Coruja Monitor v3.0
Decide se eventos correlacionados devem gerar um Alert.
"""
import logging
from datetime import datetime, timezone

from core.spec.enums import EventSeverity
from ai_agents.base_agent import BaseAgent, AgentContext, AgentResult

logger = logging.getLogger(__name__)

# Thresholds de decisão
MIN_CONFIDENCE_FOR_ALERT = 0.3
BUSINESS_HOURS = (8, 18)  # 8h às 18h


class DecisionAgent(BaseAgent):
    """
    Avalia eventos correlacionados e decide se geram Alert.
    Considera: severidade, hosts afetados, janela de manutenção, histórico.
    """

    def process(self, context: AgentContext) -> AgentResult:
        try:
            decisions = []
            root_cause_results = context.pipeline_data.get("root_cause_results", [])

            # Se não há resultados de causa raiz, avaliar eventos diretamente
            if not root_cause_results and context.events:
                root_cause_results = [{"affected_nodes_count": 1, "confidence": 0.5}]

            for rc_result in root_cause_results:
                decision = self._evaluate(rc_result, context)
                decisions.append(decision)

            should_alert = any(d["should_alert"] for d in decisions)

            return AgentResult(
                agent_name=self.name,
                success=True,
                output={
                    "should_alert": should_alert,
                    "decisions": decisions,
                    "confidence": max((d["confidence"] for d in decisions), default=0.0),
                },
            )
        except Exception as e:
            logger.error("DecisionAgent error: %s", e)
            return AgentResult(agent_name=self.name, success=False, error=str(e))

    def _evaluate(self, rc_result: dict, context: AgentContext) -> dict:
        confidence = rc_result.get("confidence", 0.5)
        affected_count = rc_result.get("affected_nodes_count", 1)

        # Verificar severidade dos eventos
        has_critical = any(
            (e.severity if isinstance(e.severity, str) else e.severity.value) == EventSeverity.CRITICAL.value
            for e in context.events
        )

        # Verificar horário de negócio
        now = datetime.now(timezone.utc)
        in_business_hours = BUSINESS_HOURS[0] <= now.hour < BUSINESS_HOURS[1]

        # Verificar histórico de falsos positivos
        false_positive_rate = self._get_false_positive_rate(context.feedback_history)

        # Decisão: alertar se confiança suficiente e não é falso positivo frequente
        should_alert = (
            confidence >= MIN_CONFIDENCE_FOR_ALERT
            and false_positive_rate < 0.5
            and (has_critical or affected_count > 1)
        )

        return {
            "should_alert": should_alert,
            "confidence": confidence,
            "has_critical": has_critical,
            "affected_count": affected_count,
            "in_business_hours": in_business_hours,
            "false_positive_rate": false_positive_rate,
        }

    def _get_false_positive_rate(self, feedback_history: list[dict]) -> float:
        if not feedback_history:
            return 0.0
        negatives = sum(1 for f in feedback_history if f.get("outcome") == "negative")
        return negatives / len(feedback_history)
