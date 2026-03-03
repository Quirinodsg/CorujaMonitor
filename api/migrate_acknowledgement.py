"""
Database migration script to add acknowledgement fields to sensors
Adds: is_acknowledged, acknowledged_by, acknowledged_at
"""

from sqlalchemy import create_engine, text
from config import settings

def migrate():
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        print("Starting migration for acknowledgement fields...")
        
        # Check if columns already exist
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='sensors' AND column_name='is_acknowledged'
        """))
        
        if result.fetchone():
            print("✓ Columns already exist in sensors table")
        else:
            print("Adding acknowledgement columns to sensors table...")
            
            # Add is_acknowledged
            conn.execute(text("""
                ALTER TABLE sensors 
                ADD COLUMN is_acknowledged BOOLEAN DEFAULT FALSE
            """))
            print("  ✓ Added is_acknowledged")
            
            # Add acknowledged_by
            conn.execute(text("""
                ALTER TABLE sensors 
                ADD COLUMN acknowledged_by INTEGER REFERENCES users(id)
            """))
            print("  ✓ Added acknowledged_by")
            
            # Add acknowledged_at
            conn.execute(text("""
                ALTER TABLE sensors 
                ADD COLUMN acknowledged_at TIMESTAMP WITH TIME ZONE
            """))
            print("  ✓ Added acknowledged_at")
            
            conn.commit()
        
        print("\n✅ Migration completed successfully!")
        print("\nNew features:")
        print("  • Sensors can be acknowledged by technicians")
        print("  • Acknowledged sensors don't trigger calls")
        print("  • Dashboard shows 'Verified by IT' status")
        print("  • Hover over sensor shows last technician note")
        print("\nNext steps:")
        print("1. Restart API service: docker compose restart api")
        print("2. Restart frontend: docker compose restart frontend")

if __name__ == "__main__":
    try:
        migrate()
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        print("\nTroubleshooting:")
        print("- Check if database is running: docker ps")
        print("- Check database connection in .env file")
