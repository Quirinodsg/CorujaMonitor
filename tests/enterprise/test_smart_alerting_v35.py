"""
QA Enterprise — Smart Alerting v3.5
Testa: cooldown, supressão topológica, agrupamento, flood, manutenção, métricas.
Nível: QA Senior + Arquiteto — cada comportamento verificado por contrato.
"""
import time
import uuid
import pytest
from datetime import datetime, timezone, timedelta

from core.spec.models import Event, Alert
from core.spec.enums import EventSeverity, AlertStatus
from alert_engine.engine import AlertEngine, DEFAULT_COOLDOWN_SECONDS
from alert_engine.suppressor import DuplicateSuppressor


# ─── Helpers ────────────────────────────────────────────────────────────────

def make_event(host_id: str, event_type: str = "cpu_high", severity: EventSeverity = EventSeverity.WARNING) -> Event:
    return Event(
        id=uuid.uuid4(),
        host_id=uuid.UUID(int=abs(hash(host_id)) % (2**128)),
        type=event_type,
        severity=severity,
        timestamp=datetime.now(timezone.utc),
    )


def make_engine(cooldown: int = 0) -> AlertEngine:
    """Engine com cooldown configurável e suppressor limpo."""
    engine = AlertEngine(cooldown_seconds=cooldown)
    return engine


# ─── 1. Cooldown ─────────────────────────────────────────────────────────────

class TestCooldown:
    def test_first_event_passes(self):
        """Primeiro evento sempre passa — cooldown não está ativo."""
        engine = make_engine(cooldown=60)
        ev = make_event("host-01", "cpu_high")
        alerts = engine.process_events([ev])
        assert len(alerts) >= 1

    def test_second_event_suppressed_within_cooldown(self):
        """Segundo evento do mesmo host:tipo dentro do cooldown é suprimido."""
        engine = make_engine(cooldown=300)
        ev1 = make_event("host-01", "cpu_high")
        ev2 = make_event("host-01", "cpu_high")

        engine.process_events([ev1])
        alerts2 = engine.process_events([ev2])

        metrics = engine.get_metrics()
        assert metrics["alerts_cooldown_suppressed"] >= 1, \
            "Segundo evento deveria ser suprimido pelo cooldown"

    def test_different_type_not_suppressed(self):
        """Evento de tipo diferente no mesmo host não é afetado pelo cooldown do outro tipo."""
        engine = make_engine(cooldown=300)
        ev_cpu = make_event("host-01", "cpu_high")
        ev_disk = make_event("host-01", "disk_full")

        engine.process_events([ev_cpu])
        # disk_full é tipo diferente — não deve ser suprimido por cooldown de cpu_high
        alerts = engine.process_events([ev_disk])
        metrics = engine.get_metrics()
        # disk_full não estava em cooldown
        assert metrics["alerts_cooldown_suppressed"] == 0 or \
               any(a.title for a in alerts), \
            "Tipo diferente não deve ser bloqueado pelo cooldown do outro tipo"

    def test_cooldown_configurable(self):
        """set_cooldown() altera o comportamento em tempo de execução."""
        engine = make_engine(cooldown=0)
        engine.set_cooldown(300)
        assert engine._cooldown_seconds == 300

    def test_zero_cooldown_never_suppresses(self):
        """Cooldown=0 nunca suprime por cooldown."""
        engine = make_engine(cooldown=0)
        ev = make_event("host-01", "cpu_high")
        engine.process_events([ev])
        engine.process_events([ev])
        metrics = engine.get_metrics()
        assert metrics["alerts_cooldown_suppressed"] == 0


# ─── 2. Supressão Topológica ─────────────────────────────────────────────────

