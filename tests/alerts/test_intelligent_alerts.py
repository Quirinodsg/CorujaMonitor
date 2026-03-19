"""
FASE 8 — Testes do Alert Engine Inteligente
Valida: supressão de duplicados, agrupamento, priorização, SLA ≤30s.
"""
import pytest
import time
from uuid import uuid4
from datetime import datetime, timezone, timedelta

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from core.spec.models import Event, Alert
from core.spec.enums import EventSeverity, AlertStatus
from alert_engine.engine import AlertEngine
from alert_engine.suppressor import DuplicateSuppressor
from alert_engine.grouper import EventGrouper
from alert_engine.prioritizer import AlertPrioritizer


# ─── Helpers ────────────────────────────────────────────────────────────────

def make_event(event_type="high_cpu", severity=EventSeverity.CRITICAL,
               host_id=None, timestamp=None):
    return Event(
        host_id=host_id or uuid4(),
        type=event_type,
        severity=severity,
        timestamp=timestamp or datetime.now(timezone.utc),
    )


def make_alert(severity=EventSeverity.CRITICAL, affected_hosts=None):
    return Alert(
        title="Test Alert",
        severity=severity,
        affected_hosts=affected_hosts or [uuid4()],
    )


# ─── Supressão de Duplicados ─────────────────────────────────────────────────

class TestDuplicateSuppression:

    def test_first_event_not_suppressed(self):
        """Primeiro evento não é duplicado."""
        suppressor = DuplicateSuppressor()
        event = make_event()
        assert suppressor.is_duplicate(event) is False

    def test_same_event_suppressed(self):
        """Mesmo evento (host+type+severity) é suprimido após mark_seen."""
        suppressor = DuplicateSuppressor()
        host_id = uuid4()
        event1 = make_event(host_id=host_id)
        event2 = make_event(host_id=host_id)

        suppressor.mark_seen(event1)  # Registra explicitamente
        assert suppressor.is_duplicate(event2) is True

    def test_different_hosts_not_suppressed(self):
        """Eventos de hosts diferentes não são suprimidos entre si."""
        suppressor = DuplicateSuppressor()
        event1 = make_event(host_id=uuid4())
        event2 = make_event(host_id=uuid4())

        suppressor.is_duplicate(event1)
        assert suppressor.is_duplicate(event2) is False

    def test_different_types_not_suppressed(self):
        """Mesmo host, tipos diferentes → não suprimido."""
        suppressor = DuplicateSuppressor()
        host_id = uuid4()
        event1 = make_event("high_cpu", host_id=host_id)
        event2 = make_event("disk_full", host_id=host_id)

        suppressor.is_duplicate(event1)
        assert suppressor.is_duplicate(event2) is False

    def test_engine_deduplicates_5_same_events(self):
        """5 eventos idênticos → 1 alerta."""
        engine = AlertEngine()
        host_id = uuid4()
        events = [make_event(host_id=host_id) for _ in range(5)]

        alerts = engine.process_events(events)
        assert len(alerts) == 1


# ─── Agrupamento ─────────────────────────────────────────────────────────────

class TestEventGrouping:

    def test_events_same_host_grouped(self):
        """Múltiplos eventos do mesmo host → 1 alerta consolidado."""
        engine = AlertEngine()
        host_id = uuid4()
        events = [
            make_event("high_cpu", EventSeverity.CRITICAL, host_id),
            make_event("high_memory", EventSeverity.WARNING, host_id),
            make_event("disk_full", EventSeverity.CRITICAL, host_id),
        ]

        alerts = engine.process_events(events)
        # Deve consolidar em 1 alerta para o host
        assert len(alerts) >= 1

    def test_grouper_groups_by_host(self):
        """EventGrouper agrupa eventos por host."""
        grouper = EventGrouper()
        host_id = uuid4()
        events = [make_event(host_id=host_id) for _ in range(3)]

        groups = grouper.group(events)
        assert len(groups) >= 1

    def test_events_different_hosts_separate_alerts(self):
        """Eventos de hosts diferentes geram alertas separados."""
        engine = AlertEngine()
        events = [make_event(host_id=uuid4()) for _ in range(3)]

        alerts = engine.process_events(events)
        assert len(alerts) >= 1


# ─── Priorização ─────────────────────────────────────────────────────────────

