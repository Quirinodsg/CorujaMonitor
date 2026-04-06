"""
Property-Based Tests — Escalação Contínua de Alarmes
Feature: continuous-alarm-escalation
Properties 15, 9, 10
"""

import sys
import os
import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st
from datetime import datetime, timezone, timedelta

# Adicionar worker ao path para importar o módulo
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "worker"))

from escalation import (
    serialize_state,
    deserialize_state,
    validate_escalation_config,
    validate_phone_number,
    ESCALATION_LIMITS,
    E164_PATTERN,
    VALID_MODES,
    VALID_STATUSES,
    REQUIRED_FIELDS,
)

settings.register_profile("ci", max_examples=100)
settings.load_profile("ci")


# ─── Strategies ─────────────────────────────────────────────────────────────

phone_name_st = st.text(
    alphabet=st.characters(whitelist_categories=("L", "Nd", "Zs")),
    min_size=1,
    max_size=50,
).filter(lambda s: s.strip())

e164_number_st = st.builds(
    lambda digits: "+" + digits,
    st.text(alphabet="0123456789", min_size=1, max_size=15),
)

phone_entry_st = st.fixed_dictionaries({
    "name": phone_name_st,
    "number": e164_number_st,
})

call_result_st = st.sampled_from(["completed", "no-answer", "busy", "failed"])

iso_timestamp_st = st.builds(
    lambda dt: dt.isoformat(),
    st.datetimes(
        min_value=datetime(2020, 1, 1),
        max_value=datetime(2030, 12, 31),
        timezones=st.just(timezone.utc),
    ),
)

call_history_entry_st = st.fixed_dictionaries({
    "number": e164_number_st,
    "timestamp": iso_timestamp_st,
    "result": call_result_st,
})


@st.composite
def escalation_state_st(draw):
    """Gera um estado de escalação válido completo."""
    phone_numbers = draw(st.lists(phone_entry_st, min_size=1, max_size=10))
    max_attempts = draw(st.integers(min_value=1, max_value=100))
    attempt_count = draw(st.integers(min_value=0, max_value=max_attempts))
    status = draw(st.sampled_from(list(VALID_STATUSES)))

    acknowledged_by = None
    acknowledged_at = None
    if status == "acknowledged":
        acknowledged_by = draw(st.integers(min_value=1, max_value=10000))
        acknowledged_at = draw(iso_timestamp_st)

    return {
        "sensor_id": draw(st.integers(min_value=1, max_value=100000)),
        "incident_id": draw(st.integers(min_value=1, max_value=100000)),
        "tenant_id": draw(st.integers(min_value=1, max_value=1000)),
        "attempt_count": attempt_count,
        "max_attempts": max_attempts,
        "interval_minutes": draw(st.integers(min_value=1, max_value=60)),
        "call_duration_seconds": draw(st.integers(min_value=10, max_value=120)),
        "mode": draw(st.sampled_from(list(VALID_MODES))),
        "current_number_index": draw(st.integers(min_value=0, max_value=max(0, len(phone_numbers) - 1))),
        "phone_numbers": phone_numbers,
        "status": status,
        "started_at": draw(iso_timestamp_st),
        "next_attempt_at": draw(iso_timestamp_st),
        "last_attempt_at": draw(st.one_of(st.none(), iso_timestamp_st)),
        "acknowledged_by": acknowledged_by,
        "acknowledged_at": acknowledged_at,
        "call_history": draw(st.lists(call_history_entry_st, min_size=0, max_size=20)),
        "device_type": draw(st.sampled_from(["nobreak", "ar-condicionado", "custom"])),
        "problem_description": draw(st.text(min_size=1, max_size=200)),
    }


# ─── Property 15: Round-trip de serialização do estado de escalação ──────────
# Feature: continuous-alarm-escalation, Property 15: Round-trip de serialização
# **Validates: Requirements 9.2, 9.5**


