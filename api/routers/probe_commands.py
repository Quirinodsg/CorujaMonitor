from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import httpx
import logging

from database import get_db
from models import Server, User, Probe
from auth import get_current_active_user

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/services/{server_id}")
async def discover_services(
    server_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Discover Windows services on a server in real-time
    Uses PowerShell for local server, WMI for remote servers
    """
    logger.info(f"[DISCOVERY] Starting service discovery for server_id={server_id}, user={current_user.email}")
    
    # Get server
    server = db.query(Server).filter(
        Server.id == server_id,
        Server.tenant_id == current_user.tenant_id
    ).first()
    
    if not server:
        logger.error(f"[DISCOVERY] Server {server_id} not found for tenant {current_user.tenant_id}")
        raise HTTPException(status_code=404, detail=f"Server with ID {server_id} not found")
    
    logger.info(f"[DISCOVERY] Found server: {server.hostname} (ID: {server.id}, IP: {server.ip_address})")
    
    # For local server (where API is running), use PowerShell
    import socket
    import json as json_lib
    local_hostname = socket.gethostname().lower()
    
    logger.info(f"[DISCOVERY] Local hostname: {local_hostname}, Server hostname: {server.hostname.lower()}")
    
    if server.hostname.lower() == local_hostname or server.ip_address in ["127.0.0.1", "localhost"]:
        try:
            logger.info(f"[DISCOVERY] Discovering services on local server: {server.hostname}")
            
            # Use PowerShell to get all services
            import subprocess
            cmd = [
                'powershell',
                '-Command',
                'Get-Service | Select-Object Name, DisplayName, Status, StartType | ConvertTo-Json'
            ]
            
            logger.info(f"[DISCOVERY] Executing PowerShell command...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            logger.info(f"[DISCOVERY] PowerShell return code: {result.returncode}")
            
            if result.returncode == 0 and result.stdout.strip():
                logger.info(f"[DISCOVERY] PowerShell output length: {len(result.stdout)} chars")
                
                services_data = json_lib.loads(result.stdout)
                
                # Handle single service (not array)
                if isinstance(services_data, dict):
                    services_data = [services_data]
                
                logger.info(f"[DISCOVERY] Parsed {len(services_data)} services from PowerShell")
                
                services = []
                for svc in services_data:
                    try:
                        services.append({
                            "name": svc.get("Name", ""),
                            "display_name": svc.get("DisplayName", svc.get("Name", "")),
                            "status": str(svc.get("Status", "Unknown")).lower(),
                            "start_type": str(svc.get("StartType", "Unknown")).lower()
                        })
                    except Exception as e:
                        logger.error(f"[DISCOVERY] Error parsing service: {e}")
                        continue
                
                # Sort by display name
                services.sort(key=lambda x: x['display_name'].lower())
                
                logger.info(f"[DISCOVERY] Successfully discovered {len(services)} services on {server.hostname}")
                
                return {
                    "server_id": server_id,
                    "hostname": server.hostname,
                    "services": services,
                    "count": len(services),
                    "method": "powershell_local"
                }
            else:
                logger.error(f"[DISCOVERY] PowerShell command failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            logger.error("[DISCOVERY] Timeout getting services via PowerShell (30s)")
        except Exception as e:
            logger.error(f"[DISCOVERY] Error getting local services: {e}", exc_info=True)
    else:
        logger.info(f"[DISCOVERY] Server {server.hostname} is not local, would need WMI/remote access")
    
    # Fallback to common services list
    logger.warning(f"[DISCOVERY] Using fallback service list for server {server_id}")
    return {
        "server_id": server_id,
        "hostname": server.hostname,
        "services": [
            {"name": "W3SVC", "display_name": "IIS Web Server", "status": "unknown", "start_type": "auto"},
            {"name": "MSSQLSERVER", "display_name": "SQL Server (MSSQLSERVER)", "status": "unknown", "start_type": "auto"},
            {"name": "MySQL", "display_name": "MySQL Server", "status": "unknown", "start_type": "auto"},
            {"name": "Spooler", "display_name": "Print Spooler", "status": "unknown", "start_type": "auto"},
            {"name": "EventLog", "display_name": "Windows Event Log", "status": "unknown", "start_type": "auto"},
            {"name": "WinRM", "display_name": "Windows Remote Management", "status": "unknown", "start_type": "auto"},
            {"name": "TermService", "display_name": "Remote Desktop Services", "status": "unknown", "start_type": "auto"},
            {"name": "Dnscache", "display_name": "DNS Client", "status": "unknown", "start_type": "auto"},
            {"name": "Dhcp", "display_name": "DHCP Client", "status": "unknown", "start_type": "auto"},
            {"name": "LanmanServer", "display_name": "Server", "status": "unknown", "start_type": "auto"},
        ],
        "note": "Using fallback list. Configure WMI or ensure server is local for real-time discovery.",
        "method": "fallback"
    }


@router.get("/disks/{server_id}")
async def discover_disks(
    server_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Discover disk drives on a server in real-time
    Uses PowerShell for local server, WMI for remote servers
    """
    # Get server
    server = db.query(Server).filter(
        Server.id == server_id,
        Server.tenant_id == current_user.tenant_id
    ).first()
    
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    # For local server, use PowerShell
    import socket
    import json as json_lib
    local_hostname = socket.gethostname().lower()
    
    if server.hostname.lower() == local_hostname or server.ip_address in ["127.0.0.1", "localhost"]:
        try:
            logger.info(f"Discovering disks on local server: {server.hostname}")
            
            # Use PowerShell to get all logical disks
            import subprocess
            cmd = [
                'powershell',
                '-Command',
                'Get-WmiObject Win32_LogicalDisk -Filter "DriveType=3" | Select-Object DeviceID, VolumeName, Size, FreeSpace | ConvertTo-Json'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0 and result.stdout.strip():
                disks_data = json_lib.loads(result.stdout)
                
                # Handle single disk (not array)
                if isinstance(disks_data, dict):
                    disks_data = [disks_data]
                
                disks = []
                for disk in disks_data:
                    try:
                        device_id = disk.get("DeviceID", "")
                        volume_name = disk.get("VolumeName", "")
                        size = float(disk.get("Size", 0))
                        free_space = float(disk.get("FreeSpace", 0))
                        
                        if size == 0:
                            continue
                        
                        used = size - free_space
                        percent_used = (used / size) * 100
                        
                        display_name = f"{volume_name} ({device_id})" if volume_name else f"Disco Local ({device_id})"
                        
                        disks.append({
                            "name": device_id,
                            "display_name": display_name,
                            "total_gb": round(size / (1024**3), 2),
                            "used_gb": round(used / (1024**3), 2),
                            "free_gb": round(free_space / (1024**3), 2),
                            "percent_used": round(percent_used, 1)
                        })
                    except Exception as e:
                        logger.error(f"Error parsing disk: {e}")
                        continue
                
                # Sort by device ID
                disks.sort(key=lambda x: x['name'])
                
                logger.info(f"Found {len(disks)} disks on {server.hostname}")
                
                return {
                    "server_id": server_id,
                    "hostname": server.hostname,
                    "disks": disks,
                    "count": len(disks)
                }
            else:
                logger.error(f"PowerShell command failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            logger.error("Timeout getting disks via PowerShell")
        except Exception as e:
            logger.error(f"Error getting local disks: {e}")
    
    # Fallback to common disks list
    logger.warning(f"Using fallback disk list for server {server_id}")
    return {
        "server_id": server_id,
        "hostname": server.hostname,
        "disks": [
            {"name": "C:", "display_name": "Disco Local (C:)", "total_gb": 0, "used_gb": 0, "free_gb": 0, "percent_used": 0},
            {"name": "D:", "display_name": "Disco Local (D:)", "total_gb": 0, "used_gb": 0, "free_gb": 0, "percent_used": 0},
        ],
        "note": "Using fallback list. Ensure server is local for real-time discovery."
    }
