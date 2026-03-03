"""
Test JWT token generation and validation
Run: docker exec -it coruja-api python test_jwt.py
"""
from auth import create_access_token, decode_token
from config import settings

print("="*50)
print("JWT Configuration Test")
print("="*50)
print(f"SECRET_KEY: {settings.SECRET_KEY[:20]}...")
print(f"JWT_ALGORITHM: {settings.JWT_ALGORITHM}")
print(f"JWT_EXPIRATION: {settings.JWT_EXPIRATION_MINUTES} minutes")
print()

# Test token creation
print("Creating test token...")
test_data = {"sub": 1, "tenant_id": 1}
token = create_access_token(test_data)
print(f"✓ Token created: {token[:50]}...")
print()

# Test token validation
print("Validating token...")
try:
    decoded = decode_token(token)
    print(f"✓ Token validated successfully!")
    print(f"  Decoded data: {decoded}")
    print()
    print("="*50)
    print("JWT is working correctly!")
    print("="*50)
except Exception as e:
    print(f"✗ Token validation failed: {e}")
    print()
    print("="*50)
    print("JWT configuration has issues!")
    print("="*50)
