"""
Test login functionality
Run inside container: python test_login.py
"""
import sys
from database import SessionLocal
from models import User
from auth import verify_password

def test_login():
    db = SessionLocal()
    
    try:
        # Check if user exists
        user = db.query(User).filter(User.email == 'admin@coruja.com').first()
        
        if not user:
            print("❌ User not found!")
            print("Run: python init_admin.py")
            return False
        
        print(f"✅ User found: {user.email}")
        print(f"   Full name: {user.full_name}")
        print(f"   Role: {user.role}")
        print(f"   Tenant ID: {user.tenant_id}")
        print(f"   Active: {user.is_active}")
        
        # Test password
        password_ok = verify_password('admin123', user.hashed_password)
        
        if password_ok:
            print("\n✅ Password is correct!")
            print("\nLogin should work with:")
            print("   Email: admin@coruja.com")
            print("   Password: admin123")
            return True
        else:
            print("\n❌ Password is incorrect!")
            print("Run: python init_admin.py")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = test_login()
    sys.exit(0 if success else 1)
