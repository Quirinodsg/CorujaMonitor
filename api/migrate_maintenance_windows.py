"""
Migration script to add maintenance_windows table
"""
from sqlalchemy import create_engine, text
from config import settings

def run_migration():
    """Add maintenance_windows table"""
    engine = create_engine(settings.DATABASE_URL)
    
    print("Starting migration for maintenance windows...")
    
    with engine.connect() as conn:
        # Create maintenance_windows table
        print("Creating maintenance_windows table...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS maintenance_windows (
                id SERIAL PRIMARY KEY,
                tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
                server_id INTEGER REFERENCES servers(id) ON DELETE CASCADE,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                start_time TIMESTAMP WITH TIME ZONE NOT NULL,
                end_time TIMESTAMP WITH TIME ZONE NOT NULL,
                created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """))
        
        # Create indexes
        print("Creating indexes...")
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_maintenance_window_tenant 
            ON maintenance_windows(tenant_id);
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_maintenance_window_server 
            ON maintenance_windows(server_id);
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_maintenance_window_time 
            ON maintenance_windows(start_time, end_time);
        """))
        
        conn.commit()
        print("✅ Migration completed successfully!")
        print("\nNew features:")
        print("  • Schedule maintenance windows for servers or entire company")
        print("  • Suppress alerts during maintenance")
        print("  • Exclude downtime from SLA reports")
        print("  • Visual indicator for servers in maintenance")

if __name__ == "__main__":
    run_migration()
