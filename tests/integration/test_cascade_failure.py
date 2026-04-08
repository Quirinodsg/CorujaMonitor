"""
Integration: CASCADE FAILURE scenario.
Switch fails → TopologyEngine blast radius → consolidated alert.
Requirements: 12.3
"""
import pytest
from core.spec.enums import NodeType


@pytest.mark.integration
class TestCascadeFailure:
    """Req 12.3 — CASCADE FAILURE: switch failure propagates via topology."""

    def test_switch_failure_blast_radius(self, topology_simulator):
        """Switch failure affects all downstream servers and services."""
        graph, failed_node, expected_affected = topology_simulator.create_cascade_scenario()
        descendants = graph.get_descendants(failed_node)
        assert len(descendants) == len(expected_affected)
        assert set(descendants) == set(expected_affected)

    def test_datacenter_cascade(self, topology_simulator):
        """Core switch failure in datacenter affects all racks and servers."""
        graph = topology_simulator.create_datacenter_topology(racks=3, servers_per_rack=4)
        nodes = list(graph._nodes.values())
        core_switch = None
        for n in nodes:
            if n.metadata.get("layer") == "core":
                core_switch = str(n.id)
                break
        if core_switch:
            descendants = graph.get_descendants(core_switch)
            assert len(descendants) > 0

    def test_leaf_node_no_cascade(self, topology_simulator):
        """Leaf node failure has zero blast radius."""
        graph = topology_simulator.create_simple_topology(switches=1, servers_per_switch=2, services_per_server=1)
        nodes = list(graph._nodes.values())
        for n in nodes:
            if n.type == NodeType.SERVICE:
                descendants = graph.get_descendants(str(n.id))
                assert len(descendants) == 0
                break

    def test_inject_failure_returns_affected(self, topology_simulator):
        """inject_failure returns correct blast radius info."""
        graph = topology_simulator.create_simple_topology(switches=1, servers_per_switch=3, services_per_server=2)
        nodes = list(graph._nodes.values())
        switch_node = None
        for n in nodes:
            if n.type == NodeType.SWITCH:
                switch_node = str(n.id)
                break
        if switch_node:
            result = topology_simulator.inject_failure(graph, switch_node)
            assert result["failed_node"] == switch_node
            assert result["blast_radius"] > 0