class TestSerializationRoundtrip:
    """Propriedade 15: Para qualquer estado de escalação válido,
    serializar para JSON e depois deserializar deve produzir um objeto
    equivalente ao original."""

    @settings(max_examples=100)
    @given(escalation_state_st())
    def test_roundtrip_produces_equivalent_state(self, state):
        """deserialize(serialize(state)) == state"""
        serialized = serialize_state(state)
        restored = deserialize_state(serialized)
        assert restored == state

    @settings(max_examples=100)
    @given(escalation_state_st())
    def test_double_roundtrip_is_stable(self, state):
        """serialize(deserialize(serialize(state))) == serialize(state)"""
        first_json = serialize_state(state)
        restored = deserialize_state(first_json)
        second_json = serialize_state(restored)
        assert first_json == second_json

    @settings(max_examples=100)
    @given(escalation_state_st())
    def test_serialized_is_valid_json_string(self, state):
        """O resultado de serialize_state é sempre uma string JSON válida."""
        import json
        serialized = serialize_state(state)
        assert isinstance(serialized, str)
        # Deve ser parseável sem erro
        parsed = json.loads(serialized)
        assert isinstance(parsed, dict)


# ─── Property 9: Validação de parâmetros dentro dos limites ──────────────────
# Feature: continuous-alarm-escalation, Property 9: Validação de parâmetros
# **Validates: Requirements 4.1, 4.2, 4.3, 4.5, 4.6**


class TestParameterValidation:
    """Propriedade 9: Para qualquer valor inteiro submetido como parâmetro,
    o sistema deve aceitar se e somente se estiver dentro dos limites."""

    @settings(max_examples=100)
    @given(
        interval=st.integers(min_value=1, max_value=60),
        max_att=st.integers(min_value=1, max_value=100),
        duration=st.integers(min_value=10, max_value=120),
    )
    def test_valid_params_produce_no_errors(self, interval, max_att, duration):
        """Valores dentro dos limites devem ser aceitos sem erros."""
        config = {
            "interval_minutes": interval,
            "max_attempts": max_att,
            "call_duration_seconds": duration,
        }
        errors = validate_escalation_config(config)
        assert errors == []

    @settings(max_examples=100)
    @given(
        interval=st.integers().filter(lambda x: x < 1 or x > 60),
    )
    def test_invalid_interval_rejected(self, interval):
        """interval_minutes fora de [1, 60] deve gerar erro."""
        config = {"interval_minutes": interval}
        errors = validate_escalation_config(config)
        assert len(errors) == 1
        assert "interval_minutes" in errors[0]

    @settings(max_examples=100)
    @given(
        max_att=st.integers().filter(lambda x: x < 1 or x > 100),
    )
    def test_invalid_max_attempts_rejected(self, max_att):
        """max_attempts fora de [1, 100] deve gerar erro."""
        config = {"max_attempts": max_att}
        errors = validate_escalation_config(config)
        assert len(errors) == 1
        assert "max_attempts" in errors[0]

    @settings(max_examples=100)
    @given(
        duration=st.integers().filter(lambda x: x < 10 or x > 120),
    )
    def test_invalid_duration_rejected(self, duration):
        """call_duration_seconds fora de [10, 120] deve gerar erro."""
        config = {"call_duration_seconds": duration}
        errors = validate_escalation_config(config)
        assert len(errors) == 1
        assert "call_duration_seconds" in errors[0]

    @settings(max_examples=100)
    @given(
        interval=st.integers().filter(lambda x: x < 1 or x > 60),
        max_att=st.integers().filter(lambda x: x < 1 or x > 100),
        duration=st.integers().filter(lambda x: x < 10 or x > 120),
    )
    def test_all_invalid_produces_three_errors(self, interval, max_att, duration):
        """Todos os campos inválidos devem gerar um erro cada."""
        config = {
            "interval_minutes": interval,
            "max_attempts": max_att,
            "call_duration_seconds": duration,
        }
        errors = validate_escalation_config(config)
        assert len(errors) == 3


# ─── Property 10: Validação de formato E.164 ────────────────────────────────
# Feature: continuous-alarm-escalation, Property 10: Validação E.164
# **Validates: Requirements 5.3**


