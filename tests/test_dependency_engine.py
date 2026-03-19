"""
Testes da Fase 2 — Dependency Engine (engine/dependency_engine.py)
Cobre: Property 3 (DAG sem ciclos), Property 4 (suspensão/reativação round-trip)
"""
import time
import pytest

from engine.dependency_engine import DependencyEngine
from core.spec.enums import SensorStatus


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def engine():
    return DependencyEngine(cache_ttl=30)


@pytest.fixture
def chain_engine():
    """Ping → TCP → WMI (cadeia de 3 níveis)."""
    e = DependencyEngine(cache_ttl=30)
    e.add_sensor("ping")
    e.add_sensor("tcp")
    e.add_sensor("wmi")
    e.add_dependency("ping", "tcp")
    e.add_dependency("tcp", "wmi")
    return e


# ---------------------------------------------------------------------------
# Property 3: DAG nunca contém ciclos
# ---------------------------------------------------------------------------

class TestDAGInvariant:
    def test_simple_dependency_is_dag(self, engine):
        engine.add_dependency("ping", "wmi")
        status = engine.get_graph_status()
        assert status["is_dag"] is True

    def test_rejects_direct_cycle(self, engine):
        engine.add_dependency("a", "b")
        with pytest.raises(ValueError, match="ciclo"):
            engine.add_dependency("b", "a")
        # Grafo deve continuar sendo DAG
        assert engine.get_graph_status()["is_dag"] is True

    def test_rejects_indirect_cycle(self, engine):
        engine.add_dependency("a", "b")
        engine.add_dependency("b", "c")
        with pytest.raises(ValueError, match="ciclo"):
            engine.add_dependency("c", "a")
        assert engine.get_graph_status()["is_dag"] is True

    def test_self_loop_rejected(self, engine):
        with pytest.raises(ValueError, match="ciclo"):
            engine.add_dependency("a", "a")

    def test_multiple_parents_allowed(self, engine):
        """Sensor com dois pais (diamante) é DAG válido."""
        engine.add_dependency("ping", "tcp")
        engine.add_dependency("ping", "snmp")
        engine.add_dependency("tcp", "wmi")
        engine.add_dependency("snmp", "wmi")
        assert engine.get_graph_status()["is_dag"] is True

    def test_graph_status_counts(self, engine):
        engine.add_dependency("ping", "wmi")
        engine.add_dependency("ping", "snmp")
        status = engine.get_graph_status()
        assert status["total_edges"] == 2
        assert status["total_nodes"] >= 3


# ---------------------------------------------------------------------------
# Property 4: Suspensão e reativação round-trip
# ---------------------------------------------------------------------------

class TestSuspensionRoundTrip:
    def test_should_execute_without_dependencies(self, engine):
        """Sensor sem dependências sempre pode executar."""
        engine.add_sensor("standalone")
        assert engine.should_execute("standalone", "host1") is True

    def test_child_suspended_when_parent_critical(self, engine):
        engine.add_dependency("ping", "wmi")
        engine.update_state("ping", "host1", SensorStatus.CRITICAL)
        assert engine.should_execute("wmi", "host1") is False

    def test_child_reactivated_when_parent_ok(self, engine):
        engine.add_dependency("ping", "wmi")
        # Suspender
        engine.update_state("ping", "host1", SensorStatus.CRITICAL)
        assert engine.should_execute("wmi", "host1") is False
        # Reativar
        engine.update_state("ping", "host1", SensorStatus.OK)
        assert engine.should_execute("wmi", "host1") is True

    def test_parent_ok_allows_child(self, engine):
        engine.add_dependency("ping", "wmi")
        engine.update_state("ping", "host1", SensorStatus.OK)
        assert engine.should_execute("wmi", "host1") is True

    def test_parent_warning_does_not_suspend(self, engine):
        """WARNING no pai não suspende filhos — apenas CRITICAL."""
        engine.add_dependency("ping", "wmi")
        engine.update_state("ping", "host1", SensorStatus.WARNING)
        assert engine.should_execute("wmi", "host1") is True

    def test_cascade_suspension(self, chain_engine):
        """Ping CRITICAL suspende TCP e WMI em cascata."""
        chain_engine.update_state("ping", "host1", SensorStatus.CRITICAL)
        assert chain_engine.should_execute("tcp", "host1") is False
        assert chain_engine.should_execute("wmi", "host1") is False

    def test_cascade_reactivation(self, chain_engine):
        """Ping OK reativa TCP e WMI."""
        chain_engine.update_state("ping", "host1", SensorStatus.CRITICAL)
        chain_engine.update_state("ping", "host1", SensorStatus.OK)
        assert chain_engine.should_execute("tcp", "host1") is True
        assert chain_engine.should_execute("wmi", "host1") is True

    def test_isolation_between_hosts(self, engine):
        """Estado de host1 não afeta host2."""
        engine.add_dependency("ping", "wmi")
        engine.update_state("ping", "host1", SensorStatus.CRITICAL)
        # host2 não tem estado — deve poder executar
        assert engine.should_execute("wmi", "host2") is True

    def test_get_suspended_sensors(self, engine):
        engine.add_dependency("ping", "wmi")
        engine.add_dependency("ping", "snmp")
        engine.update_state("ping", "host1", SensorStatus.CRITICAL)
        suspended = engine.get_suspended_sensors("host1")
        assert "wmi" in suspended
        assert "snmp" in suspended
        assert "ping" not in suspended  # pai não é suspenso, apenas filhos


# ---------------------------------------------------------------------------
# Cache TTL
# ---------------------------------------------------------------------------

class TestCacheTTL:
    def test_expired_cache_allows_execution(self):
        """Estado expirado (TTL=0) não bloqueia execução."""
        engine = DependencyEngine(cache_ttl=0)
        engine.add_dependency("ping", "wmi")
        engine.update_state("ping", "host1", SensorStatus.CRITICAL)
        # TTL=0 → expira imediatamente
        time.sleep(0.01)
        assert engine.should_execute("wmi", "host1") is True

    def test_valid_cache_blocks_execution(self):
        """Estado dentro do TTL bloqueia execução."""
        engine = DependencyEngine(cache_ttl=60)
        engine.add_dependency("ping", "wmi")
        engine.update_state("ping", "host1", SensorStatus.CRITICAL)
        assert engine.should_execute("wmi", "host1") is False


# ---------------------------------------------------------------------------
# Sensor não registrado no grafo
# ---------------------------------------------------------------------------

class TestUnregisteredSensor:
    def test_unknown_sensor_can_execute(self, engine):
        """Sensor não no grafo pode sempre executar."""
        assert engine.should_execute("unknown_sensor", "host1") is True

    def test_clear_host_cache(self, engine):
        engine.add_dependency("ping", "wmi")
        engine.update_state("ping", "host1", SensorStatus.CRITICAL)
        assert engine.should_execute("wmi", "host1") is False
        engine.clear_host_cache("host1")
        assert engine.should_execute("wmi", "host1") is True
