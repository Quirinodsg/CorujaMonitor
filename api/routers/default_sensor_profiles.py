"""
Default Sensor Profiles Router — Coruja Monitor v3.5 Enterprise Hardening
CRUD de perfis padrão de sensores por tipo de ativo.
GET  /api/v1/default-sensor-profiles
PUT  /api/v1/default-sensor-profiles/{asset_type}
"""
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import get_db
from models import DefaultSensorProfile
from auth import get_current_active_user
from models import User

router = APIRouter()
logger = logging.getLogger(__name__)

VALID_ASSET_TYPES = ("VM", "physical_server", "network_device")
VALID_ALERT_MODES = ("normal", "silent", "metric_only")

# Perfil de fábrica — aplicado quando tabela está vazia
FACTORY_PROFILES = [
    {"asset_type": "VM",              "sensor_type": "cpu",         "enabled": True,  "alert_mode": "normal",      "threshold_warning": 80, "threshold_critical": 95},
    {"asset_type": "VM",              "sensor_type": "memory",      "enabled": True,  "alert_mode": "normal",      "threshold_warning": 80, "threshold_critical": 95},
    {"asset_type": "VM",              "sensor_type": "disk",        "enabled": True,  "alert_mode": "normal",      "threshold_warning": 80, "threshold_critical": 95},
    {"asset_type": "VM",              "sensor_type": "network_in",  "enabled": True,  "alert_mode": "metric_only", "threshold_warning": 80, "threshold_critical": 95},
    {"asset_type": "VM",              "sensor_type": "network_out", "enabled": True,  "alert_mode": "metric_only", "threshold_warning": 80, "threshold_critical": 95},
    {"asset_type": "physical_server", "sensor_type": "cpu",         "enabled": True,  "alert_mode": "normal",      "threshold_warning": 80, "threshold_critical": 95},
    {"asset_type": "physical_server", "sensor_type": "memory",      "enabled": True,  "alert_mode": "normal",      "threshold_warning": 80, "threshold_critical": 95},
    {"asset_type": "physical_server", "sensor_type": "disk",        "enabled": True,  "alert_mode": "normal",      "threshold_warning": 80, "threshold_critical": 95},
    {"asset_type": "physical_server", "sensor_type": "network_in",  "enabled": True,  "alert_mode": "metric_only", "threshold_warning": 80, "threshold_critical": 95},
    {"asset_type": "physical_server", "sensor_type": "network_out", "enabled": True,  "alert_mode": "metric_only", "threshold_warning": 80, "threshold_critical": 95},
    {"asset_type": "network_device",  "sensor_type": "ping",        "enabled": True,  "alert_mode": "normal",      "threshold_warning": 100, "threshold_critical": 200},
    {"asset_type": "network_device",  "sensor_type": "network_in",  "enabled": True,  "alert_mode": "metric_only", "threshold_warning": 80,  "threshold_critical": 95},
    {"asset_type": "network_device",  "sensor_type": "network_out", "enabled": True,  "alert_mode": "metric_only", "threshold_warning": 80,  "threshold_critical": 95},
]


class DefaultSensorProfileSchema(BaseModel):
    asset_type: str
    sensor_type: str
    enabled: bool = True
    alert_mode: str = Field(default="normal", description="normal | silent | metric_only")
    threshold_warning: Optional[float] = None
    threshold_critical: Optional[float] = None

    class Config:
        from_attributes = True


class DefaultSensorProfileResponse(DefaultSensorProfileSchema):
    id: int


@router.get("/default-sensor-profiles", response_model=List[DefaultSensorProfileResponse])
async def list_profiles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Retorna todos os perfis padrão. Se tabela vazia, retorna perfil de fábrica."""
    profiles = db.query(DefaultSensorProfile).order_by(
        DefaultSensorProfile.asset_type, DefaultSensorProfile.sensor_type
    ).all()

    if not profiles:
        # Retorna fábrica como objetos temporários (sem persistir)
        return [DefaultSensorProfileResponse(id=i + 1, **p) for i, p in enumerate(FACTORY_PROFILES)]

    return profiles


@router.put("/default-sensor-profiles/{asset_type}", response_model=List[DefaultSensorProfileResponse])
async def upsert_profiles(
    asset_type: str,
    profiles: List[DefaultSensorProfileSchema],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Substitui todos os perfis de um asset_type."""
    if asset_type not in VALID_ASSET_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"asset_type deve ser um de: {', '.join(VALID_ASSET_TYPES)}"
        )

    for p in profiles:
        if p.alert_mode not in VALID_ALERT_MODES:
            raise HTTPException(
                status_code=422,
                detail=f"alert_mode '{p.alert_mode}' inválido. Use: {', '.join(VALID_ALERT_MODES)}"
            )

    # Upsert: ON CONFLICT UPDATE
    for p in profiles:
        existing = db.query(DefaultSensorProfile).filter(
            DefaultSensorProfile.asset_type == asset_type,
            DefaultSensorProfile.sensor_type == p.sensor_type,
        ).first()

        if existing:
            existing.enabled = p.enabled
            existing.alert_mode = p.alert_mode
            existing.threshold_warning = p.threshold_warning
            existing.threshold_critical = p.threshold_critical
        else:
            new_profile = DefaultSensorProfile(
                asset_type=asset_type,
                sensor_type=p.sensor_type,
                enabled=p.enabled,
                alert_mode=p.alert_mode,
                threshold_warning=p.threshold_warning,
                threshold_critical=p.threshold_critical,
            )
            db.add(new_profile)

    db.commit()
    logger.info("Perfis padrão atualizados para asset_type=%s por user %s", asset_type, current_user.email)

    return db.query(DefaultSensorProfile).filter(
        DefaultSensorProfile.asset_type == asset_type
    ).order_by(DefaultSensorProfile.sensor_type).all()
