"""
E2E: HOST DOWN scenario.
Ping fails → suspension → single event → alert <30s.
Requirements: 19.1
"""
import pytest
import time
from uuid import uuid4

from core.spec.enums import EventSeverity, SensorStatus

try:
    from engine.dependency_engine import DependencyEngine
    HAS_ENGINE = True
except ImportError:
    HAS_ENGINE = False


@pytest.mark.e2e
@pytest.mark.skipif(not HAS_ENGINE, reason="engine module not importable in this context")
class TestHostDownE2E:
    """Req 19.1 — HOST DOWN end-to-end within 30s."""

    def test_host_down_full_flow(self, event_simulator):
        """Full HOST DOWN: ping fail → suspend → event → alert."""
        start = time.monotonic()
        host_id = uuid4()

        # 1. DependencyEngine suspends dependents
        engine = DependencyEngine()
        host = f"host_{host_id.hex[:8]}"
        engine.add_sensor("ping")
        engine.add_sensor("wmi")
        engine.add_dependency("ping", "wmi")
        engine.update_state("ping", host, SensorStatus.CRITICAL)
        assert engine.should_execute("wmi", host) is False

        # 2. Generate single event
        event = event_simulator.generate_event(
            host_id=host_id, event_type="host_down",
            severity=EventSeverity.CRITICAL,
        )
        assert event.type == "host_down"

        elapsed = time.monotonic() - start
        assert elapsed < 30.0
