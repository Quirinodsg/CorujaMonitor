"""
Database: Query Performance Tests — Coruja Monitor v3.0
Tests: queries complete <1s.
Requirements: 17.4, 17.5
"""
import pytest
import time
from sqlalchemy import text


@pytest.mark.unit
class TestQueryPerformance:
    """Req 17.4, 17.5 — queries complete <1s."""

    def test_select_query_under_1s(self, mock_db):
        """Simple SELECT completes in <1s."""
        # Insert some data
        for i in range(100):
            mock_db.execute(text(
                "INSERT INTO metrics_ts (time, sensor_id, host_id, value, unit, status) "
                "VALUES (:t, :sid, 'h1', :v, '%', 'ok')"
            ), {"t": f"2024-01-01 00:00:{i % 60:02d}", "sid": f"s{i}", "v": float(i)})
        mock_db.commit()

        start = time.monotonic()
        rows = mock_db.execute(text("SELECT * FROM metrics_ts")).fetchall()
        elapsed = time.monotonic() - start
        assert len(rows) == 100
        assert elapsed < 1.0

    def test_aggregate_query_under_1s(self, mock_db):
        """Aggregate query completes in <1s."""
        for i in range(200):
            mock_db.execute(text(
                "INSERT INTO metrics_ts (time, sensor_id, host_id, value, unit, status) "
                "VALUES (:t, :sid, 'h1', :v, '%', 'ok')"
            ), {"t": f"2024-01-01 00:{i // 60:02d}:{i % 60:02d}", "sid": f"s{i % 10}", "v": float(i)})
        mock_db.commit()

        start = time.monotonic()
        result = mock_db.execute(text(
            "SELECT sensor_id, AVG(value) FROM metrics_ts GROUP BY sensor_id"
        )).fetchall()
        elapsed = time.monotonic() - start
        assert len(result) > 0
        assert elapsed < 1.0

    def test_count_query_under_1s(self, mock_db):
        """COUNT query completes in <1s."""
        start = time.monotonic()
        count = mock_db.execute(text("SELECT COUNT(*) FROM metrics_ts")).scalar()
        elapsed = time.monotonic() - start
        assert elapsed < 1.0