class TestTopologySuppression:
    def _host_uuid(self, name: str) -> uuid.UUID:
        return uuid.UUID(int=abs(hash(name)) % (2**128))

    def test_child_suppressed_when_parent_failed(self):
        """Se switch-core está em falha, server-01 (filho) deve ser suprimido."""
        engine = make_engine(cooldown=0)
        engine.set_topology({"server-01": "switch-core"})
        engine.mark_host_failed("switch-core")

        ev = Event(
            id=uuid.uuid4(),
            host_id=self._host_uuid("server-01"),
            type="host_down",
            severity=EventSeverity.CRITICAL,
            timestamp=datetime.now(timezone.utc),
        )
        # Precisamos que o engine reconheça "server-01" como string
        # O engine usa str(event.host_id) — precisamos mapear o UUID para "server-01"
        # Ajuste: usar host_id como string diretamente via topology
        engine._topology_parents = {"server-01": "switch-core"}
        engine._failed_hosts = {"switch-core"}

        # Criar evento com host_id que bate com a chave "server-01"
        ev2 = Event(
            id=uuid.uuid4(),
            host_id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
            type="host_down",
            severity=EventSeverity.CRITICAL,
            timestamp=datetime.now(timezone.utc),
        )
        engine._topology_parents = {str(ev2.host_id): "switch-core"}
        engine._failed_hosts = {"switch-core"}

        engine.process_events([ev2])
        metrics = engine.get_metrics()
        assert metrics["alerts_topology_suppressed"] >= 1, \
            "Filho de switch em falha deve ser suprimido topologicamente"

    def test_child_not_suppressed_when_parent_ok(self):
        """Filho não é suprimido se pai está OK (não em _failed_hosts)."""
        engine = make_engine(cooldown=0)
        ev = Event(
            id=uuid.uuid4(),
            host_id=uuid.UUID("00000000-0000-0000-0000-000000000002"),
            type="host_down",
            severity=EventSeverity.CRITICAL,
            timestamp=datetime.now(timezone.utc),
        )
        engine._topology_parents = {str(ev.host_id): "switch-core"}
        # switch-core NÃO está em _failed_hosts

        alerts = engine.process_events([ev])
        metrics = engine.get_metrics()
        assert metrics["alerts_topology_suppressed"] == 0, \
            "Filho não deve ser suprimido se pai está OK"

    def test_set_topology_updates_map(self):
        """set_topology() substitui o mapa completo."""
        engine = make_engine(cooldown=0)
        engine.set_topology({"h1": "sw1", "h2": "sw1"})
        assert engine._topology_parents == {"h1": "sw1", "h2": "sw1"}

    def test_mark_host_recovered_removes_suppression(self):
        """mark_host_recovered() remove host de _failed_hosts."""
        engine = make_engine(cooldown=0)
        engine.mark_host_failed("switch-core")
        assert "switch-core" in engine._failed_hosts
        engine.mark_host_recovered("switch-core")
        assert "switch-core" not in engine._failed_hosts

    def test_cascade_suppression_multiple_children(self):
        """100 filhos de um switch em falha → todos suprimidos."""
        engine = make_engine(cooldown=0)
        topology = {}
        events = []
        for i in range(100):
            hid = uuid.UUID(int=i + 1)
            topology[str(hid)] = "switch-core"
            events.append(Event(
                id=uuid.uuid4(),
                host_id=hid,
                type="host_down",
                severity=EventSeverity.CRITICAL,
                timestamp=datetime.now(timezone.utc),
            ))
        engine._topology_parents = topology
        engine._failed_hosts = {"switch-core"}

        engine.process_events(events)
        metrics = engine.get_metrics()
        assert metrics["alerts_topology_suppressed"] == 100, \
            f"Esperado 100 suprimidos, obtido {metrics['alerts_topology_suppressed']}"


# ─── 3. Flood Protection ─────────────────────────────────────────────────────

