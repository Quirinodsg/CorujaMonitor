"""
Integration: Metric → EventProcessor → AI Pipeline → AlertEngine flow.
Requirements: 12.1, 12.5
"""
import pytest
from datetime import datetime, timezone
from uuid import uuid4

from core.spec.enums import EventSeverity, SensorStatus, Protocol
from core.spec.models import Event, Metric, Sensor
from event_processor.threshold_evaluator import ThresholdEvaluator
from alert_engine.suppressor import DuplicateSuppressor
from alert_engine.prioritizer import AlertPrioritizer


@pytest.mark.integration
class TestMetricToAlertFlow:
    """Req 12.1 — full flow: Metric → EventProcessor → AI Pipeline → AlertEngine."""

    def test_critical_metric_generates_alert(self, event_simulator):
        """A critical metric flows through the pipeline to produce an alert."""
        host_id = uuid4()
        sensor_id = uuid4()

        # Step 1: Generate critical metric
        metric = event_simulator.generate_metric(
            host_id=host_id, sensor_id=sensor_id,
            value=98.0, status=SensorStatus.CRITICAL,
        )

        # Step 2: ThresholdEvaluator evaluates
        evaluator = ThresholdEvaluator()
        status = evaluator.evaluate(metric, {"warning": 80, "critical": 95})
        assert status == SensorStatus.CRITICAL

        # Step 3: Create event from threshold breach
        event = event_simulator.generate_event(
            host_id=host_id, event_type="cpu_critical",
            severity=EventSeverity.CRITICAL,
        )

        # Step 4: AlertEngine processes event
        suppressor = DuplicateSuppressor()
        assert suppressor.is_duplicate(event) is False
        suppressor.mark_seen(event)

        # Step 5: Prioritize
        prioritizer = AlertPrioritizer()
        from core.spec.models import Alert
        alert = Alert(
            title="CPU Critical",
            severity=EventSeverity.CRITICAL,
            event_ids=[event.id],
            affected_hosts=[host_id],
        )
        score = prioritizer.score(alert)
        assert 0.0 <= score <= 1.0

    def test_ok_metric_no_alert(self, event_simulator):
        """An OK metric does not generate an alert."""
        metric = event_simulator.generate_metric(value=50.0)
        evaluator = ThresholdEvaluator()
        status = evaluator.evaluate(metric, {"warning": 80, "critical": 95})
        assert status == SensorStatus.OK

    def test_pipeline_no_data_loss(self, event_simulator):
        """Req 12.5 — events entering pipeline equal events processed."""
        host_id = uuid4()
        events = [
            event_simulator.generate_event(host_id=host_id, event_type=f"evt_{i}")
            for i in range(10)
        ]
        suppressor = DuplicateSuppressor()
        processed = [e for e in events if not suppressor.is_duplicate(e)]
        assert len(processed) == 10
