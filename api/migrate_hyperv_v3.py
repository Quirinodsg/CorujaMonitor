"""
Migration: Add hardware info columns to hyperv_hosts table.
Run: docker exec -it coruja-api python migrate_hyperv_v3.py
"""
import os

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
    cols = [
        ("manufacturer", "VARCHAR(255)"),
        ("model", "VARCHAR(255)"),
        ("serial_number", "VARCHAR(255)"),
        ("bios_version", "VARCHAR(255)"),
        ("os_version", "VARCHAR(255)"),
        ("processor_name", "VARCHAR(255)"),
        ("processor_sockets", "INTEGER"),
        ("cores_per_socket", "INTEGER"),
    ]
    for name, dtype in cols:
        try:
            cursor.execute(f"ALTER TABLE hyperv_hosts ADD COLUMN IF NOT EXISTS {name} {dtype}")
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
