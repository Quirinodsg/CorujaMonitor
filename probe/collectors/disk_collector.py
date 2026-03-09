import psutil
from typing import List, Dict, Any

class DiskCollector:
    def collect(self) -> List[Dict[str, Any]]:
        """Collect disk metrics
        
        CORRECAO 09MAR: Filtros adicionados para ignorar CD-ROM, DVD e unidades vazias
        """
        metrics = []
        
        for partition in psutil.disk_partitions():
            try:
                # Skip CD-ROM, DVD, and removable drives
                # CORRECAO 09MAR: Previne monitoramento de unidades opticas
                if 'cdrom' in partition.opts.lower() or partition.fstype == '':
                    continue
                
                # Skip if no disk in drive (common for CD/DVD drives)
                # CORRECAO 09MAR: Trata erro quando CD-ROM esta vazio
                usage = psutil.disk_usage(partition.mountpoint)
                
                # Skip drives with 0 total space (empty CD/DVD drives)
                # CORRECAO 09MAR: Ignora unidades sem espaco (CD-ROM vazio)
                if usage.total == 0:
                    continue
                
                # Create a friendly sensor name for each partition
                drive_letter = partition.device.replace(':', '').replace('\\', '')
                sensor_name = f"Disco {drive_letter}"
                
                metrics.append({
                    "type": "disk",
                    "name": sensor_name,
                    "value": usage.percent,
                    "unit": "percent",
                    "status": self._get_status(usage.percent, 85, 95),
                    "metadata": {
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "fstype": partition.fstype,
                        "total": usage.total,
                        "used": usage.used,
                        "free": usage.free
                    }
                })
            except (PermissionError, OSError):
                # Skip drives that can't be accessed (CD-ROM without disk, etc)
                continue
        
        return metrics
    
    def _get_status(self, value: float, warning: float, critical: float) -> str:
        if value >= critical:
            return "critical"
        elif value >= warning:
            return "warning"
        return "ok"
