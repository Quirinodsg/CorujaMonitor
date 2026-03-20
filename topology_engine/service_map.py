"""
Service Map — Coruja Monitor v3.5 Enterprise
Grafo interativo de dependências de serviços com highlight de falhas.
Integrado ao TopologyGraph existente.
"""
import logging
from typing import Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class ServiceNode:
    """Nó do Service Map — representa um serviço ou componente."""
    def __init__(
        self,
        node_id: str,
        name: str,
        node_type: str,  # server, service, database, switch, router, firewall, app
        status: str = "ok",  # ok, warning, critical, unknown
        server_id: Optional[int] = None,
        sensor_id: Optional[int] = None,
        metadata: Optional[dict] = None,
    ):
        self.id = node_id
        self.name = name
        self.type = node_type
        self.status = status
        self.server_id = server_id
        self.sensor_id = sensor_id
        self.metadata = metadata or {}
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "status": self.status,
            "server_id": self.server_id,
            "sensor_id": self.sensor_id,
            "metadata": self.metadata,
            "updated_at": self.updated_at,
        }


class ServiceEdge:
    """Aresta do Service Map — representa dependência entre serviços."""
    def __init__(
        self,
        source: str,
        target: str,
        edge_type: str = "depends_on",  # depends_on, connects_to, hosts
        label: Optional[str] = None,
    ):
        self.source = source
        self.target = target
        self.type = edge_type
        self.label = label

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "target": self.target,
            "type": self.type,
            "label": self.label,
        }


class ServiceMap:
    """
    Mapa de serviços e dependências.
    - Constrói grafo a partir de servidores/sensores do banco
    - Propaga status de falha pelos relacionamentos
    - Exporta formato compatível com react-force-graph / D3
    """

    def __init__(self):
        self._nodes: dict[str, ServiceNode] = {}
        self._edges: list[ServiceEdge] = []

    def add_node(self, node: ServiceNode) -> None:
        self._nodes[node.id] = node

    def add_edge(self, source: str, target: str, edge_type: str = "depends_on", label: str = None) -> None:
        # Evitar duplicatas
        for e in self._edges:
            if e.source == source and e.target == target:
                return
        self._edges.append(ServiceEdge(source, target, edge_type, label))

    def update_status(self, node_id: str, status: str) -> None:
        """Atualiza status de um nó e propaga para dependentes."""
        if node_id not in self._nodes:
            return
        self._nodes[node_id].status = status
        self._nodes[node_id].updated_at = datetime.now(timezone.utc).isoformat()

        # Propagar falha para dependentes diretos
        if status == "critical":
            for edge in self._edges:
                if edge.source == node_id and edge.type == "depends_on":
                    dep = self._nodes.get(edge.target)
                    if dep and dep.status == "ok":
                        dep.status = "warning"  # Dependente fica em warning
                        dep.updated_at = datetime.now(timezone.utc).isoformat()
                        logger.debug("ServiceMap: %s → warning (depende de %s em falha)", edge.target, node_id)

    def get_impact_radius(self, node_id: str) -> list[str]:
        """Retorna todos os nós impactados por falha em node_id."""
        impacted = []
        visited = set()

        def _traverse(nid: str):
            if nid in visited:
                return
            visited.add(nid)
            for edge in self._edges:
                if edge.source == nid:
                    impacted.append(edge.target)
                    _traverse(edge.target)

        _traverse(node_id)
        return list(set(impacted))

    def to_dict(self) -> dict:
        """Exporta para formato react-force-graph."""
        # Calcular estatísticas de status
        status_counts = {"ok": 0, "warning": 0, "critical": 0, "unknown": 0}
        for node in self._nodes.values():
            status_counts[node.status] = status_counts.get(node.status, 0) + 1

        return {
            "nodes": [n.to_dict() for n in self._nodes.values()],
            "edges": [e.to_dict() for e in self._edges],
            "stats": {
                "total_nodes": len(self._nodes),
                "total_edges": len(self._edges),
                "status": status_counts,
            },
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    @classmethod
    def build_from_db(cls, db) -> "ServiceMap":
        """
        Constrói ServiceMap a partir do banco de dados.
        Usa servidores como nós e relacionamentos probe→server→sensor como arestas.
        """
        from models import Server, Sensor, Metric
        from sqlalchemy import desc

        smap = cls()

        try:
            servers = db.query(Server).filter(Server.is_active == True).all()

            for server in servers:
                # Determinar status do servidor baseado nos sensores críticos
                critical_sensors = db.query(Sensor).filter(
                    Sensor.server_id == server.id,
                    Sensor.is_active == True,
                ).all()

                server_status = "ok"
                for sensor in critical_sensors:
                    last_metric = db.query(Metric).filter(
                        Metric.sensor_id == sensor.id
                    ).order_by(desc(Metric.timestamp)).first()
                    if last_metric:
                        if last_metric.status == "critical":
                            server_status = "critical"
                            break
                        elif last_metric.status == "warning":
                            server_status = "warning"

                node = ServiceNode(
                    node_id=f"server-{server.id}",
                    name=server.hostname,
                    node_type=server.device_type or "server",
                    status=server_status,
                    server_id=server.id,
                    metadata={
                        "ip": server.ip_address,
                        "os": server.os_type,
                        "group": server.group_name,
                        "probe_id": server.probe_id,
                    },
                )
                smap.add_node(node)

                # Adicionar sensores críticos como nós filhos
                for sensor in critical_sensors:
                    if sensor.sensor_type in ("service", "database", "http"):
                        sensor_node = ServiceNode(
                            node_id=f"sensor-{sensor.id}",
                            name=sensor.name,
                            node_type=sensor.sensor_type,
                            status="ok",
                            server_id=server.id,
                            sensor_id=sensor.id,
                        )
                        smap.add_node(sensor_node)
                        smap.add_edge(
                            f"server-{server.id}",
                            f"sensor-{sensor.id}",
                            edge_type="hosts",
                            label="hosts",
                        )

                # Relacionamento probe → server
                smap.add_edge(
                    f"probe-{server.probe_id}",
                    f"server-{server.id}",
                    edge_type="monitors",
                    label="monitors",
                )

            # Propagar status de falha
            for node in list(smap._nodes.values()):
                if node.status == "critical":
                    smap.update_status(node.id, "critical")

        except Exception as e:
            logger.error("ServiceMap.build_from_db error: %s", e)

        return smap
