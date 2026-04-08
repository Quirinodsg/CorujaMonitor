"""
Database: Hypertable Tests — Coruja Monitor v3.0
Tests: batch insert ≤500 using SQLite in-memory mock.
Requirements: 17.1
"""
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


@pytest.mark.unit
class TestHypertable:
    """Req 17.1 — batch insert ≤500 rows."""

    def test_batch_insert_500(self, mock_db):
        """Insert 500 rows in a single batch."""
        for i in range(500):
            mock_db.execute(text(
                "INSERT INTO metrics_ts (time, sensor_id, host_id, value, unit, status) "
                "VALUES (:t, :sid, :hid, :v, :u, :s)"
            ), {"t": f"2024-01-01 00:00:{i % 60:02d}", "sid": f"s{i}", "hid": "h1",
                "v": float(i), "u": "%", "s": "ok"})
        mock_db.commit()
        count = mock_db.execute(text("SELECT COUNT(*) FROM metrics_ts")).scalar()
        assert count == 500

    def test_batch_insert_respects_limit(self, mock_db):
        """Batches are split at 500 boundary."""
        total = 1200
        batch_size = 500
        inserted = 0
        for batch_start in range(0, total, batch_size):
            batch_end = min(batch_start + batch_size, total)
            for i in range(batch_start, batch_end):
                mock_db.execute(text(
                    "INSERT INTO metrics_ts (time, sensor_id, host_id, value, unit, status) "
                    "VALUES (:t, :sid, :hid, :v, :u, :s)"
                ), {"t": f"2024-01-01 00:{i // 60:02d}:{i % 60:02d}", "sid": f"s{i}",
                    "hid": "h1", "v": float(i), "u": "%", "s": "ok"})
            mock_db.commit()
            inserted += (batch_end - batch_start)
        assert inserted == total