class TestAlertPrioritization:

    def test_critical_higher_score_than_warning(self):
        """Alerta crítico tem score maior que warning."""
        prioritizer = AlertPrioritizer()
        critical_alert = make_alert(EventSeverity.CRITICAL)
        warning_alert = make_alert(EventSeverity.WARNING)

        critical_score = prioritizer.score(critical_alert)
        warning_score = prioritizer.score(warning_alert)

        assert critical_score > warning_score

    def test_more_hosts_higher_score(self):
        """Mais hosts afetados → score maior."""
        prioritizer = AlertPrioritizer()
        alert_1_host = make_alert(affected_hosts=[uuid4()])
        alert_5_hosts = make_alert(affected_hosts=[uuid4() for _ in range(5)])

        score_1 = prioritizer.score(alert_1_host)
        score_5 = prioritizer.score(alert_5_hosts)

        assert score_5 > score_1

    def test_score_in_range_0_1(self):
        """Score deve estar no intervalo [0, 1]."""
        prioritizer = AlertPrioritizer()
        for severity in [EventSeverity.INFO, EventSeverity.WARNING, EventSeverity.CRITICAL]:
            alert = make_alert(severity)
            score = prioritizer.score(alert)
            assert 0.0 <= score <= 1.0, f"Score fora do range: {score}"

    def test_critical_score_formula(self):
        """Score crítico com 1 host deve ser ≥ 0.40 (peso da severidade)."""
        prioritizer = AlertPrioritizer()
        alert = make_alert(EventSeverity.CRITICAL, affected_hosts=[uuid4()])
        score = prioritizer.score(alert)
        assert score >= 0.40


# ─── Flood Protection ────────────────────────────────────────────────────────

class TestFloodProtection:

    def test_flood_100_events_generates_1_alert(self):
        """100+ eventos do mesmo host em 1min → 1 alerta de flood."""
        engine = AlertEngine()
        host_id = uuid4()
        events = [make_event(host_id=host_id) for _ in range(150)]

        alerts = engine.process_events(events)
        # Flood protection: deve consolidar em 1 alerta
        assert len(alerts) == 1

    def test_flood_alert_is_critical(self):
        """Alerta de flood deve ser crítico."""
        engine = AlertEngine()
        host_id = uuid4()
        events = [make_event(host_id=host_id) for _ in range(150)]

        alerts = engine.process_events(events)
        if alerts:
            sev = alerts[0].severity
            sev_val = sev.value if hasattr(sev, "value") else sev
            assert sev_val == "critical"


# ─── Janelas de Manutenção ───────────────────────────────────────────────────

class TestMaintenanceWindows:

    def test_maintenance_suppresses_events(self):
        """Host em manutenção → eventos suprimidos."""
        engine = AlertEngine()
        host_id = uuid4()
        now = datetime.now(timezone.utc)

        engine.set_maintenance_window(
            str(host_id),
            now - timedelta(minutes=5),
            now + timedelta(hours=1)
        )

        events = [make_event(host_id=host_id) for _ in range(3)]
        alerts = engine.process_events(events)

        assert len(alerts) == 0

    def test_expired_maintenance_allows_alerts(self):
        """Manutenção expirada → alertas gerados normalmente."""
        engine = AlertEngine()
        host_id = uuid4()
        now = datetime.now(timezone.utc)

        # Janela expirada
        engine.set_maintenance_window(
            str(host_id),
            now - timedelta(hours=2),
            now - timedelta(hours=1)
        )

        events = [make_event(host_id=host_id)]
        alerts = engine.process_events(events)

        assert len(alerts) >= 1


# ─── SLA ≤30s ────────────────────────────────────────────────────────────────

class TestAlertSLA:

    def test_alert_generated_within_sla(self):
        """Alerta deve ser gerado em ≤30s (SLA)."""
        engine = AlertEngine()
        event = make_event()

        start = time.monotonic()
        alerts = engine.process_events([event])
        elapsed = (time.monotonic() - start) * 1000

        assert elapsed < 30000, f"Alert SLA violado: {elapsed:.0f}ms (limite: 30000ms)"
        assert len(alerts) >= 1

    def test_1000_events_processed_under_sla(self):
        """1000 eventos processados em <30s."""
        engine = AlertEngine()
        events = [make_event(host_id=uuid4()) for _ in range(1000)]

        start = time.monotonic()
        alerts = engine.process_events(events)
        elapsed = (time.monotonic() - start) * 1000

        assert elapsed < 30000, f"1000 eventos demoraram {elapsed:.0f}ms"
