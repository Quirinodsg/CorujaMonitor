"""
API de Configuração de Thresholds Temporais
Baseado em melhores práticas ITIL para evitar falsos positivos
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional

from database import get_db
from models import User, ThresholdConfig
from auth import get_current_active_user, require_role

router = APIRouter()


class ThresholdConfigResponse(BaseModel):
    # Configurações Temporais
    breach_duration_seconds: int = Field(description="Tempo padrão em breach antes de criar incidente (segundos)")
    flapping_window_seconds: int = Field(description="Janela de tempo para detectar flapping (segundos)")
    flapping_threshold: int = Field(description="Número de mudanças para considerar flapping")
    
    # Configurações por Tipo de Sensor
    cpu_breach_duration: int = Field(description="Tempo em breach para CPU (segundos)")
    memory_breach_duration: int = Field(description="Tempo em breach para Memória (segundos)")
    disk_breach_duration: int = Field(description="Tempo em breach para Disco (segundos)")
    ping_breach_duration: int = Field(description="Tempo em breach para Ping (segundos)")
    service_breach_duration: int = Field(description="Tempo em breach para Serviços (segundos)")
    network_breach_duration: int = Field(description="Tempo em breach para Rede (segundos)")
    
    # Configurações de Supressão
    suppress_during_maintenance: bool = Field(description="Suprimir alertas durante manutenção")
    suppress_acknowledged: bool = Field(description="Suprimir alertas de sensores reconhecidos")
    suppress_flapping: bool = Field(description="Suprimir alertas de sensores com flapping")
    
    # Configurações de Escalação
    escalation_enabled: bool = Field(description="Habilitar escalação automática")
    escalation_time_minutes: int = Field(description="Tempo para escalar incidente (minutos)")
    escalation_severity: str = Field(description="Severidade para escalar")
    
    class Config:
        from_attributes = True


class ThresholdConfigUpdate(BaseModel):
    # Configurações Temporais
    breach_duration_seconds: Optional[int] = Field(None, ge=60, le=3600)
    flapping_window_seconds: Optional[int] = Field(None, ge=60, le=1800)
    flapping_threshold: Optional[int] = Field(None, ge=2, le=10)
    
    # Configurações por Tipo de Sensor
    cpu_breach_duration: Optional[int] = Field(None, ge=60, le=3600)
    memory_breach_duration: Optional[int] = Field(None, ge=60, le=3600)
    disk_breach_duration: Optional[int] = Field(None, ge=300, le=7200)
    ping_breach_duration: Optional[int] = Field(None, ge=30, le=600)
    service_breach_duration: Optional[int] = Field(None, ge=30, le=600)
    network_breach_duration: Optional[int] = Field(None, ge=60, le=3600)
    
    # Configurações de Supressão
    suppress_during_maintenance: Optional[bool] = None
    suppress_acknowledged: Optional[bool] = None
    suppress_flapping: Optional[bool] = None
    
    # Configurações de Escalação
    escalation_enabled: Optional[bool] = None
    escalation_time_minutes: Optional[int] = Field(None, ge=5, le=240)
    escalation_severity: Optional[str] = Field(None, pattern="^(warning|critical)$")


@router.get("/config", response_model=ThresholdConfigResponse)
async def get_threshold_config(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obter configuração de thresholds do tenant"""
    
    config = db.query(ThresholdConfig).filter(
        ThresholdConfig.tenant_id == current_user.tenant_id
    ).first()
    
    if not config:
        # Criar configuração padrão
        config = ThresholdConfig(tenant_id=current_user.tenant_id)
        db.add(config)
        db.commit()
        db.refresh(config)
    
    return config


