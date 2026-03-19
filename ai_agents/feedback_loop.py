"""
Feedback Loop — Coruja Monitor v3.0
Registra ações de remediação e resultados para aprendizado contínuo.
Property 11: resolution_time < 300s → positive; >= 300s → negative.
"""
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

logger = logging.getLogger(__name__)

POSITIVE_OUTCOME_THRESHOLD_SECONDS = 300.0


@dataclass
class RemediationAction:
    agent_name: str
    action_type: str
    target_host: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    action_id: str = field(default_factory=lambda: str(uuid4()))


@dataclass
class ActionResult:
    success: bool
    resolution_time_seconds: float


@dataclass
class FeedbackMetrics:
    actions_total: int
    actions_successful: int
    mean_resolution_time_seconds: float
    false_positive_rate: float


class FeedbackLoop:
    """
    Ciclo de feedback: ação → resultado → aprendizado.
    Armazena histórico em memória (persistência via DB quando disponível).
    """

    def __init__(self, db_session=None):
        self._db = db_session
        # {action_id: {action, result, outcome}}
        self._history: dict[str, dict] = {}
        # Pesos por tipo de ação: {action_type: weight}
        self._action_weights: dict[str, float] = {}

    def record_action(self, action: RemediationAction) -> str:
        """Persiste ação. Retorna action_id."""
        self._history[action.action_id] = {
            "action": action,
            "result": None,
            "outcome": "pending",
        }

        if self._db:
            try:
                self._db.execute(
                    """
                    INSERT INTO ai_feedback_actions
                        (action_id, agent_name, action_type, target_host, timestamp, outcome)
                    VALUES (:action_id, :agent_name, :action_type, :target_host, :timestamp, 'pending')
                    """,
                    {
                        "action_id": action.action_id,
                        "agent_name": action.agent_name,
                        "action_type": action.action_type,
                        "target_host": action.target_host,
                        "timestamp": action.timestamp,
                    },
                )
                self._db.commit()
            except Exception as e:
                logger.error("FeedbackLoop: falha ao persistir ação: %s", e)

        logger.info("FeedbackLoop: ação registrada %s (%s)", action.action_id, action.action_type)
        return action.action_id

    def record_result(self, action_id: str, result: ActionResult) -> None:
        """
        Atualiza resultado e classifica outcome.
        Property 11: < 300s → positive; >= 300s → negative.
        """
        if action_id not in self._history:
            logger.warning("FeedbackLoop: action_id %s não encontrado", action_id)
            return

        outcome = (
            "positive"
            if result.resolution_time_seconds < POSITIVE_OUTCOME_THRESHOLD_SECONDS
            else "negative"
        )

        self._history[action_id]["result"] = result
        self._history[action_id]["outcome"] = outcome

        # Ajustar peso da ação
        action = self._history[action_id]["action"]
        self._update_weight(action.action_type, outcome)

        if self._db:
            try:
                self._db.execute(
                    """
                    UPDATE ai_feedback_actions
                    SET result = :result,
                        resolution_time_seconds = :resolution_time,
                        outcome = :outcome
                    WHERE action_id = :action_id
                    """,
                    {
                        "result": "success" if result.success else "failure",
                        "resolution_time": result.resolution_time_seconds,
                        "outcome": outcome,
                        "action_id": action_id,
                    },
                )
                self._db.commit()
            except Exception as e:
                logger.error("FeedbackLoop: falha ao atualizar resultado: %s", e)

        logger.info(
            "FeedbackLoop: resultado registrado %s → %s (%.1fs)",
            action_id, outcome, result.resolution_time_seconds,
        )

    def _update_weight(self, action_type: str, outcome: str) -> None:
        """Ajusta peso da ação baseado no outcome."""
        current = self._action_weights.get(action_type, 1.0)
        if outcome == "positive":
            self._action_weights[action_type] = min(current * 1.1, 2.0)
        else:
            self._action_weights[action_type] = max(current * 0.9, 0.1)

    def get_metrics(self) -> FeedbackMetrics:
        """Retorna métricas de eficácia do feedback loop."""
        completed = [
            h for h in self._history.values()
            if h["result"] is not None
        ]

        total = len(self._history)
        successful = sum(1 for h in completed if h["result"] and h["result"].success)

        resolution_times = [
            h["result"].resolution_time_seconds
            for h in completed
            if h["result"] is not None
        ]
        mean_resolution = (
            sum(resolution_times) / len(resolution_times)
            if resolution_times else 0.0
        )

        negatives = sum(1 for h in completed if h["outcome"] == "negative")
        false_positive_rate = negatives / len(completed) if completed else 0.0

        return FeedbackMetrics(
            actions_total=total,
            actions_successful=successful,
            mean_resolution_time_seconds=mean_resolution,
            false_positive_rate=false_positive_rate,
        )

    def get_action_weight(self, action_type: str) -> float:
        return self._action_weights.get(action_type, 1.0)

    def get_history(self) -> list[dict]:
        return list(self._history.values())
