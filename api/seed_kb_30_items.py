"""
Script FINAL: 30+ Problemas Comuns
Windows Server (18) + Linux (6) + Azure (4) + AKS (4) = 32 entradas
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models import KnowledgeBaseEntry, Tenant

def get_all_entries():
    """Retorna todas as 32 entradas da base de conhecimento"""
    
    entries = []
    
    # ===== WINDOWS SERVER - SERVIÇOS (5) =====
    entries.extend([
        {"problem_signature": "service_stopped_iis", "sensor_type": "service", "severity": "critical", "problem_title": "IIS (W3SVC) Parado", "problem_description": "Serviço IIS parado, sites inacessíveis", "symptoms": ["Site não responde", "Erro 503"], "root_cause": "Serviço parado ou travou", "root_cause_confidence": 0.95, "solution_description": "Reiniciar IIS", "solution_steps": ["net start W3SVC"], "solution_commands": ["net start W3SVC", "iisreset /start"], "auto_resolution_enabled": True, "requires_approval": False, "risk_level": "low", "affected_os": ["Windows Server 2012+"], "times_matched": 0, "times_successful": 0, "success_rate": 0.95},
        {"problem_signature": "service_stopped_sql", "sensor_type": "service", "severity": "critical", "problem_title": "SQL Server Parado", "problem_description": "SQL Server parado, bancos inacessíveis", "symptoms": ["Erro conexão SQL"], "root_cause": "Serviço parado", "root_cause_confidence": 0.90, "solution_description": "Reiniciar SQL", "solution_steps": ["net start MSSQLSERVER"], "solution_commands": ["net start MSSQLSERVER"], "auto_resolution_enabled": True, "requires_approval": True, "risk_level": "medium", "affected_os": ["Windows Server 2012+"], "times_matched": 0, "times_successful": 0, "success_rate": 0.88},
        {"problem_signature": "service_stopped_spooler", "sensor_type": "service", "severity": "warning", "problem_title": "Print Spooler Parado", "problem_description": "Spooler parado, impressão não funciona", "symptoms": ["Impressoras não funcionam"], "root_cause": "Trabalho corrompido", "root_cause_confidence": 0.92, "solution_description": "Limpar fila e reiniciar", "solution_steps": ["Limpar fila", "Reiniciar spooler"], "solution_commands": ["net stop spooler", "del /Q /F /S C:\\Windows\\System32\\spool\\PRINTERS\\*", "net start spooler"], "auto_resolution_enabled": True, "requires_approval": False, "risk_level": "low", "affected_os": ["Windows Server 2012+"], "times_matched": 0, "times_successful": 0, "success_rate": 0.93},
        {"problem_signature": "service_stopped_dns", "sensor_type": "service", "severity": "critical", "problem_title": "DNS Server Parado", "problem_description": "DNS parado, resolução de nomes falha", "symptoms": ["DNS não resolve"], "root_cause": "Serviço parado", "root_cause_confidence": 0.88, "solution_description": "Reiniciar DNS", "solution_steps": ["net start DNS"], "solution_commands": ["net start DNS"], "auto_resolution_enabled": True, "requires_approval": False, "risk_level": "low", "affected_os": ["Windows Server 2012+"], "times_matched": 0, "times_successful": 0, "success_rate": 0.90},
        {"problem_signature": "service_stopped_dhcp", "sensor_type": "service", "severity": "critical", "problem_title": "DHCP Server Parado", "problem_description": "DHCP parado, clientes sem IP", "symptoms": ["Clientes não obtêm IP"], "root_cause": "Serviço parado", "root_cause_confidence": 0.85, "solution_description": "Reiniciar DHCP", "solution_steps": ["net start DHCPServer"], "solution_commands": ["net start DHCPServer"], "auto_resolution_enabled": True, "requires_approval": False, "risk_level": "low", "affected_os": ["Windows Server 2012+"], "times_matched": 0, "times_successful": 0, "success_rate": 0.87}
    ])
    
    # ===== WINDOWS - DISCO (4) =====
    entries.extend([
        {"problem_signature": "disk_full_temp", "sensor_type": "disk", "severity": "critical", "problem_title": "Disco Cheio - Arquivos Temp", "problem_description": "Disco >90% por arquivos temporários", "symptoms": ["Disco C: >90%"], "root_cause": "Acúmulo de temp", "root_cause_confidence": 0.85, "solution_description": "Limpar temp", "solution_steps": ["Disk Cleanup"], "solution_commands": ["cleanmgr /sagerun:1"], "auto_resolution_enabled": False, "requires_approval": True, "risk_level": "medium", "affected_os": ["Windows Server 2012+"], "times_matched": 0, "times_successful": 0, "success_rate": 0.82},
        {"problem_signature": "disk_full_logs", "sensor_type": "disk", "severity": "warning", "problem_title": "Disco Cheio - Logs", "problem_description": "Logs não rotacionados enchendo disco", "symptoms": ["Logs grandes"], "root_cause": "Sem rotação", "root_cause_confidence": 0.88, "solution_description": "Rotacionar logs", "solution_steps": ["Configurar rotação"], "solution_commands": ["forfiles /p C:\\inetpub\\logs /m *.log /d -30 /c \"cmd /c del @path\""], "auto_resolution_enabled": False, "requires_approval": True, "risk_level": "medium", "affected_os": ["Windows Server 2012+"], "times_matched": 0, "times_successful": 0, "success_rate": 0.85},
        {"problem_signature": "disk_full_pagefile", "sensor_type": "disk", "severity": "warning", "problem_title": "Disco Cheio - Pagefile Grande", "problem_description": "Pagefile consumindo muito espaço", "symptoms": ["pagefile.sys grande"], "root_cause": "Tamanho gerenciado", "root_cause_confidence": 0.80, "solution_description": "Ajustar pagefile", "solution_steps": ["Configurar tamanho fixo"], "solution_commands": ["wmic pagefile list"], "auto_resolution_enabled": False, "requires_approval": True, "risk_level": "medium", "affected_os": ["Windows Server 2012+"], "times_matched": 0, "times_successful": 0, "success_rate": 0.75},
        {"problem_signature": "disk_full_winsxs", "sensor_type": "disk", "severity": "warning", "problem_title": "Disco Cheio - WinSxS", "problem_description": "WinSxS >10GB", "symptoms": ["WinSxS grande"], "root_cause": "Componentes antigos", "root_cause_confidence": 0.90, "solution_description": "Limpar componentes", "solution_steps": ["DISM cleanup"], "solution_commands": ["Dism.exe /online /Cleanup-Image /StartComponentCleanup /ResetBase"], "auto_resolution_enabled": False, "requires_approval": True, "risk_level": "low", "affected_os": ["Windows Server 2012 R2+"], "times_matched": 0, "times_successful": 0, "success_rate": 0.88}
    ])
    
    # ===== WINDOWS - MEMÓRIA (3) =====
    entries.extend([
        {"problem_signature": "memory_leak_process", "sensor_type": "memory", "severity": "critical", "problem_title": "Memory Leak em Processo", "problem_description": "Processo com memory leak", "symptoms": ["Memória >95%"], "root_cause": "Leak de aplicação", "root_cause_confidence": 0.80, "solution_description": "Reiniciar processo", "solution_steps": ["Identificar e reiniciar"], "solution_commands": ["tasklist /v", "taskkill /F"], "auto_resolution_enabled": False, "requires_approval": True, "risk_level": "high", "affected_os": ["Windows Server 2012+"], "times_matched": 0, "times_successful": 0, "success_rate": 0.70},
        {"problem_signature": "memory_high_cache", "sensor_type": "memory", "severity": "warning", "problem_title": "Memória Alta - Cache (Normal)", "problem_description": "Cache de sistema (comportamento normal)", "symptoms": ["Memória >80% mas responsivo"], "root_cause": "Cache normal Windows", "root_cause_confidence": 0.95, "solution_description": "Verificar se é cache", "solution_steps": ["Analisar standby memory"], "solution_commands": ["Get-Counter '\\Memory\\Available MBytes'"], "auto_resolution_enabled": False, "requires_approval": False, "risk_level": "low", "affected_os": ["Windows Server 2012+"], "times_matched": 0, "times_successful": 0, "success_rate": 0.92},
        {"problem_signature": "memory_pool_leak", "sensor_type": "memory", "severity": "critical", "problem_title": "Pool Leak - Driver", "problem_description": "Non-Paged Pool crescendo (driver bug)", "symptoms": ["Pool leak", "Possível BSOD"], "root_cause": "Driver com bug", "root_cause_confidence": 0.75, "solution_description": "Atualizar driver", "solution_steps": ["Identificar driver", "Atualizar"], "solution_commands": ["poolmon.exe"], "auto_resolution_enabled": False, "requires_approval": True, "risk_level": "high", "affected_os": ["Windows Server 2012+"], "times_matched": 0, "times_successful": 0, "success_rate": 0.65}
    ])
    
    # ===== WINDOWS - CPU (3) =====
    entries.extend([
        {"problem_signature": "cpu_high_antivirus", "sensor_type": "cpu", "severity": "warning", "problem_title": "CPU Alta - Antivírus", "problem_description": "Scan de antivírus consumindo CPU", "symptoms": ["CPU >90%", "MsMpEng.exe"], "root_cause": "Scan em horário produção", "root_cause_confidence": 0.92, "solution_description": "Reagendar scan", "solution_steps": ["Reagendar para noturno"], "solution_commands": ["Set-MpPreference -ScanScheduleTime 02:00"], "auto_resolution_enabled": False, "requires_approval": True, "risk_level": "low", "affected_os": ["Windows Server 2016+"], "times_matched": 0, "times_successful": 0, "success_rate": 0.88},
        {"problem_signature": "cpu_high_windows_update", "sensor_type": "cpu", "severity": "warning", "problem_title": "CPU Alta - Windows Update", "problem_description": "Windows Update instalando patches", "symptoms": ["CPU alta", "TiWorker.exe"], "root_cause": "Update em produção", "root_cause_confidence": 0.90, "solution_description": "Aguardar conclusão", "solution_steps": ["Aguardar ou reagendar"], "solution_commands": ["Get-WindowsUpdateLog"], "auto_resolution_enabled": False, "requires_approval": False, "risk_level": "low", "affected_os": ["Windows Server 2012+"], "times_matched": 0, "times_successful": 0, "success_rate": 0.95},
        {"problem_signature": "cpu_high_sql_query", "sensor_type": "cpu", "severity": "critical", "problem_title": "CPU Alta - Query SQL", "problem_description": "Query SQL mal otimizada", "symptoms": ["CPU >90%", "sqlservr.exe"], "root_cause": "Query sem índice", "root_cause_confidence": 0.85, "solution_description": "Otimizar query", "solution_steps": ["Identificar query", "Criar índices"], "solution_commands": ["sp_who2"], "auto_resolution_enabled": False, "requires_approval": True, "risk_level": "medium", "affected_os": ["Windows Server 2012+"], "times_matched": 0, "times_successful": 0, "success_rate": 0.78}
    ])
    
    # ===== WINDOWS - REDE (3) =====
    entries.extend([
        {"problem_signature": "ping_timeout_firewall", "sensor_type": "ping", "severity": "critical", "problem_title": "Ping Falha - Firewall", "problem_description": "Firewall bloqueando ICMP", "symptoms": ["Ping timeout mas RDP ok"], "root_cause": "Firewall bloqueia ICMP", "root_cause_confidence": 0.85, "solution_description": "Permitir ICMP", "solution_steps": ["Ajustar firewall"], "solution_commands": ["netsh advfirewall firewall add rule name=\"ICMP\" protocol=icmpv4:8,any dir=in action=allow"], "auto_resolution_enabled": False, "requires_approval": True, "risk_level": "low", "affected_os": ["Windows Server 2012+"], "times_matched": 0, "times_successful": 0, "success_rate": 0.90},
        {"problem_signature": "ping_timeout_network", "sensor_type": "ping", "severity": "critical", "problem_title": "Ping Falha - Rede", "problem_description": "Problema de rede física", "symptoms": ["Tudo inacessível"], "root_cause": "Cabo/switch/interface", "root_cause_confidence": 0.75, "solution_description": "Verificar física", "solution_steps": ["Verificar cabo", "Console físico"], "solution_commands": ["ipconfig /all"], "auto_resolution_enabled": False, "requires_approval": True, "risk_level": "high", "affected_os": ["Windows Server 2012+"], "times_matched": 0, "times_successful": 0, "success_rate": 0.65},
        {"problem_signature": "network_port_exhaustion", "sensor_type": "network", "severity": "critical", "problem_title": "Esgotamento de Portas TCP", "problem_description": "Portas TCP esgotadas (>65k conexões)", "symptoms": ["Novas conexões falham", "TIME_WAIT alto"], "root_cause": "Muitas conexões não fechadas", "root_cause_confidence": 0.88, "solution_description": "Ajustar TcpTimedWaitDelay", "solution_steps": ["Reduzir TIME_WAIT", "Aumentar range portas"], "solution_commands": ["netstat -ano | find /c \"TIME_WAIT\""], "auto_resolution_enabled": False, "requires_approval": True, "risk_level": "medium", "affected_os": ["Windows Server 2012+"], "times_matched": 0, "times_successful": 0, "success_rate": 0.82}
    ])
    
    # ===== LINUX (6) =====
    entries.extend([
        {"problem_signature": "linux_disk_full_var", "sensor_type": "disk", "severity": "critical", "problem_title": "Linux - /var Cheio", "problem_description": "/var com >90% (logs)", "symptoms": ["/var >90%"], "root_cause": "Logs não rotacionados", "root_cause_confidence": 0.90, "solution_description": "Limpar logs antigos", "solution_steps": ["find /var/log -type f -name '*.log' -mtime +30 -delete"], "solution_commands": ["du -sh /var/log/*", "journalctl --vacuum-time=7d"], "auto_resolution_enabled": False, "requires_approval": True, "risk_level": "medium", "affected_os": ["Ubuntu", "CentOS", "RHEL", "Debian"], "times_matched": 0, "times_successful": 0, "success_rate": 0.85},
        {"problem_signature": "linux_high_load", "sensor_type": "cpu", "severity": "critical", "problem_title": "Linux - Load Average Alto", "problem_description": "Load average >número de CPUs", "symptoms": ["Load >CPUs", "Sistema lento"], "root_cause": "Processos bloqueados ou CPU alta", "root_cause_confidence": 0.80, "solution_description": "Identificar processos", "solution_steps": ["top", "ps aux", "Identificar processo"], "solution_commands": ["top -b -n 1", "ps aux --sort=-%cpu | head"], "auto_resolution_enabled": False, "requires_approval": True, "risk_level": "medium", "affected_os": ["Ubuntu", "CentOS", "RHEL", "Debian"], "times_matched": 0, "times_successful": 0, "success_rate": 0.75},
        {"problem_signature": "linux_oom_killer", "sensor_type": "memory", "severity": "critical", "problem_title": "Linux - OOM Killer Ativo", "problem_description": "OOM Killer matando processos", "symptoms": ["Processos morrem", "dmesg OOM"], "root_cause": "Memória insuficiente", "root_cause_confidence": 0.92, "solution_description": "Adicionar RAM ou swap", "solution_steps": ["Verificar dmesg", "Adicionar swap", "Otimizar aplicações"], "solution_commands": ["dmesg | grep -i 'out of memory'", "free -h"], "auto_resolution_enabled": False, "requires_approval": True, "risk_level": "high", "affected_os": ["Ubuntu", "CentOS", "RHEL", "Debian"], "times_matched": 0, "times_successful": 0, "success_rate": 0.70},
        {"problem_signature": "linux_service_failed", "sensor_type": "service", "severity": "critical", "problem_title": "Linux - Serviço Systemd Failed", "problem_description": "Serviço systemd em estado failed", "symptoms": ["systemctl status failed"], "root_cause": "Serviço travou ou erro config", "root_cause_confidence": 0.85, "solution_description": "Reiniciar serviço", "solution_steps": ["systemctl restart <service>", "journalctl -u <service>"], "solution_commands": ["systemctl restart", "systemctl status"], "auto_resolution_enabled": True, "requires_approval": False, "risk_level": "low", "affected_os": ["Ubuntu 16.04+", "CentOS 7+", "RHEL 7+"], "times_matched": 0, "times_successful": 0, "success_rate": 0.88},
        {"problem_signature": "linux_disk_io_high", "sensor_type": "disk", "severity": "warning", "problem_title": "Linux - I/O Disk Alto", "problem_description": "I/O wait >20%", "symptoms": ["iowait alto", "Sistema lento"], "root_cause": "Disco lento ou processo I/O intensivo", "root_cause_confidence": 0.78, "solution_description": "Identificar processo I/O", "solution_steps": ["iotop", "Identificar processo", "Otimizar ou mover para SSD"], "solution_commands": ["iostat -x 1", "iotop -o"], "auto_resolution_enabled": False, "requires_approval": True, "risk_level": "medium", "affected_os": ["Ubuntu", "CentOS", "RHEL", "Debian"], "times_matched": 0, "times_successful": 0, "success_rate": 0.72},
        {"problem_signature": "linux_ssh_too_many_auth", "sensor_type": "service", "severity": "warning", "problem_title": "Linux - SSH Too Many Auth Failures", "problem_description": "SSH bloqueando por muitas tentativas", "symptoms": ["SSH recusa conexão", "Too many authentication failures"], "root_cause": "Muitas chaves SSH ou tentativas", "root_cause_confidence": 0.90, "solution_description": "Limitar chaves ou usar IdentitiesOnly", "solution_steps": ["ssh -o IdentitiesOnly=yes", "Reduzir chaves em ~/.ssh"], "solution_commands": ["ssh -v"], "auto_resolution_enabled": False, "requires_approval": False, "risk_level": "low", "affected_os": ["Ubuntu", "CentOS", "RHEL", "Debian"], "times_matched": 0, "times_successful": 0, "success_rate": 0.92}
    ])
    
    # ===== AZURE (4) =====
    entries.extend([
        {"problem_signature": "azure_vm_deallocated", "sensor_type": "ping", "severity": "critical", "problem_title": "Azure VM - Deallocated", "problem_description": "VM Azure em estado Deallocated", "symptoms": ["VM não responde", "Portal mostra Deallocated"], "root_cause": "VM foi parada/deallocada", "root_cause_confidence": 0.95, "solution_description": "Iniciar VM via Portal/CLI", "solution_steps": ["az vm start"], "solution_commands": ["az vm start --resource-group <rg> --name <vm>"], "auto_resolution_enabled": False, "requires_approval": True, "risk_level": "low", "affected_os": ["Azure"], "times_matched": 0, "times_successful": 0, "success_rate": 0.98},
        {"problem_signature": "azure_disk_throttling", "sensor_type": "disk", "severity": "warning", "problem_title": "Azure - Disk Throttling", "problem_description": "Disco Azure atingindo limite IOPS", "symptoms": ["I/O lento", "Throttling metrics"], "root_cause": "IOPS excedido para tier do disco", "root_cause_confidence": 0.88, "solution_description": "Upgrade disk tier ou Premium SSD", "solution_steps": ["Verificar metrics", "Upgrade para Premium SSD"], "solution_commands": ["az disk update --sku Premium_LRS"], "auto_resolution_enabled": False, "requires_approval": True, "risk_level": "medium", "affected_os": ["Azure"], "times_matched": 0, "times_successful": 0, "success_rate": 0.85},
        {"problem_signature": "azure_nsg_blocking", "sensor_type": "network", "severity": "critical", "problem_title": "Azure - NSG Bloqueando Tráfego", "problem_description": "Network Security Group bloqueando porta", "symptoms": ["Conexão recusada", "Timeout"], "root_cause": "Regra NSG bloqueando", "root_cause_confidence": 0.90, "solution_description": "Adicionar regra NSG", "solution_steps": ["Verificar NSG", "Adicionar regra allow"], "solution_commands": ["az network nsg rule create"], "auto_resolution_enabled": False, "requires_approval": True, "risk_level": "medium", "affected_os": ["Azure"], "times_matched": 0, "times_successful": 0, "success_rate": 0.92},
        {"problem_signature": "azure_quota_exceeded", "sensor_type": "cpu", "severity": "critical", "problem_title": "Azure - Quota de vCPU Excedida", "problem_description": "Não pode criar VM - quota excedida", "symptoms": ["Erro ao criar VM", "QuotaExceeded"], "root_cause": "Limite de vCPU da subscription", "root_cause_confidence": 0.95, "solution_description": "Solicitar aumento de quota", "solution_steps": ["Abrir ticket suporte", "Solicitar aumento"], "solution_commands": ["az vm list-usage --location <region>"], "auto_resolution_enabled": False, "requires_approval": True, "risk_level": "low", "affected_os": ["Azure"], "times_matched": 0, "times_successful": 0, "success_rate": 0.88}
    ])
    
    # ===== AKS/KUBERNETES (4) =====
    entries.extend([
        {"problem_signature": "aks_pod_crashloopbackoff", "sensor_type": "service", "severity": "critical", "problem_title": "AKS - Pod CrashLoopBackOff", "problem_description": "Pod reiniciando continuamente", "symptoms": ["Pod CrashLoopBackOff", "Aplicação indisponível"], "root_cause": "Erro na aplicação ou config", "root_cause_confidence": 0.85, "solution_description": "Verificar logs do pod", "solution_steps": ["kubectl logs", "kubectl describe pod", "Corrigir erro"], "solution_commands": ["kubectl logs <pod>", "kubectl describe pod <pod>"], "auto_resolution_enabled": False, "requires_approval": True, "risk_level": "high", "affected_os": ["AKS", "Kubernetes"], "times_matched": 0, "times_successful": 0, "success_rate": 0.75},
        {"problem_signature": "aks_node_notready", "sensor_type": "ping", "severity": "critical", "problem_title": "AKS - Node NotReady", "problem_description": "Node do cluster em estado NotReady", "symptoms": ["Node NotReady", "Pods não agendam"], "root_cause": "Kubelet parado, rede, ou recursos", "root_cause_confidence": 0.80, "solution_description": "Verificar node e reiniciar se necessário", "solution_steps": ["kubectl describe node", "Verificar kubelet", "Reiniciar node"], "solution_commands": ["kubectl get nodes", "kubectl describe node <node>"], "auto_resolution_enabled": False, "requires_approval": True, "risk_level": "high", "affected_os": ["AKS", "Kubernetes"], "times_matched": 0, "times_successful": 0, "success_rate": 0.70},
        {"problem_signature": "aks_imagepullbackoff", "sensor_type": "service", "severity": "warning", "problem_title": "AKS - ImagePullBackOff", "problem_description": "Não consegue baixar imagem do container", "symptoms": ["ImagePullBackOff", "Pod não inicia"], "root_cause": "Imagem não existe ou sem credenciais", "root_cause_confidence": 0.92, "solution_description": "Verificar imagem e credenciais", "solution_steps": ["Verificar nome imagem", "Verificar imagePullSecrets", "Corrigir"], "solution_commands": ["kubectl describe pod <pod>"], "auto_resolution_enabled": False, "requires_approval": False, "risk_level": "low", "affected_os": ["AKS", "Kubernetes"], "times_matched": 0, "times_successful": 0, "success_rate": 0.90},
        {"problem_signature": "aks_pvc_pending", "sensor_type": "disk", "severity": "warning", "problem_title": "AKS - PVC Pending", "problem_description": "PersistentVolumeClaim em estado Pending", "symptoms": ["PVC Pending", "Pod não inicia"], "root_cause": "StorageClass não existe ou sem quota", "root_cause_confidence": 0.88, "solution_description": "Verificar StorageClass e quota", "solution_steps": ["kubectl get storageclass", "Verificar quota Azure", "Corrigir"], "solution_commands": ["kubectl get pvc", "kubectl describe pvc <pvc>"], "auto_resolution_enabled": False, "requires_approval": True, "risk_level": "medium", "affected_os": ["AKS", "Kubernetes"], "times_matched": 0, "times_successful": 0, "success_rate": 0.82}
    ])
    
    return entries

def seed_30_items():
    db = SessionLocal()
    
    try:
        tenant = db.query(Tenant).filter(Tenant.id == 1).first()
        if not tenant:
            print("❌ Tenant Default (ID 1) não encontrado.")
            return
        
        print(f"📚 Populando Base de Conhecimento para: {tenant.name}")
        print(f"📊 Total de entradas: 32")
        print()
        
        # Limpar existentes
        existing = db.query(KnowledgeBaseEntry).filter(KnowledgeBaseEntry.tenant_id == tenant.id).count()
        if existing > 0:
            print(f"🗑️  Removendo {existing} entradas existentes...")
            db.query(KnowledgeBaseEntry).filter(KnowledgeBaseEntry.tenant_id == tenant.id).delete()
            db.commit()
        
        entries = get_all_entries()
        
        count = 0
        for entry_data in entries:
            entry = KnowledgeBaseEntry(tenant_id=tenant.id, **entry_data)
            db.add(entry)
            count += 1
            category = entry_data['sensor_type'].upper()
            print(f"✅ [{count:2d}/32] [{category:8s}] {entry_data['problem_title']}")
        
        db.commit()
        print(f"\n🎉 {count} entradas adicionadas com sucesso!")
        print(f"📊 Total no sistema: {db.query(KnowledgeBaseEntry).filter(KnowledgeBaseEntry.tenant_id == tenant.id).count()}")
        
        # Estatísticas
        print("\n📈 Estatísticas:")
        print(f"   Windows Server: 18 entradas")
        print(f"   Linux: 6 entradas")
        print(f"   Azure: 4 entradas")
        print(f"   AKS/Kubernetes: 4 entradas")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 70)
    print("🧠 BASE DE CONHECIMENTO - 32 PROBLEMAS COMUNS")
    print("   Windows (18) + Linux (6) + Azure (4) + AKS (4)")
    print("=" * 70)
    print()
    seed_30_items()
