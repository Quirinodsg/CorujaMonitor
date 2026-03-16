#!/usr/bin/env python3
"""
Script para habilitar WMI no servidor SRVHVSPRD010
Configura credenciais WMI no banco de dados
"""
import sys
import os
from getpass import getpass

# Adicionar path da API
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models import Server

def main():
    print("═" * 70)
    print("🔧 HABILITAR WMI - SRVHVSPRD010 (192.168.31.110)")
    print("═" * 70)
    print()
    
    # Conectar ao banco
    db = SessionLocal()
    
    try:
        # Buscar servidor
        print("📊 Buscando servidor no banco de dados...")
        server = db.query(Server).filter(
            (Server.hostname.ilike('%srvhvsprd010%')) | 
            (Server.ip_address == '192.168.31.110')
        ).first()
        
        if not server:
            print("❌ Servidor não encontrado!")
            print()
            print("Servidores disponíveis:")
            servers = db.query(Server).all()
            for s in servers:
                print(f"  - {s.hostname} ({s.ip_address})")
            return 1
        
        print(f"✅ Servidor encontrado:")
        print(f"   ID: {server.id}")
        print(f"   Hostname: {server.hostname}")
        print(f"   IP: {server.ip_address}")
        print(f"   Protocolo atual: {server.monitoring_protocol or 'Não definido'}")
        print(f"   WMI habilitado: {server.wmi_enabled}")
        print()
        
        # Solicitar credenciais
        print("📝 Configurar credenciais WMI:")
        print()
        
        username = input("Usuário WMI [Administrator]: ").strip() or "Administrator"
        password = getpass("Senha WMI: ")
        
        if not password:
            print("❌ Senha não pode ser vazia!")
            return 1
        
        domain = input("Domínio WMI [deixe vazio para workgroup]: ").strip()
        
        print()
        print("📊 Configurando servidor...")
        
        # Configurar WMI
        server.monitoring_protocol = 'wmi'
        server.wmi_enabled = True
        server.wmi_username = username
        server.wmi_password_encrypted = password  # Por enquanto sem criptografia
        server.wmi_domain = domain if domain else None
        
        # Salvar
        db.commit()
        
        print()
        print("═" * 70)
        print("✅ SERVIDOR CONFIGURADO COM SUCESSO!")
        print("═" * 70)
        print()
        print("Configuração aplicada:")
        print(f"  Protocolo: {server.monitoring_protocol}")
        print(f"  WMI Habilitado: {server.wmi_enabled}")
        print(f"  Usuário: {server.wmi_username}")
        print(f"  Domínio: {server.wmi_domain or '(workgroup)'}")
        print()
        print("⏳ Próximos passos:")
        print("  1. Aguarde 1-2 minutos (próxima coleta da probe)")
        print("  2. Verifique os logs da probe na SRVSONDA001")
        print("  3. Verifique o frontend: http://192.168.31.161:3000")
        print()
        print("Logs esperados na probe:")
        print("  INFO:__main__:Using WMI for srvhvsprd010")
        print("  INFO:__main__:Collected WMI metrics from 192.168.31.110")
        print()
        
        return 0
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return 1
    finally:
        db.close()

if __name__ == "__main__":
    sys.exit(main())
