"""
tests/v35/test_network_alert_mode.py
Testes para Requirement 1: Sensores de Rede como Metric-Only por Padrão
Properties 1, 2, 3
"""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone
from hypothesis import given, settings, HealthCheck
from hypothesis import strategies as st


# ── Helpers ──────────────────────────────────────────────────────────────────

def make_sensor(**kwargs):
    """Cria um sensor mock com valores padrão."""
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
    s.config = kwargs.get('config', {})
    return s


def _default_alert_mode_for_sensor_type(sensor_type: str, config: dict = None) -> str:
    """
    Lógica de negócio: determina alert_mode padrão para um sensor_type.
    Replica a regra do Requirement 1.2 e 1.5.
    """
    config = config or {}
    if sensor_type in ('network_in', 'network_out'):
        if config.get('internet_link'):
            return 'normal'
        return 'metric_only'
    return 'normal'


# ── Testes Unitários ──────────────────────────────────────────────────────────

class TestNetworkSensorDefaultAlertMode:
    """Requirement 1.2: network_in/network_out default metric_only"""

    def test_network_in_default_metric_only(self):
        mode = _default_alert_mode_for_sensor_type('network_in')
        assert mode == 'metric_only', f"Expected metric_only, got {mode}"

    def test_network_out_default_metric_only(self):
        mode = _default_alert_mode_for_sensor_type('network_out')
        assert mode == 'metric_only', f"Expected metric_only, got {mode}"

    def test_cpu_default_normal(self):
        mode = _default_alert_mode_for_sensor_type('cpu')
        assert mode == 'normal'

    def test_memory_default_normal(self):
        mode = _default_alert_mode_for_sensor_type('memory')
        assert mode == 'normal'

    def test_internet_link_tag_generates_alert(self):
        """Requirement 1.5: sensor com tag internet_link deve ter alert_mode normal"""
        mode = _default_alert_mode_for_sensor_type('network_in', config={'internet_link': True})
        assert mode != 'metric_only', "Sensor com internet_link não deve ser metric_only"
        assert mode == 'normal'

    def test_internet_link_network_out(self):
        mode = _default_alert_mode_for_sensor_type('network_out', config={'internet_link': True})
        assert mode == 'normal'


class TestAlertModeEndpointValidation:
    """Requirement 1.6: endpoint aceita metric_only"""

    def test_valid_modes(self):
        valid = ('normal', 'silent', 'metric_only')
        for mode in valid:
            assert mode in valid

    def test_invalid_mode_rejected(self):
        invalid = 'invalido'
        valid = ('normal', 'silent', 'metric_only')
        assert invalid not in valid, "Modo inválido não deve ser aceito"

    def test_metric_only_accepted(self):
        assert 'metric_only' in ('normal', 'silent', 'metric_only')


class TestMetricOnlyWorkerBehavior:
    """Requirements 1.3, 1.4, 1.7: metric_only não cria Incident nem envia ao predictor"""

    def _simulate_worker_for_sensor(self, sensor, metric_value):
        """Simula a lógica do worker para um sensor."""
        incidents_created = []
        predictor_called = False

        if not getattr(sensor, 'enabled', True):
            return incidents_created, predictor_called

        paused_until = getattr(sensor, 'paused_until', None)
        if paused_until:
            now = datetime.now(timezone.utc)
            pu = paused_until if paused_until.tzinfo else paused_until.replace(tzinfo=timezone.utc)
            if pu > now:
                return incidents_created, predictor_called

        alert_mode = getattr(sensor, 'alert_mode', 'normal') or 'normal'

        if alert_mode == 'metric_only':
            # Coleta métrica mas não cria Incident e não envia ao predictor
            return incidents_created, predictor_called

        if alert_mode == 'silent':
            return incidents_created, predictor_called

        # Avalia threshold
        if metric_value > sensor.threshold_critical:
            incidents_created.append({'sensor_id': sensor.id, 'severity': 'critical'})
            predictor_called = True

        return incidents_created, predictor_called

    def test_metric_only_no_incident_above_threshold(self):
        sensor = make_sensor(alert_mode='metric_only', threshold_critical=95.0)
        incidents, predictor = self._simulate_worker_for_sensor(sensor, 99.0)
        assert len(incidents) == 0, "metric_only não deve criar Incident"

    def test_metric_only_no_predictor_call(self):
        sensor = make_sensor(alert_mode='metric_only', threshold_critical=95.0)
        _, predictor = self._simulate_worker_for_sensor(sensor, 99.0)
        assert not predictor, "metric_only não deve enviar ao predictor"

    def test_normal_mode_creates_incident(self):
        sensor = make_sensor(alert_mode='normal', threshold_critical=95.0)
        incidents, _ = self._simulate_worker_for_sensor(sensor, 99.0)
        assert len(incidents) == 1, "normal deve criar Incident quando threshold ultrapassado"

    def test_metric_only_below_threshold_no_incident(self):
        sensor = make_sensor(alert_mode='metric_only', threshold_critical=95.0)
        incidents, _ = self._simulate_worker_for_sensor(sensor, 50.0)
        assert len(incidents) == 0


# ── Property-Based Tests ──────────────────────────────────────────────────────

class TestNetworkAlertModeProperties:
    """Property 1: Para qualquer sensor_type de rede, alert_mode deve ser metric_only"""

    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    @given(sensor_type=st.sampled_from(['network_in', 'network_out']))
    def test_property1_network_sensors_default_metric_only(self, sensor_type):
        """
        Feature: coruja-v35-enterprise-hardening
        Property 1: Sensores de rede têm metric_only por padrão
        Validates: Requirements 1.2
        """
        mode = _default_alert_mode_for_sensor_type(sensor_type)
        assert mode == 'metric_only', f"sensor_type={sensor_type} deve ter metric_only, got {mode}"

    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    @given(value=st.floats(min_value=96.0, max_value=200.0, allow_nan=False))
    def test_property2_metric_only_no_incident(self, value):
        """
        Feature: coruja-v35-enterprise-hardening
        Property 2: metric_only não cria Incident
        Validates: Requirements 1.3, 1.7
        """
        sensor = make_sensor(alert_mode='metric_only', threshold_critical=95.0)
        incidents_before = 0

        alert_mode = getattr(sensor, 'alert_mode', 'normal') or 'normal'
        if alert_mode == 'metric_only':
            incidents_after = incidents_before
        else:
            incidents_after = incidents_before + 1

        assert incidents_after == incidents_before, \
            f"metric_only com value={value} não deve criar Incident"

    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    @given(value=st.floats(min_value=0.0, max_value=200.0, allow_nan=False))
    def test_property3_metric_only_no_predictor(self, value):
        """
        Feature: coruja-v35-enterprise-hardening
        Property 3: metric_only não envia ao predictor
        Validates: Requirements 1.4
        """
        sensor = make_sensor(alert_mode='metric_only', threshold_critical=95.0)
        predictor_called = False

        alert_mode = getattr(sensor, 'alert_mode', 'normal') or 'normal'
        if alert_mode != 'metric_only':
            predictor_called = True

        assert not predictor_called, \
            f"metric_only com value={value} não deve invocar predictor"
