"""
AI: Correlation Tests — Coruja Monitor v3.0
Tests: temporal correlation within 5min window.
Requirements: 6.8
"""
import pytest
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from ai_agents.correlation import CorrelationAgent, CORRELATION_WINDOW_MINUTES
from ai_agents.base_agent import AgentContext
from core.spec.enums import EventSeverity
from core.spec.models import Event


@pytest.mark.ai
class TestCorrelation:
    """Req 6.8 — correlation within 5min window."""

    def test_same_host_within_window_grouped(self):
        agent = CorrelationAgent()
        host_id = uuid4()
        now = datetime.now(timezone.utc)
        events = [
            Event(host_id=host_id, type="cpu", severity=EventSeverity.WARNING, timestamp=now),
            Event(host_id=host_id, type="mem", severity=EventSeverity.WARNING, timestamp=now + timedelta(minutes=2)),
        ]
        ctx = AgentContext(events=events, metrics=[], topology=None)
        result = agent.process(ctx)
        assert result.success
        assert result.output["total_groups"] == 1

    def test_different_hosts_separate_groups(self):
        agent = CorrelationAgent()
        now = datetime.now(timezone.utc)
        events = [
            Event(host_id=uuid4(), type="cpu", severity=EventSeverity.WARNING, timestamp=now),
            Event(host_id=uuid4(), type="cpu", severity=EventSeverity.WARNING, timestamp=now),
        ]
        ctx = AgentContext(events=events, metrics=[], topology=None)
        result = agent.process(ctx)
        assert result.success
        assert result.output["total_groups"] == 2

    def test_events_outside_window_separate(self):
        agent = CorrelationAgent()
        host_id = uuid4()
        now = datetime.now(timezone.utc)
        events = [
            Event(host_id=host_id, type="cpu", severity=EventSeverity.WARNING, timestamp=now),
            Event(host_id=host_id, type="cpu", severity=EventSeverity.WARNING, timestamp=now + timedelta(minutes=10)),
        ]
        ctx = AgentContext(events=events, metrics=[], topology=None)
        result = agent.process(ctx)
        assert result.success
        assert result.output["total_groups"] == 2

    def test_empty_events(self):
        agent = CorrelationAgent()
        ctx = AgentContext(events=[], metrics=[], topology=None)
        result = agent.process(ctx)
        assert result.success
        assert result.output["correlated_groups"] == []
