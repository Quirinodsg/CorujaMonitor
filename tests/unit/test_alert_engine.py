"""
Unit tests for Alert Engine — Coruja Monitor v3.0
Tests: duplicate suppression, event grouping, prioritization,
       flood protection, notifier retry, topology suppression, maintenance windows.
Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7
"""
import time
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from alert_engine.engine import AlertEngine, FLOOD_THRESHOLD
from alert_engine.grouper import EventGrouper, GROUPING_WINDOW_MINUTES
from alert_engine.notifier import AlertNotifier, MAX_RETRIES
from alert_engine.prioritizer import AlertPrioritizer, W_SEVERITY, W_HOSTS, W_CRITICAL_SERVICES, W_BUSINESS_HOURS
from alert_engine.suppressor import DuplicateSuppressor, SUPPRESSION_TTL_SECONDS
from core.spec.enums import AlertStatus, EventSeverity
from core.spec.models import Alert, Event


# ---------------------------------------------------------------------------
# Duplicate Suppression (TTL 5 min)
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestDuplicateSuppression:
    """Req 7.1 — same (host_id, type, severity) within 5 min → suppressed."""

    def test_first_event_not_duplicate(self, event_simulator):
        sup = DuplicateSuppressor()
        ev = event_simulator.generate_event()
        assert sup.is_duplicate(ev) is False

    def test_second_identical_event_is_duplicate(self, event_simulator):
        sup = DuplicateSuppressor()
        host_id = uuid4()
        ev = event_simulator.generate_event(host_id=host_id, event_type="cpu_high", severity=EventSeverity.CRITICAL)
        sup.mark_seen(ev)
        ev2 = event_simulator.generate_event(host_id=host_id, event_type="cpu_high", severity=EventSeverity.CRITICAL)
        assert sup.is_duplicate(ev2) is True

    def test_different_type_not_duplicate(self, event_simulator):
        sup = DuplicateSuppressor()
        host_id = uuid4()
        ev1 = event_simulator.generate_event(host_id=host_id, event_type="cpu_high")
        sup.mark_seen(ev1)
        ev2 = event_simulator.generate_event(host_id=host_id, event_type="disk_full")
        assert sup.is_duplicate(ev2) is False

    def test_clear_resets_cache(self, event_simulator):
        sup = DuplicateSuppressor()
        ev = event_simulator.generate_event()
        sup.mark_seen(ev)
        sup.clear()
        assert sup.is_duplicate(ev) is False


# ---------------------------------------------------------------------------
# Event Grouping (host + 5-min window)
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestEventGrouping:
    """Req 7.2 — events from same host within 5-min window grouped."""

    def test_same_host_within_window(self, event_simulator):
        grouper = EventGrouper()
        host_id = uuid4()
        now = datetime.now(timezone.utc)
        events = [
            event_simulator.generate_event(host_id=host_id, timestamp=now),
            event_simulator.generate_event(host_id=host_id, timestamp=now + timedelta(minutes=2)),
            event_simulator.generate_event(host_id=host_id, timestamp=now + timedelta(minutes=4)),
        ]
        groups = grouper.group(events)
        assert len(groups) == 1
        assert len(groups[0]) == 3

    def test_different_hosts_separate_groups(self, event_simulator):
        grouper = EventGrouper()
        now = datetime.now(timezone.utc)
        events = [
            event_simulator.generate_event(host_id=uuid4(), timestamp=now),
            event_simulator.generate_event(host_id=uuid4(), timestamp=now),
        ]
        groups = grouper.group(events)
        assert len(groups) == 2

    def test_events_outside_window_split(self, event_simulator):
        grouper = EventGrouper()
        host_id = uuid4()
        now = datetime.now(timezone.utc)
        events = [
            event_simulator.generate_event(host_id=host_id, timestamp=now),
            event_simulator.generate_event(host_id=host_id, timestamp=now + timedelta(minutes=6)),
        ]
        groups = grouper.group(events)
        assert len(groups) == 2

    def test_empty_events(self):
        grouper = EventGrouper()
        assert grouper.group([]) == []


# ---------------------------------------------------------------------------
# Prioritization (score formula with 4 factors)
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestPrioritization:
    """Req 7.3 — score = sev*0.40 + hosts*0.30 + impact*0.20 + hours*0.10, in [0,1]."""

    def test_score_in_range(self):
        pri = AlertPrioritizer()
        alert = Alert(
            title="test", severity=EventSeverity.CRITICAL,
            affected_hosts=[uuid4(), uuid4()],
        )
        score = pri.score(alert)
        assert 0.0 <= score <= 1.0

    def test_critical_higher_than_info(self):
        pri = AlertPrioritizer()
        crit = Alert(title="c", severity=EventSeverity.CRITICAL, affected_hosts=[uuid4()])
        info = Alert(title="i", severity=EventSeverity.INFO, affected_hosts=[uuid4()])
        assert pri.score(crit) > pri.score(info)

    def test_more_hosts_higher_score(self):
        pri = AlertPrioritizer()
        many = Alert(title="m", severity=EventSeverity.WARNING, affected_hosts=[uuid4() for _ in range(50)])
        few = Alert(title="f", severity=EventSeverity.WARNING, affected_hosts=[uuid4()])
        assert pri.score(many) > pri.score(few)

    def test_critical_services_factor(self):
        pri = AlertPrioritizer()
        alert = Alert(title="t", severity=EventSeverity.WARNING, affected_hosts=[uuid4()])
        score_no_crit = pri.score(alert, context={"critical_services_count": 0})
        score_with_crit = pri.score(alert, context={"critical_services_count": 5})
        assert score_with_crit > score_no_crit



