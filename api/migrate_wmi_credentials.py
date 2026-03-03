"""
Migration: Add WMI credentials fields to servers table
"""
from sqlalchemy import create_engine, text
from config import settings

def migrate():
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        # Add WMI credentials fields
        migrations = [
            """
            ALTER TABLE servers 
            ADD COLUMN IF NOT EXISTS wmi_username VARCHAR(255);
            """,
            """
            ALTER TABLE servers 
            ADD COLUMN IF NOT EXISTS wmi_password_encrypted TEXT;
            """,
            """
            ALTER TABLE servers 
            ADD COLUMN IF NOT EXISTS wmi_domain VARCHAR(255);
            """,
            """
            ALTER TABLE servers 
            ADD COLUMN IF NOT EXISTS wmi_enabled BOOLEAN DEFAULT FALSE;
            """,
            """
            COMMENT ON COLUMN servers.wmi_username IS 
            'Username for WMI remote access (e.g., Administrator or DOMAIN\\user)';
            """,
            """
            COMMENT ON COLUMN servers.wmi_password_encrypted IS 
            'Encrypted password for WMI access (use Fernet encryption)';
            """,
            """
            COMMENT ON COLUMN servers.wmi_domain IS 
            'Windows domain for WMI authentication (optional)';
            """,
            """
            COMMENT ON COLUMN servers.wmi_enabled IS 
            'Enable WMI remote monitoring for this server';
            """
        ]
        
        for migration in migrations:
            try:
                conn.execute(text(migration))
                conn.commit()
                print(f"✅ Executed: {migration[:50]}...")
            except Exception as e:
                print(f"⚠️ Warning: {e}")
                conn.rollback()
        
        print("\n✅ Migration completed successfully!")
        print("\nNOTE: WMI passwords will be encrypted using Fernet (symmetric encryption)")
        print("      Store the encryption key securely in environment variables")

if __name__ == "__main__":
    migrate()
