import psutil
from typing import List, Dict, Any
import subprocess

class ServiceCollector:
    def __init__(self, monitored_services: List[str]):
        self.monitored_services = monitored_services
    
    def collect(self) -> List[Dict[str, Any]]:
        """Collect Windows service status"""
        metrics = []
        
        for service_name in self.monitored_services:
            try:
                status = self._get_service_status(service_name)
                
                metrics.append({
                    "type": "service",
                    "name": f"service_{service_name}",
                    "value": 1 if status == "running" else 0,
                    "unit": "status",
                    "status": "ok" if status == "running" else "critical",
                    "metadata": {
                        "service_name": service_name,
                        "service_status": status
                    }
                })
            except Exception as e:
                metrics.append({
                    "type": "service",
                    "name": f"service_{service_name}",
                    "value": 0,
                    "unit": "status",
                    "status": "critical",
                    "metadata": {
                        "service_name": service_name,
                        "error": str(e)
                    }
                })
        
        return metrics
    
    def _get_service_status(self, service_name: str) -> str:
        """Get Windows service status using sc query"""
        try:
            result = subprocess.run(
                ['sc', 'query', service_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if 'RUNNING' in result.stdout:
                return 'running'
            elif 'STOPPED' in result.stdout:
                return 'stopped'
            else:
                return 'unknown'
        except Exception:
            return 'unknown'
    
    def restart_service(self, service_name: str) -> bool:
        """Attempt to restart a Windows service"""
        try:
            subprocess.run(['net', 'stop', service_name], timeout=30, check=True)
            subprocess.run(['net', 'start', service_name], timeout=30, check=True)
            return True
        except Exception:
            return False
