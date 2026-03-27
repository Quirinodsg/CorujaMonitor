"""
Migration: Add memory_demand_mb and disk_max_bytes columns to hyperv_vms table.
Run: docker exec -it coruja-api python migrate_hyperv_v2.py
"""
import sys
sys.path.insert(0, '.')
from database import engine

def migrate():
    with engine.connect() as conn:
        # Add memory_demand_mb column
        try:
            conn.execute("ALTER TABLE hyperv_vms ADD COLUMN IF NOT EXISTS memory_demand_mb INTEGER")
            print("Added memory_demand_mb column")
        except Exception as e:
            print(f"memory_demand_mb: {e}")

        # Add disk_max_bytes column
        try:
            conn.execute("ALTER TABLE hyperv_vms ADD COLUMN IF NOT EXISTS disk_max_bytes DOUBLE PRECISION")
            print("Added disk_max_bytes column")
        except Exception as e:
            print(f"disk_max_bytes: {e}")

        conn.commit()
        print("Migration complete!")

if __name__ == "__main__":
    migrate()
