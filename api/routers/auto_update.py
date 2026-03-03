"""
Sistema de Atualização Automática
Verifica, baixa e aplica atualizações do GitHub
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
import requests
import semver
import subprocess
import os
import zipfile
import shutil
from datetime import datetime
from typing import Optional
import logging

router = APIRouter(prefix="/api/updates", tags=["updates"])
logger = logging.getLogger(__name__)

# Configurações
GITHUB_REPO = os.getenv("GITHUB_REPO", "seu-usuario/coruja-monitoring")
CURRENT_VERSION_FILE = "version.txt"
UPDATE_DIR = "updates"
BACKUP_DIR = "backups"

class UpdateInfo(BaseModel):
    update_available: bool
    current_version: str
    latest_version: Optional[str] = None
    changelog: Optional[str] = None
    download_url: Optional[str] = None
    published_at: Optional[str] = None
    release_name: Optional[str] = None

class DownloadRequest(BaseModel):
    download_url: str
    version: str

def get_current_version() -> str:
    """Lê a versão atual do arquivo version.txt"""
    try:
        if os.path.exists(CURRENT_VERSION_FILE):
            with open(CURRENT_VERSION_FILE, 'r') as f:
                return f.read().strip()
        return "1.0.0"  # Versão padrão
    except Exception as e:
        logger.error(f"Erro ao ler versão atual: {e}")
        return "1.0.0"

def save_current_version(version: str):
    """Salva a nova versão no arquivo"""
    try:
        with open(CURRENT_VERSION_FILE, 'w') as f:
            f.write(version)
    except Exception as e:
        logger.error(f"Erro ao salvar versão: {e}")

@router.get("/check", response_model=UpdateInfo)
async def check_updates():
    """
    Verifica se há atualizações disponíveis no GitHub
    """
    try:
        current_version = get_current_version()
        
        # Buscar última release no GitHub
        response = requests.get(
            f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest",
            headers={"Accept": "application/vnd.github.v3+json"},
            timeout=10
        )
        
        if response.status_code == 404:
            return UpdateInfo(
                update_available=False,
                current_version=current_version,
                changelog="Nenhuma release encontrada no repositório"
            )
        
        response.raise_for_status()
        latest = response.json()
        
        # Extrair versão (remover 'v' se presente)
        latest_version = latest["tag_name"].lstrip("v")
        
        # Comparar versões usando semver
        try:
            current = semver.VersionInfo.parse(current_version)
            remote = semver.VersionInfo.parse(latest_version)
            update_available = remote > current
        except ValueError:
            # Fallback para comparação simples se não for semver válido
            update_available = latest_version != current_version
        
        # Encontrar asset para download (procurar .zip)
        download_url = None
        for asset in latest.get("assets", []):
            if asset["name"].endswith(".zip"):
                download_url = asset["browser_download_url"]
                break
        
        return UpdateInfo(
            update_available=update_available,
            current_version=current_version,
            latest_version=latest_version,
            changelog=latest.get("body", "Sem changelog disponível"),
            download_url=download_url,
            published_at=latest.get("published_at"),
            release_name=latest.get("name", f"Release {latest_version}")
        )
        
    except requests.RequestException as e:
        logger.error(f"Erro ao verificar atualizações: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Não foi possível conectar ao GitHub: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Erro inesperado ao verificar atualizações: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao verificar atualizações: {str(e)}"
        )

@router.post("/download")
async def download_update(request: DownloadRequest):
    """
    Baixa a atualização do GitHub
    """
    try:
        # Criar diretório de updates
        os.makedirs(UPDATE_DIR, exist_ok=True)
        
        update_file = os.path.join(UPDATE_DIR, f"coruja-update-{request.version}.zip")
        
        # Baixar arquivo
        logger.info(f"Baixando atualização de: {request.download_url}")
        response = requests.get(request.download_url, stream=True, timeout=300)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(update_file, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
        
        file_size = os.path.getsize(update_file)
        logger.info(f"Download concluído: {file_size} bytes")
        
        return {
            "status": "downloaded",
            "file": update_file,
            "size": file_size,
            "version": request.version
        }
        
    except requests.RequestException as e:
        logger.error(f"Erro ao baixar atualização: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Erro ao baixar atualização: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Erro inesperado ao baixar: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao baixar atualização: {str(e)}"
        )

def backup_current_version():
    """Cria backup da versão atual"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(BACKUP_DIR, f"backup_{timestamp}")
        os.makedirs(backup_path, exist_ok=True)
        
        # Backup de diretórios críticos
        dirs_to_backup = ["api", "probe", "frontend", "ai-agent"]
        
        for dir_name in dirs_to_backup:
            if os.path.exists(dir_name):
                dest = os.path.join(backup_path, dir_name)
                shutil.copytree(dir_name, dest, ignore=shutil.ignore_patterns('__pycache__', '*.pyc', 'node_modules'))
                logger.info(f"Backup criado: {dest}")
        
        # Backup de arquivos importantes
        files_to_backup = [".env", "version.txt", "docker-compose.yml"]
        for file_name in files_to_backup:
            if os.path.exists(file_name):
                shutil.copy2(file_name, backup_path)
        
        return backup_path
        
    except Exception as e:
        logger.error(f"Erro ao criar backup: {e}")
        raise