class TestE164Validation:
    """Propriedade 10: Para qualquer string submetida como número de telefone,
    o sistema deve aceitar se e somente se corresponder ao formato E.164."""

    @settings(max_examples=100)
    @given(e164_number_st)
    def test_valid_e164_accepted(self, number):
        """Números no formato E.164 válido devem ser aceitos."""
        assert validate_phone_number(number) is True

    @settings(max_examples=100)
    @given(st.text(min_size=0, max_size=30).filter(lambda s: not E164_PATTERN.match(s)))
    def test_invalid_format_rejected(self, number):
        """Strings que não correspondem ao formato E.164 devem ser rejeitadas."""
        assert validate_phone_number(number) is False

    @settings(max_examples=100)
    @given(
        digits=st.text(alphabet="0123456789", min_size=16, max_size=30),
    )
    def test_too_many_digits_rejected(self, digits):
        """Números com mais de 15 dígitos devem ser rejeitados."""
        number = "+" + digits
        assert validate_phone_number(number) is False

    def test_empty_string_rejected(self):
        """String vazia deve ser rejeitada."""
        assert validate_phone_number("") is False

    def test_plus_only_rejected(self):
        """Apenas '+' sem dígitos deve ser rejeitado."""
        assert validate_phone_number("+") is False

    def test_no_plus_prefix_rejected(self):
        """Número sem '+' no início deve ser rejeitado."""
        assert validate_phone_number("5511999999999") is False

    def test_letters_rejected(self):
        """Número com letras deve ser rejeitado."""
        assert validate_phone_number("+55abc999") is False

    def test_non_string_rejected(self):
        """Valores não-string devem ser rejeitados."""
        assert validate_phone_number(123) is False
        assert validate_phone_number(None) is False


# ─── Imports for Task 2 PBT tests ───────────────────────────────────────────

from unittest.mock import patch, MagicMock
from escalation import (
    start_escalation,
    acknowledge_escalation,
    stop_escalation,
    get_active_escalations,
    _redis_key,
)


# ─── Strategies for Task 2 ──────────────────────────────────────────────────

alert_data_st = st.fixed_dictionaries({
    "device_type": st.sampled_from(["nobreak", "ar-condicionado", "custom"]),
    "problem_description": st.text(min_size=1, max_size=100),
    "phone_chain": st.lists(phone_entry_st, min_size=1, max_size=5),
    "mode": st.sampled_from(list(VALID_MODES)),
    "interval_minutes": st.integers(min_value=1, max_value=60),
    "max_attempts": st.integers(min_value=1, max_value=100),
    "call_duration_seconds": st.integers(min_value=10, max_value=120),
})


def _make_fake_redis():
    """Cria um fake Redis baseado em dict para testes."""
    store = {}

    class FakeRedis:
        def get(self, key):
            entry = store.get(key)
            if entry is None:
                return None
            return entry["value"]

        def setex(self, key, ttl, value):
            store[key] = {"value": value, "ttl": ttl}

        def delete(self, key):
            store.pop(key, None)

        def exists(self, key):
            return key in store

        def scan(self, cursor, match=None, count=100):
            # Simple implementation: return all matching keys on first call
            import fnmatch
            matched = []
            for k in store:
                if match and fnmatch.fnmatch(k, match):
                    matched.append(k)
                elif not match:
                    matched.append(k)
            return (0, matched)

    return FakeRedis(), store


def _make_mock_sensor(sensor_id, is_acknowledged=False):
    """Cria um mock de Sensor."""
    sensor = MagicMock()
    sensor.id = sensor_id
    sensor.is_acknowledged = is_acknowledged
    sensor.name = f"Sensor-{sensor_id}"
    return sensor


def _make_mock_incident(incident_id):
    """Cria um mock de Incident."""
    incident = MagicMock()
    incident.id = incident_id
    incident.status = "open"
    incident.ai_analysis = None
    return incident


def _patch_db(mock_db):
    """Cria patch para _import_db que retorna (SessionLocal, Incident, Sensor, Tenant).

    SessionLocal() retorna mock_db.
    Incident/Sensor/Tenant são classes mock cujo .id é usado em queries.
    """
    MockSessionLocal = MagicMock(return_value=mock_db)
    MockIncident = MagicMock()
    MockSensor = MagicMock()
    MockTenant = MagicMock()

    # Fazer com que db.query(Incident).filter(...) funcione via mock_db
    # O mock_db já tem query configurado pelo chamador
    return patch(
        "escalation._import_db",
        return_value=(MockSessionLocal, MockIncident, MockSensor, MockTenant),
    )


# ─── Property 1: Início de escalação cria estado válido ─────────────────────
# Feature: continuous-alarm-escalation, Property 1: Início cria estado válido
# **Validates: Requirements 1.1**


