import psutil
from typing import List, Dict, Any

class CPUCollector:
    def collect(self) -> List[Dict[str, Any]]:
        """Collect CPU metrics"""
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        metrics = [
            {
                "type": "cpu",
                "name": "CPU",
                "value": cpu_percent,
                "unit": "percent",
                "status": self._get_status(cpu_percent, 80, 95),
                "metadata": {
                    "cpu_count": cpu_count,
                    "per_cpu": psutil.cpu_percent(percpu=True)
                }
            }
        ]
        
        return metrics
    
    def _get_status(self, value: float, warning: float, critical: float) -> str:
        if value >= critical:
            return "critical"
        elif value >= warning:
            return "warning"
        return "ok"
