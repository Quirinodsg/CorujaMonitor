"""
Router de Escalação Contínua de Alarmes — Coruja Monitor

Endpoints para gerenciar escalações ativas, configuração de escalação,
recursos monitorados e histórico de escalações.
"""

import logging
import sys
import os
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session

from database import get_db
from models import Tenant, Sensor, Server, User, Incident
from auth import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter()

# ─── Pydantic Models ────────────────────────────────────────────────────────


class AcknowledgeRequest(BaseModel):
    notes: Optional[str] = None


class EscalationConfigUpdate(BaseModel):
    enabled: Optional[bool] = None
    mode: Optional[str] = None
    interval_minutes: Optional[int] = None
    max_attempts: Optional[int] = None
    call_duration_seconds: Optional[int] = None
    phone_chain: Optional[List[Dict[str, Any]]] = None

    @field_validator("mode")
    @classmethod
    def validate_mode(cls, v):
        if v is not None and v not in ("simultaneous", "sequential"):
            raise ValueError("mode deve ser 'simultaneous' ou 'sequential'")
        return v


class ResourceItem(BaseModel):
    type: str  # "sensor" ou "server"
    id: int
    name: Optional[str] = None


class ResourcesUpdate(BaseModel):
    resources: List[ResourceItem]


# ─── Helper: importar módulo de escalação do worker ─────────────────────────

def _get_escalation_module():
    """Importa worker/escalation.py adicionando o path do worker ao sys.path."""
    # Tentar múltiplos paths possíveis (dev local e Docker)
    possible_dirs = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "worker"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "worker"),
        "/app/worker",
        os.path.join(os.getcwd(), "worker"),
    ]
    for d in possible_dirs:
        if os.path.isdir(d) and d not in sys.path:
            sys.path.insert(0, d)
    import escalation
    return escalation


# ─── Funções de validação inline (fallback se import falhar) ────────────────

def _validate_escalation_config_inline(config):
    """Validação inline caso o módulo escalation não esteja disponível."""
    limits = {"interval_minutes": (1, 60), "max_attempts": (1, 100), "call_duration_seconds": (10, 120)}
    errors = []
    for field, (mn, mx) in limits.items():
        if field in config:
            v = config[field]
            if not isinstance(v, int) or v < mn or v > mx:
                errors.append(f"{field}: valor {v} fora dos limites [{mn}, {mx}]")
    return errors


def _validate_phone_inline(number):
    """Validação E.164 inline."""
    import re
    return bool(re.match(r'^\+\d{1,15}$', str(number))) if isinstance(number, str) else False


# ─── 5.1 GET /active — lista escalações ativas do tenant ────────────────────

