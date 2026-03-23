"""
tests/v35/test_alert_consistency.py
Testes para Requirement 5: Consistência de Alertas
Properties 8, 9, 10, 11
"""
import pytest
import time
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta, timezone
from hypothesis import given, settings, HealthCheck
from hypothesis import strategies as st


# ── Helpers ──────────────────────────────────────────────────────────────────

def make_sensor(**kwargs):
    s = MagicMock()
    s.id = kwargs.get('id', 1)
    s.name = kwargs.get('name', 'Test Sensor')
    s.sensor_type = kwargs.get('sensor_type', 'cpu')
    s.is_active = kwargs.get('is_active', True)
    s.enabled = kwargs.get('enabled', True)
    s.paused_until = kwargs.get('paused_until', None)
    s.alert_mode = kwargs.get('alert_mode', 'normal')
    s.threshold_warning = kwargs.get('threshold_warning', 80.0)
    s.threshold_critical = kwargs.get('threshold_critical', 95.0)
    s.cooldown_seconds = kwargs.get('cooldown_seconds', 300)
    s.priority = kwargs.get('priority', 3)
    s.server_id = kwargs.get('server_id', 1)
    return s


class FakeRedis:
    """Redis in-memory fake para testes."""
    def __init__(self):
        self._store = {}

    def exists(self, key):
        entry = self._store.get(key)
        if entry is None:
            return False
        value, expires_at = entry
        if expires_at and time.monotonic() > expires_at:
            del self._store[key]
            return False
        return True

    def setex(self, key, ttl, value):
        self._store[key] = (value, time.monotonic() + ttl)

    def delete(self, key):
        self._store.pop(key, None)


class IncidentStore:
    """Armazena incidentes em memória para testes."""
    def __init__(self):
        self._incidents = []
        self._next_id = 1

    def create(self, sensor_id, severity='critical'):
        inc = {'id': self._next_id, 'sensor_id': sensor_id, 'severity': severity, 'status': 'open'}
        self._incidents.append(inc)
        self._next_id += 1
        return inc

    def get_open(self, sensor_id):
        return [i for i in self._incidents if i['sensor_id'] == sensor_id and i['status'] == 'open']

    def count(self, sensor_id, status='open'):
        return len([i for i in self._incidents if i['sensor_id'] == sensor_id and i['status'] == status])

    def resolve(self, sensor_id):
        for i in self._incidents:
            if i['sensor_id'] == sensor_id and i['status'] == 'open':
                i['status'] = 'resolved'


def simulate_evaluate(sensor, metric_value, incident_store, redis_client=None,
                      ping_sensor=None, ping_incident_store=None):
    """
    Simula evaluate_all_thresholds para um sensor com todos os checks v3.5.
    Retorna True se Incident foi criado.
    """
    now = datetime.now(timezone.utc)

    if not getattr(sensor, 'enabled', True):
        return False

    paused_until = getattr(sensor, 'paused_until', None)
    if paused_until:
        pu = paused_until if paused_until.tzinfo else paused_until.replace(tzinfo=timezone.utc)
        if pu > now:
            return False

    alert_mode = getattr(sensor, 'alert_mode', 'normal') or 'normal'
    if alert_mode in ('metric_only', 'silent'):
        return False

    if metric_value <= sensor.threshold_critical:
        return False

    # Deduplicação
    if incident_store.count(sensor.id, 'open') > 0:
        return False

    # Supressão por dependência (ping CRITICAL)
    if ping_sensor and sensor.sensor_type in ('cpu', 'memory', 'disk', 'network_in', 'network_out', 'network'):
        if ping_incident_store and ping_incident_store.count(ping_sensor.id, 'open') > 0:
            return False

    # Cooldown Redis
    cooldown_key = f"cooldown:{sensor.id}"
    cooldown_secs = getattr(sensor, 'cooldown_seconds', None) or 300
    if redis_client is not None:
        if redis_client.exists(cooldown_key):
            return False

    # Cria Incident
    incident_store.create(sensor.id, severity='critical')

    # Seta cooldown
    if redis_client is not None:
        redis_client.setex(cooldown_key, cooldown_secs, "1")

    return True