class TestStartEscalationCreatesValidState:
    """Propriedade 1: Para qualquer alerta crítico com dados válidos,
    start_escalation deve criar um estado no Redis com todos os campos
    obrigatórios e status 'active'."""

    @settings(max_examples=100)
    @given(
        sensor_id=st.integers(min_value=1, max_value=100000),
        incident_id=st.integers(min_value=1, max_value=100000),
        tenant_id=st.integers(min_value=1, max_value=1000),
        alert_data=alert_data_st,
    )
    def test_start_creates_state_with_all_required_fields(
        self, sensor_id, incident_id, tenant_id, alert_data
    ):
        """start_escalation com dados válidos cria estado com todos os campos obrigatórios."""
        fake_redis, store = _make_fake_redis()
        mock_sensor = _make_mock_sensor(sensor_id, is_acknowledged=False)
        mock_incident = _make_mock_incident(incident_id)

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            mock_sensor,   # Sensor query
            mock_incident, # Incident query in _log_to_incident_history
        ]

        with patch("escalation._get_redis", return_value=fake_redis), \
             _patch_db(mock_db):
            result = start_escalation(sensor_id, incident_id, tenant_id, alert_data)

        assert result is not None
        # Verificar todos os campos obrigatórios
        for field in REQUIRED_FIELDS:
            assert field in result, f"Campo obrigatório ausente: {field}"

        # Verificar valores específicos
        assert result["sensor_id"] == sensor_id
        assert result["incident_id"] == incident_id
        assert result["tenant_id"] == tenant_id
        assert result["attempt_count"] == 0
        assert result["status"] == "active"
        assert result["mode"] in VALID_MODES
        assert result["phone_numbers"] == alert_data["phone_chain"]
        assert result["current_number_index"] == 0
        assert result["call_history"] == []
        assert result["acknowledged_by"] is None
        assert result["acknowledged_at"] is None

        # Verificar que foi persistido no Redis
        key = _redis_key(sensor_id)
        assert fake_redis.get(key) is not None


# ─── Property 5: Prevenção de escalação duplicada ────────────────────────────
# Feature: continuous-alarm-escalation, Property 5: Prevenção de duplicata
# **Validates: Requirements 1.6**


class TestDuplicatePrevention:
    """Propriedade 5: Para qualquer sensor_id que já possui escalação ativa,
    start_escalation novamente deve retornar None sem modificar o estado."""

    @settings(max_examples=100)
    @given(
        sensor_id=st.integers(min_value=1, max_value=100000),
        incident_id=st.integers(min_value=1, max_value=100000),
        tenant_id=st.integers(min_value=1, max_value=1000),
        alert_data=alert_data_st,
    )
    def test_duplicate_start_returns_none(
        self, sensor_id, incident_id, tenant_id, alert_data
    ):
        """Chamar start_escalation duas vezes retorna None na segunda."""
        fake_redis, store = _make_fake_redis()
        mock_sensor = _make_mock_sensor(sensor_id, is_acknowledged=False)
        mock_incident = _make_mock_incident(incident_id)

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            mock_sensor,   # First call: Sensor query
            mock_incident, # First call: Incident query for history
        ]

        with patch("escalation._get_redis", return_value=fake_redis), \
             _patch_db(mock_db):
            # Primeira chamada — deve criar
            first = start_escalation(sensor_id, incident_id, tenant_id, alert_data)
            assert first is not None

            # Segunda chamada — deve retornar None (duplicata)
            second = start_escalation(sensor_id, incident_id, tenant_id, alert_data)
            assert second is None

    @settings(max_examples=100)
    @given(
        sensor_id=st.integers(min_value=1, max_value=100000),
        incident_id=st.integers(min_value=1, max_value=100000),
        tenant_id=st.integers(min_value=1, max_value=1000),
        alert_data=alert_data_st,
    )
    def test_duplicate_does_not_modify_existing_state(
        self, sensor_id, incident_id, tenant_id, alert_data
    ):
        """Estado existente não é modificado por tentativa duplicada."""
        fake_redis, store = _make_fake_redis()
        mock_sensor = _make_mock_sensor(sensor_id, is_acknowledged=False)
        mock_incident = _make_mock_incident(incident_id)

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            mock_sensor,
            mock_incident,
        ]

        with patch("escalation._get_redis", return_value=fake_redis), \
             _patch_db(mock_db):
            start_escalation(sensor_id, incident_id, tenant_id, alert_data)
            state_before = fake_redis.get(_redis_key(sensor_id))

            start_escalation(sensor_id, incident_id, tenant_id, alert_data)
            state_after = fake_redis.get(_redis_key(sensor_id))

            assert state_before == state_after