@router.get("/active")
async def list_active_escalations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Retorna lista de escalações ativas do tenant do usuário."""
    try:
        esc = _get_escalation_module()
        active = esc.get_active_escalations(current_user.tenant_id)
    except Exception as e:
        logger.warning("Erro ao buscar escalações ativas (Redis pode estar indisponível): %s", e)
        # Retornar lista vazia em vez de 503 — Redis indisponível não é erro fatal
        return []

    # Enriquecer com sensor_name do banco
    result = []
    for state in active:
        sensor_id = state.get("sensor_id")
        sensor = db.query(Sensor).filter(Sensor.id == sensor_id).first()
        sensor_name = sensor.name if sensor else f"Sensor #{sensor_id}"

        result.append({
            "sensor_id": sensor_id,
            "sensor_name": sensor_name,
            "incident_id": state.get("incident_id"),
            "device_type": state.get("device_type"),
            "problem_description": state.get("problem_description"),
            "started_at": state.get("started_at"),
            "attempt_count": state.get("attempt_count"),
            "max_attempts": state.get("max_attempts"),
            "next_attempt_at": state.get("next_attempt_at"),
            "status": state.get("status"),
            "mode": state.get("mode"),
            "phone_numbers": state.get("phone_numbers", []),
        })

    return result


# ─── 5.3 POST /{sensor_id}/acknowledge — reconhecer alarme ──────────────────

@router.post("/{sensor_id}/acknowledge")
async def acknowledge_alarm(
    sensor_id: int,
    request: AcknowledgeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Reconhece um alarme ativo, parando a escalação."""
    esc = _get_escalation_module()

    # Verificar se existe escalação ativa
    try:
        import redis as redis_lib
        r = redis_lib.Redis.from_url("redis://redis:6379", decode_responses=True, socket_connect_timeout=2)
        raw = r.get(f"escalation:{sensor_id}")
    except Exception:
        raise HTTPException(status_code=503, detail="Redis indisponível")

    if not raw:
        raise HTTPException(status_code=404, detail="Nenhuma escalação ativa para este sensor")

    try:
        state = esc.deserialize_state(raw)
    except ValueError:
        raise HTTPException(status_code=404, detail="Estado de escalação inválido")

    if state.get("status") != "active":
        raise HTTPException(
            status_code=409,
            detail=f"Escalação já está em status '{state.get('status')}'"
        )

    # Verificar que o sensor pertence ao tenant do usuário
    sensor = db.query(Sensor).filter(Sensor.id == sensor_id).first()
    if sensor:
        server = db.query(Server).filter(Server.id == sensor.server_id).first() if sensor.server_id else None
        if server and server.tenant_id != current_user.tenant_id:
            raise HTTPException(status_code=404, detail="Nenhuma escalação ativa para este sensor")

    result = esc.acknowledge_escalation(sensor_id, current_user.id, request.notes or "")
    if not result:
        raise HTTPException(status_code=404, detail="Nenhuma escalação ativa para este sensor")

    return {
        "success": True,
        "message": "Escalação reconhecida com sucesso",
        "sensor_id": sensor_id,
        "acknowledged_by": current_user.id,
        "acknowledged_at": result.get("acknowledged_at"),
    }


# ─── 5.4 GET/PUT /config — configuração de escalação do tenant ───────────────