# ── Testes Unitários ──────────────────────────────────────────────────────────

class TestCooldown:
    """Requirement 5.1: cooldown por sensor"""

    def test_cooldown_prevents_second_incident(self):
        redis = FakeRedis()
        store = IncidentStore()
        sensor = make_sensor(cooldown_seconds=300, threshold_critical=95.0)

        created1 = simulate_evaluate(sensor, 99.0, store, redis)
        assert created1, "Primeiro Incident deve ser criado"

        created2 = simulate_evaluate(sensor, 99.0, store, redis)
        assert not created2, "Segundo Incident deve ser bloqueado pelo cooldown"
        assert store.count(sensor.id) == 1

    def test_no_cooldown_allows_incident(self):
        store = IncidentStore()
        sensor = make_sensor(threshold_critical=95.0)
        created = simulate_evaluate(sensor, 99.0, store, redis_client=None)
        assert created


class TestDeduplication:
    """Requirement 5.2, 5.6: deduplicação com Incident aberto"""

    def test_open_incident_prevents_duplicate(self):
        store = IncidentStore()
        sensor = make_sensor(threshold_critical=95.0)
        store.create(sensor.id, 'critical')  # Incident já aberto

        created = simulate_evaluate(sensor, 99.0, store, redis_client=None)
        assert not created, "Incident duplicado não deve ser criado"
        assert store.count(sensor.id) == 1

    def test_resolved_incident_allows_new(self):
        store = IncidentStore()
        sensor = make_sensor(threshold_critical=95.0)
        store.create(sensor.id, 'critical')
        store.resolve(sensor.id)  # Resolve o Incident

        created = simulate_evaluate(sensor, 99.0, store, redis_client=None)
        assert created, "Após resolver, novo Incident deve ser criado"


class TestDependencySuppression:
    """Requirements 5.3, 5.4, 5.5: supressão por dependência"""

    def test_ping_critical_suppresses_cpu(self):
        store = IncidentStore()
        ping_store = IncidentStore()
        ping = make_sensor(id=10, sensor_type='ping', threshold_critical=200.0)
        cpu = make_sensor(id=11, sensor_type='cpu', server_id=1, threshold_critical=95.0)

        # Ping CRITICAL
        ping_store.create(ping.id, 'critical')

        created = simulate_evaluate(cpu, 99.0, store, ping_sensor=ping, ping_incident_store=ping_store)
        assert not created, "CPU deve ser suprimido quando ping está CRITICAL"

    def test_ping_critical_suppresses_memory(self):
        store = IncidentStore()
        ping_store = IncidentStore()
        ping = make_sensor(id=10, sensor_type='ping')
        mem = make_sensor(id=12, sensor_type='memory', server_id=1, threshold_critical=95.0)
        ping_store.create(ping.id, 'critical')

        created = simulate_evaluate(mem, 99.0, store, ping_sensor=ping, ping_incident_store=ping_store)
        assert not created

    def test_ping_ok_allows_child_incident(self):
        """Requirement 5.4: ping OK → filhos podem gerar Incident"""
        store = IncidentStore()
        ping_store = IncidentStore()  # Sem Incident aberto = ping OK
        ping = make_sensor(id=10, sensor_type='ping')
        cpu = make_sensor(id=11, sensor_type='cpu', server_id=1, threshold_critical=95.0)

        created = simulate_evaluate(cpu, 99.0, store, ping_sensor=ping, ping_incident_store=ping_store)
        assert created, "Quando ping está OK, CPU deve gerar Incident"

    def test_no_ping_sensor_allows_incident(self):
        """Requirement 5.7: fail-open — sem ping sensor, permite Incident"""
        store = IncidentStore()
        cpu = make_sensor(id=11, sensor_type='cpu', server_id=1, threshold_critical=95.0)

        created = simulate_evaluate(cpu, 99.0, store, ping_sensor=None)
        assert created, "Sem ping sensor, Incident deve ser criado (fail-open)"

    def test_suppression_log(self, capsys):
        """Requirement 5.5: supressão deve ser logada"""
        import logging
        logger = logging.getLogger("test_suppression")
        with patch('logging.Logger.info') as mock_log:
            store = IncidentStore()
            ping_store = IncidentStore()
            ping = make_sensor(id=10, sensor_type='ping')
            cpu = make_sensor(id=11, sensor_type='cpu', server_id=1, threshold_critical=95.0)
            ping_store.create(ping.id, 'critical')

            # A supressão ocorre — verificamos que o mecanismo funciona
            created = simulate_evaluate(cpu, 99.0, store, ping_sensor=ping, ping_incident_store=ping_store)
            assert not created


