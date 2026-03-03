"""
Database migration script to add monitoring features
Adds: device_type, monitoring_protocol, environment, SNMP fields to servers
Adds: collection_protocol, snmp_oid to sensors
Adds: notification_config to tenants
"""

from sqlalchemy import create_engine, text
from config import settings

def migrate():
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        print("Starting migration for monitoring features...")
        
        # ===== SERVERS TABLE =====
        print("\n1. Updating servers table...")
        
        # Check if columns already exist
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='servers' AND column_name='device_type'
        """))
        
        if result.fetchone():
            print("✓ Columns already exist in servers table")
        else:
            print("Adding new columns to servers table...")
            
            # Add device_type
            conn.execute(text("""
                ALTER TABLE servers 
                ADD COLUMN device_type VARCHAR(50) DEFAULT 'server'
            """))
            print("  ✓ Added device_type")
            
            # Add monitoring_protocol
            conn.execute(text("""
                ALTER TABLE servers 
                ADD COLUMN monitoring_protocol VARCHAR(20) DEFAULT 'wmi'
            """))
            print("  ✓ Added monitoring_protocol")
            
            # Add SNMP fields
            conn.execute(text("""
                ALTER TABLE servers 
                ADD COLUMN snmp_version VARCHAR(10),
                ADD COLUMN snmp_community VARCHAR(255),
                ADD COLUMN snmp_port INTEGER DEFAULT 161
            """))
            print("  ✓ Added SNMP fields")
            
            # Add environment
            conn.execute(text("""
                ALTER TABLE servers 
                ADD COLUMN environment VARCHAR(50) DEFAULT 'production'
            """))
            print("  ✓ Added environment")
            
            # Add monitoring_schedule
            conn.execute(text("""
                ALTER TABLE servers 
                ADD COLUMN monitoring_schedule JSON
            """))
            print("  ✓ Added monitoring_schedule")
            
            conn.commit()
        
        # ===== SENSORS TABLE =====
        print("\n2. Updating sensors table...")
        
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='sensors' AND column_name='collection_protocol'
        """))
        
        if result.fetchone():
            print("✓ Columns already exist in sensors table")
        else:
            print("Adding new columns to sensors table...")
            
            # Add collection_protocol
            conn.execute(text("""
                ALTER TABLE sensors 
                ADD COLUMN collection_protocol VARCHAR(20) DEFAULT 'wmi'
            """))
            print("  ✓ Added collection_protocol")
            
            # Add snmp_oid
            conn.execute(text("""
                ALTER TABLE sensors 
                ADD COLUMN snmp_oid VARCHAR(255)
            """))
            print("  ✓ Added snmp_oid")
            
            conn.commit()
        
        # ===== TENANTS TABLE =====
        print("\n3. Updating tenants table...")
        
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='tenants' AND column_name='notification_config'
        """))
        
        if result.fetchone():
            print("✓ Column already exists in tenants table")
        else:
            print("Adding notification_config to tenants table...")
            
            conn.execute(text("""
                ALTER TABLE tenants 
                ADD COLUMN notification_config JSON
            """))
            print("  ✓ Added notification_config")
            
            conn.commit()
        
        print("\n✅ Migration completed successfully!")
        print("\nNew features available:")
        print("  • Device types (server, switch, router, firewall, etc.)")
        print("  • Monitoring protocols (WMI, SNMP)")
        print("  • Environment classification (production, staging, development, custom)")
        print("  • SNMP configuration (version, community, port)")
        print("  • Notification integrations (Twilio, Teams, WhatsApp, Telegram)")
        print("  • Custom monitoring schedules")
        print("\nNext steps:")
        print("1. Restart API service: docker compose restart api")
        print("2. Restart frontend: docker compose restart frontend")
        print("3. Configure notification integrations in Companies page")

if __name__ == "__main__":
    try:
        migrate()
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        print("\nTroubleshooting:")
        print("- Check if database is running: docker ps")
        print("- Check database connection in .env file")
        print("- Check if you have proper database permissions")
