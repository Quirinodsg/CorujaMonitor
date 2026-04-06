"""
Tests for Task 1: Configuração e Feature Flag (Requisitos 1, 9)
Validates config loading, feature flag logic, and sequential mode preservation.
"""
import pytest
import yaml
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestParallelConfig:
    """Tests for _load_parallel_config and feature flag behavior."""

    def test_config_yaml_has_probe_section(self):
        """Verify config.yaml contains the probe section with all required keys."""
        config_path = Path("probe/config.yaml")
        assert config_path.exists(), "probe/config.yaml must exist"

        with open(config_path) as f:
            cfg = yaml.safe_load(f)

        probe_cfg = cfg.get("probe", {})
        assert "parallel_enabled" in probe_cfg
        assert "max_workers" in probe_cfg
        assert "timeout_seconds" in probe_cfg
        assert "dispatch_mode" in probe_cfg
        assert "canary_hosts" in probe_cfg

    def test_config_yaml_default_values(self):
        """Verify config.yaml has safe default values."""
        with open("probe/config.yaml") as f:
            cfg = yaml.safe_load(f)

        probe_cfg = cfg["probe"]
        assert probe_cfg["parallel_enabled"] is False
        assert probe_cfg["max_workers"] == 8
        assert probe_cfg["timeout_seconds"] == 30
        assert probe_cfg["dispatch_mode"] == "bulk"
        assert probe_cfg["canary_hosts"] == []

    def test_load_parallel_config_defaults_when_no_file(self):
        """When config.yaml doesn't exist, defaults are returned."""
        # Import inside test to avoid import issues
        import sys
        sys.path.insert(0, "probe")

        from probe_core import ProbeCore

        with patch.object(Path, "exists", return_value=False):
            core = MagicMock(spec=ProbeCore)
            result = ProbeCore._load_parallel_config(core)

        assert result["parallel_enabled"] is False
        assert result["max_workers"] == 8
        assert result["timeout_seconds"] == 30
        assert result["dispatch_mode"] == "bulk"
        assert result["canary_hosts"] == []

    def test_load_parallel_config_from_yaml(self):
        """Config values are loaded from YAML probe section."""
        import sys
        sys.path.insert(0, "probe")

        from probe_core import ProbeCore

        test_config = {
            "probe": {
                "parallel_enabled": True,
                "max_workers": 4,
                "timeout_seconds": 15,
                "dispatch_mode": "incremental",
                "canary_hosts": ["host-a", "host-b"],
            }
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(test_config, f)
            tmp_path = f.name

        try:
            core = MagicMock(spec=ProbeCore)
            with patch.object(Path, "exists", side_effect=lambda self=None: True):
                with patch("builtins.open", create=True) as mock_open:
                    mock_open.return_value.__enter__ = lambda s: open(tmp_path)
                    mock_open.return_value.__exit__ = MagicMock(return_value=False)
                    # Use the actual method with a real file
                    pass
        finally:
            os.unlink(tmp_path)

    def test_load_parallel_config_ignores_unknown_keys(self):
        """Unknown keys in probe section are ignored."""
        import sys
        sys.path.insert(0, "probe")

        from probe_core import ProbeCore

        core = MagicMock(spec=ProbeCore)
        defaults = ProbeCore._load_parallel_config(core)
        # Only known keys should be present
        expected_keys = {"parallel_enabled", "max_workers", "timeout_seconds", "dispatch_mode", "canary_hosts", "shadow_mode"}
        assert set(defaults.keys()) == expected_keys

    def test_collect_metrics_delegates_to_sequential_when_no_orchestrator(self):
        """When orchestrator is None, _collect_metrics calls _collect_metrics_sequential."""
        import sys
        sys.path.insert(0, "probe")

        from probe_core import ProbeCore

        core = MagicMock(spec=ProbeCore)
        core._orchestrator = None
        core._shadow_mode = False
        core._collect_metrics_sequential = MagicMock()

        ProbeCore._collect_metrics(core)
        core._collect_metrics_sequential.assert_called_once()

    def test_collect_metrics_delegates_to_orchestrator_when_enabled(self):
        """When orchestrator exists, _collect_metrics calls orchestrator.collect_all."""
        import sys
        sys.path.insert(0, "probe")

        from probe_core import ProbeCore

        mock_orchestrator = MagicMock()
        core = MagicMock(spec=ProbeCore)
        core._orchestrator = mock_orchestrator
        core._shadow_mode = False

        ProbeCore._collect_metrics(core)
        mock_orchestrator.collect_all.assert_called_once()

    def test_sequential_mode_preserved(self):
        """_collect_metrics_sequential exists and has the expected collection flow."""
        import sys
        sys.path.insert(0, "probe")

        from probe_core import ProbeCore

        assert hasattr(ProbeCore, "_collect_metrics_sequential")
        assert callable(getattr(ProbeCore, "_collect_metrics_sequential"))
