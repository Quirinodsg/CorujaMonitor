"""
Script para popular a Base de Conhecimento com problemas comuns de servidores Windows
Baseado em melhores práticas da Microsoft e experiência de campo
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models import KnowledgeBaseEntry, Tenant
from datetime import datetime

def seed_knowledge_base():
    db = SessionLocal()
    
    try:
        # Buscar tenant padrão
        tenant = db.query(Tenant).first()
        if not tenant:
            print("❌ Nenhum tenant encontrado. Crie um tenant primeiro.")
            return
        
        print(f"📚 Populando Base de Conhecimento para tenant: {tenant.name}")
        
        # Verificar se já existem entradas
        existing = db.query(KnowledgeBaseEntry).filter(
            KnowledgeBaseEntry.tenant_id == tenant.id
        ).count()
        
        if existing > 0:
            print(f"⚠️  Já existem {existing} entradas. Deseja continuar? (s/n)")
            response = input().lower()
            if response != 's':
                print("Operação cancelada.")
                return
        
        knowledge_entries = [
            # ===== SERVIÇOS WINDOWS =====
            {
                "problem_signature": "service_stopped_iis",
                "sensor_type": "service",
                "severity": "critical",
                "problem_title": "IIS (World Wide Web Publishing Service) Parado",
                "problem_description": "O serviço IIS (W3SVC) está parado, impedindo o acesso a sites e aplicações web hospedadas no servidor.",
                "symptoms": ["Site não responde", "Erro 503 Service Unavailable", "Aplicações web inacessíveis"],
                "root_cause": "Serviço IIS foi parado manualmente, falhou ao iniciar após reinicialização, ou travou devido a erro de aplicação.",
                "root_cause_confidence": 0.95,
                "solution_description": "Reiniciar o serviço IIS (W3SVC) através do Services.msc ou PowerShell",
                "solution_steps": [
                    "Verificar se o serviço W3SVC está parado",
                    "Executar: net start W3SVC",
                    "Verificar logs de eventos do Windows para erros",
                    "Confirmar que sites estão respondendo"
                ],
                "solution_commands": ["net start W3SVC", "iisreset /start"],
                "auto_resolution_enabled": True,
                "requires_approval": False,
                "risk_level": "low",
                "affected_os": ["Windows Server 2012", "Windows Server 2016", "Windows Server 2019", "Windows Server 2022"],
                "times_matched": 0,
                "times_successful": 0,
                "success_rate": 0.95
            },
            {
                "problem_signature": "service_stopped_sql",
                "sensor_type": "service",
                "severity": "critical",
                "problem_title": "SQL Server Database Engine Parado",
                "problem_description": "O serviço SQL Server (MSSQLSERVER) está parado, impedindo acesso aos bancos de dados.",
                "symptoms": ["Aplicações não conectam ao banco", "Erro de conexão SQL", "Timeout ao acessar dados"],
                "root_cause": "Serviço SQL Server foi parado, falhou ao iniciar, ou travou devido a corrupção de dados ou falta de recursos.",
                "root_cause_confidence": 0.90,
                "solution_description": "Reiniciar o serviço SQL Server através do SQL Server Configuration Manager ou Services.msc",
                "solution_steps": [
                    "Verificar se MSSQLSERVER está parado",
                    "Verificar logs do SQL Server para erros",
                    "Executar: net start MSSQLSERVER",
                    "Testar conexão com banco de dados"
                ],
                "solution_commands": ["net start MSSQLSERVER"],
                "auto_resolution_enabled": True,
                "requires_approval": True,
                "risk_level": "medium",
                "affected_os": ["Windows Server 2012", "Windows Server 2016", "Windows Server 2019", "Windows Server 2022"],
                "times_matched": 0,
                "times_successful": 0,
                "success_rate": 0.88
            },
            {
                "problem_signature": "service_stopped_spooler",
                "sensor_type": "service",
                "severity": "warning",
                "problem_title": "Print Spooler Parado",
                "problem_description": "O serviço Print Spooler está parado, impedindo impressão no servidor.",
                "symptoms": ["Impressoras não funcionam", "Trabalhos de impressão não processam", "Erro ao enviar para impressora"],
                "root_cause": "Print Spooler travou devido a trabalho de impressão corrompido ou driver de impressora com problema.",
                "root_cause_confidence": 0.92,
                "solution_description": "Limpar fila de impressão e reiniciar o serviço Spooler",
                "solution_steps": [
                    "Parar o serviço Spooler",
                    "Limpar pasta C:\\Windows\\System32\\spool\\PRINTERS",
                    "Reiniciar o serviço Spooler",
                    "Testar impressão"
                ],
                "solution_commands": [
                    "net stop spooler",
                    "del /Q /F /S C:\\Windows\\System32\\spool\\PRINTERS\\*",
                    "net start spooler"
                ],
                "auto_resolution_enabled": True,
                "requires_approval": False,
                "risk_level": "low",
                "affected_os": ["Windows Server 2012", "Windows Server 2016", "Windows Server 2019", "Windows Server 2022"],
                "times_matched": 0,
                "times_successful": 0,
                "success_rate": 0.93
            },
            
            # ===== DISCO =====
            {
                "problem_signature": "disk_full_temp",
                "sensor_type": "disk",
                "severity": "critical",
                "problem_title": "Disco Cheio - Arquivos Temporários",
                "problem_description": "Disco do sistema está com mais de 90% de uso, principalmente devido a arquivos temporários acumulados.",
                "symptoms": ["Disco C: acima de 90%", "Sistema lento", "Aplicações falhando", "Logs de 'disk full'"],
                "root_cause": "Acúmulo de arquivos temporários em C:\\Windows\\Temp, C:\\Users\\*\\AppData\\Local\\Temp, e logs não rotacionados.",
                "root_cause_confidence": 0.85,
                "solution_description": "Limpar arquivos temporários e logs antigos do Windows",
                "solution_steps": [
                    "Executar Disk Cleanup (cleanmgr.exe)",
                    "Limpar pasta C:\\Windows\\Temp",
                    "Limpar pastas de temp dos usuários",
                    "Limpar logs antigos do IIS/SQL se aplicável",
                    "Esvaziar lixeira"
                ],
                "solution_commands": [
                    "cleanmgr /sagerun:1",
                    "del /q /f /s C:\\Windows\\Temp\\*",
                    "del /q /f /s C:\\Windows\\Logs\\CBS\\*.log"
                ],
                "auto_resolution_enabled": False,
                "requires_approval": True,
                "risk_level": "medium",
                "affected_os": ["Windows Server 2012", "Windows Server 2016", "Windows Server 2019", "Windows Server 2022"],
                "prerequisites": ["Backup recente", "Verificar se não há processos críticos usando os arquivos"],
                "rollback_steps": ["Restaurar do backup se necessário"],
                "times_matched": 0,
                "times_successful": 0,
                "success_rate": 0.82
            },
            {
                "problem_signature": "disk_full_logs",
                "sensor_type": "disk",
                "severity": "warning",
                "problem_title": "Disco Cheio - Logs Não Rotacionados",
                "problem_description": "Disco está enchendo devido a logs de aplicações que não estão sendo rotacionados ou compactados.",
                "symptoms": ["Disco crescendo constantemente", "Arquivos .log grandes", "Pasta de logs com GB de dados"],
                "root_cause": "Logs de IIS, SQL Server, ou aplicações não configurados para rotação automática.",
                "root_cause_confidence": 0.88,
                "solution_description": "Configurar rotação de logs e limpar logs antigos",
                "solution_steps": [
                    "Identificar logs grandes (>100MB)",
                    "Configurar rotação automática no IIS/SQL",
                    "Arquivar logs antigos (>30 dias)",
                    "Implementar política de retenção"
                ],
                "solution_commands": [
                    "forfiles /p C:\\inetpub\\logs\\LogFiles /s /m *.log /d -30 /c \"cmd /c del @path\"",
                    "forfiles /p C:\\Program Files\\Microsoft SQL Server\\*\\MSSQL\\Log /s /m *.trc /d -30 /c \"cmd /c del @path\""
                ],
                "auto_resolution_enabled": False,
                "requires_approval": True,
                "risk_level": "medium",
                "affected_os": ["Windows Server 2012", "Windows Server 2016", "Windows Server 2019", "Windows Server 2022"],
                "times_matched": 0,
                "times_successful": 0,
                "success_rate": 0.85
            },
            
            # ===== MEMÓRIA =====
            {
                "problem_signature": "memory_leak_process",
                "sensor_type": "memory",
                "severity": "critical",
                "problem_title": "Memory Leak em Processo",
                "problem_description": "Memória do servidor está acima de 95% devido a processo com memory leak.",
                "symptoms": ["Memória constantemente alta", "Sistema lento", "Processo específico consumindo muita RAM"],
                "root_cause": "Aplicação com memory leak não liberando memória corretamente ao longo do tempo.",
                "root_cause_confidence": 0.80,
                "solution_description": "Identificar e reiniciar processo problemático",
                "solution_steps": [
                    "Identificar processo consumindo memória (Task Manager)",
                    "Verificar se é processo crítico",
                    "Reiniciar processo se não-crítico",
                    "Investigar causa raiz do leak",
                    "Aplicar patch/atualização se disponível"
                ],
                "solution_commands": [
                    "tasklist /v | sort /r /+65",
                    "taskkill /IM <processo>.exe /F"
                ],
                "auto_resolution_enabled": False,
                "requires_approval": True,
                "risk_level": "high",
                "affected_os": ["Windows Server 2012", "Windows Server 2016", "Windows Server 2019", "Windows Server 2022"],
                "times_matched": 0,
                "times_successful": 0,
                "success_rate": 0.70
            },
            
            # ===== CPU =====
            {
                "problem_signature": "cpu_high_antivirus",
                "sensor_type": "cpu",
                "severity": "warning",
                "problem_title": "CPU Alta - Antivírus em Scan",
                "problem_description": "CPU acima de 90% devido a scan de antivírus em execução.",
                "symptoms": ["CPU constantemente alta", "Processo MsMpEng.exe ou similar consumindo CPU", "Sistema lento"],
                "root_cause": "Windows Defender ou outro antivírus executando scan completo durante horário de produção.",
                "root_cause_confidence": 0.92,
                "solution_description": "Reagendar scan de antivírus para horário de baixo uso",
                "solution_steps": [
                    "Verificar se scan está em execução",
                    "Aguardar conclusão do scan se possível",
                    "Reagendar scans para horário noturno",
                    "Configurar exclusões para pastas de dados"
                ],
                "solution_commands": [
                    "Get-MpComputerStatus",
                    "Set-MpPreference -ScanScheduleDay 0 -ScanScheduleTime 02:00:00"
                ],
                "auto_resolution_enabled": False,
                "requires_approval": True,
                "risk_level": "low",
                "affected_os": ["Windows Server 2016", "Windows Server 2019", "Windows Server 2022"],
                "times_matched": 0,
                "times_successful": 0,
                "success_rate": 0.88
            },
            {
                "problem_signature": "cpu_high_windows_update",
                "sensor_type": "cpu",
                "severity": "warning",
                "problem_title": "CPU Alta - Windows Update",
                "problem_description": "CPU elevada devido a processo de Windows Update baixando ou instalando atualizações.",
                "symptoms": ["CPU alta", "Processo TiWorker.exe ou wuauclt.exe ativo", "Disco também alto"],
                "root_cause": "Windows Update instalando patches durante horário de produção.",
                "root_cause_confidence": 0.90,
                "solution_description": "Aguardar conclusão do update ou reagendar janela de manutenção",
                "solution_steps": [
                    "Verificar status do Windows Update",
                    "Aguardar conclusão se em progresso",
                    "Configurar horário de manutenção adequado",
                    "Considerar WSUS para controle centralizado"
                ],
                "solution_commands": [
                    "Get-WindowsUpdateLog",
                    "wuauclt /detectnow"
                ],
                "auto_resolution_enabled": False,
                "requires_approval": False,
                "risk_level": "low",
                "affected_os": ["Windows Server 2012", "Windows Server 2016", "Windows Server 2019", "Windows Server 2022"],
                "times_matched": 0,
                "times_successful": 0,
                "success_rate": 0.95
            },
            
            # ===== REDE/PING =====
            {
                "problem_signature": "ping_timeout_firewall",
                "sensor_type": "ping",
                "severity": "critical",
                "problem_title": "Servidor Não Responde - Firewall Bloqueando ICMP",
                "problem_description": "Servidor não responde a ping, mas está online. Firewall pode estar bloqueando ICMP.",
                "symptoms": ["Ping timeout", "Servidor acessível por RDP/SSH", "Outros serviços funcionando"],
                "root_cause": "Windows Firewall ou firewall de rede bloqueando pacotes ICMP (ping).",
                "root_cause_confidence": 0.85,
                "solution_description": "Verificar e ajustar regras de firewall para permitir ICMP",
                "solution_steps": [
                    "Verificar se servidor está realmente online (RDP/SSH)",
                    "Verificar regras do Windows Firewall",
                    "Habilitar ICMP Echo Request no firewall",
                    "Testar ping novamente"
                ],
                "solution_commands": [
                    "netsh advfirewall firewall add rule name=\"ICMP Allow incoming V4 echo request\" protocol=icmpv4:8,any dir=in action=allow",
                    "Test-NetConnection -ComputerName localhost -InformationLevel Detailed"
                ],
                "auto_resolution_enabled": False,
                "requires_approval": True,
                "risk_level": "low",
                "affected_os": ["Windows Server 2012", "Windows Server 2016", "Windows Server 2019", "Windows Server 2022"],
                "times_matched": 0,
                "times_successful": 0,
                "success_rate": 0.90
            },
            {
                "problem_signature": "ping_timeout_network",
                "sensor_type": "ping",
                "severity": "critical",
                "problem_title": "Servidor Não Responde - Problema de Rede",
                "problem_description": "Servidor completamente inacessível via rede.",
                "symptoms": ["Ping timeout", "RDP não conecta", "Todos os serviços inacessíveis"],
                "root_cause": "Problema de rede física, cabo desconectado, switch com problema, ou interface de rede desabilitada.",
                "root_cause_confidence": 0.75,
                "solution_description": "Verificar conectividade física e configuração de rede",
                "solution_steps": [
                    "Verificar cabo de rede conectado",
                    "Verificar luzes da interface de rede",
                    "Acessar console físico ou iLO/iDRAC",
                    "Verificar configuração de IP",
                    "Reiniciar interface de rede se necessário"
                ],
                "solution_commands": [
                    "ipconfig /all",
                    "netsh interface show interface",
                    "netsh interface set interface \"Ethernet\" admin=disable",
                    "netsh interface set interface \"Ethernet\" admin=enable"
                ],
                "auto_resolution_enabled": False,
                "requires_approval": True,
                "risk_level": "high",
                "affected_os": ["Windows Server 2012", "Windows Server 2016", "Windows Server 2019", "Windows Server 2022"],
                "times_matched": 0,
                "times_successful": 0,
                "success_rate": 0.65
            }
        ]
        
        # Inserir entradas
        count = 0
        for entry_data in knowledge_entries:
            entry = KnowledgeBaseEntry(
                tenant_id=tenant.id,
                **entry_data
            )
            db.add(entry)
            count += 1
            print(f"✅ Adicionado: {entry_data['problem_title']}")
        
        db.commit()
        print(f"\n🎉 {count} entradas adicionadas à Base de Conhecimento com sucesso!")
        print(f"📊 Total de entradas no sistema: {db.query(KnowledgeBaseEntry).count()}")
        
    except Exception as e:
        print(f"❌ Erro ao popular base de conhecimento: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("🧠 SEED DA BASE DE CONHECIMENTO")
    print("=" * 60)
    print()
    seed_knowledge_base()

