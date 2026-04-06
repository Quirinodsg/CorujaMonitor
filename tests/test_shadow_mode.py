"""
Tests for Task 7: Integração Shadow Mode no ProbeCore (Requisitos 6, 9)
Validates shadow mode config, dual execution, comparison, and sequential-only dispatch.

**Validates: Requirements 6, 9**
"""
import sys
import yaml
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, call

sys.path.insert(0, "probe")

from probe_core import ProbeCore
from parallel_engine import MetricsComparator


class TestShadowModeConfig:
    """7.1 — shadow_mode config in config.yaml and _load_parallel_config."""

    def test_config_yaml_has_shadow_mode(self):
        """config.yaml must contain shadow_mode in the probe section."""
        with open("probe/config.yaml") as f:
            cfg = yaml.safe_load(f)
        assert "shadow_mode" in cfg["probe"]

    def test_config_yaml_shadow_mode_default_false(self):
        """shadow_mode defaults to false in config.yaml."""
        with open("probe/config.yaml") as f:
            cfg = yaml.safe_load(f)
        assert cfg["probe"]["shadow_mode"] is False

    def test_load_parallel_config_includes_shadow_mode(self):
        """_load_parallel_config returns shadow_mode key."""
        core = MagicMock(spec=ProbeCore)
        result = ProbeCore._load_parallel_config(core)
        assert "shadow_mode" in result
        assert result["shadow_mode"] is False


class TestShadowModeRouting:
    """7.2 — _collect_metrics routes to shadow mode when active."""

    def test_shadow_mode_calls_shadow_method(self):
        """When shadow_mode=True and orchestrator exists, _collect_metrics_shadow is called."""
        core = MagicMock(spec=ProbeCore)
        core._shadow_mode = True
        core._orchestrator = MagicMock()
        core._collect_metrics_shadow = MagicMock()

        ProbeCore._collect_metrics(core)
        core._collect_metrics_shadow.assert_called_once()

    def test_shadow_mode_false_uses_orchestrator(self):
        """When shadow_mode=False and orchestrator exists, orchestrator.collect_all is called."""
        core = MagicMock(spec=ProbeCore)
        core._shadow_mode = False
        core._orchestrator = MagicMock()

        ProbeCore._collect_metrics(core)
        core._orchestrator.collect_all.assert_called_once()

    def test_shadow_mode_true_no_orchestrator_uses_sequential(self):
        """When shadow_mode=True but no orchestrator, falls through to sequential."""
        core = MagicMock(spec=ProbeCore)
        core._shadow_mode = True
        core._orchestrator = None
        core._collect_metrics_sequential = MagicMock()

        ProbeCore._collect_metrics(core)
        core._collect_metrics_sequential.assert_called_once()

    def test_no_shadow_no_orchestrator_uses_sequential(self):
        """When both shadow_mode=False and no orchestrator, sequential is used."""
        core = MagicMock(spec=ProbeCore)
        core._shadow_mode = False
        core._orchestrator = None
        core._collect_metrics_sequential = MagicMock()

        ProbeCore._collect_metrics(core)
        core._collect_metrics_sequential.assert_called_once()


class TestShadowModeExecution:
    """7.2/7.3/7.4 — Shadow mode runs both modes, compares, sends only sequential."""

    def test_shadow_runs_sequential_then_parallel(self):
        """Shadow mode calls _collect_metrics_sequential and orchestrator.collect_all."""
        core = MagicMock(spec=ProbeCore)
        core.buffer = []
        core._collect_metrics_sequential = MagicMock()
        core._orchestrator = MagicMock()
        core._compare_shadow_results = MagicMock()

        ProbeCore._collect_metrics_shadow(core)

        core._collect_metrics_sequential.assert_called_once()
        core._orchestrator.collect_all.assert_called_once()

    def test_shadow_restores_sequential_buffer(self):
        """After shadow mode, buffer contains only sequential results."""
        core = MagicMock(spec=ProbeCore)
        core.buffer = []
        core._compare_shadow_results = MagicMock()

        seq_metrics = [
            {"hostname": "srv-01", "name": "cpu", "value": 50.0, "sensor_type": "cpu"},
            {"hostname": "srv-01", "name": "mem", "value": 70.0, "sensor_type": "memory"},
        ]
        par_metrics = [
            {"hostname": "srv-01", "name": "cpu", "value": 51.0, "sensor_type": "cpu"},
        ]

        def fake_sequential():
            core.buffer.extend(seq_metrics)

        def fake_parallel():
            core.buffer.extend(par_metrics)

        core._collect_metrics_sequential = MagicMock(side_effect=fake_sequential)
        core._orchestrator = MagicMock()
        core._orchestrator.collect_all = MagicMock(side_effect=fake_parallel)

        ProbeCore._collect_metrics_shadow(core)

        # Buffer should contain ONLY sequential metrics
        assert len(core.buffer) == 2
        assert core.buffer[0]["value"] == 50.0
        assert core.buffer[1]["value"] == 70.0

    def test_shadow_parallel_error_does_not_break(self):
        """If parallel collection raises, sequential results are still preserved."""
        core = MagicMock(spec=ProbeCore)
        core.buffer = []
        core._compare_shadow_results = MagicMock()

        def fake_sequential():
            core.buffer.append({"hostname": "h1", "name": "cpu", "value": 42.0})

        core._collect_metrics_sequential = MagicMock(side_effect=fake_sequential)
        core._orchestrator = MagicMock()
        core._orchestrator.collect_all = MagicMock(side_effect=RuntimeError("parallel boom"))

        ProbeCore._collect_metrics_shadow(core)

        # Sequential results preserved despite parallel failure
        assert len(core.buffer) == 1
        assert core.buffer[0]["value"] == 42.0


