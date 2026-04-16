"""
Módulo de Escalação Contínua de Alarmes — Coruja Monitor

Gerencia o estado de escalação no Redis, validação de parâmetros
e formato E.164 para números de telefone.
"""

import json
import re
from datetime import datetime, timezone


# ─── Constantes de Validação ────────────────────────────────────────────────

ESCALATION_LIMITS = {
    "interval_minutes": {"min": 1, "max": 60, "default": 5},
    "max_attempts": {"min": 1, "max": 100, "default": 10},
    "call_duration_seconds": {"min": 10, "max": 120, "default": 30},
}

VALID_MODES = ("simultaneous", "sequential")
VALID_STATUSES = ("active", "acknowledged", "expired")

# E.164: + seguido de 1 a 15 dígitos
E164_PATTERN = re.compile(r"^\+\d{1,15}$")

# Campos obrigatórios do EscalationState
REQUIRED_FIELDS = (
    "sensor_id",
    "incident_id",
    "tenant_id",
    "attempt_count",
    "max_attempts",
    "interval_minutes",
    "call_duration_seconds",
    "mode",
    "current_number_index",
    "phone_numbers",
    "status",
    "started_at",
    "next_attempt_at",
    "last_attempt_at",
    "acknowledged_by",
    "acknowledged_at",
    "call_history",
    "device_type",
    "problem_description",
)


# ─── Serialização / Deserialização ──────────────────────────────────────────

def serialize_state(state: dict) -> str:
    """Serializa estado de escalação para JSON string (para Redis).

    Args:
        state: Dicionário com todos os campos do EscalationState.

    Returns:
        JSON string representando o estado.

    Raises:
        ValueError: Se campos obrigatórios estiverem ausentes.
        TypeError: Se o estado não for serializável para JSON.
    """
    missing = [f for f in REQUIRED_FIELDS if f not in state]
    if missing:
        raise ValueError(f"Campos obrigatórios ausentes: {', '.join(missing)}")
    return json.dumps(state, ensure_ascii=False, sort_keys=True)


def deserialize_state(json_str: str) -> dict:
    """Deserializa JSON string para dicionário de estado de escalação.

    Args:
        json_str: JSON string do Redis.

    Returns:
        Dicionário com o estado de escalação.

    Raises:
        ValueError: Se o JSON for inválido ou campos obrigatórios ausentes.
    """
    try:
        state = json.loads(json_str)
    except (json.JSONDecodeError, TypeError) as e:
        raise ValueError(f"JSON inválido: {e}")
    missing = [f for f in REQUIRED_FIELDS if f not in state]
    if missing:
        raise ValueError(f"Campos obrigatórios ausentes: {', '.join(missing)}")
    return state


# ─── Validação de Parâmetros ────────────────────────────────────────────────

def validate_escalation_config(config: dict) -> list[str]:
    """Valida parâmetros de configuração de escalação.

    Verifica se os valores estão dentro dos limites definidos:
    - interval_minutes: [1, 60]
    - max_attempts: [1, 100]
    - call_duration_seconds: [10, 120]

    Args:
        config: Dicionário com parâmetros de escalação.

    Returns:
        Lista de erros de validação. Lista vazia = válido.
    """
    errors = []
    for field, limits in ESCALATION_LIMITS.items():
        if field not in config:
            continue
        value = config[field]
        if not isinstance(value, int):
            errors.append(
                f"{field}: deve ser um inteiro, recebido {type(value).__name__}"
            )
            continue
        if value < limits["min"] or value > limits["max"]:
            errors.append(
                f"{field}: valor {value} fora dos limites [{limits['min']}, {limits['max']}]"
            )
    return errors


# ─── Validação E.164 ────────────────────────────────────────────────────────

def validate_phone_number(number: str) -> bool:
    """Valida se um número de telefone está no formato E.164.

    Formato E.164: começa com '+', seguido de 1 a 15 dígitos.
    Exemplos válidos: +5511999999999, +1, +442071234567

    Args:
        number: String do número de telefone.

    Returns:
        True se o número é válido no formato E.164, False caso contrário.
    """
    if not isinstance(number, str):
        return False
    return bool(E164_PATTERN.match(number))


