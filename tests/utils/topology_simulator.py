"""
TopologySimulator — Coruja Monitor v3.0.
Cria topologias de infraestrutura simuladas para testes.
"""
from uuid import uuid4

from core.spec.enums import NodeType
from core.spec.models import TopologyNode
from topology_engine.graph import TopologyGraph


class TopologySimulator:
    """Criador de topologias simuladas para testes."""

    def create_simple_topology(
        self,
        switches: int = 2,
        servers_per_switch: int = 3,
        services_per_server: int = 2,
    ) -> TopologyGraph:
        """
        Cria topologia simples: switches → servers → services.
        Retorna TopologyGraph populado.
        """
        graph = TopologyGraph()

        for sw_i in range(switches):
            switch_node = TopologyNode(
                type=NodeType.SWITCH,
                metadata={"name": f"switch-{sw_i}"},
            )
            graph.add_node(switch_node)

            for srv_i in range(servers_per_switch):
                server_node = TopologyNode(
                    type=NodeType.SERVER,
                    parent_id=switch_node.id,
                    metadata={"name": f"server-{sw_i}-{srv_i}"},
                )
                graph.add_node(server_node)

                for svc_i in range(services_per_server):
                    service_node = TopologyNode(
                        type=NodeType.SERVICE,
                        parent_id=server_node.id,
                        metadata={"name": f"svc-{sw_i}-{srv_i}-{svc_i}"},
                    )
                    graph.add_node(service_node)

        return graph

    def create_datacenter_topology(
        self,
        racks: int = 4,
        servers_per_rack: int = 8,
    ) -> TopologyGraph:
        """
        Cria topologia de datacenter: core_switch → rack_switches → servers.
        """
        graph = TopologyGraph()

        # Core switch
        core = TopologyNode(
            type=NodeType.SWITCH,
            metadata={"name": "core-switch", "layer": "core"},
        )
        graph.add_node(core)

        for rack_i in range(racks):
            rack_switch = TopologyNode(
                type=NodeType.SWITCH,
                parent_id=core.id,
                metadata={"name": f"rack-switch-{rack_i}", "layer": "access"},
            )
            graph.add_node(rack_switch)

            for srv_i in range(servers_per_rack):
                server = TopologyNode(
                    type=NodeType.SERVER,
                    parent_id=rack_switch.id,
                    metadata={"name": f"srv-r{rack_i}-{srv_i}"},
                )
                graph.add_node(server)

        return graph

    def inject_failure(self, graph: TopologyGraph, node_id: str) -> dict:
        """
        Simula falha em um nó e retorna blast radius esperado.
        Retorna: {"failed_node": node_id, "affected": [descendant_ids], "blast_radius": int}
        """
        descendants = graph.get_descendants(node_id)
        return {
            "failed_node": node_id,
            "affected": descendants,
            "blast_radius": len(descendants),
        }

    def create_cascade_scenario(
        self,
    ) -> tuple[TopologyGraph, str, list[str]]:
        """
        Cria cenário de cascata: switch com servidores e serviços.
        Retorna: (graph, failed_node_id, expected_affected_ids)
        """
        graph = TopologyGraph()

        switch = TopologyNode(
            type=NodeType.SWITCH,
            metadata={"name": "cascade-switch"},
        )
        graph.add_node(switch)

        expected_affected = []
        for i in range(3):
            server = TopologyNode(
                type=NodeType.SERVER,
                parent_id=switch.id,
                metadata={"name": f"cascade-srv-{i}"},
            )
            graph.add_node(server)
            expected_affected.append(str(server.id))

            svc = TopologyNode(
                type=NodeType.SERVICE,
                parent_id=server.id,
                metadata={"name": f"cascade-svc-{i}"},
            )
            graph.add_node(svc)
            expected_affected.append(str(svc.id))

        return graph, str(switch.id), expected_affected
