"""
Hyper-V Cost Config API — Coruja Monitor
GET /api/v1/hyperv/cost-config — retorna todos os itens de custo
PUT /api/v1/hyperv/cost-config — atualiza valores (batch)
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone

from database import get_db
from auth import get_current_active_user
from models import User

router = APIRouter(prefix="/api/v1/hyperv/cost-config", tags=["Hyper-V Cost Config"])


class CostItem(BaseModel):
    id: Optional[int] = None
    key: str
    label: str
    category: str
    value: float
    unit: Optional[str] = ""
    editable: Optional[bool] = True
    sort_order: Optional[int] = 0


class CostConfigResponse(BaseModel):
    items: List[CostItem]
    total_mensal: float
    reajuste_anual: float
    cost_vcpu: float
    cost_ram_gb: float
    cost_disk_gb: float
    cost_ip: float


class CostUpdateRequest(BaseModel):
    items: List[dict]  # [{key: str, value: float}, ...]


@router.get("", response_model=CostConfigResponse)
async def get_cost_config(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    rows = db.execute(
        text("SELECT id, key, label, category, value, unit, editable, sort_order FROM hyperv_cost_config ORDER BY sort_order")
    ).fetchall()

    items = []
    config = {}
    for r in rows:
        items.append(CostItem(id=r[0], key=r[1], label=r[2], category=r[3], value=r[4], unit=r[5] or "", editable=r[6], sort_order=r[7]))
        config[r[1]] = r[4]

    # Calculate totals
    infra_cats = ("infra", "rede", "software", "hardware", "pessoal")
    total = sum(i.value for i in items if i.category in infra_cats)
    reajuste = config.get("reajuste_anual", 0)
    if reajuste > 0:
        total *= (1 + reajuste / 100)

    # Unit costs from weights
    peso_cpu = config.get("peso_cpu", 40) / 100
    peso_ram = config.get("peso_ram", 25) / 100
    peso_disco = config.get("peso_disco", 25) / 100
    peso_rede = config.get("peso_rede", 10) / 100
    total_vcpus = config.get("total_vcpus", 1024) or 1
    total_ram = config.get("total_ram_gb", 1024) or 1
    total_disco = config.get("total_disco_gb", 28000) or 1
    total_ips = config.get("total_ips", 16) or 1

    return CostConfigResponse(
        items=items,
        total_mensal=round(total, 2),
        reajuste_anual=reajuste,
        cost_vcpu=round(total * peso_cpu / total_vcpus, 2),
        cost_ram_gb=round(total * peso_ram / total_ram, 2),
        cost_disk_gb=round(total * peso_disco / total_disco, 2),
        cost_ip=round(total * peso_rede / total_ips, 2),
    )


@router.put("")
async def update_cost_config(
    req: CostUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    updated = 0
    for item in req.items:
        key = item.get("key")
        value = item.get("value")
        if key is None or value is None:
            continue
        db.execute(
            text("UPDATE hyperv_cost_config SET value = :val, updated_at = :now WHERE key = :key"),
            {"val": float(value), "now": datetime.now(timezone.utc), "key": key}
        )
        updated += 1
    db.commit()
    return {"status": "ok", "updated": updated}


def get_cost_map(db):
    """Return dict of cost config values for use by FinOps engine."""
    rows = db.execute(
        text("SELECT key, value FROM hyperv_cost_config")
    ).fetchall()
    return {r[0]: r[1] for r in rows} if rows else {}
