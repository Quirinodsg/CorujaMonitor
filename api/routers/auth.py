from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, field_validator
from typing import Annotated, Optional

from database import get_db
from models import User
from auth import verify_password, create_access_token, get_password_hash

router = APIRouter()

class LoginRequest(BaseModel):
    username: str  # Can be email or username
    password: str
    mfa_code: Optional[str] = None  # Código MFA (opcional)
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        return v.lower().strip()

class LoginResponse(BaseModel):
    access_token: str = None
    token_type: str = "bearer"
    user: dict = None
    mfa_required: bool = False
    message: str = None

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
    
    # Verificar se MFA está habilitado
    if user.mfa_enabled:
        # Se MFA está habilitado mas código não foi fornecido
        if not request.mfa_code:
            return {
                "mfa_required": True,
                "message": "MFA code required"
            }
        
        # Verificar código MFA
        import pyotp
        totp = pyotp.TOTP(user.mfa_secret)
        
        # Verificar TOTP
        if not totp.verify(request.mfa_code, valid_window=1):
            # Verificar backup code
            if not (user.mfa_backup_codes and request.mfa_code in user.mfa_backup_codes):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid MFA code"
                )
            
            # Remover backup code usado
            user.mfa_backup_codes.remove(request.mfa_code)
            db.commit()
    
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
            "language": user.language,
            "mfa_enabled": user.mfa_enabled
        }
    }

class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str
    tenant_name: str
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        if '@' not in v:
            raise ValueError('Invalid email format')
        return v.lower()


# ── Azure AD (Microsoft Entra ID) OAuth2 ──────────────────────────────────────

FRONTEND_URL = "https://coruja.techbiz.com.br"
DEFAULT_REDIRECT_URI = f"{FRONTEND_URL}/api/v1/auth/azure/callback"


def _get_azure_config(db: Session) -> dict:
    """Lê config Azure AD da tabela AuthenticationConfig (salva pela UI).
    Fallback: tenta notification_config do Tenant (formato antigo).
    """
    import logging
    logger = logging.getLogger("auth.azure")

    from models import AuthenticationConfig, Tenant
    tenant = db.query(Tenant).first()
    if not tenant:
        logger.warning("Azure AD: nenhum tenant encontrado")
        return {}

    # Fonte primária: tabela authentication_config
    config = db.query(AuthenticationConfig).filter(
        AuthenticationConfig.tenant_id == tenant.id
    ).first()

    if config and config.azure_ad_config:
        logger.info("Azure AD: config encontrada em AuthenticationConfig (tenant_id=%s)", tenant.id)
        return config.azure_ad_config

    # Fallback: notification_config do tenant (formato antigo)
    if tenant.notification_config and isinstance(tenant.notification_config, dict):
        azure_cfg = tenant.notification_config.get('azure_ad', {})
        if azure_cfg.get('client_id'):
            logger.info("Azure AD: config encontrada em tenant.notification_config (fallback)")
            return azure_cfg

    logger.warning(
        "Azure AD: config NÃO encontrada. tenant_id=%s, auth_config_exists=%s, notification_config_keys=%s",
        tenant.id,
        config is not None,
        list(tenant.notification_config.keys()) if isinstance(tenant.notification_config, dict) else None,
    )
    return {}


@router.get("/azure/login")
async def azure_login(db: Session = Depends(get_db)):
    """Redireciona para login Microsoft Azure AD."""
    azure_cfg = _get_azure_config(db)
    if not azure_cfg.get('enabled') or not azure_cfg.get('client_id'):
        # Retornar info de debug para diagnosticar
        from models import AuthenticationConfig, Tenant
        tenant = db.query(Tenant).first()
        debug = {
            "tenant_exists": tenant is not None,
            "tenant_id": tenant.id if tenant else None,
        }
        if tenant:
            ac = db.query(AuthenticationConfig).filter(
                AuthenticationConfig.tenant_id == tenant.id
            ).first()
            debug["auth_config_exists"] = ac is not None
            if ac:
                debug["azure_ad_config_keys"] = list(ac.azure_ad_config.keys()) if ac.azure_ad_config else None
                debug["azure_ad_enabled"] = ac.azure_ad_config.get('enabled') if ac.azure_ad_config else None
            debug["notification_config_has_azure"] = bool(
                tenant.notification_config and isinstance(tenant.notification_config, dict)
                and tenant.notification_config.get('azure_ad')
            )
        raise HTTPException(status_code=400, detail={"error": "Azure AD não configurado", "debug": debug})

    tenant_id = azure_cfg['tenant_id']
    client_id = azure_cfg['client_id']
    redirect_uri = azure_cfg.get('redirect_uri') or DEFAULT_REDIRECT_URI

    auth_url = (
        f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/authorize"
        f"?client_id={client_id}"
        f"&response_type=code"
        f"&redirect_uri={redirect_uri}"
        f"&response_mode=query"
        f"&scope=openid+profile+email+User.Read"
    )

    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=auth_url)


