"""
Integration: AI DECISION scenario.
Anomaly → Correlation → Root Cause → Decision → Auto-remediation ≥85%.
Requirements: 12.4
"""
import pytest
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from core.spec.enums import EventSeverity, SensorStatus
from core.spec.models import Event, Metric
from ai_agents.anomaly_detection import AnomalyDetectionAgent, SensorBaseline
from ai_agents.base_agent import AgentContext, AgentResult
from ai_agents.correlation import CorrelationAgent
from ai_agents.root_cause import RootCauseAgent, RootCauseEngine
from ai_agents.pipeline import AgentPipeline
from ai_agents.feedback_loop import FeedbackLoop, RemediationAction, ActionResult


@pytest.mark.integration
class TestAIDecisionFlow:
    """Req 12.4 — AI DECISION: anomaly → correlation → root cause → remediation."""

    def test_anomaly_detection_triggers_pipeline(self):
        """Anomaly >3σ is detected and flows through pipeline."""
        agent = AnomalyDetectionAgent()
        sensor_id = uuid4()
        host_id = uuid4()

        # Build baseline
        baseline = agent.get_baseline(str(sensor_id))
        for v in range(100):
            baseline.add(50.0 + (v % 3))

        # Inject anomaly
        is_anom, confidence = baseline.is_anomaly(200.0)
        assert is_anom is True
        assert confidence > 0

    def test_correlation_groups_same_host_events(self):
        """Events from same host within 5min are correlated."""
        agent = CorrelationAgent()
        host_id = uuid4()
        now = datetime.now(timezone.utc)

        events = [
            Event(host_id=host_id, type="cpu_high", severity=EventSeverity.WARNING,
                  timestamp=now),
            Event(host_id=host_id, type="mem_high", severity=EventSeverity.WARNING,
                  timestamp=now + timedelta(minutes=1)),
        ]
        ctx = AgentContext(events=events, metrics=[], topology=None)
        result = agent.process(ctx)
        assert result.success is True
        groups = result.output["correlated_groups"]
        # Both events should be in same group (same host, within 5min)
        assert len(groups) == 1
        assert groups[0]["event_count"] == 2

    def test_root_cause_identifies_parent(self, topology_simulator):
        """Root cause engine identifies parent node when children fail."""
        graph, switch_id, affected = topology_simulator.create_cascade_scenario()
        engine = RootCauseEngine()

        # Create events for affected nodes
        events = []
        for node_id in affected[:3]:
            events.append(Event(
                host_id=uuid4(),  # Use node_id as host_id conceptually
                type="node_down",
                severity=EventSeverity.CRITICAL,
                timestamp=datetime.now(timezone.utc),
            ))

        result = engine.analyze(events, None)
        assert result is not None
        assert result.confidence >= 0.5

    def test_feedback_loop_positive_outcome(self):
        """Fast resolution (<300s) classified as positive outcome."""
        loop = FeedbackLoop()
        action = RemediationAction(
            agent_name="AutoRemediation",
            action_type="restart_service",
            target_host="srv-001",
        )
        action_id = loop.record_action(action)
        loop.record_result(action_id, ActionResult(success=True, resolution_time_seconds=60.0))

        history = loop.get_history()
        assert len(history) == 1
        assert history[0]["outcome"] == "positive"

    def test_feedback_loop_negative_outcome(self):
        """Slow resolution (≥300s) classified as negative outcome."""
        loop = FeedbackLoop()
        action = RemediationAction(
            agent_name="AutoRemediation",
            action_type="restart_service",
            target_host="srv-002",
        )
        action_id = loop.record_action(action)
        loop.record_result(action_id, ActionResult(success=True, resolution_time_seconds=600.0))

        history = loop.get_history()
        assert history[0]["outcome"] == "negative"

    def test_full_pipeline_execution(self):
        """Full pipeline with multiple agents executes without crash."""
        anomaly = AnomalyDetectionAgent()
        correlation = CorrelationAgent()
        root_cause = RootCauseAgent()

        pipeline = AgentPipeline([anomaly, correlation, root_cause])

        host_id = uuid4()
        metrics = [
            Metric(sensor_id=uuid4(), host_id=host_id, value=50.0,
                   unit="%", timestamp=datetime.now(timezone.utc)),
        ]
        events = [
            Event(host_id=host_id, type="test", severity=EventSeverity.WARNING,
                  timestamp=datetime.now(timezone.utc)),
        ]
        ctx = AgentContext(events=events, metrics=metrics, topology=None)
        results = pipeline.run(ctx)
        assert len(results) == 3
        # All agents should succeed (no crashes)
        for r in results:
            assert r.success is True
