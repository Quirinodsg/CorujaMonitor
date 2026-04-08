"""
E2E: AI DECISION scenario.
Anomaly → full pipeline → remediation ≥85% → feedback.
Requirements: 19.6
"""
import pytest
from datetime import datetime, timezone
from uuid import uuid4

from core.spec.enums import EventSeverity
from core.spec.models import Event, Metric
from ai_agents.anomaly_detection import AnomalyDetectionAgent
from ai_agents.correlation import CorrelationAgent
from ai_agents.root_cause import RootCauseAgent
from ai_agents.base_agent import AgentContext
from ai_agents.pipeline import AgentPipeline
from ai_agents.feedback_loop import FeedbackLoop, RemediationAction, ActionResult


@pytest.mark.e2e
class TestAIDecisionE2E:
    """Req 19.6 — AI DECISION: anomaly → pipeline → remediation → feedback."""

    def test_full_ai_pipeline_e2e(self):
        """Full AI pipeline processes anomaly and produces results."""
        pipeline = AgentPipeline([
            AnomalyDetectionAgent(),
            CorrelationAgent(),
            RootCauseAgent(),
        ])

        host_id = uuid4()
        now = datetime.now(timezone.utc)
        ctx = AgentContext(
            events=[Event(host_id=host_id, type="anomaly", severity=EventSeverity.CRITICAL, timestamp=now)],
            metrics=[Metric(sensor_id=uuid4(), host_id=host_id, value=99.0, unit="%", timestamp=now)],
            topology=None,
        )
        results = pipeline.run(ctx)
        assert len(results) == 3
        assert all(r.success for r in results)

    def test_feedback_weight_adjustment(self):
        """Positive outcomes increase action weight, negative decrease."""
        loop = FeedbackLoop()
        action_type = "restart_service"

        # Positive outcome
        a1 = RemediationAction(agent_name="test", action_type=action_type, target_host="h1")
        aid1 = loop.record_action(a1)
        loop.record_result(aid1, ActionResult(success=True, resolution_time_seconds=60))
        w1 = loop.get_action_weight(action_type)
        assert w1 > 1.0  # increased

        # Negative outcome
        a2 = RemediationAction(agent_name="test", action_type=action_type, target_host="h2")
        aid2 = loop.record_action(a2)
        loop.record_result(aid2, ActionResult(success=True, resolution_time_seconds=600))
        w2 = loop.get_action_weight(action_type)
        assert w2 < w1  # decreased
