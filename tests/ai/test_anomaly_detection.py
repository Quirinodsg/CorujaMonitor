"""
AI: Anomaly Detection Tests — Coruja Monitor v3.0
Tests: baseline, >3σ detection.
Requirements: 6.1
"""
import pytest
from datetime import datetime, timezone
from uuid import uuid4

from ai_agents.anomaly_detection import AnomalyDetectionAgent, SensorBaseline, ANOMALY_THRESHOLD_SIGMA
from ai_agents.base_agent import AgentContext
from core.spec.models import Metric


@pytest.mark.ai
class TestAnomalyDetection:
    """Req 6.1 — anomaly detection via Z-score >3σ."""

    def test_baseline_accumulates(self):
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
        for _ in range(50):
            bl.add(50.0)
        bl.add(51.0)  # add slight variation for non-zero std
        is_anom, confidence = bl.is_anomaly(200.0)
        assert is_anom is True
        assert confidence > 0

    def test_agent_processes_metrics(self):
        agent = AnomalyDetectionAgent()
        host_id = uuid4()
        sensor_id = uuid4()
        metrics = [
            Metric(sensor_id=sensor_id, host_id=host_id, value=50.0,
                   unit="%", timestamp=datetime.now(timezone.utc))
        ]
        ctx = AgentContext(events=[], metrics=metrics, topology=None)
        result = agent.process(ctx)
        assert result.success is True

    def test_constant_values_no_false_positive(self):
        """Constant values should not trigger anomaly (std=0)."""
        bl = SensorBaseline(window=100)
        for _ in range(50):
            bl.add(50.0)
        is_anom, _ = bl.is_anomaly(50.0)
        assert is_anom is False
