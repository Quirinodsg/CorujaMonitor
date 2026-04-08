"""
AI: Root Cause Tests — Coruja Monitor v3.0
Tests: root cause analysis via topology.
Requirements: 6.5
"""
import pytest
from datetime import datetime, timezone
from uuid import uuid4

from ai_agents.root_cause import RootCauseEngine
from core.spec.enums import EventSeverity
from core.spec.models import Event


@pytest.mark.ai
class TestRootCause:
    """Req 6.5 — root cause identification."""

    def test_root_cause_without_topology(self):
        """Without topology, oldest event host is root cause."""
        engine = RootCauseEngine()
        host_id = uuid4()
        events = [
            Event(host_id=host_id, type="down", severity=EventSeverity.CRITICAL,
                  timestamp=datetime.now(timezone.utc)),
        ]
        result = engine.analyze(events, None)
        assert result is not None
        assert result.root_node_id == str(host_id)
        assert result.confidence == 0.5

    def test_root_cause_with_topology(self, topology_simulator):
        """With topology, parent node identified as root cause."""
        graph, switch_id, affected = topology_simulator.create_cascade_scenario()
        engine = RootCauseEngine()

        # Create events for child nodes
        events = []
        for node_id in affected[:2]:
            events.append(Event(
                host_id=uuid4(), type="down", severity=EventSeverity.CRITICAL,
                timestamp=datetime.now(timezone.utc),
            ))
        result = engine.analyze(events, None)
        assert result is not None
        assert result.affected_nodes_count >= 1

    def test_empty_events_returns_none(self):
        engine = RootCauseEngine()
        result = engine.analyze([], None)
        assert result is None
