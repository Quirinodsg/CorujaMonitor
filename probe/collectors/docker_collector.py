"""
Docker Collector - Monitora containers Docker
"""
import logging
import subprocess
import json
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class DockerCollector:
    """Coleta métricas de containers Docker"""
    
    def __init__(self):
        self.name = "docker"
        self.sensor_type = "docker"
        
    def collect(self) -> List[Dict[str, Any]]:
        """Coleta métricas de todos os containers Docker"""
        metrics = []
        
        try:
            # Verifica se Docker está disponível
            if not self._is_docker_available():
                logger.warning("Docker não está disponível ou não está rodando")
                return metrics
            
            # Coleta informações dos containers
            containers = self._get_containers()
            
            if not containers:
                logger.debug("Nenhum container Docker encontrado")
                return metrics
            
            # Métricas gerais do Docker
            total_containers = len(containers)
            running_containers = sum(1 for c in containers if c['state'] == 'running')
            stopped_containers = total_containers - running_containers
            
            # Métrica: Total de containers
            metrics.append({
                'sensor_type': 'docker',
                'name': 'Docker Containers Total',
                'value': total_containers,
                'unit': 'containers',
                'status': 'ok'
            })
            
            # Métrica: Containers rodando
            metrics.append({
                'sensor_type': 'docker',
                'name': 'Docker Containers Running',
                'value': running_containers,
                'unit': 'containers',
                'status': 'ok' if running_containers > 0 else 'warning'
            })
            
            # Métrica: Containers parados
            metrics.append({
                'sensor_type': 'docker',
                'name': 'Docker Containers Stopped',
                'value': stopped_containers,
                'unit': 'containers',
                'status': 'ok' if stopped_containers == 0 else 'warning'
            })
            
            # Métricas individuais por container (top 10 containers rodando)
            running = [c for c in containers if c['state'] == 'running'][:10]
            for container in running:
                # Status do container
                metrics.append({
                    'sensor_type': 'docker',
                    'name': f"Docker {container['name']}",
                    'value': 1 if container['state'] == 'running' else 0,
                    'unit': 'status',
                    'status': 'ok' if container['state'] == 'running' else 'critical',
                    'metadata': {
                        'container_id': container['id'],
                        'image': container['image'],
                        'state': container['state'],
                        'status': container['status']
                    }
                })
                
                # CPU usage (se disponível)
                stats = self._get_container_stats(container['id'])
                if stats:
                    cpu_percent = stats.get('cpu_percent', 0)
                    memory_percent = stats.get('memory_percent', 0)
                    
                    metrics.append({
                        'sensor_type': 'docker',
                        'name': f"Docker {container['name']} CPU",
                        'value': cpu_percent,
                        'unit': 'percent',
                        'status': self._get_status(cpu_percent, 80, 95)
                    })
                    
                    metrics.append({
                        'sensor_type': 'docker',
                        'name': f"Docker {container['name']} Memory",
                        'value': memory_percent,
                        'unit': 'percent',
                        'status': self._get_status(memory_percent, 80, 95)
                    })
            
            logger.info(f"Coletadas {len(metrics)} métricas Docker")
            
        except Exception as e:
            logger.error(f"Erro ao coletar métricas Docker: {e}")
        
        return metrics
    
    def _is_docker_available(self) -> bool:
        """Verifica se Docker está disponível"""
        try:
            result = subprocess.run(
                ['docker', 'version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception as e:
            logger.debug(f"Docker não disponível: {e}")
            return False
    
    def _get_containers(self) -> List[Dict[str, Any]]:
        """Lista todos os containers Docker"""
        try:
            result = subprocess.run(
                ['docker', 'ps', '-a', '--format', '{{json .}}'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                logger.error(f"Erro ao listar containers: {result.stderr}")
                return []
            
            containers = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    try:
                        container_data = json.loads(line)
                        containers.append({
                            'id': container_data.get('ID', ''),
                            'name': container_data.get('Names', ''),
                            'image': container_data.get('Image', ''),
                            'state': container_data.get('State', ''),
                            'status': container_data.get('Status', '')
                        })
                    except json.JSONDecodeError:
                        logger.warning(f"Erro ao parsear linha: {line}")
            
            return containers
            
        except Exception as e:
            logger.error(f"Erro ao obter containers: {e}")
            return []
    
    def _get_container_stats(self, container_id: str) -> Dict[str, float]:
        """Obtém estatísticas de uso de um container"""
        try:
            result = subprocess.run(
                ['docker', 'stats', container_id, '--no-stream', '--format', '{{json .}}'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                return {}
            
            stats_data = json.loads(result.stdout.strip())
            
            # Parse CPU percentage (remove %)
            cpu_str = stats_data.get('CPUPerc', '0%').replace('%', '')
            cpu_percent = float(cpu_str) if cpu_str else 0
            
            # Parse Memory percentage (remove %)
            mem_str = stats_data.get('MemPerc', '0%').replace('%', '')
            memory_percent = float(mem_str) if mem_str else 0
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent
            }
            
        except Exception as e:
            logger.debug(f"Erro ao obter stats do container {container_id}: {e}")
            return {}
    
    def _get_status(self, value: float, warning_threshold: float, critical_threshold: float) -> str:
        """Determina o status baseado nos thresholds"""
        if value >= critical_threshold:
            return 'critical'
        elif value >= warning_threshold:
            return 'warning'
        else:
            return 'ok'