# ─── Imports para lógica central ────────────────────────────────────────────

import logging
from datetime import timedelta

logger = logging.getLogger(__name__)


def _import_redis():
    """Lazy import de redis para evitar falha quando módulo não está instalado."""
    import redis as redis_lib
    return redis_lib


def _import_db():
    """Lazy import de database/models para evitar falha de config em testes."""
    from database import SessionLocal
    from models import Incident, Sensor, Tenant
    return SessionLocal, Incident, Sensor, Tenant

# Redis connection — usado por todas as funções de escalação
_redis_client = None


def _get_redis():
    """Retorna conexão Redis singleton (lazy init)."""
    global _redis_client
    if _redis_client is None:
        redis_lib = _import_redis()
        _redis_client = redis_lib.Redis.from_url(
            "redis://redis:6379", decode_responses=True, socket_connect_timeout=2
        )
    return _redis_client


def _redis_key(sensor_id: int) -> str:
    """Chave Redis para estado de escalação."""
    return f"escalation:{sensor_id}"


def _lock_key(sensor_id: int) -> str:
    """Chave Redis para lock distribuído."""
    return f"escalation_lock:{sensor_id}"


def _log_to_incident_history(db, incident_id: int, event_type: str, details: dict):
    """Registra evento no campo ai_analysis (JSON) do incidente.

    Adiciona uma entrada ao array 'escalation_history' dentro do JSON existente.
    """
    _, Incident, _, _ = _import_db()
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        logger.warning("Incidente %d não encontrado para log de escalação", incident_id)
        return

    ai_analysis = incident.ai_analysis or {}
    if not isinstance(ai_analysis, dict):
        ai_analysis = {}

    history = ai_analysis.get("escalation_history", [])
    history.append({
        "event_type": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **details,
    })
    ai_analysis["escalation_history"] = history
    incident.ai_analysis = ai_analysis
    db.commit()


# ─── start_escalation ───────────────────────────────────────────────────────

