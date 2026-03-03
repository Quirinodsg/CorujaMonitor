from database import engine
from sqlalchemy import text

# Add new columns to servers table
with engine.connect() as conn:
    try:
        # Add public_ip column
        conn.execute(text("ALTER TABLE servers ADD COLUMN public_ip VARCHAR(50)"))
        print("✓ Added public_ip column")
    except Exception as e:
        print(f"public_ip column may already exist: {e}")
    
    try:
        # Add group_name column
        conn.execute(text("ALTER TABLE servers ADD COLUMN group_name VARCHAR(255)"))
        print("✓ Added group_name column")
    except Exception as e:
        print(f"group_name column may already exist: {e}")
    
    try:
        # Add tags column
        conn.execute(text("ALTER TABLE servers ADD COLUMN tags JSON"))
        print("✓ Added tags column")
    except Exception as e:
        print(f"tags column may already exist: {e}")
    
    conn.commit()
    print("\n✓ Database migration completed!")
