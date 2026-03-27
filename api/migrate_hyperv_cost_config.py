"""
Migration: Create hyperv_cost_config table for editable FinOps costs.
Run: docker exec -it coruja-api python migrate_hyperv_cost_config.py
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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hyperv_cost_config (
            id SERIAL PRIMARY KEY,
            key VARCHAR(50) UNIQUE NOT NULL,
            value NUMERIC(12,4) NOT NULL,
            label VARCHAR(120) NOT NULL,
            unit VARCHAR(30) NOT NULL DEFAULT '',
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """)
    conn.commit()
    print("OK: tabela hyperv_cost_config criada")

    # Seed defaults (Techbiz datacenter)
    defaults = [
        ("cost_vcpu",    19.70,   "Custo vCPU",          "R$/vCPU/mês"),
        ("cost_ram_gb",  12.31,   "Custo RAM",           "R$/GB/mês"),
        ("cost_disk_gb",  0.45,   "Custo Disco",         "R$/GB/mês"),
        ("cost_ip",     315.18,   "Custo IP Público",    "R$/IP/mês"),
    ]
    for key, value, label, unit in defaults:
        cursor.execute("""
            INSERT INTO hyperv_cost_config (key, value, label, unit)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (key) DO NOTHING
        """, (key, value, label, unit))
    conn.commit()
    print("OK: valores padrão inseridos")

    cursor.close()
    conn.close()
    print("Migration complete!")


if __name__ == "__main__":
    migrate()
