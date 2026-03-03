"""
Database migration script to add sensor notes functionality
Adds: verification_status, last_note, last_note_by, last_note_at to sensors table
Creates: sensor_notes table
"""

from sqlalchemy import create_engine, text
from config import settings

def migrate():
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        print("Starting migration...")
        
        # Check if columns already exist
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='sensors' AND column_name='verification_status'
        """))
        
        if result.fetchone():
            print("✓ Columns already exist, skipping sensor table migration")
        else:
            print("Adding new columns to sensors table...")
            
            # Add new columns to sensors table
            conn.execute(text("""
                ALTER TABLE sensors 
                ADD COLUMN verification_status VARCHAR(50) DEFAULT 'pending',
                ADD COLUMN last_note TEXT,
                ADD COLUMN last_note_by INTEGER REFERENCES users(id),
                ADD COLUMN last_note_at TIMESTAMP WITH TIME ZONE
            """))
            conn.commit()
            print("✓ Added verification_status, last_note, last_note_by, last_note_at to sensors")
        
        # Check if sensor_notes table exists
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name='sensor_notes'
        """))
        
        if result.fetchone():
            print("✓ sensor_notes table already exists")
        else:
            print("Creating sensor_notes table...")
            
            # Create sensor_notes table
            conn.execute(text("""
                CREATE TABLE sensor_notes (
                    id SERIAL PRIMARY KEY,
                    sensor_id INTEGER NOT NULL REFERENCES sensors(id) ON DELETE CASCADE,
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    note TEXT NOT NULL,
                    status VARCHAR(50) NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Create index for faster queries
            conn.execute(text("""
                CREATE INDEX idx_sensor_notes_sensor_id ON sensor_notes(sensor_id)
            """))
            conn.execute(text("""
                CREATE INDEX idx_sensor_notes_created_at ON sensor_notes(created_at DESC)
            """))
            
            conn.commit()
            print("✓ Created sensor_notes table with indexes")
        
        print("\n✅ Migration completed successfully!")
        print("\nNext steps:")
        print("1. Restart API service: docker compose restart api")
        print("2. Test sensor notes functionality in the UI")

if __name__ == "__main__":
    try:
        migrate()
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        print("\nTroubleshooting:")
        print("- Check if database is running: docker ps")
        print("- Check database connection in .env file")
        print("- Check if you have proper database permissions")
