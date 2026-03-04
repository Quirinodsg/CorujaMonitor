from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

from database import get_db
from models import AuthenticationConfig, User
from auth import get_current_active_user, require_role

router = APIRouter()


class LDAPConfig(BaseModel):
    enabled: bool = False
    server: str = ""
    port: int = 389
    use_ssl: bool = False
    base_dn: str = ""
    bind_dn: str = ""
    bind_password: str = ""
    user_filter: str = "(uid={username})"
    group_filter: str = ""
    admin_group: str = ""
    user_group: str = ""
    viewer_group: str = ""


class SAMLConfig(BaseModel):
    enabled: bool = False
    entity_id: str = ""
    sso_url: str = ""
    slo_url: str = ""
    x509_cert: str = ""
    attribute_mapping: Dict[str, str] = {"email": "email", "name": "name", "role": "role"}


class OAuth2Config(BaseModel):
    enabled: bool = False
    provider: str = "generic"
    client_id: str = ""
    client_secret: str = ""
    authorization_url: str = ""
    token_url: str = ""
    userinfo_url: str = ""
    scope: str = "openid profile email"
    attribute_mapping: Dict[str, str] = {"email": "email", "name": "name", "role": "role"}


class AzureADConfig(BaseModel):
    enabled: bool = False
    tenant_id: str = ""
    client_id: str = ""
    client_secret: str = ""
    redirect_uri: str = ""
    admin_group_id: str = ""
    user_group_id: str = ""
    viewer_group_id: str = ""


class GoogleConfig(BaseModel):
    enabled: bool = False
    client_id: str = ""
    client_secret: str = ""
    redirect_uri: str = ""
    hosted_domain: str = ""
    admin_group: str = ""
    user_group: str = ""
    viewer_group: str = ""


class OktaConfig(BaseModel):
    enabled: bool = False
    domain: str = ""
    client_id: str = ""
    client_secret: str = ""
    redirect_uri: str = ""
    admin_group: str = ""
    user_group: str = ""
    viewer_group: str = ""


class MFAConfig(BaseModel):
    enabled: bool = False
    method: str = "totp"
    issuer: str = "CorujaMonitor"
    enforce_for_admins: bool = True
    enforce_for_all: bool = False


class PasswordPolicy(BaseModel):
    min_length: int = 8
    require_uppercase: bool = True
    require_lowercase: bool = True
    require_numbers: bool = True
    require_special: bool = True
    expiry_days: int = 90
    prevent_reuse: int = 5


class SessionConfig(BaseModel):
    timeout_minutes: int = 480
    max_concurrent_sessions: int = 3
    remember_me_days: int = 30


class AuthConfigRequest(BaseModel):
    ldap: Optional[LDAPConfig] = None
    saml: Optional[SAMLConfig] = None
    oauth2: Optional[OAuth2Config] = None
    azure_ad: Optional[AzureADConfig] = None
    google: Optional[GoogleConfig] = None
    okta: Optional[OktaConfig] = None
    mfa: Optional[MFAConfig] = None
    password_policy: Optional[PasswordPolicy] = None
    session: Optional[SessionConfig] = None


