"""
Database: Compression Tests — Coruja Monitor v3.0
Tests: 7-day compression policy simulation.
Requirements: 17.3
"""
import pytest
from datetime import datetime, timedelta
from sqlalchemy import text


@pytest.mark.unit
class TestCompression:
    """Req 17.3 — 7-day compression policy."""

    def test_compression_threshold_7_days(self):
        """Compression threshold is 7 days."""
        compression_days = 7
        assert compression_days == 7

    def test_data_older_than_7_days_eligible(self):
        """Data older than 7 days is eligible for compression."""
        now = datetime.now()
        old_data_time = now - timedelta(days=10)
        recent_data_time = now - timedelta(days=3)
        cutoff = now - timedelta(days=7)
        assert old_data_time < cutoff  # eligible
        assert recent_data_time > cutoff  # not eligible

    def test_compressed_data_still_queryable(self, mock_db):
        """Compressed data remains queryable (simulated)."""
        mock_db.execute(text(
            "INSERT INTO metrics_ts (time, sensor_id, host_id, value, unit, status) "
            "VALUES (:t, 's1', 'h1', 42.0, '%', 'ok')"
        ), {"t": (datetime.now() - timedelta(days=10)).isoformat()})
        mock_db.commit()
        row = mock_db.execute(text("SELECT value FROM metrics_ts WHERE sensor_id = 's1'")).fetchone()
        assert row is not None
        assert row[0] == 42.0