def start_escalation(
    sensor_id: int,
    incident_id: int,
    tenant_id: int,
    alert_data: dict,
) -> dict | None:
    """Inicia escalação contínua para um sensor.

    Cria estado no Redis e agenda a primeira Celery task de ciclo.

    Args:
        sensor_id: ID do sensor em alerta.
        incident_id: ID do incidente associado.
        tenant_id: ID do tenant.
        alert_data: Dados do alerta contendo:
            - device_type (str): tipo do dispositivo
            - problem_description (str): descrição do problema
            - phone_chain (list[dict]): cadeia de números [{name, number}]
            - mode (str): "simultaneous" ou "sequential"
            - interval_minutes (int): intervalo entre ciclos
            - max_attempts (int): máximo de tentativas
            - call_duration_seconds (int): duração da chamada

    Returns:
        Estado de escalação criado, ou None se escalação não foi iniciada.
    """
    r = _get_redis()
    key = _redis_key(sensor_id)

    # 1. Prevenção de duplicata — já existe escalação ativa?
    existing = r.get(key)
    if existing:
        try:
            existing_state = deserialize_state(existing)
            if existing_state.get("status") == "active":
                logger.info(
                    "Escalação já ativa para sensor %d — ignorando duplicata",
                    sensor_id,
                )
                return None
        except (ValueError, Exception):
            # Estado corrompido — prosseguir com nova escalação
            pass

    # 1b. Verificar bloqueio manual (usuário parou as ligações)
    blocked_key = f"escalation_blocked:{sensor_id}"
    if r.exists(blocked_key):
        logger.info(
            "Escalação bloqueada manualmente para sensor %d — não iniciando",
            sensor_id,
        )
        return None

    # 2. Verificar se sensor já está reconhecido OU incidente está acknowledged
    SessionLocal, Incident, Sensor, Tenant = _import_db()
    db = SessionLocal()
    try:
        sensor = db.query(Sensor).filter(Sensor.id == sensor_id).first()
        if sensor and getattr(sensor, "is_acknowledged", False):
            logger.info(
                "Sensor %d já reconhecido — não iniciando escalação", sensor_id
            )
            return None

        # Verificar se o incidente associado está acknowledged ou resolvido
        if incident_id:
            incident = db.query(Incident).filter(Incident.id == incident_id).first()
            if incident and incident.status in ('acknowledged', 'resolved', 'auto_resolved'):
                logger.info(
                    "Incidente %d está %s — não iniciando escalação para sensor %d",
                    incident_id, incident.status, sensor_id,
                )
                return None

        # 3. Verificar cadeia de escalação não vazia
        phone_chain = alert_data.get("phone_chain", [])
        if not phone_chain:
            logger.error(
                "Cadeia de escalação vazia para sensor %d — não iniciando", sensor_id
            )
            return None

        # 4. Extrair parâmetros com defaults
        mode = alert_data.get("mode", "sequential")
        if mode not in VALID_MODES:
            mode = "sequential"

        interval_minutes = alert_data.get(
            "interval_minutes", ESCALATION_LIMITS["interval_minutes"]["default"]
        )
        max_attempts = alert_data.get(
            "max_attempts", ESCALATION_LIMITS["max_attempts"]["default"]
        )
        call_duration_seconds = alert_data.get(
            "call_duration_seconds",
            ESCALATION_LIMITS["call_duration_seconds"]["default"],
        )

        now = datetime.now(timezone.utc)
        next_attempt = now + timedelta(seconds=30)  # Primeira tentativa em 30s

        # 5. Criar estado inicial
        state = {
            "sensor_id": sensor_id,
            "incident_id": incident_id,
            "tenant_id": tenant_id,
            "attempt_count": 0,
            "max_attempts": max_attempts,
            "interval_minutes": interval_minutes,
            "call_duration_seconds": call_duration_seconds,
            "mode": mode,
            "current_number_index": 0,
            "phone_numbers": phone_chain,
            "status": "active",
            "started_at": now.isoformat(),
            "next_attempt_at": next_attempt.isoformat(),
            "last_attempt_at": None,
            "acknowledged_by": None,
            "acknowledged_at": None,
            "call_history": [],
            "device_type": alert_data.get("device_type", "custom"),
            "problem_description": alert_data.get("problem_description", ""),
        }

        # 6. Persistir no Redis com TTL
        ttl = max_attempts * interval_minutes * 60 + 3600  # margem de 1h
        serialized = serialize_state(state)
        r.setex(key, ttl, serialized)

        # 7. Agendar primeira Celery task
        try:
            from tasks import escalation_cycle

            escalation_cycle.apply_async(
                args=[sensor_id], eta=next_attempt
            )
            logger.info(
                "Escalação iniciada para sensor %d — próximo ciclo em %s",
                sensor_id,
                next_attempt.isoformat(),
            )
        except ImportError:
            logger.warning(
                "Task escalation_cycle não disponível — escalação criada no Redis mas sem agendamento"
            )

        # 8. Registrar início no histórico do incidente
        _log_to_incident_history(db, incident_id, "escalation_started", {
            "sensor_id": sensor_id,
            "mode": mode,
            "max_attempts": max_attempts,
            "interval_minutes": interval_minutes,
            "phone_count": len(phone_chain),
        })

        return state

    finally:
        db.close()


# ─── acknowledge_escalation ─────────────────────────────────────────────────

