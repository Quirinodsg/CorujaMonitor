"""
Unit tests for AI Pipeline — Coruja Monitor v3.0
Tests: AnomalyDetection, pipeline resilience, AutoRemediation,
       FeedbackLoop, RootCause, CircuitBreaker, correlation.
Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8
"""
import time
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from ai_agents.anomaly_detection import AnomalyDetectionAgent, SensorBaseline
from ai_agents.auto_remediation import AutoRemediationAgent, CONFIDENCE_THRESHOLD
from ai_agents.base_agent import AgentContext, AgentResult, BaseAgent
from ai_agents.correlation import CorrelationAgent, CORRELATION_WINDOW_MINUTES
from ai_agents.feedback_loop import (
    ActionResult,
    FeedbackLoop,
    RemediationAction,
    POSITIVE_OUTCOME_THRESHOLD_SECONDS,
)
from ai_agents.pipeline import AgentPipeline, CircuitBreaker, CIRCUIT_BREAKER_WINDOW
from ai_agents.root_cause import RootCauseAgent, RootCauseEngine
from core.spec.enums import EventSeverity, NodeType, SensorStatus
from core.spec.models import Event, Metric, TopologyNode
from topology_engine.graph import TopologyGraph


# ---------------------------------------------------------------------------
# AnomalyDetection
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestAnomalyDetection:
    """Req 6.1 — baseline and >3σ detection."""

    def test_baseline_accumulates_samples(self):
        bl = SensorBaseline(window=100)
        for v in [10, 20, 30]:
            bl.add(v)
        assert bl.sample_count() == 3
        assert bl.mean() == pytest.approx(20.0)

    def test_no_anomaly_within_3sigma(self):
        bl = SensorBaseline(window=100)
        for v in range(50):
            bl.add(50.0 + (v % 5))
        is_anom, _ = bl.is_anomaly(52.0)
        assert is_anom is False

    def test_anomaly_beyond_3sigma(self):
        bl = SensorBaseline(window=100)
        # Build a stable baseline around 50
        for _ in range(30):
            bl.add(50.0)
            bl.add(51.0)
            bl.add(49.0)
        is_anom, confidence = bl.is_anomaly(200.0)
        assert is_anom is True
        assert confidence > 0

    def test_agent_detects_anomaly_event(self, event_simulator):
        agent = AnomalyDetectionAgent()
        host_id = uuid4()
        sensor_id = uuid4()
        # Feed baseline with some variance so std > MIN_STD
        baseline_metrics = []
        for i in range(40):
            val = 50.0 + (i % 5) - 2  # values 48..52
            baseline_metrics.append(
                event_simulator.generate_metric(
                    host_id=host_id, sensor_id=sensor_id, value=val,
                    timestamp=datetime.now(timezone.utc) - timedelta(minutes=40 - i),
                )
            )
        ctx = AgentContext(metrics=baseline_metrics)
        agent.process(ctx)

        # Now send anomalous value far from baseline
        anomalous = event_simulator.generate_metric(
            host_id=host_id, sensor_id=sensor_id, value=500.0,
        )
        ctx2 = AgentContext(metrics=[anomalous])
        result = agent.process(ctx2)
        assert result.success is True
        assert result.output["anomalies_detected"] >= 1

    def test_constant_values_no_false_positive(self):
        bl = SensorBaseline(window=100)
        for _ in range(50):
            bl.add(42.0)
        is_anom, _ = bl.is_anomaly(42.0)
        assert is_anom is False


# ---------------------------------------------------------------------------
# Pipeline resilience
# ---------------------------------------------------------------------------

class _FailingAgent(BaseAgent):
    def process(self, context: AgentContext) -> AgentResult:
        raise RuntimeError("boom")


class _OkAgent(BaseAgent):
    def process(self, context: AgentContext) -> AgentResult:
        return AgentResult(agent_name=self.name, success=True, output={"ok": True})


