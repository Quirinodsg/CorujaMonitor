"""
Tests for Task 6: MetricsComparator — Validação MCT Shadow Mode (Requisitos 6)
Validates tolerance classification, edge cases, and summary correctness.

**Validates: Requirements 6**
"""
import pytest
from hypothesis import given, settings, HealthCheck, assume
from hypothesis import strategies as st

from probe.parallel_engine import MetricsComparator

settings.register_profile("ci", max_examples=100)
settings.load_profile("ci")

# ─── Strategies ──────────────────────────────────────────────────────────────

# Positive metric values (typical sensor readings)
positive_value_st = st.floats(min_value=0.01, max_value=1e6, allow_nan=False, allow_infinity=False)

hostname_st = st.text(
    alphabet=st.characters(whitelist_categories=("Ll", "Lu", "Nd"), whitelist_characters="-_"),
    min_size=1,
    max_size=30,
).filter(lambda s: s.strip() and not s.startswith("-"))

metric_name_st = st.text(
    alphabet=st.characters(whitelist_categories=("Ll", "Lu", "Nd"), whitelist_characters="-_ "),
    min_size=1,
    max_size=30,
).filter(lambda s: s.strip())

# Factor within tolerance: multiplier that keeps diff <= 5%
# If new_val = old_val * factor, then diff_pct = |factor - 1| * 100
# For diff <= 5%, we need |factor - 1| <= 0.05, so factor in [0.95, 1.05]
within_tolerance_factor_st = st.floats(min_value=0.95, max_value=1.05, allow_nan=False, allow_infinity=False)

# Factor outside tolerance: diff > 5%
outside_tolerance_factor_st = st.one_of(
    st.floats(min_value=0.0, max_value=0.9499, allow_nan=False, allow_infinity=False),
    st.floats(min_value=1.0501, max_value=10.0, allow_nan=False, allow_infinity=False),
)


# ─── Unit Tests ──────────────────────────────────────────────────────────────

class TestMetricsComparatorUnit:
    """Unit tests for MetricsComparator basic behavior."""

    def test_tolerance_is_5_percent(self):
        mc = MetricsComparator()
        assert mc.TOLERANCE_PCT == 5.0

    def test_both_zero_returns_ok(self):
        mc = MetricsComparator()
        result = mc.compare("host-a", "cpu", 0.0, 0.0)
        assert result["status"] == "OK"
        assert result["diff_pct"] == 0.0

    def test_old_zero_new_nonzero_returns_100_pct(self):
        mc = MetricsComparator()
        result = mc.compare("host-a", "cpu", 0.0, 42.0)
        assert result["diff_pct"] == 100.0
        assert result["status"] == "DRIFT"

    def test_exact_same_values_ok(self):
        mc = MetricsComparator()
        result = mc.compare("host-a", "cpu", 50.0, 50.0)
        assert result["status"] == "OK"
        assert result["diff_pct"] == 0.0

    def test_within_5_percent_ok(self):
        mc = MetricsComparator()
        # 100 -> 104 = 4% diff
        result = mc.compare("host-a", "cpu", 100.0, 104.0)
        assert result["status"] == "OK"
        assert result["diff_pct"] == 4.0

    def test_exactly_5_percent_ok(self):
        mc = MetricsComparator()
        # 100 -> 105 = exactly 5%
        result = mc.compare("host-a", "cpu", 100.0, 105.0)
        assert result["status"] == "OK"
        assert result["diff_pct"] == 5.0

    def test_above_5_percent_drift(self):
        mc = MetricsComparator()
        # 100 -> 106 = 6% diff
        result = mc.compare("host-a", "cpu", 100.0, 106.0)
        assert result["status"] == "DRIFT"
        assert result["diff_pct"] == 6.0

    def test_negative_direction_within_tolerance(self):
        mc = MetricsComparator()
        # 100 -> 96 = 4% diff
        result = mc.compare("host-a", "mem", 100.0, 96.0)
        assert result["status"] == "OK"
        assert result["diff_pct"] == 4.0

    def test_negative_direction_drift(self):
        mc = MetricsComparator()
        # 100 -> 90 = 10% diff
        result = mc.compare("host-a", "mem", 100.0, 90.0)
        assert result["status"] == "DRIFT"
        assert result["diff_pct"] == 10.0

    def test_compare_returns_all_fields(self):
        mc = MetricsComparator()
        result = mc.compare("srv-01", "disk", 80.0, 82.0)
        assert "host" in result
        assert "metric" in result
        assert "old" in result
        assert "new" in result
        assert "diff_pct" in result
        assert "status" in result
        assert result["host"] == "srv-01"
        assert result["metric"] == "disk"

    def test_summary_empty(self):
        mc = MetricsComparator()
        s = mc.summary
        assert s["total"] == 0
        assert s["ok"] == 0
        assert s["drifts"] == 0
        assert s["pass"] is True

    def test_summary_all_ok(self):
        mc = MetricsComparator()
        mc.compare("h1", "cpu", 100.0, 102.0)
        mc.compare("h2", "mem", 50.0, 51.0)
        s = mc.summary
        assert s["total"] == 2
        assert s["ok"] == 2
        assert s["drifts"] == 0
        assert s["pass"] is True

    def test_summary_with_drifts(self):
        mc = MetricsComparator()
        mc.compare("h1", "cpu", 100.0, 102.0)  # OK
        mc.compare("h2", "mem", 50.0, 60.0)     # DRIFT (20%)
        mc.compare("h3", "disk", 10.0, 20.0)    # DRIFT (100%)
        s = mc.summary
        assert s["total"] == 3
        assert s["ok"] == 1
        assert s["drifts"] == 2
        assert s["pass"] is False

    def test_summary_pass_false_when_any_drift(self):
        mc = MetricsComparator()
        mc.compare("h1", "cpu", 100.0, 200.0)  # DRIFT
        assert mc.summary["pass"] is False

    def test_old_zero_new_zero_special_case(self):
        """Requirement 6.6: both zero → OK with 0% diff."""
        mc = MetricsComparator()
        result = mc.compare("h1", "cpu", 0.0, 0.0)
        assert result["diff_pct"] == 0.0
        assert result["status"] == "OK"

    def test_old_zero_new_nonzero_special_case(self):
        """Requirement 6.7: sequential zero, parallel nonzero → 100% diff."""
        mc = MetricsComparator()
        result = mc.compare("h1", "cpu", 0.0, 5.0)
        assert result["diff_pct"] == 100.0
        assert result["status"] == "DRIFT"


