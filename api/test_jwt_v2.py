"""
Test JWT token generation and validation
Run: docker exec -it coruja-api python test_jwt_v2.py
"""
from auth import create_access_token
from jose import jwt, JWTError
from config import settings

print("="*50)
print("JWT Configuration Test V2")
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

# Test token validation directly with jose
print("Validating token with jose.jwt.decode...")
try:
    decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    print(f"✓ Token validated successfully!")
    print(f"  Decoded data: {decoded}")
    print()
    print("="*50)
    print("JWT is working correctly!")
    print("="*50)
except JWTError as e:
    print(f"✗ Token validation failed: {e}")
    print(f"  Error type: {type(e).__name__}")
    print()
    print("="*50)
    print("JWT configuration has issues!")
    print("="*50)
