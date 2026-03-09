import psutil
from typing import List, Dict, Any

class DiskCollector:
    def collect(self) -> List[Dict[str, Any]]:
        """Collect disk metrics"""
        metrics = []
        
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                
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
            except PermissionError:
                continue
        
        return metrics
    
    def _get_status(self, value: float, warning: float, critical: float) -> str:
        if value >= critical:
            return "critical"
        elif value >= warning:
            return "warning"
        return "ok"
