"""
Migration: Add memory_demand_mb and disk_max_bytes columns to hyperv_vms table.
Run: docker exec -it coruja-api python migrate_hyperv_v2.py
"""
import os
import logging

logger = logging.getLogger(__name__)

def get_connection():
    import psycopg2
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", 5432)),
        dbname=os.getenv("POSTGRES_DB", "coruja"),
        user=os.getenv("POSTGRES_USER", "coruja"),
        password=os.getenv("POSTGRES_PASSWORD", "coruja"),
    )

def migrate():
    conn = get_connection()
    cursor = conn.cursor()

    steps = [
        ("memory_demand_mb", "ALTER TABLE hyperv_vms ADD COLUMN IF NOT EXISTS memory_demand_mb INTEGER"),
        ("disk_max_bytes", "ALTER TABLE hyperv_vms ADD COLUMN IF NOT EXISTS disk_max_bytes DOUBLE PRECISION"),
    ]

    for name, ddl in steps:
        try:
            cursor.execute(ddl)
            conn.commit()
            print(f"OK: {name}")
        except Exception as e:
            conn.rollback()
            print(f"SKIP {name}: {e}")

    cursor.close()
    conn.close()
    print("Migration complete!")

if __name__ == "__main__":
    migrate()