@router.get("/config")
async def get_escalation_config(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Retorna configuração de escalação do tenant."""
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant não encontrado")

    notification_config = tenant.notification_config or {}
    escalation_config = notification_config.get("escalation", {})

    # Pré-popular phone_chain com números do Twilio se estiver vazia
    phone_chain = escalation_config.get("phone_chain", [])
    if not phone_chain:
        twilio_config = notification_config.get("twilio", {})
        to_numbers = twilio_config.get("to_numbers", [])
        if isinstance(to_numbers, str):
            to_numbers = [n.strip() for n in to_numbers.split(",") if n.strip()]
        if to_numbers:
            phone_chain = [
                {"name": f"Contato {i+1}", "number": n.strip(), "order": i+1}
                for i, n in enumerate(to_numbers)
            ]

    return {
        "enabled": escalation_config.get("enabled", False),
        "mode": escalation_config.get("mode", "sequential"),
        "interval_minutes": escalation_config.get("interval_minutes", 5),
        "max_attempts": escalation_config.get("max_attempts", 10),
        "call_duration_seconds": escalation_config.get("call_duration_seconds", 30),
        "phone_chain": phone_chain,
    }


@router.put("/config")
async def update_escalation_config(
    config: EscalationConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Atualiza configuração de escalação do tenant."""
    try:
        esc = _get_escalation_module()
        validate_config = esc.validate_escalation_config
        validate_phone = esc.validate_phone_number
    except Exception:
        validate_config = _validate_escalation_config_inline
        validate_phone = _validate_phone_inline

    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant não encontrado")

    # Validar parâmetros numéricos
    params_to_validate = {}
    if config.interval_minutes is not None:
        params_to_validate["interval_minutes"] = config.interval_minutes
    if config.max_attempts is not None:
        params_to_validate["max_attempts"] = config.max_attempts
    if config.call_duration_seconds is not None:
        params_to_validate["call_duration_seconds"] = config.call_duration_seconds

    if params_to_validate:
        errors = validate_config(params_to_validate)
        if errors:
            raise HTTPException(status_code=400, detail="; ".join(errors))

    # Validar números E.164 na phone_chain
    if config.phone_chain is not None:
        for i, entry in enumerate(config.phone_chain):
            number = entry.get("number", "")
            if number and not validate_phone(number):
                raise HTTPException(
                    status_code=400,
                    detail=f"Número inválido na posição {i + 1}: '{number}' não está no formato E.164"
                )

    # Atualizar notification_config
    notification_config = tenant.notification_config or {}
    escalation_config = notification_config.get("escalation", {})

    if config.enabled is not None:
        escalation_config["enabled"] = config.enabled
    if config.mode is not None:
        escalation_config["mode"] = config.mode
    if config.interval_minutes is not None:
        escalation_config["interval_minutes"] = config.interval_minutes
    if config.max_attempts is not None:
        escalation_config["max_attempts"] = config.max_attempts
    if config.call_duration_seconds is not None:
        escalation_config["call_duration_seconds"] = config.call_duration_seconds
    if config.phone_chain is not None:
        escalation_config["phone_chain"] = config.phone_chain

    notification_config["escalation"] = escalation_config
    tenant.notification_config = notification_config
    # Force SQLAlchemy to detect JSON change
    from sqlalchemy.orm.attributes import flag_modified
    flag_modified(tenant, "notification_config")
    db.commit()

    return {
        "success": True,
        "message": "Configuração de escalação atualizada",
        "config": escalation_config,
    }


# ─── 5.5 GET/PUT /resources — recursos monitorados para escalação ────────────

@router.get("/resources")
async def get_escalation_resources(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Retorna lista de recursos monitorados para escalação do tenant."""
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant não encontrado")

    notification_config = tenant.notification_config or {}
    escalation_config = notification_config.get("escalation", {})
    resources = escalation_config.get("escalation_resources", [])

    return {"resources": resources}


@router.get("/resources/search")
async def search_available_resources(
    q: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Busca servidores e sensores disponíveis para adicionar à escalação."""
    results = []
    query_lower = q.lower().strip()

    # Buscar servidores do tenant
    servers = db.query(Server).filter(
        Server.tenant_id == current_user.tenant_id,
        Server.is_active == True,
    ).all()
    for s in servers:
        if not query_lower or query_lower in (s.hostname or '').lower():
            results.append({"type": "server", "id": s.id, "name": s.hostname or f"Server #{s.id}"})

    # Buscar sensores standalone (sem server_id) e sensores com server_id do tenant
    from sqlalchemy import or_
    from models import Probe
    sensors = db.query(Sensor).outerjoin(Server, Sensor.server_id == Server.id).outerjoin(
        Probe, Sensor.probe_id == Probe.id
    ).filter(
        Sensor.is_active == True,
        or_(
            Server.tenant_id == current_user.tenant_id,
            Probe.tenant_id == current_user.tenant_id,
            (Sensor.server_id == None) & (Sensor.probe_id == None),
        )
    ).all()
    for s in sensors:
        if not query_lower or query_lower in (s.name or '').lower():
            results.append({"type": "sensor", "id": s.id, "name": s.name or f"Sensor #{s.id}"})

    return results[:30]


@router.put("/resources")
async def update_escalation_resources(
    data: ResourcesUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Atualiza lista de recursos monitorados para escalação."""
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant não encontrado")

    # Validar que cada recurso existe e está ativo
    validated_resources = []
    for resource in data.resources:
        if resource.type == "sensor":
            obj = db.query(Sensor).filter(
                Sensor.id == resource.id,
                Sensor.is_active == True,
            ).first()
            if not obj:
                raise HTTPException(
                    status_code=400,
                    detail=f"Sensor ID {resource.id} não encontrado ou inativo"
                )
            validated_resources.append({
                "type": "sensor",
                "id": obj.id,
                "name": resource.name or obj.name,
            })
        elif resource.type == "server":
            obj = db.query(Server).filter(
                Server.id == resource.id,
                Server.tenant_id == current_user.tenant_id,
                Server.is_active == True,
            ).first()
            if not obj:
                raise HTTPException(
                    status_code=400,
                    detail=f"Servidor ID {resource.id} não encontrado ou inativo"
                )
            validated_resources.append({
                "type": "server",
                "id": obj.id,
                "name": resource.name or obj.hostname,
            })
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Tipo de recurso inválido: '{resource.type}'. Use 'sensor' ou 'server'."
            )

    # Persistir
    notification_config = tenant.notification_config or {}
    escalation_config = notification_config.get("escalation", {})
    escalation_config["escalation_resources"] = validated_resources
    notification_config["escalation"] = escalation_config
    tenant.notification_config = notification_config
    from sqlalchemy.orm.attributes import flag_modified
    flag_modified(tenant, "notification_config")
    db.commit()

    return {
        "success": True,
        "message": f"{len(validated_resources)} recursos configurados para escalação",
        "resources": validated_resources,
    }


# ─── 5.7 GET /history — histórico recente de escalações ─────────────────────

@router.get("/history")
async def get_escalation_history(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Retorna histórico recente de escalações encerradas (reconhecidas, expiradas, resolvidas)."""
    # Buscar incidentes do tenant que possuem escalation_history no ai_analysis
    if current_user.role == "admin":
        query = db.query(Incident).join(Sensor)
    else:
        query = (
            db.query(Incident)
            .join(Sensor)
            .outerjoin(Server, Sensor.server_id == Server.id)
            .filter(
                (Server.tenant_id == current_user.tenant_id)
                | (Sensor.server_id == None)
            )
        )

    # Filtrar incidentes que possuem ai_analysis com escalation_history
    incidents = (
        query
        .filter(Incident.ai_analysis != None)
        .order_by(Incident.created_at.desc())
        .limit(limit * 2)  # Buscar mais para filtrar
        .all()
    )

    history = []
    for incident in incidents:
        ai_analysis = incident.ai_analysis
        if not isinstance(ai_analysis, dict):
            continue
        esc_history = ai_analysis.get("escalation_history", [])
        if not esc_history:
            continue

        # Encontrar evento de parada
        stopped_event = None
        started_event = None
        for event in esc_history:
            if event.get("event_type") == "escalation_stopped":
                stopped_event = event
            elif event.get("event_type") == "escalation_acknowledged":
                stopped_event = event
            elif event.get("event_type") == "escalation_started":
                started_event = event

        if not stopped_event and not started_event:
            continue

        sensor = db.query(Sensor).filter(Sensor.id == incident.sensor_id).first()
        history.append({
            "incident_id": incident.id,
            "sensor_id": incident.sensor_id,
            "sensor_name": sensor.name if sensor else f"Sensor #{incident.sensor_id}",
            "severity": incident.severity,
            "title": incident.title,
            "status": incident.status,
            "started_at": started_event.get("timestamp") if started_event else None,
            "ended_at": stopped_event.get("timestamp") if stopped_event else None,
            "reason": stopped_event.get("reason") if stopped_event else "acknowledged",
            "attempt_count": (stopped_event or started_event or {}).get("attempt_count", 0),
            "created_at": incident.created_at.isoformat() if incident.created_at else None,
            "resolved_at": incident.resolved_at.isoformat() if incident.resolved_at else None,
        })

        if len(history) >= limit:
            break

    return history


# ─── POST /test-call — Teste de ligação de escalação ────────────────────────


class TestCallRequest(BaseModel):
    number: str


@router.post("/test-call")
async def test_escalation_call(
    request: TestCallRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Faz uma ligação de teste para validar a configuração de escalação."""
    try:
        esc = _get_escalation_module()
        validate_phone = esc.validate_phone_number
    except Exception:
        validate_phone = _validate_phone_inline

    if not validate_phone(request.number):
        raise HTTPException(status_code=400, detail="Número inválido. Use formato E.164: +5511999999999")

    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    if not tenant or not tenant.notification_config:
        raise HTTPException(status_code=400, detail="Configuração de notificação não encontrada")

    twilio_config = tenant.notification_config.get("twilio", {})
    account_sid = twilio_config.get("account_sid")
    auth_token = twilio_config.get("auth_token")
    from_number = twilio_config.get("from_number")

    if not all([account_sid, auth_token, from_number]):
        raise HTTPException(status_code=400, detail="Twilio não configurado")

    try:
        import httpx
        # Usar API REST do Twilio diretamente (sem SDK) — funciona em qualquer container
        twiml = (
            '<Response>'
            '<Say language="pt-BR" voice="alice">'
            'Teste de escalação do Coruja Monitor. '
            'Se você está ouvindo esta mensagem, a configuração de ligação está funcionando corretamente. '
            'Obrigado.'
            '</Say>'
            '</Response>'
        )
        with httpx.Client(timeout=30.0) as http:
            resp = http.post(
                f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Calls.json",
                auth=(account_sid, auth_token),
                data={
                    "Twiml": twiml,
                    "From": from_number,
                    "To": request.number,
                    "Timeout": "30",
                },
            )
            if resp.status_code in (200, 201):
                call_data = resp.json()
                return {
                    "success": True,
                    "message": f"Ligação de teste enviada para {request.number}",
                    "call_sid": call_data.get("sid", ""),
                }
            else:
                detail = resp.json().get("message", resp.text) if resp.headers.get("content-type", "").startswith("application/json") else resp.text
                raise HTTPException(status_code=500, detail=f"Twilio erro: {detail}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao fazer ligação: {str(e)}")


# ─── 6.7 Limpeza automática de recursos removidos ───────────────────────────

def cleanup_removed_resources(db: Session, tenant_id: int):
    """Remove recursos inexistentes/inativos da lista de escalação e para escalações ativas.

    Chamado quando sensores/servidores são removidos ou desativados.
    """
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant or not tenant.notification_config:
        return

    notification_config = tenant.notification_config or {}
    escalation_config = notification_config.get("escalation", {})
    resources = escalation_config.get("escalation_resources", [])

    if not resources:
        return

    cleaned = []
    removed_sensor_ids = []

    for res in resources:
        if res.get("type") == "sensor":
            obj = db.query(Sensor).filter(
                Sensor.id == res.get("id"),
                Sensor.is_active == True,
            ).first()
            if obj:
                cleaned.append(res)
            else:
                removed_sensor_ids.append(res.get("id"))
                logger.info("Recurso removido da lista de escalação: sensor %s", res.get("id"))
        elif res.get("type") == "server":
            obj = db.query(Server).filter(
                Server.id == res.get("id"),
                Server.is_active == True,
            ).first()
            if obj:
                cleaned.append(res)
            else:
                # Parar escalações de todos os sensores deste servidor
                if res.get("id"):
                    sensors = db.query(Sensor).filter(Sensor.server_id == res.get("id")).all()
                    for s in sensors:
                        removed_sensor_ids.append(s.id)
                logger.info("Recurso removido da lista de escalação: server %s", res.get("id"))
        else:
            cleaned.append(res)

    # Parar escalações ativas para sensores removidos
    if removed_sensor_ids:
        try:
            esc = _get_escalation_module()
            for sid in removed_sensor_ids:
                esc.stop_escalation(sid, reason="resource_removed")
        except Exception as e:
            logger.warning("Erro ao parar escalação de recurso removido: %s", e)

    # Atualizar lista se houve mudança
    if len(cleaned) != len(resources):
        escalation_config["escalation_resources"] = cleaned
        notification_config["escalation"] = escalation_config
        tenant.notification_config = notification_config
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(tenant, "notification_config")
        db.commit()
        logger.info(
            "Lista de escalação limpa: %d recursos removidos para tenant %d",
            len(resources) - len(cleaned),
            tenant_id,
        )