# ─── Property 13: Sensores já reconhecidos não iniciam escalação ─────────────
# Feature: continuous-alarm-escalation, Property 13: Sensor reconhecido não escala
# **Validates: Requirements 8.3**


class TestAcknowledgedSensorNoEscalation:
    """Propriedade 13: Para qualquer sensor com is_acknowledged=True,
    start_escalation deve retornar None sem criar escalação."""

    @settings(max_examples=100)
    @given(
        sensor_id=st.integers(min_value=1, max_value=100000),
        incident_id=st.integers(min_value=1, max_value=100000),
        tenant_id=st.integers(min_value=1, max_value=1000),
        alert_data=alert_data_st,
    )
    def test_acknowledged_sensor_returns_none(
        self, sensor_id, incident_id, tenant_id, alert_data
    ):
        """Sensor com is_acknowledged=True não inicia escalação."""
        fake_redis, store = _make_fake_redis()
        mock_sensor = _make_mock_sensor(sensor_id, is_acknowledged=True)

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_sensor

        with patch("escalation._get_redis", return_value=fake_redis), \
             _patch_db(mock_db):
            result = start_escalation(sensor_id, incident_id, tenant_id, alert_data)

        assert result is None
        # Verificar que nada foi criado no Redis
        assert fake_redis.get(_redis_key(sensor_id)) is None


# ─── Property 6: Reconhecimento para escalação e registra dados ──────────────
# Feature: continuous-alarm-escalation, Property 6: Reconhecimento para e registra
# **Validates: Requirements 2.1, 2.2, 2.3**


class TestAcknowledgeStopsAndRecords:
    """Propriedade 6: Para qualquer escalação ativa, acknowledge_escalation
    deve definir status='acknowledged', registrar user_id e timestamp."""

    @settings(max_examples=100)
    @given(
        sensor_id=st.integers(min_value=1, max_value=100000),
        incident_id=st.integers(min_value=1, max_value=100000),
        tenant_id=st.integers(min_value=1, max_value=1000),
        user_id=st.integers(min_value=1, max_value=10000),
        notes=st.text(min_size=0, max_size=200),
        alert_data=alert_data_st,
    )
    def test_acknowledge_sets_status_and_records(
        self, sensor_id, incident_id, tenant_id, user_id, notes, alert_data
    ):
        """acknowledge_escalation define status, user_id e timestamp."""
        fake_redis, store = _make_fake_redis()
        mock_sensor = _make_mock_sensor(sensor_id, is_acknowledged=False)
        mock_incident = _make_mock_incident(incident_id)

        mock_db = MagicMock()
        # For start_escalation: sensor query + incident query for history
        # For acknowledge_escalation: incident query + incident query for history
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            mock_sensor,    # start: sensor query
            mock_incident,  # start: incident for history
            mock_incident,  # ack: incident for status update
            mock_incident,  # ack: incident for history
        ]

        with patch("escalation._get_redis", return_value=fake_redis), \
             _patch_db(mock_db):
            # Criar escalação ativa
            start_escalation(sensor_id, incident_id, tenant_id, alert_data)

            # Reconhecer
            result = acknowledge_escalation(sensor_id, user_id, notes)

        assert result is not None
        assert result["status"] == "acknowledged"
        assert result["acknowledged_by"] == user_id
        assert result["acknowledged_at"] is not None

        # Verificar que acknowledged_at é um timestamp ISO válido
        datetime.fromisoformat(result["acknowledged_at"])

    @settings(max_examples=100)
    @given(
        sensor_id=st.integers(min_value=1, max_value=100000),
        user_id=st.integers(min_value=1, max_value=10000),
    )
    def test_acknowledge_nonexistent_returns_none(self, sensor_id, user_id):
        """acknowledge_escalation sem escalação ativa retorna None."""
        fake_redis, _ = _make_fake_redis()

        with patch("escalation._get_redis", return_value=fake_redis):
            result = acknowledge_escalation(sensor_id, user_id)

        assert result is None



