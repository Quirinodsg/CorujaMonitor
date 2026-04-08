"""
Testes unitários do Dependency Engine — tests/unit/
Complementa tests/test_dependency_engine.py com cenários adicionais.

Requisitos: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6
"""
import time

import pytest

from core.spec.enums import SensorStatus
from engine.dependency_engine import DependencyEngine


@pytest.mark.unit
class TestAddSensor:
    """Testes de registro de sensores no grafo."""

    def test_add_sensor_creates_node(self):
        engine = DependencyEngine()
        engine.add_sensor("ping")
        status = engine.get_graph_status()
        assert status["total_nodes"] == 1

    def test_add_duplicate_sensor_is_idempotent(self):
        engine = DependencyEngine()
        engine.add_sensor("ping")
        engine.add_sensor("ping")
        assert engine.get_graph_status()["total_nodes"] == 1

    def test_add_multiple_sensors(self):
        engine = DependencyEngine()
        for s in ["ping", "wmi", "snmp", "tcp"]:
            engine.add_sensor(s)
        assert engine.get_graph_status()["total_nodes"] == 4


@pytest.mark.unit
class TestAddDependency:
    """Testes de adição de dependências e rejeição de ciclos."""

    def test_add_dependency_creates_edge(self):
        engine = DependencyEngine()
        engine.add_dependency("ping", "wmi")
        status = engine.get_graph_status()
        assert status["total_edges"] == 1
        assert status["is_dag"] is True

    def test_add_dependency_auto_creates_nodes(self):
        """add_dependency deve criar nós implicitamente se não existirem."""
        engine = DependencyEngine()
        engine.add_dependency("ping", "wmi")
        assert engine.get_graph_status()["total_nodes"] == 2

    def test_reject_cycle_three_nodes(self):
        engine = DependencyEngine()
        engine.add_dependency("a", "b")
        engine.add_dependency("b", "c")
        with pytest.raises(ValueError, match="[Cc]iclo"):
            engine.add_dependency("c", "a")
        # Grafo inalterado
        assert engine.get_graph_status()["total_edges"] == 2
        assert engine.get_graph_status()["is_dag"] is True

    def test_reject_self_loop(self):
        engine = DependencyEngine()
        with pytest.raises(ValueError):
            engine.add_dependency("x", "x")

    def test_diamond_dependency_is_valid(self):
        """A→B, A→C, B→D, C→D (diamante) é DAG válido."""
        engine = DependencyEngine()
        engine.add_dependency("a", "b")
        engine.add_dependency("a", "c")
        engine.add_dependency("b", "d")
        engine.add_dependency("c", "d")
        assert engine.get_graph_status()["is_dag"] is True
        assert engine.get_graph_status()["total_edges"] == 4


@pytest.mark.unit
class TestCascadeSuspension:
    """Testes de suspensão em cascata e reativação."""

    def test_deep_cascade_four_levels(self):
        """ping → tcp → wmi → app: CRITICAL no ping suspende todos."""
        engine = DependencyEngine(cache_ttl=60)
        engine.add_dependency("ping", "tcp")
        engine.add_dependency("tcp", "wmi")
        engine.add_dependency("wmi", "app")
        engine.update_state("ping", "h1", SensorStatus.CRITICAL)

        assert engine.should_execute("tcp", "h1") is False
        assert engine.should_execute("wmi", "h1") is False
        assert engine.should_execute("app", "h1") is False

    def test_reactivation_restores_all_descendants(self):
        engine = DependencyEngine(cache_ttl=60)
        engine.add_dependency("ping", "tcp")
        engine.add_dependency("tcp", "wmi")

        engine.update_state("ping", "h1", SensorStatus.CRITICAL)
        assert engine.should_execute("wmi", "h1") is False

        engine.update_state("ping", "h1", SensorStatus.OK)
        assert engine.should_execute("tcp", "h1") is True
        assert engine.should_execute("wmi", "h1") is True

    def test_intermediate_critical_suspends_subtree(self):
        """ping → tcp → wmi: CRITICAL no tcp suspende wmi mas não ping."""
        engine = DependencyEngine(cache_ttl=60)
        engine.add_dependency("ping", "tcp")
        engine.add_dependency("tcp", "wmi")

        engine.update_state("tcp", "h1", SensorStatus.CRITICAL)
        assert engine.should_execute("ping", "h1") is True
        assert engine.should_execute("wmi", "h1") is False

    def test_warning_does_not_suspend(self):
        engine = DependencyEngine(cache_ttl=60)
        engine.add_dependency("ping", "wmi")
        engine.update_state("ping", "h1", SensorStatus.WARNING)
        assert engine.should_execute("wmi", "h1") is True


@pytest.mark.unit
class TestHostIsolation:
    """Testes de isolamento de estado entre hosts."""

    def test_critical_on_host_a_does_not_affect_host_b(self):
        engine = DependencyEngine(cache_ttl=60)
        engine.add_dependency("ping", "wmi")
        engine.update_state("ping", "host_a", SensorStatus.CRITICAL)

        assert engine.should_execute("wmi", "host_a") is False
        assert engine.should_execute("wmi", "host_b") is True

    def test_independent_host_states(self):
        engine = DependencyEngine(cache_ttl=60)
        engine.add_dependency("ping", "wmi")

        engine.update_state("ping", "h1", SensorStatus.CRITICAL)
        engine.update_state("ping", "h2", SensorStatus.OK)

        assert engine.should_execute("wmi", "h1") is False
        assert engine.should_execute("wmi", "h2") is True

    def test_clear_host_cache_isolates(self):
        engine = DependencyEngine(cache_ttl=60)
        engine.add_dependency("ping", "wmi")
        engine.update_state("ping", "h1", SensorStatus.CRITICAL)
        engine.update_state("ping", "h2", SensorStatus.CRITICAL)

        engine.clear_host_cache("h1")
        assert engine.should_execute("wmi", "h1") is True
        assert engine.should_execute("wmi", "h2") is False


@pytest.mark.unit
class TestCacheTTLUnit:
    """Testes de expiração do cache TTL."""

    def test_expired_cache_allows_execution(self):
        engine = DependencyEngine(cache_ttl=0)
        engine.add_dependency("ping", "wmi")
        engine.update_state("ping", "h1", SensorStatus.CRITICAL)
        time.sleep(0.02)
        assert engine.should_execute("wmi", "h1") is True

    def test_non_expired_cache_blocks(self):
        engine = DependencyEngine(cache_ttl=300)
        engine.add_dependency("ping", "wmi")
        engine.update_state("ping", "h1", SensorStatus.CRITICAL)
        assert engine.should_execute("wmi", "h1") is False

    def test_ttl_default_is_30(self):
        engine = DependencyEngine()
        assert engine._cache_ttl == 30


@pytest.mark.unit
class TestRemoveDependency:
    """Testes de remoção de dependências."""

    def test_remove_existing_dependency(self):
        engine = DependencyEngine()
        engine.add_dependency("ping", "wmi")
        engine.remove_dependency("ping", "wmi")
        assert engine.get_graph_status()["total_edges"] == 0

    def test_remove_nonexistent_dependency_is_noop(self):
        engine = DependencyEngine()
        engine.remove_dependency("a", "b")  # should not raise
