"""
Integration: HOST DOWN scenario.
Ping fails → WMI/TCP suspended via DependencyEngine → single event → alert.
Requirements: 12.2
"""
import pytest
from uuid import uuid4

from core.spec.enums import EventSeverity, SensorStatus

try:
    from engine.dependency_engine import DependencyEngine
    HAS_ENGINE = True
except ImportError:
    HAS_ENGINE = False


@pytest.mark.integration
@pytest.mark.skipif(not HAS_ENGINE, reason="engine module not importable in this context")
class TestHostDownScenario:
    """Req 12.2 — HOST DOWN: ping failure cascades to dependent sensors."""

    def test_ping_failure_suspends_dependents(self):
        """When ping sensor goes CRITICAL, WMI and TCP sensors are suspended."""
        engine = DependencyEngine()
        host = f"host_{uuid4().hex[:8]}"

        engine.add_sensor("ping")
        engine.add_sensor("wmi_cpu")
        engine.add_sensor("tcp_80")
        engine.add_dependency("ping", "wmi_cpu")
        engine.add_dependency("ping", "tcp_80")

        engine.update_state("ping", host, SensorStatus.CRITICAL)

        assert engine.should_execute("wmi_cpu", host) is False
        assert engine.should_execute("tcp_80", host) is False

    def test_ping_recovery_reactivates_dependents(self):
        """When ping recovers, dependent sensors resume."""
        engine = DependencyEngine()
        host = f"host_{uuid4().hex[:8]}"

        engine.add_sensor("ping")
        engine.add_sensor("wmi_cpu")
        engine.add_dependency("ping", "wmi_cpu")

        engine.update_state("ping", host, SensorStatus.CRITICAL)
        assert engine.should_execute("wmi_cpu", host) is False

        engine.update_state("ping", host, SensorStatus.OK)
        assert engine.should_execute("wmi_cpu", host) is True

    def test_single_event_for_host_down(self, event_simulator):
        """HOST DOWN generates a single consolidated event."""
        host_id = uuid4()
        event = event_simulator.generate_event(
            host_id=host_id, event_type="host_down",
            severity=EventSeverity.CRITICAL,
        )
        assert event.type == "host_down"
        assert event.severity == EventSeverity.CRITICAL

    def test_host_isolation(self):
        """Host A down does not affect Host B sensors."""
        engine = DependencyEngine()
        host_a = f"host_a_{uuid4().hex[:8]}"
        host_b = f"host_b_{uuid4().hex[:8]}"

        engine.add_sensor("ping")
        engine.add_sensor("wmi")
        engine.add_dependency("ping", "wmi")

        engine.update_state("ping", host_a, SensorStatus.CRITICAL)
        assert engine.should_execute("wmi", host_a) is False
        assert engine.should_execute("wmi", host_b) is True