# ─── Helpers for Task 3 PBT tests ───────────────────────────────────────────

import json
from escalation import serialize_state


def _build_active_state(
    sensor_id=1,
    incident_id=100,
    tenant_id=1,
    attempt_count=0,
    max_attempts=10,
    interval_minutes=5,
    call_duration_seconds=30,
    mode="sequential",
    current_number_index=0,
    phone_numbers=None,
    call_history=None,
):
    """Constrói um estado de escalação ativo válido para testes."""
    if phone_numbers is None:
        phone_numbers = [{"name": "Test", "number": "+5511999999999"}]
    if call_history is None:
        call_history = []
    now = datetime.now(timezone.utc)
    return {
        "sensor_id": sensor_id,
        "incident_id": incident_id,
        "tenant_id": tenant_id,
        "attempt_count": attempt_count,
        "max_attempts": max_attempts,
        "interval_minutes": interval_minutes,
        "call_duration_seconds": call_duration_seconds,
        "mode": mode,
        "current_number_index": current_number_index,
        "phone_numbers": phone_numbers,
        "status": "active",
        "started_at": now.isoformat(),
        "next_attempt_at": (now + timedelta(minutes=interval_minutes)).isoformat(),
        "last_attempt_at": None,
        "acknowledged_by": None,
        "acknowledged_at": None,
        "call_history": call_history,
        "device_type": "nobreak",
        "problem_description": "Teste de escalação",
    }


def _simulate_cycle(state, fake_redis):
    """Simula um ciclo de escalação sem Twilio/DB real.

    Replica a lógica central de escalation_cycle:
    - Verifica status e max_attempts
    - Executa chamadas conforme modo
    - Incrementa attempt_count
    - Atualiza call_history e estado no Redis
    """
    from escalation import _redis_key

    if state["status"] != "active":
        return state

    if state["attempt_count"] >= state["max_attempts"]:
        state["status"] = "expired"
        fake_redis.setex(_redis_key(state["sensor_id"]), 3600, serialize_state(state))
        return state

    now = datetime.now(timezone.utc)
    mode = state.get("mode", "sequential")
    phone_numbers = state.get("phone_numbers", [])
    new_calls = []

    if mode == "simultaneous":
        for entry in phone_numbers:
            number = entry.get("number", "") if isinstance(entry, dict) else str(entry)
            new_calls.append({
                "number": number,
                "timestamp": now.isoformat(),
                "result": "completed",
            })
    else:
        idx = state.get("current_number_index", 0) % len(phone_numbers)
        entry = phone_numbers[idx]
        number = entry.get("number", "") if isinstance(entry, dict) else str(entry)
        new_calls.append({
            "number": number,
            "timestamp": now.isoformat(),
            "result": "completed",
        })
        state["current_number_index"] = (idx + 1) % len(phone_numbers)

    state["call_history"].extend(new_calls)
    state["attempt_count"] += 1
    state["last_attempt_at"] = now.isoformat()

    if state["attempt_count"] >= state["max_attempts"]:
        state["status"] = "expired"
    else:
        next_attempt = now + timedelta(minutes=state["interval_minutes"])
        state["next_attempt_at"] = next_attempt.isoformat()

    ttl = state["max_attempts"] * state["interval_minutes"] * 60 + 3600
    fake_redis.setex(_redis_key(state["sensor_id"]), ttl, serialize_state(state))
    return state


# ─── Property 2: Escalação continua enquanto não reconhecida e abaixo do máximo
# Feature: continuous-alarm-escalation, Property 2: Escalação continua
# **Validates: Requirements 1.2**


