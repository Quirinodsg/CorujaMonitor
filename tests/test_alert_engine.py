"""
Testes da Fase 8 — Alert Engine
Cobre: Property 13 (alerta consolidado único), Property 14 (supressão duplicados),
       Property 15 (score ponderado), Property 16 (flood protection),
       Property 17 (supressão em manutenção)
"""
import pytest
from uuid import uuid4
from datetime import datetime, timezone, timedelta

from core.spec.models import Event, Alert
from core.spec.enums import EventSeverity, AlertStatus
from alert_engine.suppressor import DuplicateSuppressor
from alert_engine.grouper import EventGrouper
from alert_engine.prioritizer import AlertPrioritizer
from alert_engine.engine import AlertEngine


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Property 14: DuplicateSuppressor — idempotência
# ---------------------------------------------------------------------------

class TestDuplicateSuppressor:
    def test_first_event_not_duplicate(self):
        suppressor = DuplicateSuppressor()
        event = make_event()
        assert suppressor.is_duplicate(event) is False

    def test_second_same_event_is_duplicate(self):
        """Property 14: mesmo (host_id, type, severity) → duplicado."""
        suppressor = DuplicateSuppressor()
        host_id = uuid4()
        event1 = make_event(host_id=host_id)
        event2 = make_event(host_id=host_id)  # mesmo host, tipo, severidade

        suppressor.mark_seen(event1)
        assert suppressor.is_duplicate(event2) is True

    def test_different_host_not_duplicate(self):
        suppressor = DuplicateSuppressor()
        event1 = make_event(host_id=uuid4())
        event2 = make_event(host_id=uuid4())

        suppressor.mark_seen(event1)
        assert suppressor.is_duplicate(event2) is False

    def test_different_type_not_duplicate(self):
        suppressor = DuplicateSuppressor()
        host_id = uuid4()
        event1 = make_event("high_cpu", host_id=host_id)
        event2 = make_event("low_memory", host_id=host_id)

        suppressor.mark_seen(event1)
        assert suppressor.is_duplicate(event2) is False

    def test_different_severity_not_duplicate(self):
        suppressor = DuplicateSuppressor()
        host_id = uuid4()
        event1 = make_event(severity=EventSeverity.WARNING, host_id=host_id)
        event2 = make_event(severity=EventSeverity.CRITICAL, host_id=host_id)

        suppressor.mark_seen(event1)
        assert suppressor.is_duplicate(event2) is False

    def test_clear_resets_cache(self):
        suppressor = DuplicateSuppressor()
        event = make_event()
        suppressor.mark_seen(event)
        suppressor.clear()
        assert suppressor.is_duplicate(event) is False

    def test_expired_ttl_not_duplicate(self):
        """TTL=0 → expira imediatamente."""
        suppressor = DuplicateSuppressor(ttl=0)
        event = make_event()
        suppressor.mark_seen(event)
        import time; time.sleep(0.01)
        assert suppressor.is_duplicate(event) is False


# ---------------------------------------------------------------------------
# EventGrouper
# ---------------------------------------------------------------------------

class TestEventGrouper:
    def test_same_host_same_window_grouped(self):
        grouper = EventGrouper()
        host_id = uuid4()
        now = datetime.now(timezone.utc)
        events = [
            make_event(host_id=host_id, timestamp=now),
            make_event(host_id=host_id, timestamp=now + timedelta(minutes=2)),
            make_event(host_id=host_id, timestamp=now + timedelta(minutes=4)),
        ]
        groups = grouper.group(events)
        assert len(groups) == 1
        assert len(groups[0]) == 3

    def test_same_host_different_windows_separate_groups(self):
        grouper = EventGrouper()
        host_id = uuid4()
        now = datetime.now(timezone.utc)
        events = [
            make_event(host_id=host_id, timestamp=now),
            make_event(host_id=host_id, timestamp=now + timedelta(minutes=10)),
        ]
        groups = grouper.group(events)
        assert len(groups) == 2

    def test_different_hosts_separate_groups(self):
        grouper = EventGrouper()
        now = datetime.now(timezone.utc)
        events = [
            make_event(host_id=uuid4(), timestamp=now),
            make_event(host_id=uuid4(), timestamp=now),
        ]
        groups = grouper.group(events)
        assert len(groups) == 2

    def test_empty_events(self):
        grouper = EventGrouper()
        assert grouper.group([]) == []


# ---------------------------------------------------------------------------
# Property 15: Score de prioridade respeita fórmula ponderada
# ---------------------------------------------------------------------------

class TestAlertPrioritizer:
    def test_critical_alert_high_score(self):
        """Property 15: alerta crítico deve ter score alto."""
        prioritizer = AlertPrioritizer()
        alert = make_alert(severity=EventSeverity.CRITICAL, affected_hosts=[uuid4()] * 5)
        score = prioritizer.score(alert)
        assert 0.0 <= score <= 1.0
        assert score > 0.3  # crítico deve ter score relevante

    def test_info_alert_low_score(self):
        prioritizer = AlertPrioritizer()
        alert = make_alert(severity=EventSeverity.INFO, affected_hosts=[uuid4()])
        score = prioritizer.score(alert)
        assert 0.0 <= score <= 1.0

    def test_score_formula_components(self):
        """Property 15: verificar que score respeita fórmula ponderada."""
        prioritizer = AlertPrioritizer()
        # Alerta crítico, 10 hosts, sem serviços críticos
        alert = make_alert(severity=EventSeverity.CRITICAL, affected_hosts=[uuid4()] * 10)
        score = prioritizer.score(alert, context={"max_hosts_reference": 100})

        # severity=1.0 × 0.40 = 0.40
        # hosts=10/100=0.10 × 0.30 = 0.03
        # critical_services=0 × 0.20 = 0.0
        # business_hours ∈ {0.3, 1.0} × 0.10
        # score ∈ [0.43, 0.50]
        assert 0.40 <= score <= 0.55

    def test_score_in_valid_range(self):
        """Score sempre entre 0 e 1."""
        prioritizer = AlertPrioritizer()
        for severity in [EventSeverity.INFO, EventSeverity.WARNING, EventSeverity.CRITICAL]:
            for n_hosts in [0, 1, 10, 100]:
                alert = make_alert(severity=severity, affected_hosts=[uuid4()] * n_hosts)
                score = prioritizer.score(alert)
                assert 0.0 <= score <= 1.0, f"Score fora do range: {score}"