class TestFloodProtection:
    def test_flood_triggers_single_alert(self):
        """Mais de 100 eventos do mesmo host em 1 min → 1 alerta de flood."""
        engine = make_engine(cooldown=0)
        host_id = uuid.uuid4()
        events = [
            Event(
                id=uuid.uuid4(),
                host_id=host_id,
                type="cpu_high",
                severity=EventSeverity.WARNING,
                timestamp=datetime.now(timezone.utc),
            )
            for _ in range(101)
        ]
        alerts = engine.process_events(events)
        assert len(alerts) == 1, f"Flood deve gerar 1 alerta, gerou {len(alerts)}"
        assert "FLOOD" in alerts[0].title.upper()
        metrics = engine.get_metrics()
        assert metrics["alerts_flood_protected"] >= 1

    def test_flood_alert_is_critical(self):
        """Alerta de flood deve ter severidade CRITICAL."""
        engine = make_engine(cooldown=0)
        host_id = uuid.uuid4()
        events = [
            Event(id=uuid.uuid4(), host_id=host_id, type="x", severity=EventSeverity.WARNING,
                  timestamp=datetime.now(timezone.utc))
            for _ in range(101)
        ]
        alerts = engine.process_events(events)
        assert alerts[0].severity == EventSeverity.CRITICAL or \
               alerts[0].severity == EventSeverity.CRITICAL.value


# ─── 4. Janela de Manutenção ─────────────────────────────────────────────────

class TestMaintenanceWindow:
    def test_events_suppressed_during_maintenance(self):
        """Eventos de host em manutenção são completamente suprimidos."""
        engine = make_engine(cooldown=0)
        host_id = uuid.uuid4()
        now = datetime.now(timezone.utc)
        engine.set_maintenance_window(str(host_id), now - timedelta(hours=1), now + timedelta(hours=1))

        ev = Event(id=uuid.uuid4(), host_id=host_id, type="cpu_high",
                   severity=EventSeverity.CRITICAL, timestamp=now)
        alerts = engine.process_events([ev])
        assert len(alerts) == 0, "Eventos em manutenção devem ser suprimidos"

    def test_events_pass_after_maintenance_cleared(self):
        """Após clear_maintenance_window, eventos voltam a ser processados."""
        engine = make_engine(cooldown=0)
        host_id = uuid.uuid4()
        now = datetime.now(timezone.utc)
        engine.set_maintenance_window(str(host_id), now - timedelta(hours=1), now + timedelta(hours=1))
        engine.clear_maintenance_window(str(host_id))

        ev = Event(id=uuid.uuid4(), host_id=host_id, type="cpu_high",
                   severity=EventSeverity.CRITICAL, timestamp=now)
        alerts = engine.process_events([ev])
        assert len(alerts) >= 1, "Após remover manutenção, eventos devem passar"


# ─── 5. Métricas do Engine ───────────────────────────────────────────────────

class TestEngineMetrics:
    def test_metrics_keys_present(self):
        """get_metrics() deve retornar todas as chaves esperadas."""
        engine = make_engine()
        metrics = engine.get_metrics()
        expected_keys = {
            "alerts_total", "alerts_suppressed", "alerts_grouped",
            "alerts_flood_protected", "alerts_cooldown_suppressed",
            "alerts_topology_suppressed",
        }
        assert expected_keys.issubset(set(metrics.keys())), \
            f"Chaves faltando: {expected_keys - set(metrics.keys())}"

    def test_metrics_increment_correctly(self):
        """Métricas incrementam corretamente após processamento."""
        engine = make_engine(cooldown=0)
        ev = make_event("host-metrics", "cpu_high", EventSeverity.CRITICAL)
        engine.process_events([ev])
        metrics = engine.get_metrics()
        assert metrics["alerts_total"] >= 1

    def test_empty_events_no_side_effects(self):
        """Lista vazia não altera métricas."""
        engine = make_engine()
        engine.process_events([])
        metrics = engine.get_metrics()
        assert all(v == 0 for v in metrics.values()), \
            "Nenhuma métrica deve ser incrementada com lista vazia"
