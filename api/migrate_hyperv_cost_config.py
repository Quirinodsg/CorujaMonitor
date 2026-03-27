"""
Migration: Create hyperv_cost_config table for editable datacenter costs.
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

DDL = """
CREATE TABLE IF NOT EXISTS hyperv_cost_config (
    id              SERIAL PRIMARY KEY,
    key             VARCHAR(100) UNIQUE NOT NULL,
    label           VARCHAR(255) NOT NULL,
    category        VARCHAR(50) NOT NULL,
    value           DOUBLE PRECISION NOT NULL DEFAULT 0,
    unit            VARCHAR(50) DEFAULT '',
    editable        BOOLEAN DEFAULT TRUE,
    sort_order      INTEGER DEFAULT 0,
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);
"""

SEED = [
    ("energia_cpd", "Energia elétrica CPD", "infra", 8050.13, "R$/mês", 1),
    ("energia_ac", "Energia ar condicionado", "infra", 2388.62, "R$/mês", 2),
    ("manut_nobreak", "Manutenção nobreak", "infra", 250.00, "R$/mês", 3),
    ("reparos_eletricos", "Reparos elétricos", "infra", 450.00, "R$/mês", 4),
    ("manut_ac", "Manutenção ar condicionado", "infra", 333.33, "R$/mês", 5),
    ("link_ips", "Link dedicado / IPs públicos", "rede", 3500.00, "R$/mês", 6),
    ("licenca_twilio", "Licença Twilio", "software", 25.00, "R$/mês", 7),
    ("garantia_servidores", "Garantia servidores Dell", "hardware", 1666.67, "R$/mês", 8),
    ("deprec_servidores", "Depreciação servidores", "hardware", 8333.33, "R$/mês", 9),
    ("garantia_storage", "Garantia storage", "hardware", 2000.00, "R$/mês", 10),
    ("deprec_storage", "Depreciação storage", "hardware", 2410.00, "R$/mês", 11),
    ("deprec_storage_bkp", "Depreciação storage backup", "hardware", 1000.00, "R$/mês", 12),
    ("deprec_switches", "Depreciação switches", "hardware", 581.62, "R$/mês", 13),
    ("equipe_infra", "Equipe infraestrutura (30%)", "pessoal", 19440.00, "R$/mês", 14),
    ("peso_cpu", "Peso CPU", "peso", 40, "%", 20),
    ("peso_ram", "Peso RAM", "peso", 25, "%", 21),
    ("peso_disco", "Peso Disco", "peso", 25, "%", 22),
    ("peso_rede", "Peso Rede/IP", "peso", 10, "%", 23),
    ("total_vcpus", "Total vCPUs (8:1 oversub)", "capacidade", 1024, "vCPUs", 30),
    ("total_ram_gb", "Total RAM", "capacidade", 1024, "GB", 31),
    ("total_disco_gb", "Total Disco", "capacidade", 28000, "GB", 32),
    ("total_ips", "Total IPs públicos", "capacidade", 16, "IPs", 33),
    ("reajuste_anual", "Reajuste anual", "config", 0, "%", 40),
]

def migrate():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(DDL)
        conn.commit()
        print("OK: table created")
    except Exception as e:
        conn.rollback()
        print(f"Table: {e}")

    for key, label, cat, val, unit, sort in SEED:
        try:
            cursor.execute(
                "INSERT INTO hyperv_cost_config (key, label, category, value, unit, sort_order) "
                "VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (key) DO NOTHING",
                (key, label, cat, val, unit, sort)
            )
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"SKIP {key}: {e}")

    print("Seed complete!")
    cursor.close()
    conn.close()

if __name__ == "__main__":
    migrate()
