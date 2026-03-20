"""
Sensor Controls Router — Coruja Monitor v3.0
Implementa controle estilo PRTG:
  - PATCH /sensors/{id}/pause   → pausa temporária
  - PATCH /sensors/{id}/resume  → retoma execução
  - PATCH /sensors/{id}/priority → define prioridade (1-5 estrelas)
  - GET  /sensors/{id}/status   → status completo do sensor
  - POST /sensors/dependencies  → cria dependência pai→filho
  - GET  /sensors/dependencies  → lista dependências
  - DELETE /sensors/dependencies/{parent_id}/{child_id} → remove
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db
from models import Sensor, Server, User
from auth import get_current_active_user

router = APIRouter()
logger = logging.getLogger(__name__)


# ── Schemas ───────────────────────────────────────────────────────────────────

class PauseRequest(BaseModel):
    duration_minutes: int = Field(default=60, ge=1, le=10080,
                                   description="Duração da pausa em minutos (máx 7 dias)")

class PriorityRequest(BaseModel):
    priority: int = Field(ge=1, le=5, description="Prioridade: 1 (baixa) a 5 (crítica)")

class DependencyCreate(BaseModel):
    parent_sensor_id: int
    child_sensor_id: int

class SensorControlResponse(BaseModel):
    id: int
    name: str
    enabled: bool
    paused_until: Optional[datetime]
    priority: int
    is_paused: bool
    priority_stars: str

    class Config:
        from_attributes = True


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_sensor_for_user(sensor_id: int, db: Session, current_user: User) -> Sensor:
    """Busca sensor verificando permissão de tenant."""
    if current_user.role == 'admin':
        sensor = db.query(Sensor).filter(Sensor.id == sensor_id).first()
    else:
        sensor = (
            db.query(Sensor)
            .outerjoin(Server, Sensor.server_id == Server.id)
            .filter(
                Sensor.id == sensor_id,
                Server.tenant_id == current_user.tenant_id
            )
            .first()
        )
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor não encontrado")
    return sensor


def _sensor_to_response(sensor: Sensor) -> dict:
    now = datetime.utcnow()
    is_paused = bool(
        sensor.paused_until and sensor.paused_until > now
    )
    priority = sensor.priority if sensor.priority is not None else 3
    return {
        "id": sensor.id,
        "name": sensor.name,
        "enabled": sensor.enabled if sensor.enabled is not None else True,
        "paused_until": sensor.paused_until,
        "priority": priority,
        "is_paused": is_paused,
        "priority_stars": "⭐" * priority,
    }


# ── Endpoints de Controle ─────────────────────────────────────────────────────

@router.patch("/{sensor_id}/pause")
async def pause_sensor(
    sensor_id: int,
    body: PauseRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Pausa sensor por N minutos (estilo PRTG).
    Durante a pausa o scheduler não executa o sensor.
    """
    sensor = _get_sensor_for_user(sensor_id, db, current_user)
    sensor.paused_until = datetime.utcnow() + timedelta(minutes=body.duration_minutes)
    db.commit()
    db.refresh(sensor)
    logger.info("Sensor %s pausado por %d min por user %s", sensor_id, body.duration_minutes, current_user.email)
    return {
        "message": f"Sensor '{sensor.name}' pausado por {body.duration_minutes} minutos",
        **_sensor_to_response(sensor),
    }