@pytest.mark.unit
class TestPipelineResilience:
    """Req 6.2 — agent failure doesn't stop others."""

    def test_failing_agent_does_not_stop_pipeline(self):
        agents = [_OkAgent(), _FailingAgent(), _OkAgent()]
        pipeline = AgentPipeline(agents)
        ctx = AgentContext()
        results = pipeline.run(ctx)
        assert len(results) == 3
        assert results[0].success is True
        assert results[1].success is False
        assert results[2].success is True

    def test_all_agents_succeed(self):
        agents = [_OkAgent(), _OkAgent()]
        pipeline = AgentPipeline(agents)
        results = pipeline.run(AgentContext())
        assert all(r.success for r in results)


# ---------------------------------------------------------------------------
# AutoRemediation
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestAutoRemediation:
    """Req 6.3 — only executes when confidence >= 85%."""

    def test_skips_below_threshold(self):
        agent = AutoRemediationAgent()
        ctx = AgentContext(
            pipeline_data={"should_alert": True, "decision_confidence": 0.50},
        )
        result = agent.process(ctx)
        assert result.success is True
        assert result.output["skipped"] is True

    def test_executes_at_threshold(self, event_simulator):
        agent = AutoRemediationAgent()
        host_id = uuid4()
        event = event_simulator.generate_event(
            host_id=host_id, event_type="high_cpu", severity=EventSeverity.CRITICAL,
        )
        ctx = AgentContext(
            events=[event],
            pipeline_data={"should_alert": True, "decision_confidence": 0.85},
        )
        result = agent.process(ctx)
        assert result.success is True
        assert result.output["skipped"] is False
        assert len(result.output["actions_executed"]) >= 1

    def test_skips_when_should_alert_false(self, event_simulator):
        agent = AutoRemediationAgent()
        event = event_simulator.generate_event(event_type="high_cpu")
        ctx = AgentContext(
            events=[event],
            pipeline_data={"should_alert": False, "decision_confidence": 0.95},
        )
        result = agent.process(ctx)
        assert result.output["skipped"] is True


# ---------------------------------------------------------------------------
# FeedbackLoop
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestFeedbackLoop:
    """Req 6.4, 6.7 — outcome classification and weight adjustment."""

    def test_positive_outcome_under_300s(self):
        fl = FeedbackLoop()
        action = RemediationAction(
            agent_name="test", action_type="restart_service", target_host="h1",
        )
        aid = fl.record_action(action)
        fl.record_result(aid, ActionResult(success=True, resolution_time_seconds=100.0))
        entry = fl._history[aid]
        assert entry["outcome"] == "positive"

    def test_negative_outcome_at_300s(self):
        fl = FeedbackLoop()
        action = RemediationAction(
            agent_name="test", action_type="restart_service", target_host="h1",
        )
        aid = fl.record_action(action)
        fl.record_result(aid, ActionResult(success=True, resolution_time_seconds=300.0))
        assert fl._history[aid]["outcome"] == "negative"

    def test_weight_increases_on_positive(self):
        fl = FeedbackLoop()
        action = RemediationAction(
            agent_name="test", action_type="clear_cache", target_host="h1",
        )
        initial_weight = fl.get_action_weight("clear_cache")
        aid = fl.record_action(action)
        fl.record_result(aid, ActionResult(success=True, resolution_time_seconds=60.0))
        assert fl.get_action_weight("clear_cache") > initial_weight

    def test_weight_decreases_on_negative(self):
        fl = FeedbackLoop()
        action = RemediationAction(
            agent_name="test", action_type="cleanup_logs", target_host="h1",
        )
        # First set a known weight
        fl._action_weights["cleanup_logs"] = 1.0
        aid = fl.record_action(action)
        fl.record_result(aid, ActionResult(success=False, resolution_time_seconds=600.0))
        assert fl.get_action_weight("cleanup_logs") < 1.0



