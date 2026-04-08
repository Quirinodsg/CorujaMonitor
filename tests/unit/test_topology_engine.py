"""
Unit tests for Topology Engine — Coruja Monitor v3.0
Tests: serialization round-trip, blast radius BFS, 4 hierarchical layers,
       ancestors/descendants, edge generation.
Requirements: 8.1, 8.2, 8.3, 8.4, 8.5
"""
from uuid import uuid4

import pytest

from core.spec.enums import NodeType
from core.spec.models import TopologyNode
from topology_engine.graph import TopologyGraph


# ---------------------------------------------------------------------------
# Serialization round-trip (to_dict / from_dict)
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestSerializationRoundTrip:
    """Req 8.1 — to_dict → from_dict preserves nodes and edges."""

    def test_empty_graph_round_trip(self):
        g = TopologyGraph()
        data = g.to_dict()
        g2 = TopologyGraph.from_dict(data)
        assert g2.node_count() == 0
        assert g2.edge_count() == 0

    def test_simple_topology_round_trip(self, topology_simulator):
        g = topology_simulator.create_simple_topology(switches=1, servers_per_switch=2, services_per_server=1)
        original_nodes = g.node_count()
        original_edges = g.edge_count()

        data = g.to_dict()
        g2 = TopologyGraph.from_dict(data)

        assert g2.node_count() == original_nodes
        assert g2.edge_count() == original_edges

    def test_round_trip_preserves_node_types(self, topology_simulator):
        g = topology_simulator.create_simple_topology(switches=1, servers_per_switch=2, services_per_server=1)
        data = g.to_dict()
        g2 = TopologyGraph.from_dict(data)

        for n in data["nodes"]:
            restored = g2.get_node(n["id"])
            assert restored is not None
            restored_type = restored.type if isinstance(restored.type, str) else restored.type.value
            assert restored_type == n["type"]

    def test_round_trip_preserves_edges(self, topology_simulator):
        g = topology_simulator.create_simple_topology(switches=1, servers_per_switch=3, services_per_server=0)
        data = g.to_dict()
        g2 = TopologyGraph.from_dict(data)
        original_edges = set((e["source"], e["target"]) for e in data["edges"])
        restored_edges = set(g2.all_edges())
        assert original_edges == restored_edges


# ---------------------------------------------------------------------------
# Blast radius BFS
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestBlastRadius:
    """Req 8.2, 8.4 — blast radius = descendants via BFS."""

    def test_switch_failure_blast_radius(self, topology_simulator):
        graph, failed_id, expected = topology_simulator.create_cascade_scenario()
        descendants = graph.get_descendants(failed_id)
        assert set(descendants) == set(expected)

    def test_leaf_node_zero_blast_radius(self, topology_simulator):
        g = topology_simulator.create_simple_topology(switches=1, servers_per_switch=1, services_per_server=1)
        nodes = g.to_dict()["nodes"]
        service_nodes = [n for n in nodes if n["type"] == "service"]
        assert len(service_nodes) > 0
        descendants = g.get_descendants(service_nodes[0]["id"])
        assert len(descendants) == 0

    def test_blast_radius_matches_inject_failure(self, topology_simulator):
        g = topology_simulator.create_simple_topology(switches=1, servers_per_switch=3, services_per_server=2)
        nodes = g.to_dict()["nodes"]
        switch_id = [n["id"] for n in nodes if n["type"] == "switch"][0]
        info = topology_simulator.inject_failure(g, switch_id)
        assert info["blast_radius"] == len(g.get_descendants(switch_id))


# ---------------------------------------------------------------------------
# 4 hierarchical layers
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestHierarchicalLayers:
    """Req 8.3 — switch → server → service (+ application)."""

    def test_three_layer_hierarchy(self, topology_simulator):
        g = topology_simulator.create_simple_topology(switches=1, servers_per_switch=2, services_per_server=2)
        nodes = g.to_dict()["nodes"]
        types = {n["type"] for n in nodes}
        assert "switch" in types
        assert "server" in types
        assert "service" in types

    def test_four_layer_with_application(self):
        g = TopologyGraph()
        switch = TopologyNode(type=NodeType.SWITCH, metadata={"name": "sw"})
        g.add_node(switch)
        server = TopologyNode(type=NodeType.SERVER, parent_id=switch.id, metadata={"name": "srv"})
        g.add_node(server)
        service = TopologyNode(type=NodeType.SERVICE, parent_id=server.id, metadata={"name": "svc"})
        g.add_node(service)
        app = TopologyNode(type=NodeType.APPLICATION, parent_id=service.id, metadata={"name": "app"})
        g.add_node(app)

        types = {n["type"] for n in g.to_dict()["nodes"]}
        assert types == {"switch", "server", "service", "application"}
        # Switch descendants should include all 3 children
        desc = g.get_descendants(str(switch.id))
        assert len(desc) == 3


# ---------------------------------------------------------------------------
# Ancestors / Descendants
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestAncestorsDescendants:
    """Req 8.4 — correct ancestor/descendant queries."""

    def test_ancestors_of_leaf(self, topology_simulator):
        g = topology_simulator.create_simple_topology(switches=1, servers_per_switch=1, services_per_server=1)
        nodes = g.to_dict()["nodes"]
        service = [n for n in nodes if n["type"] == "service"][0]
        ancestors = g.get_ancestors(service["id"])
        # Should have server and switch as ancestors
        assert len(ancestors) == 2

    def test_descendants_of_root(self, topology_simulator):
        g = topology_simulator.create_simple_topology(switches=1, servers_per_switch=2, services_per_server=1)
        nodes = g.to_dict()["nodes"]
        switch = [n for n in nodes if n["type"] == "switch"][0]
        desc = g.get_descendants(switch["id"])
        # 2 servers + 2 services = 4
        assert len(desc) == 4

    def test_nonexistent_node_returns_empty(self):
        g = TopologyGraph()
        assert g.get_ancestors("nonexistent") == []
        assert g.get_descendants("nonexistent") == []


# ---------------------------------------------------------------------------
# Edge generation
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestEdgeGeneration:
    """Req 8.5 — edges generated from parent-child relationships."""

    def test_edges_match_parent_child(self, topology_simulator):
        g = topology_simulator.create_simple_topology(switches=1, servers_per_switch=2, services_per_server=0)
        edges = g.all_edges()
        nodes = g.to_dict()["nodes"]
        switch_id = [n["id"] for n in nodes if n["type"] == "switch"][0]
        server_ids = [n["id"] for n in nodes if n["type"] == "server"]
        for sid in server_ids:
            assert (switch_id, sid) in edges

    def test_explicit_add_edge(self):
        g = TopologyGraph()
        n1 = TopologyNode(type=NodeType.SWITCH, metadata={"name": "a"})
        n2 = TopologyNode(type=NodeType.SERVER, metadata={"name": "b"})
        g.add_node(n1)
        g.add_node(n2)
        g.add_edge(str(n1.id), str(n2.id))
        assert (str(n1.id), str(n2.id)) in g.all_edges()