# ─── Property-Based Test: Tolerance ──────────────────────────────────────────

class TestComparatorTolerance:
    """
    Property: metrics with difference ≤ 5% are always classified as "OK".

    **Validates: Requirements 6**
    """

    @given(
        host=hostname_st,
        metric=metric_name_st,
        old_val=positive_value_st,
        factor=within_tolerance_factor_st,
    )
    @settings(
        max_examples=200,
        suppress_health_check=[HealthCheck.too_slow],
        deadline=None,
    )
    def test_comparator_tolerance(self, host, metric, old_val, factor):
        """
        Métricas com diferença ≤5% sempre classificadas como "OK".
        We generate old_val > 0 and new_val = old_val * factor where factor ∈ [0.95, 1.05],
        guaranteeing diff_pct = |factor - 1| * 100 ≤ 5%.

        **Validates: Requirements 6**
        """
        new_val = old_val * factor
        mc = MetricsComparator()
        result = mc.compare(host, metric, old_val, new_val)

        # Core property: within tolerance → always OK
        assert result["status"] == "OK", (
            f"Expected OK for {old_val} -> {new_val} "
            f"(factor={factor}, diff_pct={result['diff_pct']})"
        )
        assert result["diff_pct"] <= 5.01  # small rounding tolerance

    @given(
        host=hostname_st,
        metric=metric_name_st,
        old_val=positive_value_st,
        factor=outside_tolerance_factor_st,
    )
    @settings(
        max_examples=200,
        suppress_health_check=[HealthCheck.too_slow],
        deadline=None,
    )
    def test_comparator_drift_detection(self, host, metric, old_val, factor):
        """
        Métricas com diferença > 5% sempre classificadas como "DRIFT".

        **Validates: Requirements 6**
        """
        new_val = old_val * factor
        mc = MetricsComparator()
        result = mc.compare(host, metric, old_val, new_val)

        # Core property: outside tolerance → always DRIFT
        assert result["status"] == "DRIFT", (
            f"Expected DRIFT for {old_val} -> {new_val} "
            f"(factor={factor}, diff_pct={result['diff_pct']})"
        )
        assert result["diff_pct"] > 5.0
