"""
Chaos: Event Flood Tests — Coruja Monitor v3.0
Tests: event flood simulation.
Requirements: 14.4, 14.6
"""
import pytest
from uuid import uuid4

from core.spec.enums import EventSeverity


@pytest.mark.chaos
class TestEventFloodChaos:
    """Req 14.4, 14.6 — event flood chaos simulation."""

    def test_flood_generates_many_events(self, event_simulator):
        """Flood generates specified number of events."""
        host_id = uuid4()
        events = event_simulator.generate_flood(host_id=host_id, count=1000)
        assert len(events) == 1000

    def test_flood_events_within_window(self, event_simulator):
        """All flood events are within the specified time window."""
        host_id = uuid4()
        events = event_simulator.generate_flood(host_id=host_id, count=500, window_seconds=60.0)
        first = events[0].timestamp
        last = events[-1].timestamp
        span = (last - first).total_seconds()
        assert span <= 60.0

    def test_flood_all_critical(self, event_simulator):
        """Flood events are all CRITICAL severity."""
        host_id = uuid4()
        events = event_simulator.generate_flood(host_id=host_id, count=50)
        assert all(e.severity == EventSeverity.CRITICAL for e in events)