def extract_update(update_file: str):
    """Extrai arquivos da atualização"""
    try:
        logger.info(f"Extraindo atualização: {update_file}")
        
        with zipfile.ZipFile(update_file, 'r') as zip_ref:
            # Extrair para diretório temporário
            temp_dir = os.path.join(UPDATE_DIR, "temp")
            os.makedirs(temp_dir, exist_ok=True)
            zip_ref.extractall(temp_dir)
        
        return temp_dir
        
    except Exception as e:
        logger.error(f"Erro ao extrair atualização: {e}")
        raise

def apply_update_files(temp_dir: str):
    """Aplica os arquivos da atualização"""
    try:
        # Copiar arquivos novos
        for item in os.listdir(temp_dir):
            source = os.path.join(temp_dir, item)
            dest = item
            
            if os.path.isdir(source):
                if os.path.exists(dest):
                    shutil.rmtree(dest)
                shutil.copytree(source, dest)
                logger.info(f"Diretório atualizado: {dest}")
            else:
                shutil.copy2(source, dest)
                logger.info(f"Arquivo atualizado: {dest}")
        
    except Exception as e:
        logger.error(f"Erro ao aplicar arquivos: {e}")
        raise

@router.post("/apply")
async def apply_update(background_tasks: BackgroundTasks, version: str):
    """
    Aplica a atualização e reinicia o sistema
    """
    try:
        update_file = os.path.join(UPDATE_DIR, f"coruja-update-{version}.zip")
        
        if not os.path.exists(update_file):
            raise HTTPException(
                status_code=404,
                detail="Arquivo de atualização não encontrado. Execute o download primeiro."
            )
        
        # 1. Criar backup
        logger.info("Criando backup da versão atual...")
        backup_path = backup_current_version()
        
        # 2. Extrair atualização
        logger.info("Extraindo arquivos da atualização...")
        temp_dir = extract_update(update_file)
        
        # 3. Aplicar arquivos
        logger.info("Aplicando atualização...")
        apply_update_files(temp_dir)
        
        # 4. Atualizar versão
        save_current_version(version)
        
        # 5. Limpar arquivos temporários
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        # 6. Agendar reinício
        logger.info("Agendando reinício do sistema...")
        
        # Executar script de reinício em background
        if os.name == 'nt':  # Windows
            background_tasks.add_task(
                subprocess.Popen,
                ["powershell", "-File", "update_and_restart.ps1"],
                shell=True
            )
        else:  # Linux/Mac
            background_tasks.add_task(
                subprocess.Popen,
                ["bash", "update_and_restart.sh"],
                shell=False
            )
        
        return {
            "status": "success",
            "message": "Atualização aplicada com sucesso. Sistema será reiniciado em 5 segundos.",
            "backup_path": backup_path,
            "new_version": version
        }
        
    except Exception as e:
        logger.error(f"Erro ao aplicar atualização: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao aplicar atualização: {str(e)}"
        )

@router.get("/history")
async def get_update_history():
    """
    Retorna histórico de backups/atualizações
    """
    try:
        if not os.path.exists(BACKUP_DIR):
            return {"backups": []}
        
        backups = []
        for backup_name in os.listdir(BACKUP_DIR):
            backup_path = os.path.join(BACKUP_DIR, backup_name)
            if os.path.isdir(backup_path):
                stat = os.stat(backup_path)
                backups.append({
                    "name": backup_name,
                    "path": backup_path,
                    "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "size": sum(
                        os.path.getsize(os.path.join(dirpath, filename))
                        for dirpath, _, filenames in os.walk(backup_path)
                        for filename in filenames
                    )
                })
        
        # Ordenar por data (mais recente primeiro)
        backups.sort(key=lambda x: x["created_at"], reverse=True)
        
        return {"backups": backups}
        
    except Exception as e:
        logger.error(f"Erro ao listar backups: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao listar histórico: {str(e)}"
        )

@router.post("/rollback")
async def rollback_update(backup_name: str):
    """
    Reverte para um backup anterior
    """
    try:
        backup_path = os.path.join(BACKUP_DIR, backup_name)
        
        if not os.path.exists(backup_path):
            raise HTTPException(
                status_code=404,
                detail="Backup não encontrado"
            )
        
        # Criar backup da versão atual antes de reverter
        logger.info("Criando backup de segurança antes do rollback...")
        safety_backup = backup_current_version()
        
        # Restaurar arquivos do backup
        logger.info(f"Restaurando backup: {backup_name}")
        
        for item in os.listdir(backup_path):
            source = os.path.join(backup_path, item)
            dest = item
            
            if os.path.isdir(source):
                if os.path.exists(dest):
                    shutil.rmtree(dest)
                shutil.copytree(source, dest)
            else:
                shutil.copy2(source, dest)
        
        return {
            "status": "success",
            "message": f"Sistema revertido para backup: {backup_name}",
            "safety_backup": safety_backup
        }
        
    except Exception as e:
        logger.error(f"Erro ao reverter atualização: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao reverter: {str(e)}"
        )
