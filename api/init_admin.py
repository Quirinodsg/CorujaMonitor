"""
Script to create initial admin user
Run: docker exec -it coruja-api python init_admin.py
"""
from database import SessionLocal
from models import User, Tenant
from auth import get_password_hash

def create_admin_user():
    db = SessionLocal()
    
    try:
        # Check if admin already exists
        existing_user = db.query(User).filter(User.email == 'admin@coruja.com').first()
        if existing_user:
            print("❌ Admin user already exists!")
            print(f"   Email: admin@coruja.com")
            return
        
        # Create default tenant
        tenant = db.query(Tenant).filter(Tenant.slug == 'default').first()
        if not tenant:
            tenant = Tenant(name='Default', slug='default')
            db.add(tenant)
            db.flush()
            print("✅ Created default tenant")
        
        # Create admin user
        admin_user = User(
            email='admin@coruja.com',
            hashed_password=get_password_hash('admin123'),
            full_name='Administrator',
            tenant_id=tenant.id,
            role='admin',
            language='pt-BR'
        )
        db.add(admin_user)
        db.commit()
        
        print("\n" + "="*50)
        print("✅ Admin user created successfully!")
        print("="*50)
        print(f"   Email: admin@coruja.com")
        print(f"   Password: admin123")
        print(f"   Role: admin")
        print("="*50)
        print("\n⚠️  IMPORTANT: Change the password after first login!")
        print("\n")
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()
