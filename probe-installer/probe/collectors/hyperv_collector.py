from typing import List, Dict, Any
import subprocess

class HyperVCollector:
    def collect(self) -> List[Dict[str, Any]]:
        """Collect Hyper-V metrics"""
        metrics = []
        
        try:
            # Check if Hyper-V is available
            vms = self._get_vms()
            
            for vm in vms:
                metrics.append({
                    "type": "hyperv",
                    "name": f"vm_{vm['name']}",
                    "value": 1 if vm['state'] == 'Running' else 0,
                    "unit": "status",
                    "status": "ok" if vm['state'] == 'Running' else "warning",
                    "metadata": {
                        "vm_name": vm['name'],
                        "vm_state": vm['state']
                    }
                })
        except Exception as e:
            # Hyper-V not available or error
            pass
        
        return metrics
    
    def _get_vms(self) -> List[Dict[str, str]]:
        """Get list of Hyper-V VMs using PowerShell"""
        try:
            result = subprocess.run(
                ['powershell', '-Command', 'Get-VM | Select-Object Name, State | ConvertTo-Json'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                import json
                vms_data = json.loads(result.stdout)
                if isinstance(vms_data, dict):
                    vms_data = [vms_data]
                return [{'name': vm['Name'], 'state': vm['State']} for vm in vms_data]
        except Exception:
            pass
        
        return []