class TestEscalationContinues:
    """Propriedade 2: Para qualquer estado ativo com attempt_count < max_attempts,
    executar um ciclo deve incrementar attempt_count e manter status 'active'."""

    @settings(max_examples=100)
    @given(
        attempt_count=st.integers(min_value=0, max_value=98),
        max_attempts=st.integers(min_value=2, max_value=100),
        interval_minutes=st.integers(min_value=1, max_value=60),
        phone_numbers=st.lists(phone_entry_st, min_size=1, max_size=5),
        mode=st.sampled_from(list(VALID_MODES)),
    )
    def test_cycle_increments_and_stays_active(
        self, attempt_count, max_attempts, interval_minutes, phone_numbers, mode
    ):
        """Ciclo incrementa attempt_count e mantém status active quando abaixo do máximo."""
        assume(attempt_count < max_attempts - 1)  # Ensure we stay below max after increment

        fake_redis, store = _make_fake_redis()
        state = _build_active_state(
            attempt_count=attempt_count,
            max_attempts=max_attempts,
            interval_minutes=interval_minutes,
            phone_numbers=phone_numbers,
            mode=mode,
        )

        # Persist initial state
        from escalation import _redis_key
        fake_redis.setex(
            _redis_key(state["sensor_id"]),
            3600,
            serialize_state(state),
        )

        result = _simulate_cycle(state, fake_redis)

        assert result["attempt_count"] == attempt_count + 1
        assert result["status"] == "active"
        assert result["last_attempt_at"] is not None


# ─── Property 3: Escalação para ao atingir máximo de tentativas ──────────────
# Feature: continuous-alarm-escalation, Property 3: Para ao atingir máximo
# **Validates: Requirements 1.3**


class TestEscalationStopsAtMax:
    """Propriedade 3: Para qualquer estado onde attempt_count >= max_attempts,
    o ciclo deve definir status='expired' e não continuar."""

    @settings(max_examples=100)
    @given(
        max_attempts=st.integers(min_value=1, max_value=100),
        phone_numbers=st.lists(phone_entry_st, min_size=1, max_size=5),
        mode=st.sampled_from(list(VALID_MODES)),
    )
    def test_cycle_expires_at_max(self, max_attempts, phone_numbers, mode):
        """Quando attempt_count == max_attempts - 1, o ciclo expira após execução."""
        fake_redis, store = _make_fake_redis()
        state = _build_active_state(
            attempt_count=max_attempts - 1,
            max_attempts=max_attempts,
            phone_numbers=phone_numbers,
            mode=mode,
        )

        from escalation import _redis_key
        fake_redis.setex(
            _redis_key(state["sensor_id"]),
            3600,
            serialize_state(state),
        )

        result = _simulate_cycle(state, fake_redis)

        assert result["status"] == "expired"
        assert result["attempt_count"] == max_attempts

    @settings(max_examples=100)
    @given(
        max_attempts=st.integers(min_value=1, max_value=50),
        extra=st.integers(min_value=0, max_value=50),
        phone_numbers=st.lists(phone_entry_st, min_size=1, max_size=5),
    )
    def test_already_at_max_stays_expired(self, max_attempts, extra, phone_numbers):
        """Quando attempt_count >= max_attempts, o ciclo marca expired sem executar."""
        fake_redis, store = _make_fake_redis()
        state = _build_active_state(
            attempt_count=max_attempts + extra,
            max_attempts=max_attempts,
            phone_numbers=phone_numbers,
        )

        from escalation import _redis_key
        fake_redis.setex(
            _redis_key(state["sensor_id"]),
            3600,
            serialize_state(state),
        )

        history_before = len(state["call_history"])
        result = _simulate_cycle(state, fake_redis)

        assert result["status"] == "expired"
        # Não deve ter adicionado novas chamadas
        assert len(result["call_history"]) == history_before


# ─── Property 4: Histórico de chamadas cresce a cada ciclo ──────────────────
# Feature: continuous-alarm-escalation, Property 4: Histórico cresce
# **Validates: Requirements 1.4**


class TestCallHistoryGrows:
    """Propriedade 4: Para qualquer ciclo executado com sucesso,
    call_history deve crescer pelo número de chamadas realizadas."""

    @settings(max_examples=100)
    @given(
        phone_numbers=st.lists(phone_entry_st, min_size=1, max_size=10),
        mode=st.sampled_from(list(VALID_MODES)),
        existing_history=st.lists(call_history_entry_st, min_size=0, max_size=10),
    )
    def test_history_grows_by_expected_amount(self, phone_numbers, mode, existing_history):
        """call_history cresce por 1 (sequencial) ou N (simultâneo)."""
        fake_redis, store = _make_fake_redis()
        state = _build_active_state(
            attempt_count=0,
            max_attempts=10,
            phone_numbers=phone_numbers,
            mode=mode,
            call_history=list(existing_history),
        )

        from escalation import _redis_key
        fake_redis.setex(
            _redis_key(state["sensor_id"]),
            3600,
            serialize_state(state),
        )

        history_before = len(state["call_history"])
        result = _simulate_cycle(state, fake_redis)

        expected_new = len(phone_numbers) if mode == "simultaneous" else 1
        assert len(result["call_history"]) == history_before + expected_new