@router.get("/azure/callback")
async def azure_callback(code: str = None, error: str = None, db: Session = Depends(get_db)):
    """Callback do Azure AD após autenticação."""
    from fastapi.responses import RedirectResponse
    import httpx

    if error:
        return RedirectResponse(url=f"{FRONTEND_URL}/?azure_error={error}")

    if not code:
        return RedirectResponse(url=f"{FRONTEND_URL}/?azure_error=no_code")

    azure_cfg = _get_azure_config(db)
    if not azure_cfg.get('client_id'):
        return RedirectResponse(url=f"{FRONTEND_URL}/?azure_error=not_configured")

    tenant_id = azure_cfg['tenant_id']
    client_id = azure_cfg['client_id']
    client_secret = azure_cfg['client_secret']
    redirect_uri = azure_cfg.get('redirect_uri') or DEFAULT_REDIRECT_URI
    admin_group_id = azure_cfg.get('admin_group_id', '')

    # Trocar code por token
    try:
        async with httpx.AsyncClient() as client:
            token_resp = await client.post(
                f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token",
                data={
                    'client_id': client_id,
                    'client_secret': client_secret,
                    'code': code,
                    'redirect_uri': redirect_uri,
                    'grant_type': 'authorization_code',
                    'scope': 'openid profile email User.Read',
                }
            )

            if token_resp.status_code != 200:
                return RedirectResponse(url=f"{FRONTEND_URL}/?azure_error=token_failed")

            tokens = token_resp.json()
            access_token = tokens.get('access_token')

            # Buscar perfil do usuário
            profile_resp = await client.get(
                'https://graph.microsoft.com/v1.0/me',
                headers={'Authorization': f'Bearer {access_token}'}
            )

            if profile_resp.status_code != 200:
                return RedirectResponse(url=f"{FRONTEND_URL}/?azure_error=profile_failed")

            profile = profile_resp.json()

            # Verificar grupos do usuário para determinar role
            is_admin = False
            if admin_group_id:
                try:
                    groups_resp = await client.post(
                        'https://graph.microsoft.com/v1.0/me/checkMemberObjects',
                        headers={'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'},
                        json={'ids': [admin_group_id]}
                    )
                    if groups_resp.status_code == 200:
                        member_ids = groups_resp.json().get('value', [])
                        is_admin = admin_group_id in member_ids
                except Exception:
                    pass

    except Exception as e:
        return RedirectResponse(url=f"{FRONTEND_URL}/?azure_error=request_failed")

    email = (profile.get('mail') or profile.get('userPrincipalName', '')).lower()
    full_name = profile.get('displayName', email.split('@')[0])

    if not email:
        return RedirectResponse(url=f"{FRONTEND_URL}/?azure_error=no_email")

    role = 'admin' if is_admin else 'viewer'

    # Buscar ou criar usuário
    from models import Tenant
    tenant = db.query(Tenant).first()
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(
            email=email,
            full_name=full_name,
            hashed_password=get_password_hash(f'azure_{email}_{tenant_id}'),
            role=role,
            tenant_id=tenant.id,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        user.full_name = full_name
        if is_admin and user.role != 'admin':
            user.role = 'admin'
        db.commit()

    # Gerar JWT do Coruja
    coruja_token = create_access_token(data={"sub": str(user.id), "tenant_id": user.tenant_id})

    # Redirecionar para frontend com token
    from urllib.parse import quote
    return RedirectResponse(
        url=f"{FRONTEND_URL}/?azure_token={coruja_token}&azure_user={quote(email)}&azure_name={quote(full_name)}&azure_role={role}"
    )

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