@router.put("/config")
async def update_threshold_config(
    updates: ThresholdConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Atualizar configuração de thresholds (admin only)"""
    
    config = db.query(ThresholdConfig).filter(
        ThresholdConfig.tenant_id == current_user.tenant_id
    ).first()
    
    if not config:
        config = ThresholdConfig(tenant_id=current_user.tenant_id)
        db.add(config)
    
    # Atualizar campos fornecidos
    update_data = updates.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(config, field, value)
    
    db.commit()
    db.refresh(config)
    
    return {
        "message": "Configuração atualizada com sucesso",
        "config": config
    }


@router.get("/presets")
async def get_threshold_presets(
    current_user: User = Depends(get_current_active_user)
):
    """Obter presets de configuração baseados em ITIL"""
    
    return {
        "presets": [
            {
                "name": "Conservador (ITIL Padrão)",
                "description": "Reduz falsos positivos, ideal para ambientes estáveis",
                "config": {
                    "cpu_breach_duration": 600,  # 10 min
                    "memory_breach_duration": 900,  # 15 min
                    "disk_breach_duration": 1800,  # 30 min
                    "ping_breach_duration": 180,  # 3 min
                    "service_breach_duration": 120,  # 2 min
                    "network_breach_duration": 600,  # 10 min
                    "flapping_threshold": 3,
                    "flapping_window_seconds": 300
                }
            },
            {
                "name": "Balanceado",
                "description": "Equilíbrio entre detecção rápida e falsos positivos",
                "config": {
                    "cpu_breach_duration": 300,  # 5 min
                    "memory_breach_duration": 600,  # 10 min
                    "disk_breach_duration": 900,  # 15 min
                    "ping_breach_duration": 120,  # 2 min
                    "service_breach_duration": 60,  # 1 min
                    "network_breach_duration": 300,  # 5 min
                    "flapping_threshold": 4,
                    "flapping_window_seconds": 240
                }
            },
            {
                "name": "Agressivo",
                "description": "Detecção rápida, pode gerar mais falsos positivos",
                "config": {
                    "cpu_breach_duration": 120,  # 2 min
                    "memory_breach_duration": 300,  # 5 min
                    "disk_breach_duration": 600,  # 10 min
                    "ping_breach_duration": 60,  # 1 min
                    "service_breach_duration": 30,  # 30 seg
                    "network_breach_duration": 120,  # 2 min
                    "flapping_threshold": 5,
                    "flapping_window_seconds": 180
                }
            },
            {
                "name": "Crítico Apenas",
                "description": "Apenas para ambientes críticos 24/7",
                "config": {
                    "cpu_breach_duration": 60,  # 1 min
                    "memory_breach_duration": 120,  # 2 min
                    "disk_breach_duration": 300,  # 5 min
                    "ping_breach_duration": 30,  # 30 seg
                    "service_breach_duration": 30,  # 30 seg
                    "network_breach_duration": 60,  # 1 min
                    "flapping_threshold": 6,
                    "flapping_window_seconds": 120
                }
            }
        ]
    }


@router.post("/apply-preset/{preset_name}")
async def apply_threshold_preset(
    preset_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Aplicar um preset de configuração"""
    
    presets = {
        "conservador": {
            "cpu_breach_duration": 600,
            "memory_breach_duration": 900,
            "disk_breach_duration": 1800,
            "ping_breach_duration": 180,
            "service_breach_duration": 120,
            "network_breach_duration": 600,
            "flapping_threshold": 3,
            "flapping_window_seconds": 300
        },
        "balanceado": {
            "cpu_breach_duration": 300,
            "memory_breach_duration": 600,
            "disk_breach_duration": 900,
            "ping_breach_duration": 120,
            "service_breach_duration": 60,
            "network_breach_duration": 300,
            "flapping_threshold": 4,
            "flapping_window_seconds": 240
        },
        "agressivo": {
            "cpu_breach_duration": 120,
            "memory_breach_duration": 300,
            "disk_breach_duration": 600,
            "ping_breach_duration": 60,
            "service_breach_duration": 30,
            "network_breach_duration": 120,
            "flapping_threshold": 5,
            "flapping_window_seconds": 180
        },
        "critico": {
            "cpu_breach_duration": 60,
            "memory_breach_duration": 120,
            "disk_breach_duration": 300,
            "ping_breach_duration": 30,
            "service_breach_duration": 30,
            "network_breach_duration": 60,
            "flapping_threshold": 6,
            "flapping_window_seconds": 120
        }
    }
    
    if preset_name.lower() not in presets:
        raise HTTPException(status_code=404, detail="Preset não encontrado")
    
    config = db.query(ThresholdConfig).filter(
        ThresholdConfig.tenant_id == current_user.tenant_id
    ).first()
    
    if not config:
        config = ThresholdConfig(tenant_id=current_user.tenant_id)
        db.add(config)
    
    # Aplicar preset
    preset_config = presets[preset_name.lower()]
    for field, value in preset_config.items():
        setattr(config, field, value)
    
    db.commit()
    db.refresh(config)
    
    return {
        "message": f"Preset '{preset_name}' aplicado com sucesso",
        "config": config
    }
