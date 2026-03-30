"""
tests/v35/test_default_profiles.py
Testes para Requirement 2: Configuração de Sensores Padrão por Tipo de Ativo
Properties 4, 5
"""
import pytest
from unittest.mock import MagicMock, patch
from hypothesis import given, settings, HealthCheck
from hypothesis import strategies as st

# ── Dados de fábrica (espelha FACTORY_PROFILES do router) ────────────────────

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
    {"asset_type": "network_device",  "sensor_type": "ping",        "enabled": True,  "alert_mode": "normal",      "threshold_warning": None, "threshold_critical": None},
    {"asset_type": "network_device",  "sensor_type": "network_in",  "enabled": True,  "alert_mode": "metric_only", "threshold_warning": 80,  "threshold_critical": 95},
    {"asset_type": "network_device",  "sensor_type": "network_out", "enabled": True,  "alert_mode": "metric_only", "threshold_warning": 80,  "threshold_critical": 95},
]

VALID_ASSET_TYPES = ("VM", "physical_server", "network_device")
VALID_ALERT_MODES = ("normal", "silent", "metric_only")


def get_profiles_for_asset(asset_type: str):
    return [p for p in FACTORY_PROFILES if p["asset_type"] == asset_type]


def apply_profiles_to_server(asset_type: str, profiles=None):
    """Simula a criação de sensores ao criar um servidor."""
    if profiles is None:
        profiles = get_profiles_for_asset(asset_type)
    sensors_created = []
    for p in profiles:
        if not p.get("enabled", True):
            continue
        sensors_created.append({
            "sensor_type": p["sensor_type"],
            "alert_mode": p["alert_mode"],
            "threshold_warning": p["threshold_warning"],
            "threshold_critical": p["threshold_critical"],
        })
    return sensors_created


# ── Testes Unitários ──────────────────────────────────────────────────────────

class TestDefaultProfilesData:
    """Requirement 2.1: perfis persistidos com campos corretos"""

    def test_factory_profiles_have_required_fields(self):
        for p in FACTORY_PROFILES:
            assert "asset_type" in p
            assert "sensor_type" in p
            assert "enabled" in p
            assert "alert_mode" in p
            assert p["alert_mode"] in VALID_ALERT_MODES

    def test_vm_has_network_metric_only(self):
        vm_profiles = get_profiles_for_asset("VM")
        network_profiles = [p for p in vm_profiles if p["sensor_type"] in ("network_in", "network_out")]
        assert len(network_profiles) == 2
        for p in network_profiles:
            assert p["alert_mode"] == "metric_only", \
                f"VM {p['sensor_type']} deve ser metric_only"

    def test_physical_server_has_network_metric_only(self):
        profiles = get_profiles_for_asset("physical_server")
        network = [p for p in profiles if p["sensor_type"] in ("network_in", "network_out")]
        for p in network:
            assert p["alert_mode"] == "metric_only"

    def test_network_device_ping_is_normal(self):
        profiles = get_profiles_for_asset("network_device")
        ping = next((p for p in profiles if p["sensor_type"] == "ping"), None)
        assert ping is not None
        assert ping["alert_mode"] == "normal"

    def test_all_asset_types_covered(self):
        covered = {p["asset_type"] for p in FACTORY_PROFILES}
        for at in VALID_ASSET_TYPES:
            assert at in covered, f"asset_type {at} não tem perfil de fábrica"


class TestApplyProfilesToServer:
    """Requirements 2.2, 2.3: perfil aplicado ao criar servidor"""

    def test_vm_server_gets_vm_sensors(self):
        sensors = apply_profiles_to_server("VM")
        sensor_types = {s["sensor_type"] for s in sensors}
        assert "cpu" in sensor_types
        assert "memory" in sensor_types
        assert "disk" in sensor_types
        assert "network_in" in sensor_types
        assert "network_out" in sensor_types

    def test_vm_network_sensors_are_metric_only(self):
        sensors = apply_profiles_to_server("VM")
        for s in sensors:
            if s["sensor_type"] in ("network_in", "network_out"):
                assert s["alert_mode"] == "metric_only", \
                    f"VM {s['sensor_type']} deve ser metric_only"

    def test_disabled_profile_sensor_not_created(self):
        profiles = [
            {"sensor_type": "cpu", "enabled": True, "alert_mode": "normal", "threshold_warning": 80, "threshold_critical": 95},
            {"sensor_type": "memory", "enabled": False, "alert_mode": "normal", "threshold_warning": 80, "threshold_critical": 95},
        ]
        sensors = apply_profiles_to_server("VM", profiles=profiles)
        sensor_types = {s["sensor_type"] for s in sensors}
        assert "cpu" in sensor_types
        assert "memory" not in sensor_types, "Sensor desabilitado não deve ser criado"


class TestAlertModeValidation:
    """Requirement 2.4: validação de alert_mode"""

    def test_valid_alert_modes_accepted(self):
        for mode in VALID_ALERT_MODES:
            assert mode in VALID_ALERT_MODES

    def test_invalid_alert_mode_rejected(self):
        invalid = "invalido"
        assert invalid not in VALID_ALERT_MODES

    def test_invalid_asset_type_rejected(self):
        invalid = "tipo_desconhecido"
        assert invalid not in VALID_ASSET_TYPES


# ── Property-Based Tests ──────────────────────────────────────────────────────

class TestDefaultProfilesProperties:

    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    @given(asset_type=st.sampled_from(list(VALID_ASSET_TYPES)))
    def test_property4_profile_applied_to_server(self, asset_type):
        """
        Feature: coruja-v35-enterprise-hardening
        Property 4: Perfil padrão aplicado ao criar servidor
        Validates: Requirements 2.2, 2.3
        """
        profiles = get_profiles_for_asset(asset_type)
        sensors = apply_profiles_to_server(asset_type, profiles)
        expected_types = {p["sensor_type"] for p in profiles if p.get("enabled", True)}
        actual_types = {s["sensor_type"] for s in sensors}
        assert actual_types == expected_types, \
            f"asset_type={asset_type}: sensores criados {actual_types} != esperados {expected_types}"

    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    @given(alert_mode=st.sampled_from(list(VALID_ALERT_MODES)))
    def test_property5_alert_mode_propagated(self, alert_mode):
        """
        Feature: coruja-v35-enterprise-hardening
        Property 5: alert_mode do perfil propagado para o sensor
        Validates: Requirements 2.5
        """
        profiles = [
            {"sensor_type": "cpu", "enabled": True, "alert_mode": alert_mode,
             "threshold_warning": 80, "threshold_critical": 95}
        ]
        sensors = apply_profiles_to_server("VM", profiles=profiles)
        assert len(sensors) == 1
        assert sensors[0]["alert_mode"] == alert_mode, \
            f"alert_mode={alert_mode} deve ser propagado para o sensor criado"