# ---------------------------------------------------------------------------
# Property 16: Flood protection
# ---------------------------------------------------------------------------

class TestFloodProtection:
    def test_flood_protection_triggers_single_alert(self):
        """Property 16: > 100 eventos/min → 1 alerta de alta prioridade."""
        engine = AlertEngine()
        host_id = uuid4()
        # Gerar 101 eventos do mesmo host
        events = [make_event(host_id=host_id) for _ in range(101)]
        alerts = engine.process_events(events)
        # Deve gerar exatamente 1 alerta de flood
        assert len(alerts) == 1
        assert alerts[0].severity == EventSeverity.CRITICAL.value

    def test_below_flood_threshold_no_flood_alert(self):
        """Abaixo de 100 eventos → sem flood protection."""
        engine = AlertEngine()
        host_id = uuid4()
        # 50 eventos — abaixo do threshold
        events = [make_event(host_id=host_id) for _ in range(50)]
        alerts = engine.process_events(events)
        # Pode gerar alertas normais, mas não flood
        for alert in alerts:
            assert "FLOOD" not in alert.title


# ---------------------------------------------------------------------------
# Property 17: Supressão em janela de manutenção
# ---------------------------------------------------------------------------

class TestMaintenanceWindow:
    def test_events_suppressed_during_maintenance(self):
        """Property 17: host em manutenção → nenhum alerta."""
        engine = AlertEngine()
        host_id = uuid4()
        now = datetime.now(timezone.utc)

        # Configurar janela de manutenção ativa
        engine.set_maintenance_window(
            str(host_id),
            start=now - timedelta(hours=1),
            end=now + timedelta(hours=1),
        )

        events = [make_event(host_id=host_id) for _ in range(5)]
        alerts = engine.process_events(events)
        assert alerts == []

    def test_events_not_suppressed_outside_maintenance(self):
        """Fora da janela de manutenção → alertas normais."""
        engine = AlertEngine()
        host_id = uuid4()
        now = datetime.now(timezone.utc)

        # Janela de manutenção no passado
        engine.set_maintenance_window(
            str(host_id),
            start=now - timedelta(hours=3),
            end=now - timedelta(hours=1),
        )

        events = [make_event(host_id=host_id)]
        alerts = engine.process_events(events)
        assert len(alerts) >= 1

    def test_clear_maintenance_window(self):
        engine = AlertEngine()
        host_id = uuid4()
        now = datetime.now(timezone.utc)

        engine.set_maintenance_window(
            str(host_id),
            start=now - timedelta(hours=1),
            end=now + timedelta(hours=1),
        )
        engine.clear_maintenance_window(str(host_id))

        events = [make_event(host_id=host_id)]
        alerts = engine.process_events(events)
        assert len(alerts) >= 1


# ---------------------------------------------------------------------------
# Property 13: Alerta consolidado único por grupo correlacionado
# ---------------------------------------------------------------------------

class TestAlertConsolidation:
    def test_multiple_events_same_host_single_alert(self):
        """Property 13: múltiplos eventos do mesmo host → 1 alerta."""
        engine = AlertEngine()
        host_id = uuid4()
        now = datetime.now(timezone.utc)
        events = [
            make_event("high_cpu", host_id=host_id, timestamp=now),
            make_event("low_memory", host_id=host_id, timestamp=now + timedelta(seconds=30)),
        ]
        alerts = engine.process_events(events)
        # Eventos do mesmo host na mesma janela → 1 alerta
        assert len(alerts) == 1

    def test_events_different_hosts_separate_alerts(self):
        """Hosts diferentes → alertas separados."""
        engine = AlertEngine()
        events = [make_event(host_id=uuid4()), make_event(host_id=uuid4())]
        alerts = engine.process_events(events)
        assert len(alerts) == 2

    def test_alert_contains_all_affected_hosts(self):
        """Alerta consolidado deve listar todos os hosts afetados."""
        engine = AlertEngine()
        host_id = uuid4()
        events = [
            make_event("high_cpu", host_id=host_id),
            make_event("low_memory", host_id=host_id),
        ]
        alerts = engine.process_events(events)
        assert len(alerts) == 1
        assert host_id in alerts[0].affected_hosts


# ---------------------------------------------------------------------------
# Métricas do AlertEngine
# ---------------------------------------------------------------------------

class TestAlertEngineMetrics:
    def test_metrics_track_suppressed(self):
        engine = AlertEngine()
        host_id = uuid4()
        event = make_event(host_id=host_id)

        # Primeiro evento — não duplicado
        engine.process_events([event])
        # Segundo evento igual — duplicado
        engine.process_events([make_event(host_id=host_id)])

        metrics = engine.get_metrics()
        assert metrics["alerts_suppressed"] >= 1

    def test_empty_events_no_alerts(self):
        engine = AlertEngine()
        alerts = engine.process_events([])
        assert alerts == []
