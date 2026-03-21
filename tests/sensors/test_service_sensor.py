"""
Testes para o sensor de serviço Windows (WMI Win32_Service).
Usa mocks para simular conexão WMI — não requer Windows.
"""
import pytest
import time
from unittest.mock import MagicMock, patch, call
from hypothesis import given, settings
from hypothesis import strategies as st

from tests.sensors.service_specs import ServiceEventSpec, ServiceStatusSpec, ServiceStreamingSpec


# ── Helpers ──────────────────────────────────────────────────────────────────

def make_wmi_service(name="Spooler", display_name="Print Spooler",
                     state="Running", start_mode="Auto"):
    svc = MagicMock()
    svc.Name = name
    svc.DisplayName = display_name
    svc.State = state
    svc.StartMode = start_mode
    return svc


def make_wmi_event(service_name="Spooler", display_name="Print Spooler", state="Stopped"):
    """Simula um evento WMI __InstanceModificationEvent para Win32_Service"""
    target = MagicMock()
    target.Name = service_name
    target.DisplayName = display_name
    target.State = state

    event = MagicMock()
    event.TargetInstance = target
    return event


# ── WMIEngine.collect_services ────────────────────────────────────────────────

class TestWMIEngineCollectServices:
    def _make_engine(self, rows):
        from probe.engine.wmi_engine import WMIEngine
        conn = MagicMock()
        conn.query.return_value = rows
        return WMIEngine(conn)

    def test_running_service_returns_value_1(self):
        engine = self._make_engine([make_wmi_service(state="Running")])
        metrics = engine.collect_services()
        assert len(metrics) == 1
        assert metrics[0]["value"] == 1
        assert metrics[0]["status"] == "ok"

    def test_stopped_service_returns_value_0(self):
        engine = self._make_engine([make_wmi_service(state="Stopped")])
        metrics = engine.collect_services()
        assert len(metrics) == 1
        assert metrics[0]["value"] == 0
        assert metrics[0]["status"] == "critical"

    def test_metric_type_is_service(self):
        engine = self._make_engine([make_wmi_service()])
        metrics = engine.collect_services()
        assert metrics[0]["type"] == "service"

    def test_metadata_contains_service_name(self):
        engine = self._make_engine([make_wmi_service(name="W32Time")])
        metrics = engine.collect_services()
        assert metrics[0]["metadata"]["service_name"] == "W32Time"

    def test_empty_rows_returns_empty_list(self):
        engine = self._make_engine([])
        assert engine.collect_services() == []

    def test_filter_auto_only_uses_correct_wql(self):
        conn = MagicMock()
        conn.query.return_value = []
        from probe.engine.wmi_engine import WMIEngine
        engine = WMIEngine(conn)
        engine.collect_services(filter_auto_only=True)
        call_args = conn.query.call_args[0][0]
        assert "StartMode='Auto'" in call_args

    def test_no_filter_uses_full_wql(self):
        conn = MagicMock()
        conn.query.return_value = []
        from probe.engine.wmi_engine import WMIEngine
        engine = WMIEngine(conn)
        engine.collect_services(filter_auto_only=False)
        call_args = conn.query.call_args[0][0]
        # Sem filtro: WHERE StartMode='Auto' não deve aparecer
        assert "WHERE StartMode='Auto'" not in call_args

    def test_unit_is_state(self):
        """ServiceStatusSpec: unit deve ser 'state'"""
        from probe.engine.wmi_engine import WMIEngine
        conn = MagicMock()
        conn.query.return_value = [make_wmi_service()]
        engine = WMIEngine(conn)
        metrics = engine.collect_services()
        assert metrics[0]["unit"] == ServiceStatusSpec.UNIT

    def test_metadata_has_all_required_fields(self):
        """ServiceStatusSpec: metadata deve ter service_name, display_name, state, start_mode"""
        from probe.engine.wmi_engine import WMIEngine
        conn = MagicMock()
        conn.query.return_value = [make_wmi_service(
            name="W32Time", display_name="Windows Time", state="Running", start_mode="Auto"
        )]
        engine = WMIEngine(conn)
        metrics = engine.collect_services()
        meta = metrics[0]["metadata"]
        assert "service_name" in meta
        assert "display_name" in meta
        assert "state" in meta
        assert "start_mode" in meta