@router.patch("/{sensor_id}/resume")
async def resume_sensor(
    sensor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retoma execução do sensor imediatamente.
    Limpa paused_until e garante enabled=True.
    """
    sensor = _get_sensor_for_user(sensor_id, db, current_user)
    sensor.paused_until = None
    sensor.enabled = True
    db.commit()
    db.refresh(sensor)
    logger.info("Sensor %s retomado por user %s", sensor_id, current_user.email)
    return {
        "message": f"Sensor '{sensor.name}' retomado",
        **_sensor_to_response(sensor),
    }


@router.patch("/{sensor_id}/disable")
async def disable_sensor(
    sensor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Desabilita sensor permanentemente (enabled=False)."""
    sensor = _get_sensor_for_user(sensor_id, db, current_user)
    sensor.enabled = False
    db.commit()
    db.refresh(sensor)
    return {"message": f"Sensor '{sensor.name}' desabilitado", **_sensor_to_response(sensor)}


@router.patch("/{sensor_id}/enable")
async def enable_sensor(
    sensor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Habilita sensor (enabled=True)."""
    sensor = _get_sensor_for_user(sensor_id, db, current_user)
    sensor.enabled = True
    sensor.paused_until = None
    db.commit()
    db.refresh(sensor)
    return {"message": f"Sensor '{sensor.name}' habilitado", **_sensor_to_response(sensor)}


@router.patch("/{sensor_id}/priority")
async def set_sensor_priority(
    sensor_id: int,
    body: PriorityRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Define prioridade do sensor (1-5 estrelas, estilo PRTG).
    Apenas sensores com priority=5 geram alertas externos (Telegram/Teams).
    """
    sensor = _get_sensor_for_user(sensor_id, db, current_user)
    old_priority = sensor.priority
    sensor.priority = body.priority
    db.commit()
    db.refresh(sensor)
    logger.info(
        "Sensor %s prioridade alterada %d→%d por user %s",
        sensor_id, old_priority or 3, body.priority, current_user.email
    )
    return {
        "message": f"Prioridade de '{sensor.name}' definida para {body.priority} {'⭐' * body.priority}",
        "note": "Apenas sensores ⭐⭐⭐⭐⭐ (5) geram alertas externos (Telegram/Teams)",
        **_sensor_to_response(sensor),
    }


@router.get("/{sensor_id}/status")
async def get_sensor_control_status(
    sensor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Retorna status completo de controle do sensor."""
    sensor = _get_sensor_for_user(sensor_id, db, current_user)
    return _sensor_to_response(sensor)


# ── Endpoints de Dependências ─────────────────────────────────────────────────

@router.post("/dependencies")
async def create_dependency(
    body: DependencyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Cria dependência pai→filho entre sensores.
    Regra: se pai = CRITICAL → filho é suspenso automaticamente.
    Exemplo: Ping (pai) → WMI (filho)
    """
    # Verificar que ambos existem e pertencem ao tenant
    parent = _get_sensor_for_user(body.parent_sensor_id, db, current_user)
    child = _get_sensor_for_user(body.child_sensor_id, db, current_user)

    if parent.id == child.id:
        raise HTTPException(status_code=400, detail="Sensor não pode depender de si mesmo")

    # Verificar se já existe
    existing = db.execute(text(
        "SELECT id FROM sensor_dependencies WHERE parent_sensor_id = :p AND child_sensor_id = :c"
    ), {"p": parent.id, "c": child.id}).fetchone()

    if existing:
        raise HTTPException(status_code=409, detail="Dependência já existe")

    # Verificar ciclo simples (filho não pode ser pai do pai)
    reverse = db.execute(text(
        "SELECT id FROM sensor_dependencies WHERE parent_sensor_id = :p AND child_sensor_id = :c"
    ), {"p": child.id, "c": parent.id}).fetchone()
    if reverse:
        raise HTTPException(status_code=400, detail="Criaria ciclo: filho já é pai do pai")

    db.execute(text(
        "INSERT INTO sensor_dependencies (parent_sensor_id, child_sensor_id) VALUES (:p, :c)"
    ), {"p": parent.id, "c": child.id})
    db.commit()

    logger.info("Dependência criada: sensor %s → sensor %s", parent.id, child.id)
    return {
        "message": f"Dependência criada: '{parent.name}' → '{child.name}'",
        "parent": {"id": parent.id, "name": parent.name, "type": parent.sensor_type},
        "child": {"id": child.id, "name": child.name, "type": child.sensor_type},
        "rule": "Se pai = CRITICAL → filho suspenso automaticamente",
    }


@router.get("/dependencies")
async def list_dependencies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Lista todas as dependências do tenant."""
    try:
        if current_user.role == 'admin':
            rows = db.execute(text("""
                SELECT sd.id, sd.parent_sensor_id, sd.child_sensor_id,
                       sp.name as parent_name, sp.sensor_type as parent_type,
                       sc.name as child_name, sc.sensor_type as child_type
                FROM sensor_dependencies sd
                JOIN sensors sp ON sp.id = sd.parent_sensor_id
                JOIN sensors sc ON sc.id = sd.child_sensor_id
                ORDER BY sd.id
            """)).fetchall()
        else:
            rows = db.execute(text("""
                SELECT sd.id, sd.parent_sensor_id, sd.child_sensor_id,
                       sp.name as parent_name, sp.sensor_type as parent_type,
                       sc.name as child_name, sc.sensor_type as child_type
                FROM sensor_dependencies sd
                JOIN sensors sp ON sp.id = sd.parent_sensor_id
                JOIN sensors sc ON sc.id = sd.child_sensor_id
                JOIN servers srv ON srv.id = sp.server_id
                WHERE srv.tenant_id = :tid
                ORDER BY sd.id
            """), {"tid": current_user.tenant_id}).fetchall()

        return [
            {
                "id": r.id,
                "parent_sensor_id": r.parent_sensor_id,
                "parent_name": r.parent_name,
                "parent_type": r.parent_type,
                "child_sensor_id": r.child_sensor_id,
                "child_name": r.child_name,
                "child_type": r.child_type,
                "rule": "CRITICAL → suspende filho",
            }
            for r in rows
        ]
    except Exception as e:
        logger.error("Erro ao listar dependências: %s", e)
        return []


@router.delete("/dependencies/{parent_id}/{child_id}")
async def delete_dependency(
    parent_id: int,
    child_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Remove dependência entre sensores."""
    result = db.execute(text(
        "DELETE FROM sensor_dependencies WHERE parent_sensor_id = :p AND child_sensor_id = :c"
    ), {"p": parent_id, "c": child_id})
    db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Dependência não encontrada")
    return {"message": "Dependência removida"}