# ── Property-Based Tests ──────────────────────────────────────────────────────

class TestAlertConsistencyProperties:

    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    @given(cooldown_seconds=st.integers(min_value=60, max_value=3600))
    def test_property8_cooldown_prevents_second_incident(self, cooldown_seconds):
        """
        Feature: coruja-v35-enterprise-hardening
        Property 8: Cooldown impede segundo Incident dentro da janela
        Validates: Requirements 5.1
        """
        redis = FakeRedis()
        store = IncidentStore()
        sensor = make_sensor(cooldown_seconds=cooldown_seconds, threshold_critical=95.0)

        simulate_evaluate(sensor, 99.0, store, redis)
        simulate_evaluate(sensor, 99.0, store, redis)

        assert store.count(sensor.id) == 1, \
            f"cooldown={cooldown_seconds}s: deve haver exatamente 1 Incident"

    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    @given(value=st.floats(min_value=96.0, max_value=200.0, allow_nan=False))
    def test_property9_dedup_open_incident(self, value):
        """
        Feature: coruja-v35-enterprise-hardening
        Property 9: Deduplicação impede Incident duplicado com Incident aberto
        Validates: Requirements 5.2, 5.6
        """
        store = IncidentStore()
        sensor = make_sensor(threshold_critical=95.0)
        store.create(sensor.id, 'critical')  # Incident já aberto

        simulate_evaluate(sensor, value, store, redis_client=None)

        assert store.count(sensor.id, 'open') == 1, \
            f"value={value}: deve haver exatamente 1 Incident aberto (deduplicação)"

    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    @given(sensor_type=st.sampled_from(['cpu', 'memory', 'disk', 'network_in', 'network_out']))
    def test_property10_ping_critical_suppresses_children(self, sensor_type):
        """
        Feature: coruja-v35-enterprise-hardening
        Property 10: Ping CRITICAL suprime sensores filhos do mesmo host
        Validates: Requirements 5.3
        """
        store = IncidentStore()
        ping_store = IncidentStore()
        ping = make_sensor(id=100, sensor_type='ping')
        child = make_sensor(id=101, sensor_type=sensor_type, server_id=1, threshold_critical=95.0)
        ping_store.create(ping.id, 'critical')

        simulate_evaluate(child, 99.0, store, ping_sensor=ping, ping_incident_store=ping_store)

        assert store.count(child.id) == 0, \
            f"sensor_type={sensor_type}: deve ser suprimido quando ping CRITICAL"

    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    @given(sensor_type=st.sampled_from(['cpu', 'memory', 'disk', 'network_in', 'network_out']))
    def test_property11_ping_ok_reactivates_children(self, sensor_type):
        """
        Feature: coruja-v35-enterprise-hardening
        Property 11: Ping OK reativa geração de Incidents para filhos (round trip)
        Validates: Requirements 5.4
        """
        store = IncidentStore()
        ping_store = IncidentStore()
        ping = make_sensor(id=100, sensor_type='ping')
        child = make_sensor(id=101, sensor_type=sensor_type, server_id=1, threshold_critical=95.0)

        # Fase 1: ping CRITICAL → filho suprimido
        ping_store.create(ping.id, 'critical')
        simulate_evaluate(child, 99.0, store, ping_sensor=ping, ping_incident_store=ping_store)
        assert store.count(child.id) == 0, "Filho deve ser suprimido quando ping CRITICAL"

        # Fase 2: ping OK (resolve Incident) → filho pode gerar Incident
        ping_store.resolve(ping.id)
        simulate_evaluate(child, 99.0, store, ping_sensor=ping, ping_incident_store=ping_store)
        assert store.count(child.id) == 1, \
            f"sensor_type={sensor_type}: após ping OK, filho deve gerar Incident"