def acknowledge_escalation(
    sensor_id: int,
    user_id: int,
    notes: str = "",
) -> dict | None:
    """Reconhece uma escalação ativa, parando o loop de ligações.

    Args:
        sensor_id: ID do sensor com escalação ativa.
        user_id: ID do usuário que reconheceu.
        notes: Notas opcionais do reconhecimento.

    Returns:
        Estado atualizado, ou None se não havia escalação ativa.
    """
    r = _get_redis()
    key = _redis_key(sensor_id)

    raw = r.get(key)
    if not raw:
        logger.warning("Nenhuma escalação encontrada para sensor %d", sensor_id)
        return None

    try:
        state = deserialize_state(raw)
    except ValueError:
        logger.error("Estado corrompido no Redis para sensor %d", sensor_id)
        return None

    if state.get("status") != "active":
        logger.info(
            "Escalação para sensor %d já está em status '%s'",
            sensor_id,
            state.get("status"),
        )
        return None

    # 1. Marcar como reconhecido
    now = datetime.now(timezone.utc)
    state["status"] = "acknowledged"
    state["acknowledged_by"] = user_id
    state["acknowledged_at"] = now.isoformat()

    # 2. Atualizar Redis (manter por um tempo para consulta, depois limpar)
    serialized = serialize_state(state)
    r.setex(key, 3600, serialized)  # Manter 1h para histórico

    # 3. Atualizar incidente no banco
    SessionLocal, Incident, _, _ = _import_db()
    db = SessionLocal()
    try:
        incident_id = state.get("incident_id")
        if incident_id:
            incident = db.query(Incident).filter(Incident.id == incident_id).first()
            if incident:
                incident.status = "acknowledged"
                db.commit()

            # 4. Registrar encerramento no histórico
            _log_to_incident_history(db, incident_id, "escalation_acknowledged", {
                "sensor_id": sensor_id,
                "acknowledged_by": user_id,
                "notes": notes,
                "attempt_count": state.get("attempt_count", 0),
            })
    finally:
        db.close()

    logger.info(
        "Escalação reconhecida para sensor %d por usuário %d", sensor_id, user_id
    )
    return state


# ─── stop_escalation ────────────────────────────────────────────────────────

def stop_escalation(sensor_id: int, reason: str = "manual") -> dict | None:
    """Para uma escalação ativa por qualquer motivo.

    Args:
        sensor_id: ID do sensor.
        reason: Motivo da parada (ex: "acknowledged", "resolved", "expired", "manual").

    Returns:
        Estado final, ou None se não havia escalação.
    """
    r = _get_redis()
    key = _redis_key(sensor_id)

    raw = r.get(key)
    if not raw:
        return None

    try:
        state = deserialize_state(raw)
    except ValueError:
        # Estado corrompido — limpar
        r.delete(key)
        r.delete(_lock_key(sensor_id))
        return None

    # Atualizar status baseado no motivo
    if reason == "expired":
        state["status"] = "expired"
    elif reason in ("acknowledged", "resolved"):
        state["status"] = "acknowledged"
    else:
        state["status"] = "acknowledged"  # default: parar = acknowledged

    # Registrar no histórico do incidente
    SessionLocal, _, _, _ = _import_db()
    db = SessionLocal()
    try:
        incident_id = state.get("incident_id")
        if incident_id:
            _log_to_incident_history(db, incident_id, "escalation_stopped", {
                "sensor_id": sensor_id,
                "reason": reason,
                "attempt_count": state.get("attempt_count", 0),
            })
    finally:
        db.close()

    # Limpar Redis — remover estado e lock
    r.delete(key)
    r.delete(_lock_key(sensor_id))

    logger.info("Escalação parada para sensor %d — motivo: %s", sensor_id, reason)
    return state


# ─── get_active_escalations ─────────────────────────────────────────────────

def get_active_escalations(tenant_id: int) -> list[dict]:
    """Retorna lista de escalações ativas para um tenant.

    Args:
        tenant_id: ID do tenant.

    Returns:
        Lista de estados de escalação ativos do tenant.
    """
    r = _get_redis()
    active = []

    # Buscar todas as chaves de escalação
    cursor = 0
    keys = []
    while True:
        cursor, batch = r.scan(cursor, match="escalation:*", count=100)
        # Filtrar apenas chaves numéricas (excluir locks)
        for k in batch:
            key_str = k if isinstance(k, str) else k.decode("utf-8")
            suffix = key_str.split(":")[-1]
            if suffix.isdigit():
                keys.append(key_str)
        if cursor == 0:
            break

    # Ler e filtrar por tenant
    for key in keys:
        raw = r.get(key)
        if not raw:
            continue
        try:
            state = deserialize_state(raw)
        except ValueError:
            continue

        if state.get("tenant_id") == tenant_id and state.get("status") == "active":
            active.append(state)

    return active
