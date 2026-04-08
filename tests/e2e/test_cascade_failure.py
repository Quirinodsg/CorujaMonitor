"""
E2E: CASCADE FAILURE scenario.
Switch fails → topology → blast radius → alert.
Requirements: 19.4
"""
import pytest
from core.spec.enums import NodeType


@pytest.mark.e2e
class TestCascadeFailureE2E:
    """Req 19.4 — CASCADE FAILURE: switch → topology → blast radius → alert."""

    def test_cascade_full_flow(self, topology_simulator):
        """Full cascade: switch failure → blast radius calculation."""
        graph, failed_node, expected = topology_simulator.create_cascade_scenario()
        descendants = graph.get_descendants(failed_node)
        assert set(descendants) == set(expected)
        assert len(descendants) > 0

    def test_blast_radius_includes_services(self, topology_simulator):
        """Blast radius includes both servers and services."""
        graph = topology_simulator.create_simple_topology(
            switches=1, servers_per_switch=2, services_per_server=2,
        )
        nodes = list(graph._nodes.values())
        switch = next(n for n in nodes if n.type == NodeType.SWITCH)
        descendants = graph.get_descendants(str(switch.id))
        assert len(descendants) >= 4
