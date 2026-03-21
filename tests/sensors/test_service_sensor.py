"""
Testes para o sensor de serviço Windows (WMI Win32_Service).
Usa mocks para simular conexão WMI — não requer Windows.
"""
import pytest
from unittest.mock import MagicMock, patch
from hypothesis import given, settings
from hypothesis import strategies as st


# ── Helpers ──────────────────────────────────────────────────────────────────

def make_wmi_service(name="Spooler", display_name="Print Spooler",
                     state="Running", start_mode="Auto"):
    svc = MagicMock()
    svc.Name = name
    svc.DisplayName = display_name
    svc.State = state
    svc.StartMode = start_mode
    return svc


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
        assert "StartMode" not in call_args


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
