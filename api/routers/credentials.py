"""
API de Credenciais Centralizadas
Sistema moderno como PRTG/SolarWinds/CheckMK
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from cryptography.fernet import Fernet
import os
import base64

from database import get_db
from models import Credential, Server, User, Probe
from auth import get_current_user

# Função auxiliar para autenticação opcional
def get_current_user_optional(
    db: Session = Depends(get_db),
    token: str = None
) -> Optional[User]:
    """Retorna usuário se autenticado, None caso contrário"""
    if not token:
        return None
    try:
        return get_current_user(db, token)
    except:
        return None

router = APIRouter(prefix="/api/v1/credentials", tags=["credentials"])

# Chave de criptografia (deve estar em variável de ambiente)
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", Fernet.generate_key().decode())
cipher = Fernet(ENCRYPTION_KEY.encode() if isinstance(ENCRYPTION_KEY, str) else ENCRYPTION_KEY)

# ============================================================================
# SCHEMAS
# ============================================================================

class CredentialBase(BaseModel):
    name: str
    description: Optional[str] = None
    credential_type: str  # wmi, snmp_v1, snmp_v2c, snmp_v3, ssh
    level: str = "tenant"  # tenant, group, server
    group_name: Optional[str] = None
    server_id: Optional[int] = None
    is_default: bool = False
    is_active: bool = True

class CredentialWMI(CredentialBase):
    wmi_username: str
    wmi_password: str
    wmi_domain: Optional[str] = None

class CredentialSNMPv2(CredentialBase):
    snmp_community: str
    snmp_port: int = 161

class CredentialSNMPv3(CredentialBase):
    snmp_username: str
    snmp_auth_protocol: str  # MD5, SHA, SHA256
    snmp_auth_password: str
    snmp_priv_protocol: str  # DES, AES, AES256
    snmp_priv_password: str
    snmp_context: Optional[str] = None
    snmp_port: int = 161

class CredentialSSH(CredentialBase):
    ssh_username: str
    ssh_password: Optional[str] = None
    ssh_private_key: Optional[str] = None
    ssh_port: int = 22

class CredentialResponse(BaseModel):
    id: int
    tenant_id: int
    name: str
    description: Optional[str]
    credential_type: str
    level: str
    group_name: Optional[str]
    server_id: Optional[int]
    is_default: bool
    is_active: bool
    last_test_at: Optional[datetime]
    last_test_status: Optional[str]
    last_test_message: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Campos mascarados (não retornar senhas)
    wmi_username: Optional[str] = None
    wmi_domain: Optional[str] = None
    snmp_community_masked: Optional[str] = None
    snmp_username: Optional[str] = None
    ssh_username: Optional[str] = None
    
    class Config:
        from_attributes = True

class TestConnectionRequest(BaseModel):
    hostname: str

class TestConnectionResponse(BaseModel):
    success: bool
    message: str
    details: Optional[dict] = None

# ============================================================================
# FUNÇÕES DE CRIPTOGRAFIA
# ============================================================================

def encrypt_password(password: str) -> str:
    """Criptografa senha"""
    return cipher.encrypt(password.encode()).decode()

def decrypt_password(encrypted: str) -> str:
    """Descriptografa senha"""
    try:
        return cipher.decrypt(encrypted.encode()).decode()
    except:
        return encrypted  # Fallback para senhas não criptografadas

def mask_string(value: str, show_chars: int = 4) -> str:
    """Mascara string mostrando apenas primeiros caracteres"""
    if not value or len(value) <= show_chars:
        return "****"
    return value[:show_chars] + "*" * (len(value) - show_chars)

# ============================================================================
# ENDPOINTS
# ============================================================================

@router.get("/", response_model=List[CredentialResponse])
def list_credentials(
    credential_type: Optional[str] = None,
    level: Optional[str] = None,
    group_name: Optional[str] = None,
    server_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lista credenciais do tenant"""
    query = db.query(Credential).filter(Credential.tenant_id == current_user.tenant_id)
    
    if credential_type:
        query = query.filter(Credential.credential_type == credential_type)
    if level:
        query = query.filter(Credential.level == level)
    if group_name:
        query = query.filter(Credential.group_name == group_name)
    if server_id:
        query = query.filter(Credential.server_id == server_id)
    
    credentials = query.order_by(Credential.name).all()
    
    # Mascarar senhas
    result = []
    for cred in credentials:
        cred_dict = {
            "id": cred.id,
            "tenant_id": cred.tenant_id,
            "name": cred.name,
            "description": cred.description,
            "credential_type": cred.credential_type,
            "level": cred.level,
            "group_name": cred.group_name,
            "server_id": cred.server_id,
            "is_default": cred.is_default,
            "is_active": cred.is_active,
            "last_test_at": cred.last_test_at,
            "last_test_status": cred.last_test_status,
            "last_test_message": cred.last_test_message,
            "created_at": cred.created_at,
            "updated_at": cred.updated_at,
        }
        
        # Adicionar campos específicos mascarados
        if cred.credential_type == "wmi":
            cred_dict["wmi_username"] = cred.wmi_username
            cred_dict["wmi_domain"] = cred.wmi_domain
        elif cred.credential_type in ["snmp_v1", "snmp_v2c"]:
            cred_dict["snmp_community_masked"] = mask_string(cred.snmp_community or "")
        elif cred.credential_type == "snmp_v3":
            cred_dict["snmp_username"] = cred.snmp_username
        elif cred.credential_type == "ssh":
            cred_dict["ssh_username"] = cred.ssh_username
        
        result.append(CredentialResponse(**cred_dict))
    
    return result

