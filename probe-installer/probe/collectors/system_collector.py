import psutil
import socket
import httpx
from datetime import datetime
from typing import List, Dict, Any

class SystemCollector:
    def collect(self) -> List[Dict[str, Any]]:
        """Collect system information"""
        metrics = []
        
        # Get uptime
        boot_time = psutil.boot_time()
        uptime_seconds = datetime.now().timestamp() - boot_time
        uptime_days = uptime_seconds / 86400
        
        # Get IP addresses
        try:
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
        except:
            ip_address = "unknown"
        
        # Get public IP
        public_ip = "unknown"
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get('https://api.ipify.org?format=text')
                if response.status_code == 200:
                    public_ip = response.text.strip()
        except:
            pass
        
        metrics.append({
            "type": "system",
            "name": "Uptime",
            "value": uptime_days,
            "unit": "days",
            "status": "ok",
            "metadata": {
                "boot_time": datetime.fromtimestamp(boot_time).isoformat(),
                "uptime_seconds": uptime_seconds,
                "ip_address": ip_address,
                "public_ip": public_ip,
                "hostname": hostname
            }
        })
        
        return metrics
