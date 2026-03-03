#!/usr/bin/env python3
"""
Script para atualizar o IP do servidor no banco de dados
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

from database import SessionLocal
from models import Server

def atualizar_ip_servidor(hostname: str, novo_ip: str):
    """Atualiza o IP de um servidor"""
    db = SessionLocal()
    try:
        # Buscar servidor
        servidor = db.query(Server).filter(Server.hostname == hostname).first()
        
        if not servidor:
            print(f"❌ Servidor '{hostname}' não encontrado")
            return False
        
        print(f"📋 Servidor encontrado:")
        print(f"   Hostname: {servidor.hostname}")
        print(f"   IP Atual: {servidor.ip_address}")
        print(f"   IP Público Atual: {servidor.public_ip}")
        
        # Atualizar IP
        servidor.ip_address = novo_ip
        db.commit()
        
        print(f"\n✅ IP atualizado com sucesso!")
        print(f"   Novo IP: {servidor.ip_address}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao atualizar IP: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def listar_servidores():
    """Lista todos os servidores"""
    db = SessionLocal()
    try:
        servidores = db.query(Server).all()
        
        if not servidores:
            print("❌ Nenhum servidor encontrado")
            return
        
        print(f"\n📋 Servidores cadastrados ({len(servidores)}):\n")
        for srv in servidores:
            print(f"   Hostname: {srv.hostname}")
            print(f"   IP: {srv.ip_address}")
            print(f"   IP Público: {srv.public_ip}")
            print(f"   Tenant ID: {srv.tenant_id}")
            print(f"   Ativo: {'Sim' if srv.is_active else 'Não'}")
            print()
        
    except Exception as e:
        print(f"❌ Erro ao listar servidores: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 50)
    print("  ATUALIZAR IP DO SERVIDOR")
    print("=" * 50)
    print()
    
    # Listar servidores primeiro
    listar_servidores()
    
    # Atualizar IP do DESKTOP-P9VGN04
    hostname = "DESKTOP-P9VGN04"
    novo_ip = "192.168.0.41"
    
    print(f"🔄 Atualizando IP de '{hostname}' para '{novo_ip}'...\n")
    
    if atualizar_ip_servidor(hostname, novo_ip):
        print("\n✅ Operação concluída com sucesso!")
        print("   Recarregue a página no navegador para ver o novo IP")
    else:
        print("\n❌ Falha na operação")