# ---------------------------------------------------------------------------
# RootCause
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestRootCause:
    """Req 6.5 — parent node identification."""

    def test_identifies_parent_with_multiple_children_offline(self, topology_simulator, event_simulator):
        graph = topology_simulator.create_simple_topology(switches=1, servers_per_switch=3, services_per_server=0)
        nodes = graph.to_dict()["nodes"]
        switch_id = None
        server_ids = []
        for n in nodes:
            if n["type"] == "switch":
                switch_id = n["id"]
            elif n["type"] == "server":
                server_ids.append(n["id"])

        # Create events for 2+ children
        events = [
            event_simulator.generate_event(
                host_id=sid, event_type="host_down", severity=EventSeverity.CRITICAL,
            )
            for sid in server_ids[:2]
        ]
        engine = RootCauseEngine()
        result = engine.analyze(events, graph)
        assert result is not None
        assert result.root_node_id == switch_id
        assert result.confidence >= 0.5

    def test_no_topology_uses_oldest_event(self, event_simulator):
        engine = RootCauseEngine()
        now = datetime.now(timezone.utc)
        events = [
            event_simulator.generate_event(
                host_id=uuid4(), timestamp=now - timedelta(minutes=5),
            ),
            event_simulator.generate_event(
                host_id=uuid4(), timestamp=now,
            ),
        ]
        result = engine.analyze(events, None)
        assert result is not None
        assert result.root_node_id == str(events[0].host_id)


# ---------------------------------------------------------------------------
# CircuitBreaker
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestCircuitBreaker:
    """Req 6.6 — open after >50% failures, close after 5 min."""

    def test_stays_closed_with_successes(self):
        cb = CircuitBreaker(window=10)
        for _ in range(10):
            cb.record(True)
        assert cb.is_open() is False

    def test_opens_after_majority_failures(self):
        cb = CircuitBreaker(window=10)
        for _ in range(4):
            cb.record(True)
        for _ in range(6):
            cb.record(False)
        assert cb.is_open() is True

    def test_closes_after_timeout(self):
        cb = CircuitBreaker(window=10)
        for _ in range(10):
            cb.record(False)
        assert cb.is_open() is True
        # Simulate time passing and clear results so failure rate check doesn't re-open
        cb._open_until = time.monotonic() - 1
        cb._results.clear()
        assert cb.is_open() is False

    def test_reset_clears_state(self):
        cb = CircuitBreaker(window=10)
        for _ in range(10):
            cb.record(False)
        cb.reset()
        assert cb.is_open() is False


# ---------------------------------------------------------------------------
# Correlation — 5-min window
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestCorrelation:
    """Req 6.8 — events within 5-min window grouped by host."""

    def test_same_host_within_window_grouped(self, event_simulator):
        agent = CorrelationAgent()
        host_id = uuid4()
        now = datetime.now(timezone.utc)
        events = [
            event_simulator.generate_event(host_id=host_id, timestamp=now),
            event_simulator.generate_event(host_id=host_id, timestamp=now + timedelta(minutes=2)),
            event_simulator.generate_event(host_id=host_id, timestamp=now + timedelta(minutes=4)),
        ]
        ctx = AgentContext(events=events)
        result = agent.process(ctx)
        assert result.success is True
        groups = result.output["correlated_groups"]
        assert len(groups) == 1
        assert groups[0]["event_count"] == 3

    def test_different_hosts_separate_groups(self, event_simulator):
        agent = CorrelationAgent()
        now = datetime.now(timezone.utc)
        events = [
            event_simulator.generate_event(host_id=uuid4(), timestamp=now),
            event_simulator.generate_event(host_id=uuid4(), timestamp=now),
        ]
        ctx = AgentContext(events=events)
        result = agent.process(ctx)
        groups = result.output["correlated_groups"]
        assert len(groups) == 2

    def test_events_outside_window_split(self, event_simulator):
        agent = CorrelationAgent()
        host_id = uuid4()
        now = datetime.now(timezone.utc)
        events = [
            event_simulator.generate_event(host_id=host_id, timestamp=now),
            event_simulator.generate_event(host_id=host_id, timestamp=now + timedelta(minutes=6)),
        ]
        ctx = AgentContext(events=events)
        result = agent.process(ctx)
        groups = result.output["correlated_groups"]
        assert len(groups) == 2