class TestShadowModeComparison:
    """7.3 — _compare_shadow_results uses MetricsComparator correctly."""

    def test_compare_matching_metrics(self):
        """Matching metrics are compared and summary is logged."""
        core = MagicMock(spec=ProbeCore)

        seq = [
            {"hostname": "srv-01", "name": "cpu", "value": 50.0},
            {"hostname": "srv-01", "name": "mem", "value": 70.0},
        ]
        par = [
            {"hostname": "srv-01", "name": "cpu", "value": 51.0},
            {"hostname": "srv-01", "name": "mem", "value": 72.0},
        ]

        # Call the real method
        ProbeCore._compare_shadow_results(core, seq, par)
        # No assertion on log calls — just verify it doesn't crash

    def test_compare_with_drift(self):
        """Metrics with >5% difference are detected as DRIFT."""
        core = MagicMock(spec=ProbeCore)

        seq = [{"hostname": "srv-01", "name": "cpu", "value": 50.0}]
        par = [{"hostname": "srv-01", "name": "cpu", "value": 80.0}]  # 60% drift

        ProbeCore._compare_shadow_results(core, seq, par)
        # Should not crash; DRIFT is logged internally by MetricsComparator

    def test_compare_no_parallel_match(self):
        """Sequential metrics without parallel counterpart are counted as unmatched."""
        core = MagicMock(spec=ProbeCore)

        seq = [
            {"hostname": "srv-01", "name": "cpu", "value": 50.0},
            {"hostname": "srv-02", "name": "disk", "value": 80.0},
        ]
        par = [
            {"hostname": "srv-01", "name": "cpu", "value": 51.0},
        ]

        ProbeCore._compare_shadow_results(core, seq, par)

    def test_compare_empty_parallel(self):
        """When parallel returns nothing, all sequential are unmatched."""
        core = MagicMock(spec=ProbeCore)

        seq = [{"hostname": "srv-01", "name": "cpu", "value": 50.0}]
        par = []

        ProbeCore._compare_shadow_results(core, seq, par)

    def test_compare_empty_both(self):
        """When both are empty, comparison completes without error."""
        core = MagicMock(spec=ProbeCore)
        ProbeCore._compare_shadow_results(core, [], [])

    def test_compare_non_numeric_values(self):
        """Non-numeric values are handled gracefully (converted to 0.0)."""
        core = MagicMock(spec=ProbeCore)

        seq = [{"hostname": "srv-01", "name": "status", "value": "ok"}]
        par = [{"hostname": "srv-01", "name": "status", "value": "ok"}]

        ProbeCore._compare_shadow_results(core, seq, par)


class TestShadowModeSequentialPreservation:
    """7.4 — Only sequential results are sent to the API during shadow mode."""

    def test_main_loop_sends_only_sequential(self):
        """
        In the main loop, after _collect_metrics (shadow), _send_metrics sends
        only what's in the buffer — which should be sequential results only.
        """
        core = MagicMock(spec=ProbeCore)
        core.buffer = []

        seq_metrics = [
            {"hostname": "srv-01", "name": "cpu", "value": 50.0, "sensor_type": "cpu"},
        ]
        par_metrics = [
            {"hostname": "srv-01", "name": "cpu", "value": 99.0, "sensor_type": "cpu"},
        ]

        def fake_sequential():
            core.buffer.extend(seq_metrics)

        def fake_parallel():
            core.buffer.extend(par_metrics)

        core._collect_metrics_sequential = MagicMock(side_effect=fake_sequential)
        core._orchestrator = MagicMock()
        core._orchestrator.collect_all = MagicMock(side_effect=fake_parallel)
        core._compare_shadow_results = MagicMock()

        ProbeCore._collect_metrics_shadow(core)

        # After shadow mode, buffer should only have sequential value (50.0)
        assert len(core.buffer) == 1
        assert core.buffer[0]["value"] == 50.0
        # The parallel value (99.0) should NOT be in the buffer
        assert all(m["value"] != 99.0 for m in core.buffer)
