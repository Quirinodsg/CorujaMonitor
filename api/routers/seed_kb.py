"""
Endpoint para popular Base de Conhecimento com 80 itens
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import KnowledgeBaseEntry, Tenant, User
from auth import get_current_active_user, require_role

router = APIRouter()

def get_kb_entries():
    """Retorna 80 entradas da base de conhecimento"""
    entries = []
    
    # WINDOWS (15)
    win = [
        ("win_disk_full", "disk", "critical", "Disco C: Cheio", "Disco >95%", "Temp files", 0.92, ["cleanmgr /sagerun:1"], True, False, "low"),
        ("win_mem_high", "memory", "warning", "Memória Alta", "RAM >90%", "Memory leak", 0.85, ["Get-Process | Sort WS"], False, True, "medium"),
        ("win_cpu_high", "cpu", "warning", "CPU Alta", "CPU >85%", "Processo alto", 0.80, ["Get-Process | Sort CPU"], False, True, "medium"),
        ("win_iis_stopped", "service", "critical", "IIS Parado", "W3SVC stopped", "Serviço parou", 0.96, ["net start W3SVC"], True, False, "low"),
        ("win_sql_stopped", "service", "critical", "SQL Server Parado", "MSSQLSERVER stopped", "Serviço parou", 0.88, ["net start MSSQLSERVER"], True, True, "medium"),
        ("win_dns_stopped", "service", "critical", "DNS Parado", "DNS stopped", "Serviço parou", 0.94, ["net start DNS"], True, False, "low"),
        ("win_dhcp_stopped", "service", "critical", "DHCP Parado", "DHCP stopped", "Serviço parou", 0.93, ["net start DHCPServer"], True, False, "low"),
        ("win_ad_stopped", "service", "critical", "Active Directory Parado", "NTDS stopped", "Serviço parou", 0.85, ["net start NTDS"], False, True, "high"),
        ("win_spooler_stopped", "service", "warning", "Print Spooler Parado", "Spooler stopped", "Fila travada", 0.93, ["net stop spooler", "net start spooler"], True, False, "low"),
        ("win_updates_pending", "system", "warning", "Updates Pendentes", "Patches aguardando", "Updates instalados", 0.90, ["Get-WindowsUpdate"], False, True, "medium"),
        ("win_event_log_full", "system", "warning", "Event Log Cheio", "Logs cheios", "Logs não rotacionados", 0.88, ["wevtutil cl Application"], True, False, "low"),
        ("win_time_sync_fail", "system", "warning", "Sincronização Tempo", "Time out of sync", "NTP falhou", 0.87, ["w32tm /resync"], True, False, "low"),
        ("win_cert_expired", "system", "critical", "Certificado Expirado", "SSL cert expired", "Cert venceu", 0.95, ["Renovar certificado"], False, True, "high"),
        ("win_backup_failed", "system", "critical", "Backup Falhou", "Backup error", "Espaço/permissão", 0.82, ["Verificar logs"], False, True, "high"),
        ("win_firewall_blocking", "network", "warning", "Firewall Bloqueando", "Conexão bloqueada", "Regra firewall", 0.85, ["netsh advfirewall show"], False, True, "medium"),
    ]
    
    # LINUX (15)
    linux = [
        ("linux_disk_full", "disk", "critical", "Disco Cheio Linux", "Disco >95%", "Logs grandes", 0.90, ["df -h"], False, True, "medium"),
        ("linux_mem_high", "memory", "warning", "Memória Alta Linux", "RAM >90%", "Processo alto", 0.83, ["free -m"], False, True, "medium"),
        ("linux_cpu_high", "cpu", "warning", "CPU Alta Linux", "CPU >85%", "Processo alto", 0.78, ["top"], False, True, "medium"),
        ("linux_apache_down", "service", "critical", "Apache Parado", "httpd stopped", "Serviço parou", 0.94, ["systemctl start apache2"], True, False, "low"),
        ("linux_nginx_down", "service", "critical", "Nginx Parado", "nginx stopped", "Serviço parou", 0.95, ["systemctl start nginx"], True, False, "low"),
        ("linux_mysql_down", "service", "critical", "MySQL Parado", "mysqld stopped", "Serviço parou", 0.89, ["systemctl start mysql"], True, True, "medium"),
        ("linux_ssh_down", "service", "critical", "SSH Parado", "sshd stopped", "Serviço parou", 0.92, ["systemctl start sshd"], True, False, "low"),
        ("linux_docker_down", "service", "critical", "Docker Parado", "docker stopped", "Serviço parou", 0.91, ["systemctl start docker"], True, False, "low"),
        ("linux_ntp_unsync", "system", "warning", "NTP Dessincronizado", "Time drift", "NTP falhou", 0.86, ["ntpdate pool.ntp.org"], True, False, "low"),
        ("linux_zombie_procs", "system", "warning", "Processos Zumbis", "Zombie processes", "Processos órfãos", 0.75, ["ps aux | grep Z"], False, True, "medium"),
        ("linux_load_high", "system", "warning", "Load Average Alto", "Load >5", "Muitos processos", 0.80, ["uptime"], False, True, "medium"),
        ("linux_swap_high", "memory", "warning", "Swap Alto", "Swap >80%", "Pouca RAM", 0.82, ["free -m"], False, True, "medium"),
        ("linux_inode_full", "disk", "critical", "Inodes Esgotados", "No inodes", "Muitos arquivos", 0.88, ["df -i"], False, True, "high"),
        ("linux_oom_killer", "memory", "critical", "OOM Killer Ativo", "Out of memory", "RAM esgotada", 0.85, ["dmesg | grep oom"], False, True, "high"),
        ("linux_fs_readonly", "disk", "critical", "Filesystem Read-Only", "FS remounted RO", "Erro disco", 0.87, ["mount -o remount,rw /"], False, True, "high"),
    ]
    
    # DOCKER (10)
    docker = [
        ("docker_container_down", "docker", "critical", "Container Parado", "Container stopped", "Container crashed", 0.92, ["docker start"], True, False, "low"),
        ("docker_high_mem", "docker", "warning", "Container Alto Memória", "Container >90% mem", "Memory leak", 0.80, ["docker stats"], False, True, "medium"),
        ("docker_disk_full", "docker", "critical", "Docker Disk Full", "No space left", "Images/volumes", 0.88, ["docker system prune"], True, True, "medium"),
        ("docker_network_issue", "docker", "warning", "Rede Docker Problema", "Network error", "Bridge issue", 0.75, ["docker network ls"], False, True, "medium"),
        ("docker_compose_down", "docker", "critical", "Docker Compose Down", "Stack down", "Compose failed", 0.85, ["docker-compose up -d"], True, False, "low"),
        ("docker_registry_unreachable", "docker", "warning", "Registry Inacessível", "Pull failed", "Network/auth", 0.82, ["docker login"], False, True, "medium"),
        ("docker_volume_full", "docker", "critical", "Volume Docker Cheio", "Volume full", "Dados acumulados", 0.86, ["docker volume ls"], False, True, "high"),
        ("docker_daemon_down", "service", "critical", "Docker Daemon Parado", "dockerd stopped", "Daemon crashed", 0.90, ["systemctl start docker"], True, False, "low"),
        ("docker_swarm_node_down", "docker", "critical", "Swarm Node Down", "Node unavailable", "Node failed", 0.83, ["docker node ls"], False, True, "high"),
        ("docker_healthcheck_fail", "docker", "warning", "Healthcheck Falhando", "Container unhealthy", "App issue", 0.78, ["docker inspect"], False, True, "medium"),
    ]
    
    # AZURE/AKS (10)
    azure = [
        ("aks_pod_crashloop", "kubernetes", "critical", "Pod CrashLoopBackOff", "Pod restarting", "App error", 0.85, ["kubectl describe pod"], False, True, "high"),
        ("aks_node_notready", "kubernetes", "critical", "Node NotReady", "Node down", "Node issue", 0.88, ["kubectl get nodes"], False, True, "high"),
        ("aks_pvc_pending", "kubernetes", "warning", "PVC Pending", "Volume pending", "Storage issue", 0.82, ["kubectl get pvc"], False, True, "medium"),
        ("aks_hpa_not_scaling", "kubernetes", "warning", "HPA Não Escalando", "No scaling", "Metrics issue", 0.78, ["kubectl get hpa"], False, True, "medium"),
        ("aks_ingress_down", "kubernetes", "critical", "Ingress Controller Down", "Ingress failed", "Controller issue", 0.86, ["kubectl get ingress"], False, True, "high"),
        ("azure_vm_stopped", "azure", "critical", "VM Azure Parada", "VM deallocated", "VM stopped", 0.90, ["az vm start"], True, True, "medium"),
        ("azure_sql_high_dtu", "azure", "warning", "Azure SQL Alto DTU", "DTU >90%", "Query pesada", 0.83, ["Verificar queries"], False, True, "medium"),
        ("azure_storage_throttle", "azure", "warning", "Storage Throttling", "Throttled requests", "Limite atingido", 0.80, ["Aumentar tier"], False, True, "medium"),
        ("azure_app_service_down", "azure", "critical", "App Service Down", "App stopped", "App crashed", 0.87, ["az webapp start"], True, False, "low"),
        ("azure_function_timeout", "azure", "warning", "Function Timeout", "Execution timeout", "Código lento", 0.75, ["Otimizar código"], False, True, "medium"),
    ]
    
    # REDE/UBIQUITI (10)
    network = [
        ("ubnt_ap_offline", "snmp", "critical", "AP Ubiquiti Offline", "AP não responde", "AP sem energia/rede", 0.88, ["Verificar PoE"], False, True, "medium"),
        ("ubnt_ap_high_clients", "snmp", "warning", "AP Muitos Clientes", "Clients >50", "Sobrecarga", 0.82, ["Balancear carga"], False, True, "low"),
        ("ubnt_ap_weak_signal", "snmp", "warning", "Sinal Fraco AP", "Signal <-70dBm", "Interferência", 0.75, ["Ajustar canal"], False, True, "low"),
        ("ubnt_switch_port_down", "snmp", "warning", "Porta Switch Down", "Port down", "Cabo/dispositivo", 0.85, ["Verificar cabo"], False, True, "medium"),
        ("ubnt_switch_high_errors", "snmp", "warning", "Switch Alto Erros", "CRC errors", "Cabo ruim", 0.80, ["Trocar cabo"], False, True, "medium"),
        ("network_high_latency", "ping", "warning", "Latência Alta", "Ping >100ms", "Congestionamento", 0.78, ["Verificar link"], False, True, "medium"),
        ("network_packet_loss", "ping", "critical", "Perda de Pacotes", "Loss >5%", "Link instável", 0.83, ["Verificar ISP"], False, True, "high"),
        ("network_bandwidth_full", "snmp", "warning", "Banda Saturada", "Bandwidth >90%", "Tráfego alto", 0.80, ["QoS/upgrade"], False, True, "medium"),
        ("network_dns_slow", "network", "warning", "DNS Lento", "DNS >500ms", "DNS server issue", 0.82, ["Trocar DNS"], False, True, "low"),
        ("network_dhcp_pool_full", "network", "critical", "Pool DHCP Esgotado", "No IPs available", "Pool pequeno", 0.87, ["Expandir pool"], False, True, "high"),
    ]
    
    # NOBREAK/UPS (5)
    ups = [
        ("ups_on_battery", "snmp", "critical", "Nobreak em Bateria", "On battery", "Falta energia", 0.95, ["Verificar energia"], False, True, "high"),
        ("ups_low_battery", "snmp", "critical", "Bateria Baixa UPS", "Battery <20%", "Bateria fraca", 0.92, ["Trocar bateria"], False, True, "high"),
        ("ups_overload", "snmp", "warning", "Nobreak Sobrecarregado", "Load >90%", "Muitos equipamentos", 0.85, ["Reduzir carga"], False, True, "medium"),
        ("ups_battery_test_fail", "snmp", "warning", "Teste Bateria Falhou", "Test failed", "Bateria ruim", 0.88, ["Trocar bateria"], False, True, "high"),
        ("ups_high_temp", "snmp", "warning", "Temperatura Alta UPS", "Temp >40C", "Ventilação ruim", 0.80, ["Melhorar ventilação"], False, True, "medium"),
    ]
    
    # AR-CONDICIONADO (5)
    ac = [
        ("ac_high_temp", "snmp", "critical", "Temperatura Alta Sala", "Temp >28C", "AC não resfria", 0.90, ["Verificar AC"], False, True, "high"),
        ("ac_unit_offline", "snmp", "critical", "AC Offline", "AC não responde", "AC desligado", 0.92, ["Ligar AC"], False, True, "high"),
        ("ac_filter_dirty", "snmp", "warning", "Filtro AC Sujo", "Airflow baixo", "Filtro entupido", 0.85, ["Limpar filtro"], False, True, "low"),
        ("ac_compressor_fail", "snmp", "critical", "Compressor AC Falhou", "No cooling", "Compressor quebrado", 0.88, ["Chamar técnico"], False, True, "high"),
        ("ac_humidity_high", "snmp", "warning", "Umidade Alta", "Humidity >70%", "AC não desumidifica", 0.80, ["Verificar AC"], False, True, "medium"),
    ]
    
    # WEB APPLICATIONS (10)
    webapp = [
        ("webapp_http_500", "http", "critical", "Erro 500 Aplicação", "HTTP 500", "App error", 0.85, ["Verificar logs"], False, True, "high"),
        ("webapp_http_503", "http", "critical", "Serviço Indisponível", "HTTP 503", "App down", 0.90, ["Reiniciar app"], True, False, "low"),
        ("webapp_slow_response", "http", "warning", "Resposta Lenta", "Response >3s", "Query lenta", 0.78, ["Otimizar queries"], False, True, "medium"),
        ("webapp_ssl_expired", "http", "critical", "Certificado SSL Expirado", "SSL expired", "Cert venceu", 0.95, ["Renovar SSL"], False, True, "high"),
        ("webapp_high_error_rate", "http", "warning", "Taxa Erro Alta", "Errors >5%", "Bug na app", 0.80, ["Verificar logs"], False, True, "medium"),
        ("webapp_db_connection_fail", "http", "critical", "Conexão DB Falhou", "DB error", "DB down/creds", 0.88, ["Verificar DB"], False, True, "high"),
        ("webapp_session_timeout", "http", "warning", "Timeout Sessão", "Session expired", "Config timeout", 0.75, ["Ajustar timeout"], False, True, "low"),
        ("webapp_memory_leak", "http", "warning", "Memory Leak App", "Memory growing", "Leak no código", 0.82, ["Reiniciar app"], True, True, "medium"),
        ("webapp_cache_full", "http", "warning", "Cache Cheio", "Cache full", "Cache não limpa", 0.85, ["Limpar cache"], True, False, "low"),
        ("webapp_api_rate_limit", "http", "warning", "Rate Limit Atingido", "429 Too Many", "Muitas requests", 0.83, ["Aumentar limite"], False, True, "medium"),
    ]
    
    # Combinar todas as listas
    all_items = win + linux + docker + azure + network + ups + ac + webapp
    
    # Converter para formato de entrada
    for sig, stype, sev, title, desc, cause, rate, cmds, auto, approval, risk in all_items:
        entries.append({
            "problem_signature": sig,
            "sensor_type": stype,
            "severity": sev,
            "problem_title": title,
            "problem_description": desc,
            "symptoms": [desc],
            "root_cause": cause,
            "root_cause_confidence": rate,
            "solution_description": f"Resolver {title}",
            "solution_steps": ["Executar comandos"],
            "solution_commands": cmds,
            "auto_resolution_enabled": auto,
            "requires_approval": approval,
            "risk_level": risk,
            "affected_os": ["Multi-platform"],
            "times_matched": 0,
            "times_successful": 0,
            "success_rate": rate
        })
    
    return entries

@router.post("/populate")
async def populate_knowledge_base(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Popula a base de conhecimento com 80 itens (admin only)"""
    try:
        entries = get_kb_entries()
        
        existing = db.query(KnowledgeBaseEntry).filter(
            KnowledgeBaseEntry.tenant_id == current_user.tenant_id
        ).count()
        
        count = 0
        for entry_data in entries:
            # Verificar se já existe
            exists = db.query(KnowledgeBaseEntry).filter(
                KnowledgeBaseEntry.tenant_id == current_user.tenant_id,
                KnowledgeBaseEntry.problem_signature == entry_data["problem_signature"]
            ).first()
            
            if not exists:
                entry = KnowledgeBaseEntry(
                    tenant_id=current_user.tenant_id,
                    **entry_data
                )
                db.add(entry)
                count += 1
        
        db.commit()
        
        total = db.query(KnowledgeBaseEntry).filter(
            KnowledgeBaseEntry.tenant_id == current_user.tenant_id
        ).count()
        
        return {
            "success": True,
            "message": f"Base de conhecimento populada com sucesso",
            "entries_before": existing,
            "entries_added": count,
            "entries_total": total
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