# ---------------------------------------------------------------------------
# Flood Protection (>100 events/min)
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestFloodProtection:
    """Req 7.4 — >100 events/min from same host → 1 consolidated alert."""

    def test_flood_triggers_single_alert(self, event_simulator):
        engine = AlertEngine()
        host_id = uuid4()
        events = event_simulator.generate_flood(host_id=host_id, count=150, window_seconds=60)
        alerts = engine.process_events(events)
        assert len(alerts) == 1
        assert alerts[0].severity in (EventSeverity.CRITICAL.value, EventSeverity.CRITICAL)
        assert alerts[0].root_cause == "flood_protection"

    def test_below_threshold_no_flood(self, event_simulator):
        engine = AlertEngine()
        host_id = uuid4()
        now = datetime.now(timezone.utc)
        events = [
            event_simulator.generate_event(host_id=host_id, event_type="cpu_warn", timestamp=now + timedelta(seconds=i))
            for i in range(5)
        ]
        alerts = engine.process_events(events)
        # Should create normal alerts, not flood
        for a in alerts:
            assert a.root_cause != "flood_protection"


# ---------------------------------------------------------------------------
# Notifier retry 3x backoff
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestNotifierRetry:
    """Req 7.5 — retry 3x with exponential backoff."""

    def test_success_on_first_try(self):
        notifier = AlertNotifier()
        alert = Alert(title="t", severity=EventSeverity.WARNING, affected_hosts=[uuid4()])
        results = notifier.notify(alert, ["email"])
        assert results["email"] is True

    def test_retry_on_failure(self):
        notifier = AlertNotifier(channels_config={"webhook": {"url": "https://example.com/hook"}})
        alert = Alert(title="t", severity=EventSeverity.CRITICAL, affected_hosts=[uuid4()])
        # Mock _send to fail then succeed
        call_count = 0
        original_send = notifier._send

        def flaky_send(a, channel):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("timeout")
            return True

        notifier._send = flaky_send
        with patch("alert_engine.notifier.time.sleep"):
            result = notifier._notify_with_retry(alert, "webhook")
        assert result is True
        assert call_count == 3

    def test_all_retries_fail(self):
        notifier = AlertNotifier()
        alert = Alert(title="t", severity=EventSeverity.WARNING, affected_hosts=[uuid4()])

        def always_fail(a, channel):
            raise ConnectionError("down")

        notifier._send = always_fail
        with patch("alert_engine.notifier.time.sleep"):
            result = notifier._notify_with_retry(alert, "webhook")
        assert result is False


# ---------------------------------------------------------------------------
# Topology Suppression
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestTopologySuppression:
    """Req 7.6 — parent in failure → children suppressed."""

    def test_children_suppressed_when_parent_failed(self, event_simulator):
        engine = AlertEngine()
        child1 = uuid4()
        child2 = uuid4()
        engine.set_topology({str(child1): "switch-core", str(child2): "switch-core"})
        engine.mark_host_failed("switch-core")

        events = [
            event_simulator.generate_event(host_id=child1, event_type="cpu_high"),
            event_simulator.generate_event(host_id=child2, event_type="disk_full"),
        ]
        alerts = engine.process_events(events)
        assert len(alerts) == 0

    def test_no_suppression_without_parent_failure(self, event_simulator):
        engine = AlertEngine()
        engine.set_topology({"server-01": "switch-core"})
        # switch-core NOT marked as failed
        host_id = uuid4()
        events = [event_simulator.generate_event(host_id=host_id, event_type="cpu_high", severity=EventSeverity.CRITICAL)]
        alerts = engine.process_events(events)
        assert len(alerts) >= 1


# ---------------------------------------------------------------------------
# Maintenance Windows
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestMaintenanceWindows:
    """Req 7.7 — events from hosts in active maintenance filtered."""

    def test_events_filtered_during_maintenance(self, event_simulator):
        engine = AlertEngine()
        host_id = uuid4()
        now = datetime.now(timezone.utc)
        engine.set_maintenance_window(
            str(host_id),
            now - timedelta(hours=1),
            now + timedelta(hours=1),
        )
        events = [event_simulator.generate_event(host_id=host_id, event_type="cpu_high")]
        alerts = engine.process_events(events)
        assert len(alerts) == 0

    def test_events_pass_outside_maintenance(self, event_simulator):
        engine = AlertEngine()
        host_id = uuid4()
        now = datetime.now(timezone.utc)
        engine.set_maintenance_window(
            str(host_id),
            now - timedelta(hours=3),
            now - timedelta(hours=1),  # already ended
        )
        events = [event_simulator.generate_event(host_id=host_id, event_type="cpu_high", severity=EventSeverity.CRITICAL)]
        alerts = engine.process_events(events)
        assert len(alerts) >= 1
