"""
Service Map Router — Coruja Monitor v3.5 Enterprise
GET /api/v1/service-map — grafo de dependências
GET /api/v1/service-map/impact/{node_id} — raio de impacto
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from topology_engine.service_map import ServiceMap

router = APIRouter(prefix="/api/v1/service-map", tags=["Service Map"])


@router.get("")
def get_service_map(db: Session = Depends(get_db)):
    """Retorna grafo completo de serviços e dependências."""
    smap = ServiceMap.build_from_db(db)
    return smap.to_dict()


@router.get("/impact/{node_id}")
def get_impact_radius(node_id: str, db: Session = Depends(get_db)):
    """Retorna nós impactados por falha em node_id."""
    smap = ServiceMap.build_from_db(db)
    impacted = smap.get_impact_radius(node_id)
    node = smap._nodes.get(node_id)
    return {
        "node_id": node_id,
        "node_name": node.name if node else node_id,
        "impacted_nodes": impacted,
        "impact_count": len(impacted),
    }