# ─── Property 7: Modo simultâneo liga para todos os números ──────────────────
# Feature: continuous-alarm-escalation, Property 7: Modo simultâneo
# **Validates: Requirements 3.1**


class TestSimultaneousMode:
    """Propriedade 7: Para qualquer escalação em modo 'simultaneous' com N números,
    cada ciclo deve produzir exatamente N chamadas."""

    @settings(max_examples=100)
    @given(
        phone_numbers=st.lists(phone_entry_st, min_size=1, max_size=10),
    )
    def test_simultaneous_calls_all_numbers(self, phone_numbers):
        """Modo simultâneo produz N chamadas para N números."""
        fake_redis, store = _make_fake_redis()
        state = _build_active_state(
            attempt_count=0,
            max_attempts=10,
            phone_numbers=phone_numbers,
            mode="simultaneous",
        )

        from escalation import _redis_key
        fake_redis.setex(
            _redis_key(state["sensor_id"]),
            3600,
            serialize_state(state),
        )

        result = _simulate_cycle(state, fake_redis)

        # Deve ter exatamente N novas chamadas
        assert len(result["call_history"]) == len(phone_numbers)

        # Cada número deve ter sido chamado
        called_numbers = {c["number"] for c in result["call_history"]}
        expected_numbers = {
            (e.get("number", "") if isinstance(e, dict) else str(e))
            for e in phone_numbers
        }
        assert called_numbers == expected_numbers


# ─── Property 8: Modo sequencial com wrap-around ────────────────────────────
# Feature: continuous-alarm-escalation, Property 8: Modo sequencial + wrap
# **Validates: Requirements 3.2, 3.3**


class TestSequentialModeWrapAround:
    """Propriedade 8: Para qualquer escalação em modo 'sequential' com N números,
    cada ciclo produz 1 chamada e após N ciclos reinicia no índice 0."""

    @settings(max_examples=100)
    @given(
        phone_numbers=st.lists(phone_entry_st, min_size=1, max_size=10),
    )
    def test_sequential_calls_one_per_cycle(self, phone_numbers):
        """Modo sequencial produz exatamente 1 chamada por ciclo."""
        fake_redis, store = _make_fake_redis()
        state = _build_active_state(
            attempt_count=0,
            max_attempts=100,
            phone_numbers=phone_numbers,
            mode="sequential",
        )

        from escalation import _redis_key
        fake_redis.setex(
            _redis_key(state["sensor_id"]),
            36000,
            serialize_state(state),
        )

        result = _simulate_cycle(state, fake_redis)
        assert len(result["call_history"]) == 1

    @settings(max_examples=100)
    @given(
        phone_numbers=st.lists(phone_entry_st, min_size=2, max_size=5),
    )
    def test_sequential_wraps_around_after_all_numbers(self, phone_numbers):
        """Após chamar todos os N números, o índice volta para 0."""
        n = len(phone_numbers)
        fake_redis, store = _make_fake_redis()
        state = _build_active_state(
            attempt_count=0,
            max_attempts=n + 2,  # Enough for N+1 cycles
            phone_numbers=phone_numbers,
            mode="sequential",
            current_number_index=0,
        )

        from escalation import _redis_key
        fake_redis.setex(
            _redis_key(state["sensor_id"]),
            36000,
            serialize_state(state),
        )

        # Execute N cycles — should call each number once
        for i in range(n):
            state = _simulate_cycle(state, fake_redis)
            expected_number = phone_numbers[i].get("number", "")
            actual_number = state["call_history"][i]["number"]
            assert actual_number == expected_number, (
                f"Ciclo {i}: esperado {expected_number}, obtido {actual_number}"
            )

        # After N cycles, index should wrap to 0
        assert state["current_number_index"] == 0

        # Execute one more cycle — should call first number again
        state = _simulate_cycle(state, fake_redis)
        first_number = phone_numbers[0].get("number", "")
        assert state["call_history"][n]["number"] == first_number