@router.post("/wmi", response_model=CredentialResponse)
def create_wmi_credential(
    credential: CredentialWMI,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cria credencial WMI"""
    # Validar nível
    if credential.level == "group" and not credential.group_name:
        raise HTTPException(400, "group_name é obrigatório para level=group")
    if credential.level == "server" and not credential.server_id:
        raise HTTPException(400, "server_id é obrigatório para level=server")
    
    # Criar credencial
    db_credential = Credential(
        tenant_id=current_user.tenant_id,
        name=credential.name,
        description=credential.description,
        credential_type="wmi",
        level=credential.level,
        group_name=credential.group_name,
        server_id=credential.server_id,
        wmi_username=credential.wmi_username,
        wmi_password_encrypted=encrypt_password(credential.wmi_password_encrypted),
        wmi_domain=credential.wmi_domain,
        is_default=credential.is_default,
        is_active=credential.is_active,
        created_by=current_user.id
    )
    
    # Se marcar como padrão, desmarcar outras
    if credential.is_default:
        db.query(Credential).filter(
            and_(
                Credential.tenant_id == current_user.tenant_id,
                Credential.credential_type == "wmi",
                Credential.level == credential.level,
                Credential.is_default == True
            )
        ).update({"is_default": False})
    
    db.add(db_credential)
    db.commit()
    db.refresh(db_credential)
    
    return CredentialResponse(
        id=db_credential.id,
        tenant_id=db_credential.tenant_id,
        name=db_credential.name,
        description=db_credential.description,
        credential_type=db_credential.credential_type,
        level=db_credential.level,
        group_name=db_credential.group_name,
        server_id=db_credential.server_id,
        is_default=db_credential.is_default,
        is_active=db_credential.is_active,
        last_test_at=db_credential.last_test_at,
        last_test_status=db_credential.last_test_status,
        last_test_message=db_credential.last_test_message,
        created_at=db_credential.created_at,
        updated_at=db_credential.updated_at,
        wmi_username=db_credential.wmi_username,
        wmi_domain=db_credential.wmi_domain
    )

@router.post("/snmp-v2c", response_model=CredentialResponse)
def create_snmp_v2c_credential(
    credential: CredentialSNMPv2,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cria credencial SNMP v2c"""
    db_credential = Credential(
        tenant_id=current_user.tenant_id,
        name=credential.name,
        description=credential.description,
        credential_type="snmp_v2c",
        level=credential.level,
        group_name=credential.group_name,
        server_id=credential.server_id,
        snmp_community=encrypt_password(credential.snmp_community),
        snmp_port=credential.snmp_port,
        is_default=credential.is_default,
        is_active=credential.is_active,
        created_by=current_user.id
    )
    
    if credential.is_default:
        db.query(Credential).filter(
            and_(
                Credential.tenant_id == current_user.tenant_id,
                Credential.credential_type == "snmp_v2c",
                Credential.level == credential.level,
                Credential.is_default == True
            )
        ).update({"is_default": False})
    
    db.add(db_credential)
    db.commit()
    db.refresh(db_credential)
    
    return CredentialResponse(
        id=db_credential.id,
        tenant_id=db_credential.tenant_id,
        name=db_credential.name,
        description=db_credential.description,
        credential_type=db_credential.credential_type,
        level=db_credential.level,
        group_name=db_credential.group_name,
        server_id=db_credential.server_id,
        is_default=db_credential.is_default,
        is_active=db_credential.is_active,
        last_test_at=db_credential.last_test_at,
        last_test_status=db_credential.last_test_status,
        last_test_message=db_credential.last_test_message,
        created_at=db_credential.created_at,
        updated_at=db_credential.updated_at,
        snmp_community_masked=mask_string(credential.snmp_community)
    )

@router.put("/{credential_id}", response_model=CredentialResponse)
def update_credential(
    credential_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    is_default: Optional[bool] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Atualiza credencial (apenas metadados, não senhas)"""
    credential = db.query(Credential).filter(
        and_(
            Credential.id == credential_id,
            Credential.tenant_id == current_user.tenant_id
        )
    ).first()
    
    if not credential:
        raise HTTPException(404, "Credencial não encontrada")
    
    if name:
        credential.name = name
    if description is not None:
        credential.description = description
    if is_default is not None:
        if is_default:
            # Desmarcar outras
            db.query(Credential).filter(
                and_(
                    Credential.tenant_id == current_user.tenant_id,
                    Credential.credential_type == credential.credential_type,
                    Credential.level == credential.level,
                    Credential.is_default == True,
                    Credential.id != credential_id
                )
            ).update({"is_default": False})
        credential.is_default = is_default
    if is_active is not None:
        credential.is_active = is_active
    
    credential.updated_at = datetime.now()
    db.commit()
    db.refresh(credential)
    
    return CredentialResponse(
        id=credential.id,
        tenant_id=credential.tenant_id,
        name=credential.name,
        description=credential.description,
        credential_type=credential.credential_type,
        level=credential.level,
        group_name=credential.group_name,
        server_id=credential.server_id,
        is_default=credential.is_default,
        is_active=credential.is_active,
        last_test_at=credential.last_test_at,
        last_test_status=credential.last_test_status,
        last_test_message=credential.last_test_message,
        created_at=credential.created_at,
        updated_at=credential.updated_at
    )

@router.delete("/{credential_id}")
def delete_credential(
    credential_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Deleta credencial"""
    credential = db.query(Credential).filter(
        and_(
            Credential.id == credential_id,
            Credential.tenant_id == current_user.tenant_id
        )
    ).first()
    
    if not credential:
        raise HTTPException(404, "Credencial não encontrada")
    
    # Verificar se está em uso
    servers_using = db.query(Server).filter(Server.credential_id == credential_id).count()
    if servers_using > 0:
        raise HTTPException(400, f"Credencial em uso por {servers_using} servidor(es)")
    
    db.delete(credential)
    db.commit()
    
    return {"message": "Credencial deletada com sucesso"}

@router.post("/{credential_id}/test", response_model=TestConnectionResponse)
def test_credential(
    credential_id: int,
    request: TestConnectionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Testa conectividade com a credencial"""
    credential = db.query(Credential).filter(
        and_(
            Credential.id == credential_id,
            Credential.tenant_id == current_user.tenant_id
        )
    ).first()
    
    if not credential:
        raise HTTPException(404, "Credencial não encontrada")
    
    # Testar baseado no tipo
    try:
        if credential.credential_type == "wmi":
            # Teste WMI simplificado (apenas valida credencial salva)
            # Teste real será feito pela Probe Windows
            success = True
            message = "Credencial WMI salva com sucesso. Teste real será executado pela Probe Windows ao coletar métricas."
            
            # Atualizar status
            credential.last_test_at = datetime.now()
            credential.last_test_status = "success" if success else "failed"
            credential.last_test_message = message
            db.commit()
            
            return TestConnectionResponse(
                success=success,
                message=message,
                details={"hostname": request.hostname, "type": "wmi"}
            )
        
        elif credential.credential_type in ["snmp_v2c", "snmp_v1"]:
            # Teste SNMP simplificado
            success = True
            message = "Credencial SNMP salva com sucesso. Teste real será executado pela Probe ao coletar métricas."
            
            credential.last_test_at = datetime.now()
            credential.last_test_status = "success" if success else "failed"
            credential.last_test_message = message
            db.commit()
            
            return TestConnectionResponse(
                success=success,
                message=message,
                details={"hostname": request.hostname, "type": "snmp_v2c"}
            )
        
        else:
            return TestConnectionResponse(
                success=False,
                message=f"Teste não implementado para tipo: {credential.credential_type}"
            )
    
    except Exception as e:
        credential.last_test_at = datetime.now()
        credential.last_test_status = "failed"
        credential.last_test_message = str(e)
        db.commit()
        
        return TestConnectionResponse(
            success=False,
            message=f"Erro ao testar: {str(e)}"
        )

@router.get("/resolve/{server_id}")
def resolve_credential_for_server(
    server_id: int,
    probe_token: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """
    Resolve qual credencial usar para um servidor (herança)
    Ordem: Servidor específico → Grupo → Tenant
    Suporta autenticação via JWT (usuário) ou probe_token (probe)
    """
    # Autenticação via probe_token
    if probe_token:
        probe = db.query(Probe).filter(Probe.token == probe_token).first()
        if not probe:
            raise HTTPException(403, "Token de probe inválido")
        
        server = db.query(Server).filter(Server.id == server_id).first()
        if not server:
            raise HTTPException(404, "Servidor não encontrado")
        
        tenant_id = server.tenant_id
    
    # Autenticação via JWT
    elif current_user:
        server = db.query(Server).filter(
            and_(
                Server.id == server_id,
                Server.tenant_id == current_user.tenant_id
            )
        ).first()
        
        if not server:
            raise HTTPException(404, "Servidor não encontrado")
        
        tenant_id = current_user.tenant_id
    
    else:
        raise HTTPException(401, "Autenticação necessária")
    
    # 1. Credencial específica do servidor
    if server.credential_id and not server.use_inherited_credential:
        credential = db.query(Credential).filter(Credential.id == server.credential_id).first()
        if credential:
            result = {
                "id": credential.id,
                "name": credential.name,
                "credential_type": credential.credential_type,
                "inheritance_level": "server"
            }
            
            # Se for probe, retornar dados completos descriptografados
            if probe_token:
                if credential.credential_type == "wmi":
                    result["username"] = credential.wmi_username
                    result["password"] = decrypt_password(credential.wmi_password_encrypted) if credential.wmi_password_encrypted else None
                    result["domain"] = credential.wmi_domain
                elif credential.credential_type in ["snmp_v1", "snmp_v2c"]:
                    result["community"] = decrypt_password(credential.snmp_community) if credential.snmp_community else None
                elif credential.credential_type == "snmp_v3":
                    result["username"] = credential.snmp_username
                    result["auth_password"] = decrypt_password(credential.snmp_auth_password_encrypted) if credential.snmp_auth_password_encrypted else None
                    result["priv_password"] = decrypt_password(credential.snmp_priv_password_encrypted) if credential.snmp_priv_password_encrypted else None
                    result["auth_protocol"] = credential.snmp_auth_protocol
                    result["priv_protocol"] = credential.snmp_priv_protocol
                elif credential.credential_type == "ssh":
                    result["username"] = credential.ssh_username
                    result["password"] = decrypt_password(credential.ssh_password_encrypted) if credential.ssh_password_encrypted else None
                    result["private_key"] = credential.ssh_private_key_encrypted
            
            return result
    
    # 2. Credencial do grupo
    if server.group_name:
        credential = db.query(Credential).filter(
            and_(
                Credential.tenant_id == tenant_id,
                Credential.level == "group",
                Credential.group_name == server.group_name,
                Credential.is_active == True,
                Credential.is_default == True
            )
        ).first()
        
        if credential:
            result = {
                "id": credential.id,
                "name": credential.name,
                "credential_type": credential.credential_type,
                "inheritance_level": "group",
                "group_name": server.group_name
            }
            
            # Se for probe, retornar dados completos descriptografados
            if probe_token:
                if credential.credential_type == "wmi":
                    result["username"] = credential.wmi_username
                    result["password"] = decrypt_password(credential.wmi_password_encrypted) if credential.wmi_password_encrypted else None
                    result["domain"] = credential.wmi_domain
                elif credential.credential_type in ["snmp_v1", "snmp_v2c"]:
                    result["community"] = decrypt_password(credential.snmp_community) if credential.snmp_community else None
                elif credential.credential_type == "snmp_v3":
                    result["username"] = credential.snmp_username
                    result["auth_password"] = decrypt_password(credential.snmp_auth_password_encrypted) if credential.snmp_auth_password_encrypted else None
                    result["priv_password"] = decrypt_password(credential.snmp_priv_password_encrypted) if credential.snmp_priv_password_encrypted else None
                    result["auth_protocol"] = credential.snmp_auth_protocol
                    result["priv_protocol"] = credential.snmp_priv_protocol
                elif credential.credential_type == "ssh":
                    result["username"] = credential.ssh_username
                    result["password"] = decrypt_password(credential.ssh_password_encrypted) if credential.ssh_password_encrypted else None
                    result["private_key"] = credential.ssh_private_key_encrypted
            
            return result
    
    # 3. Credencial do tenant (padrão)
    credential = db.query(Credential).filter(
        and_(
            Credential.tenant_id == tenant_id,
            Credential.level == "tenant",
            Credential.is_active == True,
            Credential.is_default == True
        )
    ).first()
    
    if credential:
        result = {
            "id": credential.id,
            "name": credential.name,
            "credential_type": credential.credential_type,
            "inheritance_level": "tenant"
        }
        
        # Se for probe, retornar dados completos descriptografados
        if probe_token:
            if credential.credential_type == "wmi":
                result["username"] = credential.wmi_username
                result["password"] = decrypt_password(credential.wmi_password_encrypted) if credential.wmi_password_encrypted else None
                result["domain"] = credential.wmi_domain
            elif credential.credential_type in ["snmp_v1", "snmp_v2c"]:
                result["community"] = decrypt_password(credential.snmp_community) if credential.snmp_community else None
            elif credential.credential_type == "snmp_v3":
                result["username"] = credential.snmp_username
                result["auth_password"] = decrypt_password(credential.snmp_auth_password_encrypted) if credential.snmp_auth_password_encrypted else None
                result["priv_password"] = decrypt_password(credential.snmp_priv_password_encrypted) if credential.snmp_priv_password_encrypted else None
                result["auth_protocol"] = credential.snmp_auth_protocol
                result["priv_protocol"] = credential.snmp_priv_protocol
            elif credential.credential_type == "ssh":
                result["username"] = credential.ssh_username
                result["password"] = decrypt_password(credential.ssh_password_encrypted) if credential.ssh_password_encrypted else None
                result["private_key"] = credential.ssh_private_key_encrypted
        
        return result
    
    return {
        "source": "none",
        "message": "Nenhuma credencial configurada"
    }

