"""
AI Configuration API - Status e configuração do Ollama
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import httpx
from datetime import datetime

from database import get_db
from models import User, AutoResolutionConfig
from auth import get_current_active_user, require_role

router = APIRouter()


class OllamaStatusResponse(BaseModel):
    online: bool
    url: str
    model: str
    version: Optional[str]
    error: Optional[str]


class AutoResolutionConfigResponse(BaseModel):
    auto_resolution_enabled: bool
    require_approval_for_critical: bool
    min_confidence_threshold: float
    min_success_rate_threshold: float
    
    cpu_auto_resolve: bool
    memory_auto_resolve: bool
    disk_auto_resolve: bool
    service_auto_resolve: bool
    network_auto_resolve: bool
    
    max_executions_per_hour: int
    max_executions_per_day: int
    cooldown_minutes: int
    
    class Config:
        from_attributes = True


@router.get("/status", response_model=OllamaStatusResponse)
async def get_ollama_status(
    current_user: User = Depends(get_current_active_user)
):
    """Verificar status do Ollama"""
    import os
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
    preferred_model = os.getenv("AI_MODEL", "llama3.2")

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{ollama_url}/api/tags")

            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])
                model_names = [m.get("name", "") for m in models]

                # Usar o modelo preferido se instalado, senão o primeiro disponível
                active_model = preferred_model
                model_installed = any(m.startswith(preferred_model.split(":")[0]) for m in model_names)
                if not model_installed and model_names:
                    active_model = model_names[0]
                    model_installed = True

                return OllamaStatusResponse(
                    online=True,
                    url=ollama_url,
                    model=active_model if model_installed else "not_installed",
                    version=data.get("version"),
                    error=None if model_installed else f"Modelo {preferred_model} não instalado"
                )
            else:
                return OllamaStatusResponse(
                    online=False, url=ollama_url, model=preferred_model,
                    version=None, error=f"HTTP {response.status_code}"
                )

    except httpx.ConnectError:
        return OllamaStatusResponse(
            online=False, url=ollama_url, model=preferred_model,
            version=None, error="Connection refused - Ollama não está rodando"
        )
    except Exception as e:
        return OllamaStatusResponse(
            online=False, url=ollama_url, model=preferred_model,
            version=None, error=str(e)
        )


@router.post("/test")
async def test_ollama_connection(
    current_user: User = Depends(require_role("admin"))
):
    """Testar conexão com Ollama"""
    
    import os
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{ollama_url}/api/generate",
                json={
                    "model": "llama2",
                    "prompt": "Say 'Hello, I am working!' in one sentence.",
                    "stream": False
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "response": data.get("response", ""),
                    "model": data.get("model", "llama2"),
                    "total_duration": data.get("total_duration", 0)
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "detail": response.text
                }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/models")
async def list_ollama_models(
    current_user: User = Depends(get_current_active_user)
):
    """Listar modelos disponíveis no Ollama"""
    
    import os
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{ollama_url}/api/tags")
            
            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])
                
                return {
                    "success": True,
                    "models": [
                        {
                            "name": m.get("name"),
                            "size": m.get("size"),
                            "modified_at": m.get("modified_at")
                        }
                        for m in models
                    ]
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}"
                }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/auto-resolution/config", response_model=AutoResolutionConfigResponse)
async def get_auto_resolution_config(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obter configuração de auto-resolução"""
    
    config = db.query(AutoResolutionConfig).filter(
        AutoResolutionConfig.tenant_id == current_user.tenant_id
    ).first()
    
    if not config:
        # Create default config
        config = AutoResolutionConfig(
            tenant_id=current_user.tenant_id,
            auto_resolution_enabled=False,
            require_approval_for_critical=True,
            min_confidence_threshold=0.80,
            min_success_rate_threshold=0.85,
            cpu_auto_resolve=False,
            memory_auto_resolve=False,
            disk_auto_resolve=True,
            service_auto_resolve=False,
            network_auto_resolve=False,
            max_executions_per_hour=5,
            max_executions_per_day=20,
            cooldown_minutes=30
        )
        db.add(config)
        db.commit()
        db.refresh(config)
    
    return config


@router.put("/auto-resolution/config")
async def update_auto_resolution_config(
    auto_resolution_enabled: Optional[bool] = None,
    require_approval_for_critical: Optional[bool] = None,
    min_confidence_threshold: Optional[float] = None,
    min_success_rate_threshold: Optional[float] = None,
    cpu_auto_resolve: Optional[bool] = None,
    memory_auto_resolve: Optional[bool] = None,
    disk_auto_resolve: Optional[bool] = None,
    service_auto_resolve: Optional[bool] = None,
    network_auto_resolve: Optional[bool] = None,
    max_executions_per_hour: Optional[int] = None,
    max_executions_per_day: Optional[int] = None,
    cooldown_minutes: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Atualizar configuração de auto-resolução (admin only)"""
    
    config = db.query(AutoResolutionConfig).filter(
        AutoResolutionConfig.tenant_id == current_user.tenant_id
    ).first()
    
    if not config:
        config = AutoResolutionConfig(tenant_id=current_user.tenant_id)
        db.add(config)
    
    # Update fields
    if auto_resolution_enabled is not None:
        config.auto_resolution_enabled = auto_resolution_enabled
    if require_approval_for_critical is not None:
        config.require_approval_for_critical = require_approval_for_critical
    if min_confidence_threshold is not None:
        config.min_confidence_threshold = min_confidence_threshold
    if min_success_rate_threshold is not None:
        config.min_success_rate_threshold = min_success_rate_threshold
    
    if cpu_auto_resolve is not None:
        config.cpu_auto_resolve = cpu_auto_resolve
    if memory_auto_resolve is not None:
        config.memory_auto_resolve = memory_auto_resolve
    if disk_auto_resolve is not None:
        config.disk_auto_resolve = disk_auto_resolve
    if service_auto_resolve is not None:
        config.service_auto_resolve = service_auto_resolve
    if network_auto_resolve is not None:
        config.network_auto_resolve = network_auto_resolve
    
    if max_executions_per_hour is not None:
        config.max_executions_per_hour = max_executions_per_hour
    if max_executions_per_day is not None:
        config.max_executions_per_day = max_executions_per_day
    if cooldown_minutes is not None:
        config.cooldown_minutes = cooldown_minutes
    
    config.updated_at = datetime.now()
    db.commit()
    db.refresh(config)
    
    return {"message": "Configuration updated successfully", "config": config}
