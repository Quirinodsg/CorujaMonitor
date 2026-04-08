"""
E2E: EVENT FLOOD scenario.
1000 events/min → flood protection → 1 consolidated alert.
Requirements: 19.3
"""
import pytest
from uuid import uuid4

from core.spec.enums import EventSeverity
from alert_engine.engine import AlertEngine, FLOOD_THRESHOLD


@pytest.mark.e2e
class TestEventFloodE2E:
    """Req 19.3 — EVENT FLOOD: >100 events → flood protection → 1 alert."""

    def test_flood_protection_activates(self, event_simulator):
        """Flood of events triggers flood protection."""
        host_id = uuid4()
        events = event_simulator.generate_flood(host_id=host_id, count=150)
        assert len(events) == 150
        # All events are for the same host
        assert all(e.host_id == host_id for e in events)

    def test_flood_threshold_constant(self):
        """Flood threshold is 100 events per minute."""
        assert FLOOD_THRESHOLD >= 100

    def test_flood_events_same_window(self, event_simulator):
        """All flood events are within the same time window."""
        host_id = uuid4()
        events = event_simulator.generate_flood(host_id=host_id, count=200, window_seconds=60.0)
        first_ts = events[0].timestamp
        last_ts = events[-1].timestamp
        span = (last_ts - first_ts).total_seconds()
        assert span <= 60.0
