"""
MFA (Multi-Factor Authentication) Router
Suporte para TOTP (Google Authenticator, Authy, etc)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
import pyotp
import qrcode
import io
import base64
import secrets
from datetime import datetime

from database import get_db
from models import User
from auth import get_current_active_user, get_password_hash, verify_password

router = APIRouter()


class MFASetupResponse(BaseModel):
    secret: str
    qr_code: str  # Base64 encoded QR code image
    backup_codes: List[str]
    issuer: str
    account_name: str


class MFAEnableRequest(BaseModel):
    password: str  # Confirmar senha antes de habilitar
    code: str  # Código TOTP para verificar


class MFAVerifyRequest(BaseModel):
    code: str  # Código TOTP ou backup code


class MFADisableRequest(BaseModel):
    password: str
    code: str  # Código TOTP para confirmar


def generate_backup_codes(count: int = 10) -> List[str]:
    """Gera códigos de backup aleatórios"""
    codes = []
    for _ in range(count):
        # Gerar código de 8 dígitos
        code = ''.join([str(secrets.randbelow(10)) for _ in range(8)])
        # Formatar como XXXX-XXXX
        formatted = f"{code[:4]}-{code[4:]}"
        codes.append(formatted)
    return codes


def generate_qr_code(secret: str, account_name: str, issuer: str = "CorujaMonitor") -> str:
    """Gera QR code para TOTP e retorna como base64"""
    
    # Criar URI do TOTP
    totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=account_name,
        issuer_name=issuer
    )
    
    # Gerar QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(totp_uri)
    qr.make(fit=True)
    
    # Criar imagem
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Converter para base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"


@router.post("/mfa/setup", response_model=MFASetupResponse)
async def setup_mfa(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Inicia configuração do MFA
    Gera secret, QR code e backup codes
    """
    
    # Verificar se MFA já está habilitado
    if current_user.mfa_enabled:
        raise HTTPException(
            status_code=400,
            detail="MFA already enabled. Disable it first to reconfigure."
        )
    
    # Gerar secret TOTP
    secret = pyotp.random_base32()
    
    # Gerar backup codes
    backup_codes = generate_backup_codes()
    
    # Gerar QR code
    qr_code = generate_qr_code(
        secret=secret,
        account_name=current_user.email,
        issuer="CorujaMonitor"
    )
    
    # Salvar secret temporariamente (será confirmado no enable)
    current_user.mfa_secret = secret
    current_user.mfa_backup_codes = backup_codes
    db.commit()
    
    return {
        "secret": secret,
        "qr_code": qr_code,
        "backup_codes": backup_codes,
        "issuer": "CorujaMonitor",
        "account_name": current_user.email
    }


@router.post("/mfa/enable")
async def enable_mfa(
    request: MFAEnableRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Habilita MFA após verificar senha e código TOTP
    """
    
    # Verificar senha
    if not verify_password(request.password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
        )
    
    # Verificar se secret foi gerado
    if not current_user.mfa_secret:
        raise HTTPException(
            status_code=400,
            detail="MFA not configured. Call /mfa/setup first."
        )
    
    # Verificar código TOTP
    totp = pyotp.TOTP(current_user.mfa_secret)
    if not totp.verify(request.code, valid_window=1):
        raise HTTPException(
            status_code=400,
            detail="Invalid TOTP code"
        )
    
    # Habilitar MFA
    current_user.mfa_enabled = True
    db.commit()
    
    return {
        "message": "MFA enabled successfully",
        "backup_codes": current_user.mfa_backup_codes
    }


@router.post("/mfa/verify")
async def verify_mfa(
    request: MFAVerifyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Verifica código MFA (TOTP ou backup code)
    """
    
    if not current_user.mfa_enabled:
        raise HTTPException(
            status_code=400,
            detail="MFA not enabled"
        )
    
    # Tentar verificar como TOTP
    totp = pyotp.TOTP(current_user.mfa_secret)
    if totp.verify(request.code, valid_window=1):
        return {"message": "MFA verified successfully", "method": "totp"}
    
    # Tentar verificar como backup code
    if current_user.mfa_backup_codes and request.code in current_user.mfa_backup_codes:
        # Remover backup code usado
        current_user.mfa_backup_codes.remove(request.code)
        db.commit()
        
        return {
            "message": "MFA verified successfully",
            "method": "backup_code",
            "remaining_codes": len(current_user.mfa_backup_codes)
        }
    
    raise HTTPException(
        status_code=400,
        detail="Invalid MFA code"
    )


@router.post("/mfa/disable")
async def disable_mfa(
    request: MFADisableRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Desabilita MFA após verificar senha e código
    """
    
    if not current_user.mfa_enabled:
        raise HTTPException(
            status_code=400,
            detail="MFA not enabled"
        )
    
    # Verificar senha
    if not verify_password(request.password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
        )
    
    # Verificar código TOTP
    totp = pyotp.TOTP(current_user.mfa_secret)
    if not totp.verify(request.code, valid_window=1):
        raise HTTPException(
            status_code=400,
            detail="Invalid TOTP code"
        )
    
    # Desabilitar MFA
    current_user.mfa_enabled = False
    current_user.mfa_secret = None
    current_user.mfa_backup_codes = None
    db.commit()
    
    return {"message": "MFA disabled successfully"}


@router.get("/mfa/status")
async def get_mfa_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retorna status do MFA do usuário
    """
    
    return {
        "enabled": current_user.mfa_enabled,
        "backup_codes_remaining": len(current_user.mfa_backup_codes) if current_user.mfa_backup_codes else 0,
        "configured": current_user.mfa_secret is not None
    }


@router.post("/mfa/regenerate-backup-codes")
async def regenerate_backup_codes(
    password: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Regenera códigos de backup
    """
    
    if not current_user.mfa_enabled:
        raise HTTPException(
            status_code=400,
            detail="MFA not enabled"
        )
    
    # Verificar senha
    if not verify_password(password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
        )
    
    # Gerar novos backup codes
    backup_codes = generate_backup_codes()
    current_user.mfa_backup_codes = backup_codes
    db.commit()
    
    return {
        "message": "Backup codes regenerated successfully",
        "backup_codes": backup_codes
    }
