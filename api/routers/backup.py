from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
import subprocess
import os
from datetime import datetime
from pathlib import Path

from database import get_db
from models import User
from auth import get_current_active_user
from config import settings

router = APIRouter()

BACKUP_DIR = Path("/app/backups")
BACKUP_DIR.mkdir(exist_ok=True)

@router.get("/list")
async def list_backups(current_user: User = Depends(get_current_active_user)):
    """Lista todos os backups disponíveis"""
    try:
        backups = []
        if BACKUP_DIR.exists():
            for backup_file in sorted(BACKUP_DIR.glob("*.sql"), reverse=True):
                stat = backup_file.stat()
                backups.append({
                    "filename": backup_file.name,
                    "size": stat.st_size,
                    "size_mb": round(stat.st_size / (1024 * 1024), 2),
                    "created_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "path": str(backup_file)
                })
        
        return {
            "backups": backups,
            "total": len(backups)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar backups: {str(e)}")

@router.post("/create")
async def create_backup(current_user: User = Depends(get_current_active_user)):
    """Cria um novo backup do banco de dados"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"coruja_backup_{timestamp}.sql"
        backup_path = BACKUP_DIR / backup_filename
        
        # Executar pg_dump
        cmd = [
            "pg_dump",
            "-h", settings.POSTGRES_HOST,
            "-U", settings.POSTGRES_USER,
            "-d", settings.POSTGRES_DB,
            "-f", str(backup_path)
        ]
        
        env = os.environ.copy()
        env["PGPASSWORD"] = settings.POSTGRES_PASSWORD
        
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception(f"pg_dump falhou: {result.stderr}")
        
        # Verificar se arquivo foi criado
        if not backup_path.exists():
            raise Exception("Arquivo de backup não foi criado")
        
        stat = backup_path.stat()
        
        return {
            "success": True,
            "message": f"✅ Backup criado com sucesso!",
            "backup": {
                "filename": backup_filename,
                "size": stat.st_size,
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "created_at": datetime.fromtimestamp(stat.st_mtime).isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar backup: {str(e)}")

@router.post("/restore/{filename}")
async def restore_backup(
    filename: str,
    current_user: User = Depends(get_current_active_user)
):
    """Restaura um backup do banco de dados"""
    try:
        backup_path = BACKUP_DIR / filename
        
        if not backup_path.exists():
            raise HTTPException(status_code=404, detail="Backup não encontrado")
        
        # Dropar e recriar schema
        drop_cmd = [
            "psql",
            "-h", settings.POSTGRES_HOST,
            "-U", settings.POSTGRES_USER,
            "-d", settings.POSTGRES_DB,
            "-c", "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
        ]
        
        env = os.environ.copy()
        env["PGPASSWORD"] = settings.POSTGRES_PASSWORD
        
        result = subprocess.run(drop_cmd, env=env, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception(f"Falha ao dropar schema: {result.stderr}")
        
        # Restaurar backup
        restore_cmd = [
            "psql",
            "-h", settings.POSTGRES_HOST,
            "-U", settings.POSTGRES_USER,
            "-d", settings.POSTGRES_DB,
            "-f", str(backup_path)
        ]
        
        result = subprocess.run(restore_cmd, env=env, capture_output=True, text=True)
        
        if result.returncode != 0:
            # Mesmo com warnings, pode ter sucesso
            if "ERROR" in result.stderr:
                raise Exception(f"Falha ao restaurar: {result.stderr}")
        
        return {
            "success": True,
            "message": f"✅ Backup restaurado com sucesso!",
            "filename": filename
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao restaurar backup: {str(e)}")

@router.get("/download/{filename}")
async def download_backup(
    filename: str,
    current_user: User = Depends(get_current_active_user)
):
    """Faz download de um backup"""
    try:
        backup_path = BACKUP_DIR / filename
        
        if not backup_path.exists():
            raise HTTPException(status_code=404, detail="Backup não encontrado")
        
        return FileResponse(
            path=str(backup_path),
            filename=filename,
            media_type="application/sql"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao baixar backup: {str(e)}")

@router.delete("/delete/{filename}")
async def delete_backup(
    filename: str,
    current_user: User = Depends(get_current_active_user)
):
    """Deleta um backup"""
    try:
        backup_path = BACKUP_DIR / filename
        
        if not backup_path.exists():
            raise HTTPException(status_code=404, detail="Backup não encontrado")
        
        backup_path.unlink()
        
        return {
            "success": True,
            "message": f"✅ Backup deletado com sucesso!",
            "filename": filename
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao deletar backup: {str(e)}")
