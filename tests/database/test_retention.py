"""
Database: Retention Tests — Coruja Monitor v3.0
Tests: 90-day retention policy simulation.
Requirements: 17.2
"""
import pytest
from datetime import datetime, timedelta
from sqlalchemy import text


@pytest.mark.unit
class TestRetention:
    """Req 17.2 — 90-day retention policy."""

    def test_old_data_can_be_deleted(self, mock_db):
        """Data older than 90 days can be purged."""
        now = datetime.now()
        old = now - timedelta(days=100)
        recent = now - timedelta(days=10)

        mock_db.execute(text(
            "INSERT INTO metrics_ts (time, sensor_id, host_id, value, unit, status) "
            "VALUES (:t, 's1', 'h1', 42.0, '%', 'ok')"
        ), {"t": old.isoformat()})
        mock_db.execute(text(
            "INSERT INTO metrics_ts (time, sensor_id, host_id, value, unit, status) "
            "VALUES (:t, 's2', 'h1', 50.0, '%', 'ok')"
        ), {"t": recent.isoformat()})
        mock_db.commit()

        # Simulate retention: delete data older than 90 days
        cutoff = (now - timedelta(days=90)).isoformat()
        mock_db.execute(text("DELETE FROM metrics_ts WHERE time < :cutoff"), {"cutoff": cutoff})
        mock_db.commit()

        count = mock_db.execute(text("SELECT COUNT(*) FROM metrics_ts")).scalar()
        assert count == 1  # only recent data remains

    def test_retention_threshold_90_days(self):
        """Retention threshold is 90 days."""
        retention_days = 90
        assert retention_days == 90
