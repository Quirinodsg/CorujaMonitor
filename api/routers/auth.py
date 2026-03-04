from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, field_validator
from typing import Annotated

from database import get_db
from models import User
from auth import verify_password, create_access_token, get_password_hash

router = APIRouter()

class LoginRequest(BaseModel):
    username: str  # Can be email or username
    password: str
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        return v.lower().strip()

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    # Try to find user by email (username field can contain email)
    user = db.query(User).filter(User.email == request.username).first()
    
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    # Pass user_id as string for JWT 'sub' claim
    access_token = create_access_token(data={"sub": str(user.id), "tenant_id": user.tenant_id})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "tenant_id": user.tenant_id,
            "language": user.language
        }
    }

class RegisterRequest(BaseModel):
    email: str  # Changed from EmailStr to allow .local domains
    password: str
    full_name: str
    tenant_name: str
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        if '@' not in v:
            raise ValueError('Invalid email format')
        return v.lower()

@router.post("/register")
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    # Check if user exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create tenant
    from models import Tenant
    tenant_slug = request.tenant_name.lower().replace(" ", "-")
    tenant = Tenant(name=request.tenant_name, slug=tenant_slug)
    db.add(tenant)
    db.flush()
    
    # Create user
    hashed_password = get_password_hash(request.password)
    user = User(
        email=request.email,
        hashed_password=hashed_password,
        full_name=request.full_name,
        tenant_id=tenant.id,
        role="admin"
    )
    db.add(user)
    db.commit()
    
    return {"message": "User registered successfully", "user_id": user.id}
