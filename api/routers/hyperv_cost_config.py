"""
Hyper-V Cost Config API — Coruja Monitor
GET  /api/v1/hyperv/cost-config       → lista custos editáveis
PUT  /api/v1/hyperv/cost-config       → atualiza custos
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, List
from datetime import datetime, timezone

from database import get_db
from auth import get_current_active_user
from models import User
from sqlalchemy.orm import Session
from sqlalchemy import text

router = APIRouter(prefix="/api/v1/hyperv/cost-config", tags=["Hyper-V Cost Config"])


class CostConfigItem(BaseModel):
    key: str
    value: float
    label: str
    unit: str


class CostConfigResponse(BaseModel):
    items: List[CostConfigItem]


class CostConfigUpdate(BaseModel):
    costs: Dict[str, float]  # {"cost_vcpu": 19.70, "cost_ram_gb": 12.31, ...}


# ── Defaults (fallback if table doesn't exist yet) ──
DEFAULTS = {
    "cost_vcpu":    {"value": 19.70,  "label": "Custo vCPU",       "unit": "R$/vCPU/mês"},
    "cost_ram_gb":  {"value": 12.31,  "label": "Custo RAM",        "unit": "R$/GB/mês"},
    "cost_disk_gb": {"value": 0.45,   "label": "Custo Disco",      "unit": "R$/GB/mês"},
    "cost_ip":      {"value": 315.18, "label": "Custo IP Público", "unit": "R$/IP/mês"},
}


def get_cost_map(db: Session) -> Dict[str, float]:
    """Return {key: value} dict from DB, with fallback to defaults."""
    try:
        rows = db.execute(text("SELECT key, value FROM hyperv_cost_config")).fetchall()
        if rows:
            return {r[0]: float(r[1]) for r in rows}
    except Exception:
        pass
    return {k: v["value"] for k, v in DEFAULTS.items()}


@router.get("/", response_model=CostConfigResponse)
async def get_cost_config(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Lista custos editáveis do FinOps Hyper-V."""
    try:
        rows = db.execute(
            text("SELECT key, value, label, unit FROM hyperv_cost_config ORDER BY id")
        ).fetchall()
        if rows:
            return CostConfigResponse(
                items=[CostConfigItem(key=r[0], value=float(r[1]), label=r[2], unit=r[3]) for r in rows]
            )
    except Exception:
        pass
    # Fallback
    return CostConfigResponse(
        items=[CostConfigItem(key=k, value=v["value"], label=v["label"], unit=v["unit"]) for k, v in DEFAULTS.items()]
    )


@router.put("/")
async def update_cost_config(
    body: CostConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Atualiza custos unitários do FinOps Hyper-V."""
    now = datetime.now(timezone.utc)
    updated = []
    for key, value in body.costs.items():
        if value < 0:
            raise HTTPException(status_code=400, detail=f"Valor negativo não permitido: {key}")
        try:
            db.execute(
                text("UPDATE hyperv_cost_config SET value = :val, updated_at = :ts WHERE key = :key"),
                {"val": value, "ts": now, "key": key},
            )
            updated.append(key)
        except Exception:
            pass
    db.commit()
    return {"status": "ok", "updated": updated}
