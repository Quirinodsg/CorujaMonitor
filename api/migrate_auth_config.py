"""
Migration script to create authentication_config table
Run this script to add the authentication configuration table to the database
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, JSON, Index, text
from sqlalchemy.sql import func
from database import Base, engine as db_engine
from models import AuthenticationConfig
from config import settings

def migrate():
    print("🔄 Starting authentication_config table migration...")
    
    engine = db_engine
    
    try:
        # Check if table already exists
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'authentication_config'
                );
            """))
            exists = result.scalar()
            
            if exists:
                print("⚠️  Table 'authentication_config' already exists. Skipping creation.")
                return
        
        # Create the table
        AuthenticationConfig.__table__.create(engine, checkfirst=True)
        print("✅ Table 'authentication_config' created successfully!")
        
        # Verify table was created
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'authentication_config'
                ORDER BY ordinal_position;
            """))
            columns = result.fetchall()
            
            print("\n📋 Table structure:")
            for col in columns:
                print(f"   - {col[0]}: {col[1]}")
        
        print("\n✅ Migration completed successfully!")
        print("\n📝 Next steps:")
        print("   1. Restart the API: docker-compose restart api")
        print("   2. Rebuild frontend: docker-compose build frontend && docker-compose up -d frontend")
        print("   3. Access Settings > Segurança in the web interface")
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        raise

if __name__ == "__main__":
    migrate()