# ── SmartCollector.collect_services ──────────────────────────────────────────

class TestSmartCollectorServices:
    def test_collect_services_delegates_to_wmi_engine(self):
        from probe.engine.smart_collector import SmartCollector
        conn = MagicMock()
        conn.query.return_value = [make_wmi_service()]
        sc = SmartCollector(wmi_connection=conn)
        metrics = sc.collect_services()
        assert len(metrics) == 1
        assert metrics[0]["type"] == "service"

    def test_collect_all_includes_services(self):
        from probe.engine.smart_collector import SmartCollector
        conn = MagicMock()
        # Return service row for any query
        conn.query.return_value = [make_wmi_service()]
        sc = SmartCollector(wmi_connection=conn)
        all_metrics = sc.collect_all()
        types = [m["type"] for m in all_metrics]
        assert "service" in types

    def test_collect_services_no_conn_returns_empty(self):
        from probe.engine.smart_collector import SmartCollector
        sc = SmartCollector(wmi_connection=None)
        assert sc.collect_services() == []


# ── WMIEventListener._dispatch ────────────────────────────────────────────────

class TestWMIEventListenerDispatch:
    """
    Testa que _dispatch parseia TargetInstance corretamente
    conforme ServiceEventSpec.
    """

    def _make_listener(self):
        from probe.event_engine.wmi_event_listener import WMIEventListener
        callback = MagicMock()
        listener = WMIEventListener(callback=callback, host="testhost")
        return listener, callback

    def test_service_stopped_dispatches_service_down(self):
        """Running → Stopped deve gerar event_type='service_down', status='critical'"""
        listener, callback = self._make_listener()
        event = make_wmi_event(service_name="Spooler", state="Stopped")
        listener._dispatch("service_change", event)

        callback.assert_called_once()
        result = callback.call_args[0][0]
        assert result["event_type"] == "service_down"
        assert result["status"] == "critical"
        assert result["value"] == 0.0
        assert result["metadata"]["service_name"] == "Spooler"
        assert result["metadata"]["state"] == "Stopped"

    def test_service_running_dispatches_service_recovered(self):
        """Stopped → Running deve gerar event_type='service_recovered', status='ok'"""
        listener, callback = self._make_listener()
        event = make_wmi_event(service_name="Spooler", state="Running")
        listener._dispatch("service_change", event)

        callback.assert_called_once()
        result = callback.call_args[0][0]
        assert result["event_type"] == "service_recovered"
        assert result["status"] == "ok"
        assert result["value"] == 1.0

    def test_non_service_event_still_dispatches(self):
        """Eventos não-service (disk_failure, security_event) devem ser despachados"""
        listener, callback = self._make_listener()
        event = MagicMock()
        listener._dispatch("disk_failure", event)
        callback.assert_called_once()
        result = callback.call_args[0][0]
        assert result["event_type"] == "disk_failure"

    def test_dispatch_includes_host(self):
        """Resultado deve incluir o host correto"""
        listener, callback = self._make_listener()
        event = make_wmi_event(state="Stopped")
        listener._dispatch("service_change", event)
        result = callback.call_args[0][0]
        assert result["host"] == "testhost"

    def test_dispatch_includes_timestamp(self):
        """Resultado deve incluir timestamp numérico"""
        listener, callback = self._make_listener()
        event = make_wmi_event(state="Stopped")
        before = time.time()
        listener._dispatch("service_change", event)
        after = time.time()
        result = callback.call_args[0][0]
        assert before <= result["timestamp"] <= after

    def test_broken_target_instance_does_not_raise(self):
        """Se TargetInstance lançar exceção, _dispatch não deve propagar"""
        listener, callback = self._make_listener()
        event = MagicMock()
        # Fazer TargetInstance.Name lançar exceção
        type(event.TargetInstance).Name = property(lambda self: (_ for _ in ()).throw(RuntimeError("WMI error")))
        # Não deve lançar
        listener._dispatch("service_change", event)
        # callback ainda deve ser chamado (com fallback)
        callback.assert_called_once()


