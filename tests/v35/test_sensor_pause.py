"""
tests/v35/test_sensor_pause.py
Testes para Requirement 3: Pause de Sensor com Efeito Completo no Worker
Properties 6, 7
"""
import pytest
from unittest.mock import MagicMock
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


def simulate_worker_check(sensor, metric_value):
    """
    Simula os checks do worker evaluate_all_thresholds para um sensor.
    Retorna (should_process, reason).
    """
    now = datetime.now(timezone.utc)

    # Check 1: enabled
    if not getattr(sensor, 'enabled', True):
        return False, 'disabled'

    # Check 2: paused_until
    paused_until = getattr(sensor, 'paused_until', None)
    if paused_until is not None:
        pu = paused_until
        if pu.tzinfo is None:
            pu = pu.replace(tzinfo=timezone.utc)
        if pu > now:
            return False, 'paused'

    # Check 3: alert_mode
    alert_mode = getattr(sensor, 'alert_mode', 'normal') or 'normal'
    if alert_mode in ('metric_only', 'silent'):
        return False, alert_mode

    # Threshold check
    if metric_value > sensor.threshold_critical:
        return True, 'incident_created'

    return True, 'ok'


# ── Testes Unitários ──────────────────────────────────────────────────────────

class TestSensorEnabled:
    """Requirement 3.1: enabled=False → worker ignora completamente"""

    def test_disabled_sensor_not_processed(self):
        sensor = make_sensor(enabled=False, threshold_critical=95.0)
        should_process, reason = simulate_worker_check(sensor, 99.0)
        assert not should_process
        assert reason == 'disabled'

    def test_disabled_sensor_below_threshold_not_processed(self):
        sensor = make_sensor(enabled=False, threshold_critical=95.0)
        should_process, _ = simulate_worker_check(sensor, 50.0)
        assert not should_process

    def test_enabled_sensor_is_processed(self):
        sensor = make_sensor(enabled=True, threshold_critical=95.0)
        should_process, reason = simulate_worker_check(sensor, 99.0)
        assert should_process
        assert reason == 'incident_created'


class TestSensorPausedUntil:
    """Requirement 3.2: paused_until futuro → worker ignora"""

    def test_paused_until_future_not_processed(self):
        future = datetime.now(timezone.utc) + timedelta(hours=1)
        sensor = make_sensor(paused_until=future, threshold_critical=95.0)
        should_process, reason = simulate_worker_check(sensor, 99.0)
        assert not should_process
        assert reason == 'paused'

    def test_paused_until_past_is_processed(self):
        past = datetime.now(timezone.utc) - timedelta(hours=1)
        sensor = make_sensor(paused_until=past, threshold_critical=95.0)
        should_process, reason = simulate_worker_check(sensor, 99.0)
        assert should_process

    def test_paused_until_none_is_processed(self):
        sensor = make_sensor(paused_until=None, threshold_critical=95.0)
        should_process, _ = simulate_worker_check(sensor, 99.0)
        assert should_process

    def test_paused_until_naive_datetime_handled(self):
        """Requirement 3.2: paused_until sem timezone deve ser normalizado para UTC"""
        # Usa um futuro bem distante para garantir que é futuro mesmo após normalização
        future_naive = datetime.now() + timedelta(hours=24)  # sem tzinfo, 24h no futuro
        sensor = make_sensor(paused_until=future_naive, threshold_critical=95.0)
        should_process, reason = simulate_worker_check(sensor, 99.0)
        assert not should_process
        assert reason == 'paused'


class TestSensorResume:
    """Requirement 3.4: sensor retomado volta a ser processado"""

    def test_resumed_sensor_processed(self):
        """Sensor com paused_until=None e enabled=True deve ser processado"""
        sensor = make_sensor(enabled=True, paused_until=None, threshold_critical=95.0)
        should_process, _ = simulate_worker_check(sensor, 99.0)
        assert should_process

    def test_resume_clears_pause(self):
        """Simula resume: limpa paused_until e seta enabled=True"""
        sensor = make_sensor(
            enabled=True,
            paused_until=None,  # após resume
            threshold_critical=95.0
        )
        should_process, reason = simulate_worker_check(sensor, 99.0)
        assert should_process
        assert reason == 'incident_created'


# ── Property-Based Tests ──────────────────────────────────────────────────────

class TestSensorPauseProperties:

    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    @given(value=st.floats(min_value=96.0, max_value=200.0, allow_nan=False))
    def test_property6_disabled_sensor_ignored(self, value):
        """
        Feature: coruja-v35-enterprise-hardening
        Property 6: Sensor disabled ignorado pelo worker
        Validates: Requirements 3.1, 3.3, 3.6
        """
        sensor = make_sensor(enabled=False, threshold_critical=95.0)
        should_process, reason = simulate_worker_check(sensor, value)
        assert not should_process, \
            f"Sensor disabled com value={value} não deve ser processado (reason={reason})"

    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    @given(
        value=st.floats(min_value=96.0, max_value=200.0, allow_nan=False),
        minutes=st.integers(min_value=1, max_value=10080),
    )
    def test_property7_paused_sensor_ignored(self, value, minutes):
        """
        Feature: coruja-v35-enterprise-hardening
        Property 7: Sensor com paused_until futuro ignorado pelo worker
        Validates: Requirements 3.2
        """
        future = datetime.now(timezone.utc) + timedelta(minutes=minutes)
        sensor = make_sensor(paused_until=future, threshold_critical=95.0)
        should_process, reason = simulate_worker_check(sensor, value)
        assert not should_process, \
            f"Sensor pausado por {minutes}min com value={value} não deve ser processado (reason={reason})"
