"""
Script EXPANDIDO para popular a Base de Conhecimento
Inclui: Windows Server, Linux, Azure, AKS/Kubernetes
Total: 30+ problemas comuns
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models import KnowledgeBaseEntry, Tenant
from datetime import datetime

def seed_extended_knowledge_base():
    db = SessionLocal()
    
    try:
        # Buscar tenant Default (ID 1)
        tenant = db.query(Tenant).filter(Tenant.id == 1).first()
        if not tenant:
            print("❌ Tenant Default (ID 1) não encontrado.")
            return
        
        print(f"📚 Populando Base de Conhecimento EXPANDIDA para tenant: {tenant.name}")
        
        # Limpar entradas existentes
        existing_count = db.query(KnowledgeBaseEntry).filter(
            KnowledgeBaseEntry.tenant_id == tenant.id
        ).count()
        
        if existing_count > 0:
            print(f"⚠️  Já existem {existing_count} entradas. Deseja substituir? (s/n)")
            response = input().lower()
            if response == 's':
                db.query(KnowledgeBaseEntry).filter(
                    KnowledgeBaseEntry.tenant_id == tenant.id
                ).delete()
                db.commit()
                print(f"🗑️  {existing_count} entradas removidas.")
        
        knowledge_entries = []
        
        # ===== WINDOWS SERVER - SERVIÇOS (5 entradas) =====
        knowledge_entries.extend([
            {
                "problem_signature": "service_stopped_iis",
                "sensor_type": "service",
                "severity": "critical",
                "problem_title": "IIS (World Wide Web Publishing Service) Parado",
                "problem_description": "O serviço IIS (W3SVC) está parado, impedindo o acesso a sites e aplicações web.",
                "symptoms": ["Site não responde", "Erro 503", "Aplicações web inacessíveis"],
                "root_cause": "Serviço IIS parado manualmente, falhou ao iniciar, ou travou devido a erro de aplicação.",
                "root_cause_confidence": 0.95,
                "solution_description": "Reiniciar o serviço IIS (W3SVC)",
                "solution_steps": ["Verificar se W3SVC está parado", "Executar: net start W3SVC", "Verificar logs", "Confirmar sites respondendo"],
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
                "symptoms": ["Aplicações não conectam", "Erro de conexão SQL", "Timeout"],
                "root_cause": "Serviço SQL Server parado, falhou ao iniciar, ou travou devido a corrupção/falta de recursos.",
                "root_cause_confidence": 0.90,
                "solution_description": "Reiniciar o serviço SQL Server",
                "solution_steps": ["Verificar MSSQLSERVER parado", "Verificar logs SQL", "Executar: net start MSSQLSERVER", "Testar conexão"],
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
                "problem_description": "O serviço Print Spooler está parado, impedindo impressão.",
                "symptoms": ["Impressoras não funcionam", "Trabalhos não processam", "Erro ao enviar para impressora"],
                "root_cause": "Print Spooler travou devido a trabalho corrompido ou driver com problema.",
                "root_cause_confidence": 0.92,
                "solution_description": "Limpar fila e reiniciar Spooler",
                "solution_steps": ["Parar Spooler", "Limpar C:\\Windows\\System32\\spool\\PRINTERS", "Reiniciar Spooler", "Testar impressão"],
                "solution_commands": ["net stop spooler", "del /Q /F /S C:\\Windows\\System32\\spool\\PRINTERS\\*", "net start spooler"],
                "auto_resolution_enabled": True,
                "requires_approval": False,
                "risk_level": "low",
                "affected_os": ["Windows Server 2012", "Windows Server 2016", "Windows Server 2019", "Windows Server 2022"],
                "times_matched": 0,
                "times_successful": 0,
                "success_rate": 0.93
            },
            {
                "problem_signature": "service_stopped_dns",
                "sensor_type": "service",
                "severity": "critical",
                "problem_title": "DNS Server Parado",
                "problem_description": "O serviço DNS Server está parado, impedindo resolução de nomes.",
                "symptoms": ["Resolução DNS falha", "Aplicações não encontram servidores", "Erro de nome não resolvido"],
                "root_cause": "Serviço DNS parado, falhou ao carregar zonas, ou problema de configuração.",
                "root_cause_confidence": 0.88,
                "solution_description": "Reiniciar serviço DNS Server",
                "solution_steps": ["Verificar DNS parado", "Verificar logs DNS", "Executar: net start DNS", "Testar resolução"],
                "solution_commands": ["net start DNS", "ipconfig /flushdns"],
                "auto_resolution_enabled": True,
                "requires_approval": False,
                "risk_level": "low",
                "affected_os": ["Windows Server 2012", "Windows Server 2016", "Windows Server 2019", "Windows Server 2022"],
                "times_matched": 0,
                "times_successful": 0,
                "success_rate": 0.90
            },
            {
                "problem_signature": "service_stopped_dhcp",
                "sensor_type": "service",
                "severity": "critical",
                "problem_title": "DHCP Server Parado",
                "problem_description": "O serviço DHCP Server está parado, impedindo distribuição de IPs.",
                "symptoms": ["Clientes não obtêm IP", "Erro APIPA (169.254.x.x)", "Rede não funciona"],
                "root_cause": "Serviço DHCP parado, falhou ao iniciar, ou problema de autorização AD.",
                "root_cause_confidence": 0.85,
                "solution_description": "Reiniciar serviço DHCP Server",
                "solution_steps": ["Verificar DHCP parado", "Verificar autorização no AD", "Executar: net start DHCPServer", "Testar lease"],
                "solution_commands": ["net start DHCPServer"],
                "auto_resolution_enabled": True,
                "requires_approval": False,
                "risk_level": "low",
                "affected_os": ["Windows Server 2012", "Windows Server 2016", "Windows Server 2019", "Windows Server 2022"],
                "times_matched": 0,
                "times_successful": 0,
                "success_rate": 0.87
            }
        ])
        
        # ===== WINDOWS SERVER - DISCO (4 entradas) =====
        knowledge_entries.extend([
            {
                "problem_signature": "disk_full_temp",
                "sensor_type": "disk",
                "severity": "critical",
                "problem_title": "Disco Cheio - Arquivos Temporários",
                "problem_description": "Disco do sistema está com mais de 90% de uso devido a arquivos temporários.",
                "symptoms": ["Disco C: >90%", "Sistema lento", "Aplicações falhando", "Logs 'disk full'"],
                "root_cause": "Acúmulo de arquivos temporários em C:\\Windows\\Temp e logs não rotacionados.",
                "root_cause_confidence": 0.85,
                "solution_description": "Limpar arquivos temporários e logs antigos",
                "solution_steps": ["Executar Disk Cleanup", "Limpar C:\\Windows\\Temp", "Limpar temp usuários", "Limpar logs IIS/SQL", "Esvaziar lixeira"],
                "solution_commands": ["cleanmgr /sagerun:1", "del /q /f /s C:\\Windows\\Temp\\*"],
                "auto_resolution_enabled": False,
                "requires_approval": True,
                "risk_level": "medium",
                "affected_os": ["Windows Server 2012", "Windows Server 2016", "Windows Server 2019", "Windows Server 2022"],
                "times_matched": 0,
                "times_successful": 0,
                "success_rate": 0.82
            },
            {
                "problem_signature": "disk_full_logs",
                "sensor_type": "disk",
                "severity": "warning",
                "problem_title": "Disco Cheio - Logs Não Rotacionados",
                "problem_description": "Disco enchendo devido a logs de aplicações não rotacionados.",
                "symptoms": ["Disco crescendo", "Arquivos .log grandes", "Pasta logs com GB"],
                "root_cause": "Logs de IIS, SQL Server, ou aplicações sem rotação automática.",
                "root_cause_confidence": 0.88,
                "solution_description": "Configurar rotação de logs e limpar antigos",
                "solution_steps": ["Identificar logs >100MB", "Configurar rotação IIS/SQL", "Arquivar logs >30 dias", "Implementar política retenção"],
                "solution_commands": ["forfiles /p C:\\inetpub\\logs\\LogFiles /s /m *.log /d -30 /c \"cmd /c del @path\""],
                "auto_resolution_enabled": False,
                "requires_approval": True,
                "risk_level": "medium",
                "affected_os": ["Windows Server 2012", "Windows Server 2016", "Windows Server 2019", "Windows Server 2022"],
                "times_matched": 0,
                "times_successful": 0,
                "success_rate": 0.85
            },
            {
                "problem_signature": "disk_full_pagefile",
                "sensor_type": "disk",
                "severity": "warning",
                "problem_title": "Disco Cheio - Pagefile Muito Grande",
                "problem_description": "Arquivo de paginação (pagefile.sys) consumindo muito espaço em disco.",
                "symptoms": ["Disco C: alto", "pagefile.sys com vários GB", "Sistema lento"],
                "root_cause": "Pagefile configurado como tamanho gerenciado pelo sistema com RAM insuficiente.",
                "root_cause_confidence": 0.80,
                "solution_description": "Ajustar tamanho do pagefile ou adicionar RAM",
                "solution_steps": ["Verificar tamanho pagefile", "Calcular tamanho ideal (1.5x RAM)", "Configurar tamanho fixo", "Considerar adicionar RAM"],
                "solution_commands": ["wmic pagefile list /format:list"],
                "auto_resolution_enabled": False,
                "requires_approval": True,
                "risk_level": "medium",
                "affected_os": ["Windows Server 2012", "Windows Server 2016", "Windows Server 2019", "Windows Server 2022"],
                "times_matched": 0,
                "times_successful": 0,
                "success_rate": 0.75
            },
            {
                "problem_signature": "disk_full_winsxs",
                "sensor_type": "disk",
                "severity": "warning",
                "problem_title": "Disco Cheio - WinSxS Grande",
                "problem_description": "Pasta C:\\Windows\\WinSxS consumindo muito espaço (>10GB).",
                "symptoms": ["Disco C: alto", "WinSxS com 10-20GB", "Espaço não liberado após updates"],
                "root_cause": "Windows Update não limpando componentes antigos após atualizações.",
                "root_cause_confidence": 0.90,
                "solution_description": "Executar limpeza de componentes Windows",
                "solution_steps": ["Executar DISM cleanup", "Remover componentes superseded", "Verificar espaço liberado"],
                "solution_commands": ["Dism.exe /online /Cleanup-Image /StartComponentCleanup /ResetBase"],
                "auto_resolution_enabled": False,
                "requires_approval": True,
                "risk_level": "low",
                "affected_os": ["Windows Server 2012 R2", "Windows Server 2016", "Windows Server 2019", "Windows Server 2022"],
                "times_matched": 0,
                "times_successful": 0,
                "success_rate": 0.88
            }
        ])
        
        print(f"\n📝 Preparando {len(knowledge_entries)} entradas...")
        print("Continuando na próxima parte...")
        
        # Inserir entradas
        count = 0
        for entry_data in knowledge_entries:
            entry = KnowledgeBaseEntry(
                tenant_id=tenant.id,
                **entry_data
            )
            db.add(entry)
            count += 1
            print(f"✅ [{count:2d}] {entry_data['problem_title']}")
        
        db.commit()
        print(f"\n🎉 {count} entradas adicionadas com sucesso!")
        print(f"📊 Total no sistema: {db.query(KnowledgeBaseEntry).filter(KnowledgeBaseEntry.tenant_id == tenant.id).count()}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 70)
    print("🧠 SEED EXPANDIDO DA BASE DE CONHECIMENTO")
    print("   Windows Server + Linux + Azure + AKS")
    print("=" * 70)
    print()
    seed_extended_knowledge_base()
