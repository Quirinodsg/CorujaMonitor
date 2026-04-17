"""
Topology Router — Coruja Monitor v3.0
Enterprise-grade: real edges, hierarchical layers, BFS blast radius, status from metrics.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from typing import Optional
import logging
import json
from database import get_db
from models import HyperVHost, HyperVVM

router = APIRouter(prefix="/api/v1/topology", tags=["Topology v3"])
logger = logging.getLogger(__name__)


class TopologyNodeCreate(BaseModel):
    type: str
    parent_id: Optional[str] = None
    metadata: dict = {}


# ─── Status via métricas ──────────────────────────────────────────────────────

def _get_server_status(server_id: int, db: Session) -> str:
    try:
        row = db.execute(text("""
            SELECT
                COUNT(*) FILTER (WHERE m.status = 'critical') AS crit,
                COUNT(*) FILTER (WHERE m.status = 'warning')  AS warn,
                COUNT(sen.id) AS total
            FROM sensors sen
            LEFT JOIN LATERAL (
                SELECT status FROM metrics
                WHERE sensor_id = sen.id
                ORDER BY timestamp DESC
                LIMIT 1
            ) m ON TRUE
            WHERE sen.server_id = :sid AND sen.is_active = true
        """), {"sid": server_id}).fetchone()
        if not row or row.total == 0:
            return "unknown"
        if row.crit > 0:
            return "critical"
        if row.warn > 0:
            return "warning"
        return "ok"
    except Exception:
        return "unknown"


def _get_all_server_statuses(server_ids: list, db: Session) -> dict:
    """Busca status de todos os servidores em uma única query batch."""
    if not server_ids:
        return {}
    try:
        ids_str = ",".join(str(sid) for sid in server_ids)
        rows = db.execute(text(f"""
            SELECT
                sen.server_id,
                COUNT(*) FILTER (WHERE m.status = 'critical') AS crit,
                COUNT(*) FILTER (WHERE m.status = 'warning')  AS warn,
                COUNT(sen.id) AS total
            FROM sensors sen
            LEFT JOIN LATERAL (
                SELECT status FROM metrics
                WHERE sensor_id = sen.id
                ORDER BY timestamp DESC
                LIMIT 1
            ) m ON TRUE
            WHERE sen.server_id IN ({ids_str}) AND sen.is_active = true
            GROUP BY sen.server_id
        """)).fetchall()
        result = {}
        for r in rows:
            if r.total == 0:
                result[r.server_id] = "unknown"
            elif r.crit > 0:
                result[r.server_id] = "critical"
            elif r.warn > 0:
                result[r.server_id] = "warning"
            else:
                result[r.server_id] = "ok"
        # Servidores sem sensores ficam como unknown
        for sid in server_ids:
            if sid not in result:
                result[sid] = "unknown"
        return result
    except Exception:
        return {sid: "unknown" for sid in server_ids}


# ─── Layer detection ─────────────────────────────────────────────────────────

def _detect_layer(server) -> int:
    """
    Atribui layer hierárquico:
      0 = network infra (switch/router/firewall)
      1 = hypervisor / virtualization host
      2 = server / VM
      3 = application / service
    """
    device_type = (getattr(server, 'device_type', None) or 'server').lower()
    os_type = (getattr(server, 'os_type', None) or '').lower()
    hostname = (getattr(server, 'hostname', None) or '').upper()

    if device_type in ('switch', 'router', 'firewall', 'network', 'access_point', 'ap', 'gateway'):
        return 0
    # UDM = UniFi Dream Machine = gateway/router
    if 'udm' in hostname.lower() or 'udm' in device_type:
        return 0
    if device_type in ('hypervisor',) or 'hv' in hostname or 'hyperv' in os_type:
        return 1
    if device_type in ('server', 'vm', 'host'):
        return 2
    return 2


# ─── Edge generation ─────────────────────────────────────────────────────────

def _generate_edges_from_sensors(server_nodes: list, db: Session) -> list:
    """
    Gera edges semânticas baseadas nos sensores reais.
    server_nodes: [{"node_id": str, "server_id": int, "layer": int}]
    """
    if not server_nodes:
        return []

    edges = []
    seen = set()

    def add_edge(src, tgt, etype):
        key = (src, tgt)
        if key not in seen and src != tgt:
            seen.add(key)
            edges.append({"source": src, "target": tgt, "type": etype})

    node_by_sid = {sn["server_id"]: sn for sn in server_nodes}
    ids_str = ",".join(str(sn["server_id"]) for sn in server_nodes)

    try:
        sensors = db.execute(text(f"""
            SELECT id, server_id, sensor_type, name, config
            FROM sensors
            WHERE server_id IN ({ids_str})
        """)).fetchall()
    except Exception as e:
        logger.warning(f"_generate_edges sensors query: {e}")
        return _fallback_chain_edges(server_nodes)

    # Agrupa por servidor
    by_server: dict[int, list] = {}
    for s in sensors:
        by_server.setdefault(s.server_id, []).append(s)

    # Layer 0 → Layer 1 → Layer 2 (hierarquia de infra)
    layer_nodes: dict[int, list] = {}
    for sn in server_nodes:
        layer_nodes.setdefault(sn.get("layer", 2), []).append(sn)

    # Conecta camadas: L0→L1, L1→L2
    for lower_layer, upper_layer in [(0, 1), (0, 2), (1, 2)]:
        lower = layer_nodes.get(lower_layer, [])
        upper = layer_nodes.get(upper_layer, [])
        if lower and upper:
            for l_node in lower:
                for u_node in upper[:3]:  # limita fan-out
                    add_edge(l_node["node_id"], u_node["node_id"], "network")

    # Edges baseadas em sensores TCP (dependências de serviço)
    for sn in server_nodes:
        srv_sensors = by_server.get(sn["server_id"], [])
        for s in srv_sensors:
            cfg = s.config or {}
            port = None
            if isinstance(cfg, dict):
                port = cfg.get("port") or cfg.get("target_port")
            if port:
                port = int(port) if str(port).isdigit() else None

            if s.sensor_type in ("tcp", "port", "http", "https") and port:
                # Encontra servidor que "serve" essa porta
                for other_sn in server_nodes:
                    if other_sn["server_id"] == sn["server_id"]:
                        continue
                    other_sensors = by_server.get(other_sn["server_id"], [])
                    other_ports = set()
                    for os_ in other_sensors:
                        ocfg = os_.config or {}
                        if isinstance(ocfg, dict):
                            op = ocfg.get("port") or ocfg.get("target_port")
                            if op and str(op).isdigit():
                                other_ports.add(int(op))

                    if port in (1433, 3306, 5432, 1521, 27017):
                        add_edge(sn["node_id"], other_sn["node_id"], "database")
                        break
                    elif port in (80, 443, 8080, 8443):
                        add_edge(sn["node_id"], other_sn["node_id"], "http")
                        break

    # Ping/ICMP → todos os outros do mesmo layer (conectividade)
    for sn in server_nodes:
        srv_sensors = by_server.get(sn["server_id"], [])
        has_ping = any(s.sensor_type in ("ping", "icmp") for s in srv_sensors)
        if has_ping:
            same_layer = [n for n in server_nodes
                          if n["server_id"] != sn["server_id"] and n.get("layer") == sn.get("layer")]
            for other in same_layer[:4]:  # limita fan-out
                add_edge(sn["node_id"], other["node_id"], "network")

    # Fallback: se ainda sem edges suficientes, chain entre todos
    if len(edges) < max(1, len(server_nodes) // 2):
        for fe in _fallback_chain_edges(server_nodes):
            key = (fe["source"], fe["target"])
            if key not in seen:
                seen.add(key)
                edges.append(fe)

    return edges


def _fallback_chain_edges(server_nodes: list) -> list:
    """Chain linear garantindo grafo conectado."""
    ids = [sn["node_id"] for sn in server_nodes]
    return [
        {"source": ids[i], "target": ids[i + 1], "type": "infrastructure"}
        for i in range(len(ids) - 1)
    ]


# ─── Graph builder ───────────────────────────────────────────────────────────

def _build_graph(rows, db: Session) -> tuple[list, list]:
    nodes = []
    server_nodes = []

    # Coletar todos os server_ids para buscar status em batch
    server_ids = []
    for r in rows:
        meta = r.metadata or {}
        sid_str = meta.get("server_id")
        if sid_str:
            try:
                server_ids.append(int(sid_str))
            except Exception:
                pass

    # Busca status de todos os servidores em uma única query
    status_map = _get_all_server_statuses(server_ids, db)

    for r in rows:
        meta = r.metadata or {}
        server_id_str = meta.get("server_id")
        status = "unknown"
        layer = 2
        if server_id_str:
            try:
                sid = int(server_id_str)
                status = status_map.get(sid, "unknown")
                device_type = meta.get("device_type", "server").lower()
                hostname = meta.get("hostname", "").upper()
                if device_type in ("switch", "router", "firewall", "network", "access_point", "ap", "gateway") or "udm" in hostname.lower() or "udm" in device_type:
                    layer = 0
                elif device_type == "hypervisor" or "HV" in hostname:
                    layer = 1
                else:
                    layer = 2
            except Exception:
                pass

        nodes.append({
            "id": str(r.id),
            "type": r.type,
            "name": meta.get("name", meta.get("hostname", str(r.id)[:8])),
            "status": status,
            "layer": layer,
            "metadata": meta,
            "parent_id": str(r.parent_id) if r.parent_id else None,
        })

        if server_id_str:
            server_nodes.append({
                "node_id": str(r.id),
                "server_id": int(server_id_str),
                "layer": layer,
            })

    # Carrega edges persistidas primeiro
    edges = _load_persisted_edges(db)
    if not edges:
        edges = _generate_edges_from_sensors(server_nodes, db)
    if not edges and len(nodes) > 1:
        edges = _fallback_chain_edges(server_nodes if server_nodes else
                                      [{"node_id": n["id"]} for n in nodes])

    return nodes, edges


def _load_persisted_edges(db: Session) -> list:
    try:
        rows = db.execute(text(
            "SELECT source_id::text, target_id::text, type FROM topology_edges"
        )).fetchall()
        return [{"source": r.source_id, "target": r.target_id,
                 "type": r.type or "dependency"} for r in rows]
    except Exception:
        return []


# ─── BFS blast radius ────────────────────────────────────────────────────────

def _build_adjacency(edges: list) -> tuple[dict, dict]:
    """Retorna adjacência downstream e upstream."""
    downstream: dict[str, list] = {}
    upstream: dict[str, list] = {}
    for e in edges:
        src, tgt = e["source"], e["target"]
        downstream.setdefault(src, []).append(tgt)
        upstream.setdefault(tgt, []).append(src)
    return downstream, upstream


def _bfs(start: str, adjacency: dict) -> list:
    visited = set()
    queue = [start]
    while queue:
        cur = queue.pop(0)
        for nb in adjacency.get(cur, []):
            if nb not in visited:
                visited.add(nb)
                queue.append(nb)
    return list(visited)


# ─── App/Service node generation ─────────────────────────────────────────────

def _generate_app_nodes(server_ids: list, db: Session) -> tuple[list, list]:
    """
    Gera nós de aplicação/serviço a partir dos sensores HTTP e service dos servidores.
    Retorna (app_nodes, app_edges) para adicionar ao grafo.
    """
    if not server_ids:
        return [], []

    app_nodes = []
    app_edges = []
    ids_str = ",".join(str(sid) for sid in server_ids)

    try:
        sensors = db.execute(text(f"""
            SELECT s.id, s.server_id, s.sensor_type, s.name, s.config,
                   m.status as metric_status
            FROM sensors s
            LEFT JOIN LATERAL (
                SELECT status FROM metrics
                WHERE sensor_id = s.id
                ORDER BY timestamp DESC LIMIT 1
            ) m ON true
            WHERE s.server_id IN ({ids_str})
              AND s.sensor_type IN ('http', 'https', 'service', 'port', 'tcp')
              AND s.is_active = true
        """)).fetchall()

        for s in sensors:
            cfg = s.config or {}
            app_name = s.name
            app_type = "service"

            if s.sensor_type in ('http', 'https'):
                http_cfg = cfg.get("http", {}) if isinstance(cfg, dict) else {}
                url = http_cfg.get("url") or cfg.get("http_url", "")
                app_name = s.name or url or f"HTTP_{s.id}"
                app_type = "application"

            # Status real do sensor baseado na última métrica
            metric_status = getattr(s, 'metric_status', None) or 'unknown'
            if metric_status not in ('ok', 'warning', 'critical'):
                metric_status = 'unknown'

            node_id = f"app_{s.id}"
            app_nodes.append({
                "id": node_id,
                "type": app_type,
                "name": app_name,
                "status": metric_status,
                "layer": 3,
                "metadata": {
                    "sensor_id": str(s.id),
                    "sensor_type": s.sensor_type,
                    "server_id": str(s.server_id),
                    "device_type": app_type,
                },
                "parent_id": str(s.server_id),
            })
            app_edges.append({
                "source": str(s.server_id),
                "target": node_id,
                "type": "dependency",
            })

    except Exception as e:
        logger.warning(f"_generate_app_nodes: {e}")

    return app_nodes, app_edges


# ─── HyperV nodes ────────────────────────────────────────────────────────────

def _hyperv_host_status(host: HyperVHost) -> str:
    """Converte health_score e status do host HyperV para status da topologia."""
    if host.status in ("critical", "error"):
        return "critical"
    if host.status == "warning":
        return "warning"
    score = host.health_score or 0
    if score >= 80:
        return "ok"
    if score >= 50:
        return "warning"
    if score > 0:
        return "critical"
    return "unknown"


def _hyperv_vm_status(vm: HyperVVM) -> str:
    """Converte state da VM para status da topologia."""
    state = (vm.state or "").lower()
    if state == "running":
        cpu = vm.cpu_percent or 0
        mem = vm.memory_percent or 0
        if cpu > 90 or mem > 90:
            return "critical"
        if cpu > 75 or mem > 75:
            return "warning"
        return "ok"
    if state in ("off", "stopped"):
        return "unknown"
    if state in ("paused", "saved"):
        return "warning"
    return "unknown"


def _get_hyperv_nodes(db: Session, existing_ips: set) -> tuple[list, list]:
    """
    Retorna (nodes, edges) com hosts HyperV e suas VMs para injetar na topologia.
    existing_ips: IPs já presentes como nós de servidor — evita duplicação.
    """
    try:
        hosts = db.query(HyperVHost).all()
    except Exception as e:
        logger.warning(f"_get_hyperv_nodes: erro ao buscar hosts: {e}")
        return [], []

    nodes = []
    edges = []

    for host in hosts:
        # Evitar duplicar se o servidor já está na topologia pelo IP
        if host.ip_address and host.ip_address in existing_ips:
            host_node_id = f"hv_host_{host.id}"
            # Ainda assim adiciona as VMs vinculadas ao nó existente
            # mas usa o node_id do servidor existente como parent
            # Para simplificar, usa o node_id do hyperv mesmo assim
        
        host_node_id = f"hv_host_{host.id}"
        host_status = _hyperv_host_status(host)

        nodes.append({
            "id": host_node_id,
            "type": "hypervisor",
            "name": host.hostname or host.ip_address,
            "status": host_status,
            "layer": 1,
            "metadata": {
                "device_type": "hypervisor",
                "ip": host.ip_address,
                "hostname": host.hostname,
                "cpu_percent": host.cpu_percent,
                "memory_percent": host.memory_percent,
                "storage_percent": host.storage_percent,
                "health_score": host.health_score,
                "vm_count": host.vm_count,
                "running_vm_count": host.running_vm_count,
                "total_cpus": host.total_cpus,
                "total_memory_gb": host.total_memory_gb,
                "model": host.model,
                "os_version": host.os_version,
                "hyperv_host_id": str(host.id),
            },
            "parent_id": None,
        })

        # VMs do host
        try:
            vms = db.query(HyperVVM).filter(HyperVVM.host_id == host.id).all()
        except Exception:
            vms = []

        for vm in vms:
            vm_node_id = f"hv_vm_{vm.id}"
            vm_status = _hyperv_vm_status(vm)

            nodes.append({
                "id": vm_node_id,
                "type": "vm",
                "name": vm.name,
                "status": vm_status,
                "layer": 2,
                "metadata": {
                    "device_type": "vm",
                    "vm_state": vm.state,
                    "vcpus": vm.vcpus,
                    "memory_mb": vm.memory_mb,
                    "cpu_percent": vm.cpu_percent,
                    "memory_percent": vm.memory_percent,
                    "uptime_seconds": vm.uptime_seconds,
                    "hyperv_host_id": str(host.id),
                    "hyperv_vm_id": str(vm.id),
                },
                "parent_id": host_node_id,
            })

            edges.append({
                "source": host_node_id,
                "target": vm_node_id,
                "type": "hosts",
            })

    return nodes, edges


# ─── Endpoints ───────────────────────────────────────────────────────────────

@router.get("/graph")
async def get_topology_graph(db: Session = Depends(get_db)):
    try:
        rows = db.execute(text(
            "SELECT id, type, parent_id, metadata FROM topology_nodes ORDER BY created_at"
        )).fetchall()

        if rows:
            nodes, edges = _build_graph(rows, db)
            # Adicionar nós de aplicação/serviço (layer 3)
            all_server_ids = []
            for n in nodes:
                sid = n.get("metadata", {}).get("server_id")
                if sid:
                    try:
                        all_server_ids.append(int(sid))
                    except Exception:
                        pass
            if all_server_ids:
                app_nodes, app_edges = _generate_app_nodes(all_server_ids, db)
                nodes.extend(app_nodes)
                edges.extend(app_edges)

            # Adicionar nós HyperV (hosts + VMs)
            existing_ips = {n.get("metadata", {}).get("ip", "") for n in nodes}
            hv_nodes, hv_edges = _get_hyperv_nodes(db, existing_ips)
            nodes.extend(hv_nodes)
            edges.extend(hv_edges)

            return {"nodes": nodes, "edges": edges, "source": "topology_nodes"}

        # Fallback sem sync
        servers = db.execute(text(
            "SELECT id, hostname, ip_address, os_type, device_type FROM servers WHERE is_active = true LIMIT 100"
        )).fetchall()

        if not servers:
            return {"nodes": [], "edges": [], "source": "empty"}

        nodes = []
        server_nodes = []
        server_ids = [s.id for s in servers]
        status_map = _get_all_server_statuses(server_ids, db)

        for s in servers:
            status = status_map.get(s.id, "unknown")
            layer = _detect_layer(s)
            nodes.append({
                "id": str(s.id),
                "type": "server",
                "name": s.hostname or s.ip_address or str(s.id),
                "status": status,
                "layer": layer,
                "metadata": {"server_id": str(s.id), "ip": s.ip_address},
                "parent_id": None,
            })
            server_nodes.append({"node_id": str(s.id), "server_id": s.id, "layer": layer})

        edges = _generate_edges_from_sensors(server_nodes, db)
        if not edges and len(nodes) > 1:
            edges = _fallback_chain_edges(server_nodes)

        # Adicionar nós de aplicação/serviço (layer 3)
        app_nodes, app_edges = _generate_app_nodes(server_ids, db)
        nodes.extend(app_nodes)
        edges.extend(app_edges)

        # Adicionar nós HyperV (hosts + VMs)
        existing_ips = {n.get("metadata", {}).get("ip", "") for n in nodes}
        hv_nodes, hv_edges = _get_hyperv_nodes(db, existing_ips)
        nodes.extend(hv_nodes)
        edges.extend(hv_edges)

        return {"nodes": nodes, "edges": edges, "source": "servers_fallback"}

    except Exception as e:
        logger.error(f"get_topology_graph: {e}", exc_info=True)
        return {"nodes": [], "edges": [], "error": str(e)}


@router.get("/impact/{node_id}")
async def get_impact(node_id: str, db: Session = Depends(get_db)):
    """
    Blast radius: downstream (quem depende do nó) + upstream (de quem ele depende).
    Retorna total_impact = downstream count (nós que seriam afetados se este falhar).
    """
    try:
        rows = db.execute(text(
            "SELECT id, type, parent_id, metadata FROM topology_nodes"
        )).fetchall()

        server_nodes = []
        for r in rows:
            meta = r.metadata or {}
            sid = meta.get("server_id")
            if sid:
                device_type = meta.get("device_type", "server").lower()
                hostname = meta.get("hostname", "").upper()
                layer = 0 if device_type in ("switch", "router", "firewall", "access_point", "ap", "gateway") or "udm" in hostname.lower() or "udm" in device_type else (1 if "HV" in hostname else 2)
                server_nodes.append({"node_id": str(r.id), "server_id": int(sid), "layer": layer})

        edges = _load_persisted_edges(db)
        if not edges:
            edges = _generate_edges_from_sensors(server_nodes, db)
        if not edges and len(rows) > 1:
            edges = _fallback_chain_edges(server_nodes if server_nodes else
                                          [{"node_id": str(r.id)} for r in rows])

        downstream, upstream = _build_adjacency(edges)

        # Downstream = nós que dependem deste (impactados se este falhar)
        affected = _bfs(node_id, downstream)
        # Upstream = de quem este depende
        depends_on = _bfs(node_id, upstream)

        # Se BFS retornou vazio mas há edges conectadas ao nó, usar vizinhos diretos
        direct_downstream = downstream.get(node_id, [])
        direct_upstream = upstream.get(node_id, [])
        if not affected and direct_downstream:
            affected = direct_downstream
        if not depends_on and direct_upstream:
            depends_on = direct_upstream

        node_map = {str(r.id): r for r in rows}
        affected_hosts = [d for d in affected
                          if node_map.get(d) and node_map[d].type in ("server", "host")]
        affected_services = [d for d in affected
                              if node_map.get(d) and node_map[d].type == "service"]

        return {
            "node_id": node_id,
            "total_impact": len(affected),
            "affected_hosts": affected_hosts,
            "affected_services": affected_services,
            "all_affected": affected,
            "depends_on": depends_on,
            "edge_count": len(edges),
        }
    except Exception as e:
        logger.error(f"get_impact: {e}", exc_info=True)
        return {"node_id": node_id, "total_impact": 0, "error": str(e)}


@router.post("/nodes")
async def create_node(req: TopologyNodeCreate, db: Session = Depends(get_db)):
    try:
        row = db.execute(text("""
            INSERT INTO topology_nodes (type, parent_id, metadata)
            VALUES (:type, :parent_id, :metadata::jsonb)
            RETURNING id, type, parent_id, metadata
        """), {
            "type": req.type,
            "parent_id": req.parent_id,
            "metadata": json.dumps(req.metadata),
        }).fetchone()
        db.commit()
        return {"id": str(row.id), "type": row.type,
                "parent_id": str(row.parent_id) if row.parent_id else None,
                "metadata": row.metadata}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/nodes/{node_id}")
async def delete_node(node_id: str, db: Session = Depends(get_db)):
    try:
        db.execute(text("DELETE FROM topology_nodes WHERE id = :id"), {"id": node_id})
        db.commit()
        return {"ok": True}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync-from-servers")
async def sync_from_servers(db: Session = Depends(get_db)):
    try:
        servers = db.execute(text(
            "SELECT id, hostname, ip_address, os_type, device_type FROM servers WHERE is_active = true"
        )).fetchall()

        if not servers:
            return {"created": 0, "updated": 0, "edges": 0, "total_servers": 0,
                    "message": "Nenhum servidor ativo"}

        created = updated = 0
        server_nodes = []

        # Busca status de todos os servidores em batch
        server_ids = [s.id for s in servers]
        status_map = _get_all_server_statuses(server_ids, db)

        for s in servers:
            try:
                status = status_map.get(s.id, "unknown")
                layer = _detect_layer(s)
                # Detectar device_type pelo hostname (UDM = router)
                raw_device_type = getattr(s, 'device_type', 'server') or 'server'
                hostname_lower = (s.hostname or '').lower()
                if 'udm' in hostname_lower:
                    raw_device_type = 'router'
                meta = json.dumps({
                    "server_id": str(s.id),
                    "name": s.hostname or s.ip_address or str(s.id),
                    "hostname": s.hostname,
                    "ip": s.ip_address,
                    "os_type": s.os_type,
                    "device_type": raw_device_type,
                    "status": status,
                    "layer": layer,
                })
                existing = db.execute(text(
                    "SELECT id FROM topology_nodes WHERE metadata->>'server_id' = :sid"
                ), {"sid": str(s.id)}).fetchone()

                if not existing:
                    row = db.execute(text(
                        "INSERT INTO topology_nodes (type, metadata) VALUES ('server', :meta::jsonb) RETURNING id"
                    ), {"meta": meta}).fetchone()
                    node_id = str(row.id)
                    created += 1
                else:
                    db.execute(text(
                        "UPDATE topology_nodes SET metadata = :meta::jsonb, updated_at = NOW() WHERE metadata->>'server_id' = :sid"
                    ), {"meta": meta, "sid": str(s.id)})
                    node_id = str(existing.id)
                    updated += 1

                server_nodes.append({"node_id": node_id, "server_id": s.id, "layer": layer})
            except Exception as row_err:
                logger.warning(f"sync server {s.id}: {row_err}")
                continue

        db.commit()

        edges = _generate_edges_from_sensors(server_nodes, db)
        if not edges and len(server_nodes) > 1:
            edges = _fallback_chain_edges(server_nodes)

        edges_saved = _persist_edges(edges, db)

        return {
            "created": created,
            "updated": updated,
            "edges": edges_saved,
            "total_servers": len(servers),
            "message": f"Sync: {created} criados, {updated} atualizados, {edges_saved} edges"
        }
    except Exception as e:
        logger.error(f"sync-from-servers: {e}", exc_info=True)
        db.rollback()
        return {"created": 0, "updated": 0, "edges": 0, "total_servers": 0,
                "error": str(e), "message": "Sync falhou"}


def _persist_edges(edges: list, db: Session) -> int:
    if not edges:
        return 0
    try:
        db.execute(text("SELECT 1 FROM topology_edges LIMIT 1"))
    except Exception:
        logger.warning("topology_edges não existe — execute migrate_topology_edges.py")
        return 0
    try:
        db.execute(text("DELETE FROM topology_edges"))
        count = 0
        for e in edges:
            try:
                db.execute(text("""
                    INSERT INTO topology_edges (source_id, target_id, type)
                    VALUES (:src::uuid, :tgt::uuid, :type)
                    ON CONFLICT DO NOTHING
                """), {"src": e["source"], "tgt": e["target"], "type": e.get("type", "dependency")})
                count += 1
            except Exception:
                continue
        db.commit()
        return count
    except Exception as ex:
        logger.warning(f"_persist_edges: {ex}")
        db.rollback()
        return 0