@router.get("/auth-config")
async def get_auth_config(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get authentication configuration for current tenant"""
    config = db.query(AuthenticationConfig).filter(
        AuthenticationConfig.tenant_id == current_user.tenant_id
    ).first()
    
    if not config:
        # Return default configuration
        return {
            "ldap": LDAPConfig().dict(),
            "saml": SAMLConfig().dict(),
            "oauth2": OAuth2Config().dict(),
            "azure_ad": AzureADConfig().dict(),
            "google": GoogleConfig().dict(),
            "okta": OktaConfig().dict(),
            "mfa": MFAConfig().dict(),
            "password_policy": PasswordPolicy().dict(),
            "session": SessionConfig().dict()
        }
    
    return {
        "ldap": config.ldap_config or LDAPConfig().dict(),
        "saml": config.saml_config or SAMLConfig().dict(),
        "oauth2": config.oauth2_config or OAuth2Config().dict(),
        "azure_ad": config.azure_ad_config or AzureADConfig().dict(),
        "google": config.google_config or GoogleConfig().dict(),
        "okta": config.okta_config or OktaConfig().dict(),
        "mfa": config.mfa_config or MFAConfig().dict(),
        "password_policy": config.password_policy or PasswordPolicy().dict(),
        "session": config.session_config or SessionConfig().dict()
    }


@router.put("/auth-config")
async def update_auth_config(
    request: AuthConfigRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Update authentication configuration (admin only)"""
    config = db.query(AuthenticationConfig).filter(
        AuthenticationConfig.tenant_id == current_user.tenant_id
    ).first()
    
    if not config:
        config = AuthenticationConfig(tenant_id=current_user.tenant_id)
        db.add(config)
    
    # Update configurations
    if request.ldap:
        config.ldap_config = request.ldap.dict()
    if request.saml:
        config.saml_config = request.saml.dict()
    if request.oauth2:
        config.oauth2_config = request.oauth2.dict()
    if request.azure_ad:
        config.azure_ad_config = request.azure_ad.dict()
    if request.google:
        config.google_config = request.google.dict()
    if request.okta:
        config.okta_config = request.okta.dict()
    if request.mfa:
        config.mfa_config = request.mfa.dict()
    if request.password_policy:
        config.password_policy = request.password_policy.dict()
    if request.session:
        config.session_config = request.session.dict()
    
    config.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(config)
    
    return {"message": "Authentication configuration updated successfully"}


@router.post("/auth-config/test/{provider}")
async def test_auth_config(
    provider: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Test authentication configuration for a specific provider"""
    config = db.query(AuthenticationConfig).filter(
        AuthenticationConfig.tenant_id == current_user.tenant_id
    ).first()
    
    if not config:
        raise HTTPException(status_code=404, detail="Authentication configuration not found")
    
    # Test based on provider
    if provider == "ldap":
        ldap_config = config.ldap_config
        if not ldap_config or not ldap_config.get("enabled"):
            raise HTTPException(status_code=400, detail="LDAP not enabled")
        
        # TODO: Implement actual LDAP connection test
        # For now, just validate configuration
        required_fields = ["server", "base_dn", "bind_dn", "bind_password"]
        missing = [f for f in required_fields if not ldap_config.get(f)]
        if missing:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required LDAP fields: {', '.join(missing)}"
            )
        
        return {"message": "LDAP configuration is valid. Connection test not yet implemented."}
    
    elif provider == "saml":
        saml_config = config.saml_config
        if not saml_config or not saml_config.get("enabled"):
            raise HTTPException(status_code=400, detail="SAML not enabled")
        
        required_fields = ["entity_id", "sso_url", "x509_cert"]
        missing = [f for f in required_fields if not saml_config.get(f)]
        if missing:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required SAML fields: {', '.join(missing)}"
            )
        
        return {"message": "SAML configuration is valid. Connection test not yet implemented."}
    
    elif provider == "azure_ad":
        azure_config = config.azure_ad_config
        if not azure_config or not azure_config.get("enabled"):
            raise HTTPException(status_code=400, detail="Azure AD not enabled")
        
        required_fields = ["tenant_id", "client_id", "client_secret", "redirect_uri"]
        missing = [f for f in required_fields if not azure_config.get(f)]
        if missing:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required Azure AD fields: {', '.join(missing)}"
            )
        
        return {"message": "Azure AD configuration is valid. Connection test not yet implemented."}
    
    elif provider == "oauth2":
        oauth2_config = config.oauth2_config
        if not oauth2_config or not oauth2_config.get("enabled"):
            raise HTTPException(status_code=400, detail="OAuth2 not enabled")
        
        required_fields = ["client_id", "client_secret", "authorization_url", "token_url", "userinfo_url"]
        missing = [f for f in required_fields if not oauth2_config.get(f)]
        if missing:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required OAuth2 fields: {', '.join(missing)}"
            )
        
        return {"message": "OAuth2 configuration is valid. Connection test not yet implemented."}
    
    else:
        raise HTTPException(status_code=400, detail=f"Unknown provider: {provider}")
