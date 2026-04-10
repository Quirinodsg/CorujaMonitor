"""
Testes de propriedade para notification-silent-failure bugfix.

Bug Condition Tests: validam que os 3 bugs foram corrigidos.
Preservation Tests: garantem que o comportamento existente não foi quebrado.

**Validates: Requirements 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.3, 2.4, 3.1, 3.2, 3.3, 3.4, 3.5**
"""
import sys
import os
import logging
from unittest.mock import MagicMock, patch
from hypothesis import given, settings, HealthCheck
from hypothesis import strategies as st

# Adicionar worker ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'worker'))

from notification_dispatcher import (
    resolve_channels,
    VALID_CHANNELS,
    VALID_SENSOR_TYPES,
    DEFAULT_MATRIX,
    METRIC_ONLY_TYPES,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_sensor(server_id=None, probe_id=None, sensor_type='http', sensor_id=1):
    sensor = MagicMock()
    sensor.id = sensor_id
    sensor.server_id = server_id
    sensor.probe_id = probe_id
    sensor.sensor_type = sensor_type
    sensor.name = f'sensor_{sensor_id}'
    sensor.priority = 3
    return sensor


def _make_incident(incident_id=10, sensor_id=1):
    incident = MagicMock()
    incident.id = incident_id
    incident.sensor_id = sensor_id
    incident.title = 'Test incident'
    incident.description = 'desc'
    incident.severity = 'critical'
    incident.created_at = None
    return incident


def _make_tenant(tenant_id=7):
    tenant = MagicMock()
    tenant.id = tenant_id
    tenant.notification_matrix = None
    tenant.notification_config = {}
    return tenant


def _make_db_mock(incident, sensor, server, probe, tenant):
    """Cria um mock de db.query que retorna os objetos fornecidos por nome de classe."""
    mock_db = MagicMock()

    def db_query_side_effect(model):
        q = MagicMock()
        name = getattr(model, '__name__', str(model))
        if name == 'Incident':
            q.filter.return_value.first.return_value = incident
        elif name == 'Sensor':
            q.filter.return_value.first.return_value = sensor
        elif name == 'Server':
            q.filter.return_value.first.return_value = server
        elif name == 'Probe':
            q.filter.return_value.first.return_value = probe
        elif name == 'Tenant':
            q.filter.return_value.first.return_value = tenant
        else:
            q.filter.return_value.first.return_value = None
        return q

    mock_db.query.side_effect = db_query_side_effect
    return mock_db


def _patch_db_modules(mock_db):
    """
    Mocka database e models no sys.modules para evitar importação real
    (que falha por pydantic config no ambiente de teste).
    As classes em mock_models têm __name__ correto para o side_effect funcionar.
    """
    mock_database = MagicMock()
    mock_database.SessionLocal = MagicMock(return_value=mock_db)

    mock_models = MagicMock()
    for cls_name in ('Incident', 'Sensor', 'Server', 'Tenant', 'Probe'):
        cls_mock = MagicMock()
        cls_mock.__name__ = cls_name
        setattr(mock_models, cls_name, cls_mock)

    return patch.dict('sys.modules', {
        'database': mock_database,
        'models': mock_models,
    })


# ---------------------------------------------------------------------------
# Bug Condition Tests
# ---------------------------------------------------------------------------

class TestBugConditionStandaloneSensorWithProbe:
    """
    Bug 1 — Sensor standalone com probe_id válido deve resolver tenant via probe.

    **Validates: Requirements 2.1**
    """

    def test_bug_condition_standalone_sensor_with_probe_resolves_tenant(self):
        """
        Para sensor com server_id=None e probe_id válido, dispatch_notifications
        deve resolver o tenant via probe (não retornar 'Tenant não encontrado').
        """
        sensor = _make_sensor(server_id=None, probe_id=42, sensor_type='http')
        incident = _make_incident()
        tenant = _make_tenant(tenant_id=7)

        probe = MagicMock()
        probe.id = 42
        probe.tenant_id = 7

        mock_db = _make_db_mock(incident, sensor, server=None, probe=probe, tenant=tenant)

        with _patch_db_modules(mock_db):
            from notification_dispatcher import dispatch_notifications
            result = dispatch_notifications(incident_id=10)

        # O resultado NÃO deve conter 'Tenant não encontrado'
        failed_errors = [f.get('error', '') for f in result.get('failed', [])]
        assert 'Tenant não encontrado' not in failed_errors, (
            f"Bug 1 ainda presente: dispatch retornou 'Tenant não encontrado' "
            f"para sensor standalone com probe_id válido. failed={result['failed']}"
        )


class TestBugConditionStandaloneSensorNoProbe:
    """
    Bug 1 (variante) — Sensor standalone sem probe_id deve logar warning e retornar falha explícita.

    **Validates: Requirements 2.2**
    """

    def test_bug_condition_standalone_sensor_no_probe_logs_warning(self, caplog):
        """
        Para sensor com server_id=None e probe_id=None, dispatch_notifications deve:
        - Retornar failed=[{'channel': 'all', 'error': 'Tenant não encontrado'}]
        - Logar um warning (não falhar silenciosamente)
        """
        sensor = _make_sensor(server_id=None, probe_id=None, sensor_type='http')
        incident = _make_incident()

        mock_db = _make_db_mock(incident, sensor, server=None, probe=None, tenant=None)

        with _patch_db_modules(mock_db):
            with caplog.at_level(logging.WARNING, logger='notification_dispatcher'):
                from notification_dispatcher import dispatch_notifications
                result = dispatch_notifications(incident_id=10)

        # Deve retornar falha explícita
        assert result.get('failed') == [{'channel': 'all', 'error': 'Tenant não encontrado'}], (
            f"Bug 1 (sem probe) ainda presente: resultado inesperado: {result}"
        )

        # Deve ter logado um warning (não falha silenciosa)
        warning_messages = [r.message for r in caplog.records if r.levelno >= logging.WARNING]
        assert any('Tenant não encontrado' in msg or 'tenant' in msg.lower() for msg in warning_messages), (
            f"Bug 1 (sem probe) ainda presente: nenhum warning logado. "
            f"Logs capturados: {warning_messages}"
        )


class TestBugConditionRebootEmailRemoved:
    """
    Bug 3 — _send_reboot_email com tenant hardcoded deve ser removida.

    **Validates: Requirements 2.4**
    """

    def test_bug_condition_reboot_email_function_removed(self):
        """
        Verifica que _send_reboot_email NÃO existe em worker/tasks.py.
        O teste FALHA se a função ainda existir (confirma que o bug ainda está presente).
        """
        tasks_path = os.path.join(os.path.dirname(__file__), '..', 'worker', 'tasks.py')
        tasks_path = os.path.abspath(tasks_path)

        with open(tasks_path, 'r', encoding='utf-8') as f:
            source = f.read()

        func_defined = 'def _send_reboot_email(' in source

        assert not func_defined, (
            "Bug 3 ainda presente: _send_reboot_email ainda existe em worker/tasks.py. "
            "A função contém 'Tenant.id == 1' hardcoded e deve ser removida. "
            "Ela é código morto — o reboot já usa dispatch_notifications_task corretamente."
        )


class TestBugConditionAutoResolveCallsDispatchResolution:
    """
    Bug 2 — Auto-resolve deve chamar dispatch_resolution_task.delay.

    **Validates: Requirements 2.3**
    """

    def test_bug_condition_auto_resolve_calls_dispatch_resolution(self):
        """
        Verifica que o bloco de auto-resolve em evaluate_all_thresholds
        chama dispatch_resolution_task.delay quando sensor volta ao normal.
        """
        tasks_path = os.path.join(os.path.dirname(__file__), '..', 'worker', 'tasks.py')
        tasks_path = os.path.abspath(tasks_path)

        with open(tasks_path, 'r', encoding='utf-8') as f:
            source = f.read()

        # Verificar que dispatch_resolution_task.delay está presente no source
        assert 'dispatch_resolution_task' in source, (
            "Bug 2 ainda presente: 'dispatch_resolution_task' não encontrado em worker/tasks.py"
        )
        assert 'dispatch_resolution_task.delay' in source, (
            "Bug 2 ainda presente: 'dispatch_resolution_task.delay' não encontrado em worker/tasks.py. "
            "O auto-resolve deve chamar dispatch_resolution_task.delay(incident.id)"
        )

        # Verificar que está no contexto do auto-resolve
        assert 'Auto-resolvido: sensor voltou ao normal' in source, (
            "Texto de auto-resolve não encontrado em tasks.py"
        )

        # Verificar que dispatch_resolution_task.delay aparece após o commit de resolução
        resolve_idx = source.find('Auto-resolvido: sensor voltou ao normal')
        dispatch_idx = source.find('dispatch_resolution_task.delay', resolve_idx)

        assert dispatch_idx != -1, (
            "Bug 2 ainda presente: dispatch_resolution_task.delay não aparece após "
            "o bloco de auto-resolve em tasks.py"
        )


# ---------------------------------------------------------------------------
# Preservation Tests
# ---------------------------------------------------------------------------

class TestPreservationResolveChannels:
    """
    Preservation — resolve_channels deve retornar canais válidos e não-vazios
    para todos os sensor_types exceto metric_only.

    **Validates: Requirements 3.1, 3.2, 3.3**
    """

    @given(
        sensor_type=st.sampled_from(sorted(VALID_SENSOR_TYPES - METRIC_ONLY_TYPES))
    )
    @settings(suppress_health_check=[HealthCheck.too_slow], max_examples=50)
    def test_preservation_resolve_channels_never_empty(self, sensor_type):
        """
        Para qualquer sensor_type válido (exceto network_in/network_out),
        resolve_channels retorna conjunto não-vazio e subconjunto de VALID_CHANNELS.

        **Validates: Requirements 3.1, 3.2, 3.5**
        """
        channels = resolve_channels(sensor_type)

        assert isinstance(channels, set), (
            f"resolve_channels('{sensor_type}') deve retornar set, retornou {type(channels)}"
        )
        assert len(channels) > 0, (
            f"resolve_channels('{sensor_type}') retornou conjunto vazio — "
            f"deve ter fallback para {{'email'}}"
        )
        assert channels.issubset(VALID_CHANNELS), (
            f"resolve_channels('{sensor_type}') retornou canais inválidos: "
            f"{channels - VALID_CHANNELS}"
        )

    def test_preservation_resolve_channels_metric_only_empty(self):
        """
        DEFAULT_MATRIX tem lista vazia para network_in/network_out (metric_only).
        METRIC_ONLY_TYPES contém ambos. dispatch_notifications intercepta antes de
        chamar resolve_channels para esses tipos.

        **Validates: Requirements 3.3**
        """
        # Verificar que DEFAULT_MATRIX tem lista vazia para esses tipos
        assert DEFAULT_MATRIX['network_in'] == [], (
            "DEFAULT_MATRIX['network_in'] deve ser [] (metric_only)"
        )
        assert DEFAULT_MATRIX['network_out'] == [], (
            "DEFAULT_MATRIX['network_out'] deve ser [] (metric_only)"
        )

        # Verificar que METRIC_ONLY_TYPES contém ambos
        assert 'network_in' in METRIC_ONLY_TYPES
        assert 'network_out' in METRIC_ONLY_TYPES

        # resolve_channels aplica fallback 'email' para listas vazias
        # (o dispatch_notifications é quem ignora metric_only antes de chamar resolve_channels)
        channels_in = resolve_channels('network_in')
        channels_out = resolve_channels('network_out')
        assert isinstance(channels_in, set)
        assert isinstance(channels_out, set)


class TestPreservationDefaultMatrix:
    """
    Preservation — DEFAULT_MATRIX deve conter os tipos esperados com os canais corretos.

    **Validates: Requirements 3.1, 3.2, 3.3**
    """

    def test_preservation_default_matrix_matches_ui(self):
        """
        Verifica que DEFAULT_MATRIX contém os tipos esperados com os canais corretos
        conforme a UI de configuração.

        **Validates: Requirements 3.1, 3.2, 3.3**
        """
        # ping: contém email, teams, ticket
        ping_channels = set(DEFAULT_MATRIX.get('ping', []))
        assert 'email' in ping_channels, "DEFAULT_MATRIX['ping'] deve conter 'email'"
        assert 'teams' in ping_channels, "DEFAULT_MATRIX['ping'] deve conter 'teams'"
        assert 'ticket' in ping_channels, "DEFAULT_MATRIX['ping'] deve conter 'ticket'"

        # http: contém email, teams, ticket, sms, whatsapp
        http_channels = set(DEFAULT_MATRIX.get('http', []))
        assert 'email' in http_channels, "DEFAULT_MATRIX['http'] deve conter 'email'"
        assert 'teams' in http_channels, "DEFAULT_MATRIX['http'] deve conter 'teams'"
        assert 'ticket' in http_channels, "DEFAULT_MATRIX['http'] deve conter 'ticket'"
        assert 'sms' in http_channels, "DEFAULT_MATRIX['http'] deve conter 'sms'"
        assert 'whatsapp' in http_channels, "DEFAULT_MATRIX['http'] deve conter 'whatsapp'"

        # system: contém apenas email
        system_channels = set(DEFAULT_MATRIX.get('system', []))
        assert system_channels == {'email'}, (
            f"DEFAULT_MATRIX['system'] deve conter apenas 'email', contém: {system_channels}"
        )

        # network_in: lista vazia
        assert DEFAULT_MATRIX.get('network_in') == [], (
            "DEFAULT_MATRIX['network_in'] deve ser lista vazia"
        )

        # network_out: lista vazia
        assert DEFAULT_MATRIX.get('network_out') == [], (
            "DEFAULT_MATRIX['network_out'] deve ser lista vazia"
        )


class TestPreservationSensorWithServerId:
    """
    Preservation — Sensor com server_id válido deve usar server.tenant_id (não fallback probe).

    **Validates: Requirements 3.1**
    """

    def test_preservation_sensor_with_server_id_uses_server_tenant(self):
        """
        Para sensor com server_id válido, dispatch_notifications usa server.tenant_id
        (não o caminho de fallback probe).
        """
        sensor = _make_sensor(server_id=5, probe_id=99, sensor_type='ping')
        incident = _make_incident()
        tenant = _make_tenant(tenant_id=3)

        server = MagicMock()
        server.id = 5
        server.tenant_id = 3
        server.hostname = 'server-prod-01'

        probe_called = []

        mock_db = MagicMock()

        def db_query_side_effect(model):
            q = MagicMock()
            name = getattr(model, '__name__', str(model))
            if name == 'Incident':
                q.filter.return_value.first.return_value = incident
            elif name == 'Sensor':
                q.filter.return_value.first.return_value = sensor
            elif name == 'Server':
                q.filter.return_value.first.return_value = server
            elif name == 'Probe':
                probe_called.append(True)
                q.filter.return_value.first.return_value = None
            elif name == 'Tenant':
                q.filter.return_value.first.return_value = tenant
            else:
                q.filter.return_value.first.return_value = None
            return q

        mock_db.query.side_effect = db_query_side_effect

        with _patch_db_modules(mock_db):
            from notification_dispatcher import dispatch_notifications
            result = dispatch_notifications(incident_id=10)

        # Não deve ter retornado 'Tenant não encontrado'
        failed_errors = [f.get('error', '') for f in result.get('failed', [])]
        assert 'Tenant não encontrado' not in failed_errors, (
            f"Sensor com server_id válido não deveria retornar 'Tenant não encontrado'. "
            f"failed={result['failed']}"
        )

        # O caminho de fallback via Probe não deve ter sido acionado
        assert len(probe_called) == 0, (
            "Sensor com server_id válido não deve consultar Probe para resolver tenant. "
            f"Probe foi consultado {len(probe_called)} vez(es)."
        )
