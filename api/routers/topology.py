"""
Topology Router — Coruja Monitor v3.0
Grafo real: nodes + edges + status via métricas + blast radius BFS.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from typing import Optional
import logging
import json
from database import get_db

router = APIRouter(prefix="/api/v1/topology", tags=["Topology v3"])
logger = logging.getLogger(__name__)


# ─── Schemas ─────────────────────────────────────────────────────────────────

class TopologyNodeCreate(BaseModel):
    type: str
    parent_id: Optional[str] = None
    metadata: dict = {}


# ─── Status helper ───────────────────────────────────────────────────────────

def _get_server_status(server_id: int, db: Session) -> str:
    """Deriva status via última métrica de cada sensor (mesma lógica do observability)."""
    try:
        row = db.execute(text("""
            WITH latest AS (
                SELECT DISTINCT ON (sen.id)
                    sen.id,
                    m.status
                FROM sensors sen
                LEFT JOIN metrics m ON m.sensor_id = sen.id
                WHERE sen.server_id = :sid
                ORDER BY sen.id, m.timestamp DESC
            )
            SELECT
                COUNT(*) FILTER (WHERE status = 'critical') AS critical_count,
                COUNT(*) FILTER (WHERE status = 'warning')  AS warning_count,
                COUNT(*) AS total
            FROM latest
        """), {"sid": server_id}).fetchone()

        if not row or row.total == 0:
            return "unknown"
        if row.critical_count > 0:
            return "critical"
        if row.warning_count > 0:
            return "warning"
        return "ok"
    except Exception:
        return "unknown"


# ─── Edge generation ─────────────────────────────────────────────────────────

def _generate_edges_from_sensors(server_nodes: list, db: Session) -> list:
    """
    Gera edges reais baseados nos sensores de cada servidor.
    Regras:
      1. Ping → todos os outros sensores do mesmo host (dependência de conectividade)
      2. Sensor TCP porta 1433 → marca dependência de banco
      3. Fallback: chain linear se nenhuma relação encontrada
    """
    edges = []
    # server_nodes: list of dicts com {node_id, server_id}
    server_id_to_node = {sn["server_id"]: sn["node_id"] for sn in server_nodes}

    if not server_id_to_node:
        return edges

    try:
        # Busca todos os sensores dos servidores relevantes
        ids_placeholder = ",".join(str(i) for i in server_id_to_node.keys())
        sensors = db.execute(text(f"""
            SELECT id, server_id, sensor_type, name, config
            FROM sensors
            WHERE server_id IN ({ids_placeholder})
            ORDER BY server_id, sensor_type
        """)).fetchall()
    except Exception as e:
        logger.warning(f"_generate_edges_from_sensors: {e}")
        return _fallback_chain_edges(list(server_id_to_node.values()))

    # Agrupa sensores por servidor
    by_server: dict[int, list] = {}
    for s in sensors:
        by_server.setdefault(s.server_id, []).append(s)

    seen = set()

    def add_edge(src, tgt, etype="dependency"):
        key = (src, tgt)
        if key not in seen and src != tgt:
            seen.add(key)
            edges.append({"source": src, "target": tgt, "type": etype})

    for server_id, node_id in server_id_to_node.items():
        srv_sensors = by_server.get(server_id, [])
        ping_sensors = [s for s in srv_sensors if s.sensor_type in ("ping", "icmp")]
        other_sensors = [s for s in srv_sensors if s.sensor_type not in ("ping", "icmp")]

        # Ping → outros sensores do mesmo host (conectividade é pré-requisito)
        for ping in ping_sensors:
            for other in other_sensors:
                # Cria nó virtual para o sensor se quisermos granularidade
                # Por ora: ping node → server node (self-loop representando dependência interna)
                pass  # edges entre servers, não entre sensors

        # Dependência entre servidores via TCP
        for s in srv_sensors:
            if s.sensor_type in ("tcp", "port"):
                cfg = s.config or {}
                port = cfg.get("port") if isinstance(cfg, dict) else None
                # SQL Server → relaciona com outros servidores que têm sensores WMI/SNMP
                if port in (1433, 3306, 5432, 1521):
                    for other_sid, other_nid in server_id_to_node.items():
                        if other_sid != server_id:
                            add_edge(node_id, other_nid, "database")
                            break  # apenas 1 relação de banco por servidor
                # HTTP/HTTPS → relaciona como serviço web
                elif port in (80, 443, 8080, 8443):
                    for other_sid, other_nid in server_id_to_node.items():
                        if other_sid != server_id:
                            add_edge(other_nid, node_id, "http")
                            break

    # Se ainda não temos edges suficientes, cria chain entre todos os nós
    # (representa que todos dependem da infraestrutura base)
    if len(edges) < max(1, len(server_id_to_node) // 2):
        chain = _fallback_chain_edges(list(server_id_to_node.values()))
        for e in chain:
            key = (e["source"], e["target"])
            if key not in seen:
                seen.add(key)
                edges.append(e)

    return edges


def _fallback_chain_edges(node_ids: list) -> list:
    """Garante grafo conectado: chain linear entre todos os nós."""
    edges = []
    for i in range(len(node_ids) - 1):
        edges.append({
            "source": node_ids[i],
            "target": node_ids[i + 1],
            "type": "infrastructure"
        })
    return edges


# ─── Graph builder ───────────────────────────────────────────────────────────

def _build_graph(rows, db: Session) -> tuple[list, list]:
    """Constrói nodes + edges com status em tempo real."""
    nodes = []
    server_nodes = []  # para geração de edges

    for r in rows:
        meta = r.metadata or {}
        server_id_str = meta.get("server_id")
        status = "unknown"
        if server_id_str:
            try:
                status = _get_server_status(int(server_id_str), db)
            except Exception:
                pass

        node = {
            "id": str(r.id),
            "type": r.type,
            "name": meta.get("name", meta.get("hostname", str(r.id)[:8])),
            "status": status,
            "metadata": meta,
            "parent_id": str(r.parent_id) if r.parent_id else None,
        }
        nodes.append(node)

        if server_id_str:
            server_nodes.append({"node_id": str(r.id), "server_id": int(server_id_str)})

    # Edges: primeiro tenta topology_edges persistidas
    edges = _load_persisted_edges(db)

    # Se não há edges persistidas, gera dinamicamente
    if not edges:
        edges = _generate_edges_from_sensors(server_nodes, db)

    # Fallback absoluto: nunca retornar grafo sem edges se há >1 nó
    if not edges and len(nodes) > 1:
        edges = _fallback_chain_edges([n["id"] for n in nodes])

    return nodes, edges


def _load_persisted_edges(db: Session) -> list:
    """Carrega edges da tabela topology_edges se existir."""
    try:
        rows = db.execute(text(
            "SELECT source_id, target_id, type FROM topology_edges"
        )).fetchall()
        return [{"source": str(r.source_id), "target": str(r.target_id), "type": r.type or "dependency"} for r in rows]
    except Exception:
        return []


# ─── BFS blast radius ────────────────────────────────────────────────────────

def _bfs_descendants(node_id: str, adjacency: dict[str, list]) -> list:
    """BFS para calcular todos os nós afetados downstream."""
    visited = set()
    queue = [node_id]
    while queue:
        current = queue.pop(0)
        for neighbor in adjacency.get(current, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return list(visited)


# ─── Endpoints ───────────────────────────────────────────────────────────────

@router.get("/graph")
async def get_topology_graph(db: Session = Depends(get_db)):
    """Retorna grafo completo com nodes, edges e status em tempo real."""
    try:
        rows = db.execute(text(
            "SELECT id, type, parent_id, metadata FROM topology_nodes ORDER BY created_at"
        )).fetchall()

        if rows:
            nodes, edges = _build_graph(rows, db)
            return {"nodes": nodes, "edges": edges, "source": "topology_nodes"}

        # Fallback: servidores monitorados sem sync prévio
        servers = db.execute(text(
            "SELECT id, hostname, ip_address FROM servers WHERE is_active = true LIMIT 100"
        )).fetchall()

        if not servers:
            return {"nodes": [], "edges": [], "source": "empty"}

        nodes = []
        for s in servers:
            status = _get_server_status(s.id, db)
            nodes.append({
                "id": str(s.id),
                "type": "server",
                "name": s.hostname or s.ip_address or str(s.id),
                "status": status,
                "metadata": {"server_id": str(s.id), "ip": s.ip_address},
                "parent_id": None,
            })

        edges = _generate_edges_from_sensors(
            [{"node_id": str(s.id), "server_id": s.id} for s in servers], db
        )
        if not edges and len(nodes) > 1:
            edges = _fallback_chain_edges([n["id"] for n in nodes])

        return {"nodes": nodes, "edges": edges, "source": "servers_fallback"}

    except Exception as e:
        logger.error(f"get_topology_graph error: {e}", exc_info=True)
        return {"nodes": [], "edges": [], "error": str(e)}


@router.get("/impact/{node_id}")
async def get_impact(node_id: str, db: Session = Depends(get_db)):
    """Calcula blast radius real via BFS no grafo de dependências."""
    try:
        rows = db.execute(text(
            "SELECT id, type, parent_id, metadata FROM topology_nodes"
        )).fetchall()

        # Constrói adjacência a partir de edges
        server_nodes = []
        for r in rows:
            meta = r.metadata or {}
            sid = meta.get("server_id")
            if sid:
                server_nodes.append({"node_id": str(r.id), "server_id": int(sid)})

        edges = _load_persisted_edges(db)
        if not edges:
            edges = _generate_edges_from_sensors(server_nodes, db)
        if not edges and len(rows) > 1:
            edges = _fallback_chain_edges([str(r.id) for r in rows])

        # Monta adjacência direcional
        adjacency: dict[str, list] = {}
        for e in edges:
            adjacency.setdefault(e["source"], []).append(e["target"])

        descendants = _bfs_descendants(node_id, adjacency)

        node_map = {str(r.id): r for r in rows}
        affected_hosts = [d for d in descendants if node_map.get(d) and node_map[d].type in ("server", "host")]
        affected_services = [d for d in descendants if node_map.get(d) and node_map[d].type == "service"]

        return {
            "node_id": node_id,
            "total_impact": len(descendants),
            "affected_hosts": affected_hosts,
            "affected_services": affected_services,
            "all_affected": descendants,
        }
    except Exception as e:
        logger.error(f"get_impact error: {e}", exc_info=True)
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
        return {
            "id": str(row.id),
            "type": row.type,
            "parent_id": str(row.parent_id) if row.parent_id else None,
            "metadata": row.metadata,
        }
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
    """
    Popula/atualiza topology_nodes + gera e persiste topology_edges.
    """
    try:
        servers = db.execute(text(
            "SELECT id, hostname, ip_address, os_type FROM servers WHERE is_active = true"
        )).fetchall()

        if not servers:
            return {"created": 0, "updated": 0, "edges": 0, "total_servers": 0,
                    "message": "Nenhum servidor ativo encontrado"}

        created = 0
        updated = 0
        server_nodes = []

        for s in servers:
            try:
                status = _get_server_status(s.id, db)
                meta = json.dumps({
                    "server_id": str(s.id),
                    "name": s.hostname or s.ip_address or str(s.id),
                    "hostname": s.hostname,
                    "ip": s.ip_address,
                    "os_type": s.os_type,
                    "status": status,
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

                server_nodes.append({"node_id": node_id, "server_id": s.id})

            except Exception as row_err:
                logger.warning(f"sync servidor {s.id}: {row_err}")
                continue

        db.commit()

        # Gera e persiste edges
        edges = _generate_edges_from_sensors(server_nodes, db)
        if not edges and len(server_nodes) > 1:
            edges = _fallback_chain_edges([sn["node_id"] for sn in server_nodes])

        edges_saved = _persist_edges(edges, db)

        return {
            "created": created,
            "updated": updated,
            "edges": edges_saved,
            "total_servers": len(servers),
            "message": f"Sync concluído: {created} criados, {updated} atualizados, {edges_saved} edges geradas"
        }

    except Exception as e:
        logger.error(f"sync-from-servers error: {e}", exc_info=True)
        db.rollback()
        return {"created": 0, "updated": 0, "edges": 0, "total_servers": 0,
                "error": str(e), "message": "Sync falhou"}


def _persist_edges(edges: list, db: Session) -> int:
    """Persiste edges na tabela topology_edges (upsert)."""
    if not edges:
        return 0
    try:
        # Verifica se tabela existe
        db.execute(text("SELECT 1 FROM topology_edges LIMIT 1"))
    except Exception:
        logger.warning("topology_edges não existe — execute migrate_topology_edges.py")
        return 0

    try:
        # Limpa edges antigas e reinsere
        db.execute(text("DELETE FROM topology_edges"))
        count = 0
        for e in edges:
            try:
                db.execute(text("""
                    INSERT INTO topology_edges (source_id, target_id, type)
                    VALUES (:src, :tgt, :type)
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
