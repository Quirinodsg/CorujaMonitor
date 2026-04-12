"""
Admin Tools Router - Ferramentas administrativas do sistema
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
import subprocess
import os
import json
import shutil

from database import get_db
from models import Tenant, User, Probe
from auth import get_current_active_user, require_role

router = APIRouter()


class MaintenanceModeRequest(BaseModel):
    enabled: bool
    message: Optional[str] = "Sistema em manutenção. Voltamos em breve."


class BackupResponse(BaseModel):
    success: bool
    backup_file: Optional[str] = None
    size_mb: Optional[float] = None
    message: str


@router.post("/maintenance-mode")
async def toggle_maintenance_mode(
    request: MaintenanceModeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """
    Ativar/desativar modo manutenção
    Cria arquivo .maintenance na raiz do projeto
    """
    try:
        maintenance_file = ".maintenance"
        
        if request.enabled:
            # Criar arquivo de manutenção
            with open(maintenance_file, 'w') as f:
                json.dump({
                    'enabled': True,
                    'message': request.message,
                    'started_at': datetime.now().isoformat(),
                    'started_by': current_user.email
                }, f)
            
            return {
                'success': True,
                'message': 'Modo manutenção ativado',
                'maintenance_mode': True
            }
        else:
            # Remover arquivo de manutenção
            if os.path.exists(maintenance_file):
                os.remove(maintenance_file)
            
            return {
                'success': True,
                'message': 'Modo manutenção desativado',
                'maintenance_mode': False
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao alterar modo manutenção: {str(e)}")


@router.get("/maintenance-mode/status")
async def get_maintenance_status():
    """Verificar status do modo manutenção"""
    maintenance_file = ".maintenance"
    
    if os.path.exists(maintenance_file):
        try:
            with open(maintenance_file, 'r') as f:
                data = json.load(f)
            return {
                'enabled': True,
                'message': data.get('message'),
                'started_at': data.get('started_at'),
                'started_by': data.get('started_by')
            }
        except:
            return {'enabled': False}
    
    return {'enabled': False}


@router.post("/reset-probes")
async def reset_all_probes(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """
    Reset de todas as probes
    Limpa last_heartbeat para forçar reconexão
    """
    try:
        probes = db.query(Probe).filter(Probe.tenant_id == current_user.tenant_id).all()
        
        reset_count = 0
        for probe in probes:
            probe.last_heartbeat = None
            reset_count += 1
        
        db.commit()
        
        return {
            'success': True,
            'message': f'{reset_count} probe(s) resetada(s) com sucesso',
            'probes_reset': reset_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao resetar probes: {str(e)}")


@router.post("/restart-system")
async def restart_system(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_role("admin"))
):
    """
    Reiniciar sistema
    Nota: Dentro do container, não podemos reiniciar outros containers
    Esta função apenas registra a solicitação
    """
    try:
        # Dentro do container, não temos acesso ao Docker host
        # Retornar mensagem informativa
        return {
            'success': True,
            'message': 'Para reiniciar o sistema, execute no host: docker-compose restart api frontend worker',
            'note': 'Esta ação deve ser executada manualmente no servidor host'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")


@router.post("/backup-database")
async def backup_database(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """
    Criar backup do banco de dados PostgreSQL
    Usa conexão direta ao invés de docker exec
    """
    try:
        # Criar diretório de backups se não existir
        backup_dir = "backups"
        os.makedirs(backup_dir, exist_ok=True)
        
        # Nome do arquivo de backup
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f"{backup_dir}/coruja_backup_{timestamp}.sql"
        
        # Usar pg_dump via subprocess com variáveis de ambiente
        # Assumindo que pg_dump está disponível no container
        env = os.environ.copy()
        env['PGPASSWORD'] = os.getenv('POSTGRES_PASSWORD', 'coruja123')
        
        result = subprocess.run(
            [
                'pg_dump',
                '-h', os.getenv('POSTGRES_HOST', 'postgres'),
                '-U', os.getenv('POSTGRES_USER', 'coruja'),
                '-d', os.getenv('POSTGRES_DB', 'coruja_db'),
                '-f', backup_file
            ],
            env=env,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            # Calcular tamanho
            size_bytes = os.path.getsize(backup_file)
            size_mb = size_bytes / (1024 * 1024)
            
            return {
                'success': True,
                'message': 'Backup criado com sucesso',
                'backup_file': backup_file,
                'size_mb': round(size_mb, 2),
                'timestamp': timestamp
            }
        else:
            raise Exception(f"pg_dump falhou: {result.stderr}")
            
    except FileNotFoundError:
        # pg_dump não está disponível no container
        raise HTTPException(
            status_code=500, 
            detail="pg_dump não disponível. Instale postgresql-client no container ou use backup manual."
        )
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="Timeout ao criar backup (>5min)")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar backup: {str(e)}")


@router.get("/backups")
async def list_backups(
    current_user: User = Depends(require_role("admin"))
):
    """Listar backups disponíveis"""
    try:
        backup_dir = "backups"
        
        if not os.path.exists(backup_dir):
            return {'backups': []}
        
        backups = []
        for filename in os.listdir(backup_dir):
            if filename.endswith('.sql'):
                filepath = os.path.join(backup_dir, filename)
                size_bytes = os.path.getsize(filepath)
                size_mb = size_bytes / (1024 * 1024)
                mtime = os.path.getmtime(filepath)
                
                backups.append({
                    'filename': filename,
                    'size_mb': round(size_mb, 2),
                    'created_at': datetime.fromtimestamp(mtime).isoformat()
                })
        
        # Ordenar por data (mais recente primeiro)
        backups.sort(key=lambda x: x['created_at'], reverse=True)
        
        return {'backups': backups}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar backups: {str(e)}")


@router.post("/clear-cache")
async def clear_cache(
    current_user: User = Depends(require_role("admin"))
):
    """
    Limpar cache do Redis
    """
    try:
        # Usar redis-py ao invés de subprocess
        import redis
        
        # Conectar ao Redis (mesmo host que a aplicação usa)
        r = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)
        
        # Executar FLUSHDB
        r.flushdb()
        
        return {
            'success': True,
            'message': 'Cache limpo com sucesso',
            'redis_response': 'OK'
        }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao limpar cache: {str(e)}")


@router.get("/logs")
async def get_system_logs(
    service: str = "api",
    lines: int = 100,
    current_user: User = Depends(require_role("admin"))
):
    """
    Obter logs do sistema
    Lê arquivos de log locais ao invés de usar docker logs
    """
    try:
        # Mapear serviços para arquivos de log
        log_files = {
            'api': '/app/logs/api.log',
            'worker': '/app/logs/worker.log',
        }
        
        # Para API, podemos ler o log local
        if service == 'api':
            log_file = 'logs/api.log'
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    all_lines = f.readlines()
                    logs = ''.join(all_lines[-lines:])
            else:
                logs = "Log file not found. Logs may not be configured."
        else:
            # Para outros serviços, retornar mensagem
            logs = f"Logs do serviço {service} não disponíveis via API.\nUse: docker logs coruja-{service}"
        
        return {
            'success': True,
            'service': service,
            'lines': lines,
            'logs': logs
        }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter logs: {str(e)}")


@router.get("/system-status")
async def get_system_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """
    Obter status geral do sistema
    Verifica conexões com serviços ao invés de usar docker
    """
    try:
        services_status = []
        
        # Verificar PostgreSQL
        try:
            db.execute("SELECT 1")
            services_status.append({
                'name': 'PostgreSQL',
                'service': 'postgres',
                'state': 'running',
                'status': 'healthy'
            })
        except:
            services_status.append({
                'name': 'PostgreSQL',
                'service': 'postgres',
                'state': 'unknown',
                'status': 'unhealthy'
            })
        
        # Verificar Redis
        try:
            import redis
            r = redis.Redis(host='redis', port=6379, db=0, socket_connect_timeout=2)
            r.ping()
            services_status.append({
                'name': 'Redis',
                'service': 'redis',
                'state': 'running',
                'status': 'healthy'
            })
        except:
            services_status.append({
                'name': 'Redis',
                'service': 'redis',
                'state': 'unknown',
                'status': 'unhealthy'
            })
        
        # API está rodando (óbvio, já que estamos aqui)
        services_status.append({
            'name': 'API',
            'service': 'api',
            'state': 'running',
            'status': 'healthy'
        })
        
        # Verificar modo manutenção
        maintenance_mode = os.path.exists('.maintenance')
        
        return {
            'success': True,
            'containers': services_status,
            'maintenance_mode': maintenance_mode,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter status: {str(e)}")


@router.get("/disk-usage")
async def get_disk_usage(
    current_user: User = Depends(require_role("admin"))
):
    """
    Obter uso de disco do sistema
    """
    try:
        # Uso de disco total
        total, used, free = shutil.disk_usage("/")
        
        # Tamanho dos backups
        backup_size = 0
        backup_dir = "backups"
        if os.path.exists(backup_dir):
            for filename in os.listdir(backup_dir):
                filepath = os.path.join(backup_dir, filename)
                if os.path.isfile(filepath):
                    backup_size += os.path.getsize(filepath)
        
        return {
            'success': True,
            'disk': {
                'total_gb': round(total / (1024**3), 2),
                'used_gb': round(used / (1024**3), 2),
                'free_gb': round(free / (1024**3), 2),
                'used_percent': round((used / total) * 100, 2)
            },
            'backups_mb': round(backup_size / (1024**2), 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter uso de disco: {str(e)}")


@router.post("/force-redispatch-datacenter")
async def force_redispatch_datacenter(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """
    Força re-dispatch completo (SMS + WhatsApp + phone_call) para incidentes
    abertos de sensores de datacenter (Nobreak/Ar-condicionado).
    Limpa o cooldown Redis para permitir re-notificação imediata.
    """
    from models import Incident, Sensor
    import redis as redis_lib

    # Limpar cooldowns Redis dos incidentes abertos de datacenter
    try:
        r = redis_lib.Redis.from_url("redis://redis:6379", decode_responses=True, socket_connect_timeout=2)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Redis indisponível: {e}")

    datacenter_keywords = ('nobreak', 'engetron', 'ups', 'ar-condicionado', 'ar condicionado', 'conflex', 'hvac')

    open_incidents = db.query(Incident).filter(
        Incident.status.in_(['open', 'acknowledged'])
    ).all()

    dispatched = []
    for incident in open_incidents:
        sensor = db.query(Sensor).filter(Sensor.id == incident.sensor_id).first()
        if not sensor:
            continue
        name_lower = (sensor.name or '').lower()
        if not any(kw in name_lower for kw in datacenter_keywords):
            continue

        # Limpar cooldown para forçar re-notificação
        try:
            r.delete(f"notified:{incident.id}")
        except Exception:
            pass

        dispatched.append({
            'incident_id': incident.id,
            'sensor_name': sensor.name,
            'severity': incident.severity,
        })

    return {
        'success': True,
        'message': f'{len(dispatched)} incidentes de datacenter marcados para re-dispatch',
        'incidents': dispatched,
        'note': 'O worker vai re-notificar via SMS/WhatsApp/phone_call no próximo ciclo (até 1 minuto)'
    }