# ── ThresholdEvaluator.get_event_type ────────────────────────────────────────

class TestThresholdEvaluatorServiceEvents:
    """Valida que get_event_type mapeia corretamente para serviços"""

    def test_service_critical_maps_to_service_down(self):
        from event_processor.threshold_evaluator import ThresholdEvaluator
        from core.spec.enums import SensorStatus
        ev = ThresholdEvaluator()
        assert ev.get_event_type("service", SensorStatus.CRITICAL) == "service_down"

    def test_service_ok_maps_to_service_recovered(self):
        """ServiceEventSpec: transição para OK deve gerar 'service_recovered'"""
        from event_processor.threshold_evaluator import ThresholdEvaluator
        from core.spec.enums import SensorStatus
        ev = ThresholdEvaluator()
        assert ev.get_event_type("service", SensorStatus.OK) == "service_recovered"

    def test_service_event_spec_transitions_covered(self):
        """Todos os event_types do ServiceEventSpec devem estar mapeados"""
        from event_processor.threshold_evaluator import ThresholdEvaluator
        from core.spec.enums import SensorStatus
        ev = ThresholdEvaluator()
        # Transições com evento definido no spec
        assert ev.get_event_type("service", SensorStatus.CRITICAL) == "service_down"
        assert ev.get_event_type("service", SensorStatus.OK) == "service_recovered"


# ── Property-based tests ──────────────────────────────────────────────────────

@given(
    state=st.sampled_from(["Running", "Stopped", "Paused", "Start Pending", "Stop Pending"]),
    name=st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"))),
)
@settings(max_examples=50)
def test_service_value_is_binary(state, name):
    """value deve ser sempre 0 ou 1 independente do estado"""
    from probe.engine.wmi_engine import WMIEngine
    conn = MagicMock()
    conn.query.return_value = [make_wmi_service(name=name, state=state)]
    engine = WMIEngine(conn)
    metrics = engine.collect_services(filter_auto_only=False)
    assert len(metrics) == 1
    assert metrics[0]["value"] in (0, 1)


@given(
    states=st.lists(
        st.sampled_from(["Running", "Stopped"]),
        min_size=1,
        max_size=20
    )
)
@settings(max_examples=30)
def test_service_status_matches_value(states):
    """status='ok' ↔ value=1, status='critical' ↔ value=0"""
    from probe.engine.wmi_engine import WMIEngine
    conn = MagicMock()
    conn.query.return_value = [
        make_wmi_service(name=f"Svc{i}", state=s)
        for i, s in enumerate(states)
    ]
    engine = WMIEngine(conn)
    metrics = engine.collect_services(filter_auto_only=False)
    for m in metrics:
        if m["value"] == 1:
            assert m["status"] == "ok"
        else:
            assert m["status"] == "critical"


@given(
    state=st.sampled_from(["Running", "Stopped"]),
)
@settings(max_examples=30)
def test_wmi_event_dispatch_value_matches_state(state):
    """
    PBT: para qualquer estado Running/Stopped,
    _dispatch deve produzir value=1 ↔ Running, value=0 ↔ Stopped
    """
    from probe.event_engine.wmi_event_listener import WMIEventListener
    callback = MagicMock()
    listener = WMIEventListener(callback=callback, host="host")
    event = make_wmi_event(state=state)
    listener._dispatch("service_change", event)
    result = callback.call_args[0][0]
    if state == "Running":
        assert result["value"] == 1.0
        assert result["status"] == "ok"
    else:
        assert result["value"] == 0.0
        assert result["status"] == "critical"
