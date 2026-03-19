"""
Topology Router — Coruja Monitor v3.0
Endpoints REST para topologia de rede e blast radius.
Lê/escreve na tabela topology_nodes (criada pelo migrate_v3.py).
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from typing import Optional
from database import get_db

router = APIRouter(prefix="/api/v1/topology", tags=["Topology v3"])


# ─── Schemas ─────────────────────────────────────────────────────────────────

class TopologyNodeCreate(BaseModel):
    type: str          # switch, server, service, application
    parent_id: Optional[str] = None
    metadata: dict = {}


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _build_graph(rows):
    """Constrói nodes/edges a partir das linhas do banco."""
    nodes = []
    edges = []
    for r in rows:
        meta = r.metadata or {}
        nodes.append({
            "id": str(r.id),
            "type": r.type,
            "name": meta.get("name", meta.get("hostname", str(r.id)[:8])),
            "status": meta.get("status", "unknown"),
            "metadata": meta,
            "parent_id": str(r.parent_id) if r.parent_id else None,
        })
        if r.parent_id:
            edges.append({"source": str(r.parent_id), "target": str(r.id)})
    return nodes, edges


def _get_descendants(node_id: str, all_rows) -> list:
    """Retorna todos os descendentes de um nó recursivamente."""
    children = [r for r in all_rows if r.parent_id and str(r.parent_id) == node_id]
    result = [str(c.id) for c in children]
    for c in children:
        result.extend(_get_descendants(str(c.id), all_rows))
    return result


# ─── Endpoints ───────────────────────────────────────────────────────────────

@router.get("/graph")
async def get_topology_graph(db: Session = Depends(get_db)):
    """
    Retorna grafo completo de topologia.
    Também injeta servidores monitorados como nós se topology_nodes estiver vazio.
    """
    try:
        rows = db.execute(text(
            "SELECT id, type, parent_id, metadata FROM topology_nodes ORDER BY created_at"
        )).fetchall()

        if rows:
            nodes, edges = _build_graph(rows)
            return {"nodes": nodes, "edges": edges, "source": "topology_nodes"}

        # Fallback: construir topologia a partir dos servidores monitorados
        servers = db.execute(text(
            "SELECT id, name, ip_address FROM servers WHERE is_active = true LIMIT 100"
        )).fetchall()

        if not servers:
            return {"nodes": [], "edges": [], "source": "empty"}

        nodes = []
        for s in servers:
            nodes.append({
                "id": str(s.id),
                "type": "server",
                "name": s.name or s.ip_address or str(s.id),
                "status": "unknown",
                "metadata": {"ip": s.ip_address},
                "parent_id": None,
            })

        return {"nodes": nodes, "edges": [], "source": "servers_fallback"}

    except Exception as e:
        return {"nodes": [], "edges": [], "error": str(e)}


@router.get("/impact/{node_id}")
async def get_impact(node_id: str, db: Session = Depends(get_db)):
    """Calcula blast radius de um nó."""
    try:
        rows = db.execute(text(
            "SELECT id, type, parent_id, metadata FROM topology_nodes"
        )).fetchall()

        descendants = _get_descendants(node_id, rows)

        affected_hosts = [d for d in descendants
                          if any(str(r.id) == d and r.type in ("server", "host") for r in rows)]
        affected_services = [d for d in descendants
                             if any(str(r.id) == d and r.type == "service" for r in rows)]

        return {
            "node_id": node_id,
            "total_impact": len(descendants),
            "affected_hosts": affected_hosts,
            "affected_services": affected_services,
            "all_affected": descendants,
        }
    except Exception as e:
        return {"node_id": node_id, "total_impact": 0, "error": str(e)}


@router.post("/nodes")
async def create_node(req: TopologyNodeCreate, db: Session = Depends(get_db)):
    """Cria nó de topologia manualmente."""
    try:
        import json
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
    """Remove nó de topologia."""
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
    Popula topology_nodes a partir dos servidores monitorados.
    Útil para inicializar a topologia sem descoberta SNMP.
    """
    try:
        import json
        servers = db.execute(text(
            "SELECT id, name, ip_address FROM servers WHERE is_active = true"
        )).fetchall()

        created = 0
        for s in servers:
            existing = db.execute(text(
                "SELECT id FROM topology_nodes WHERE metadata->>'server_id' = :sid"
            ), {"sid": str(s.id)}).fetchone()

            if not existing:
                db.execute(text("""
                    INSERT INTO topology_nodes (type, metadata)
                    VALUES ('server', :meta::jsonb)
                """), {"meta": json.dumps({
                    "server_id": str(s.id),
                    "name": s.name or s.ip_address,
                    "hostname": s.name,
                    "ip": s.ip_address,
                    "status": "unknown",
                })})
                created += 1

        db.commit()
        return {"created": created, "total_servers": len(servers)}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
