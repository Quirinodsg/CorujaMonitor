#!/usr/bin/env python3
"""
Atualizar hostname do servidor .110 no banco de dados
Para permitir autenticação Kerberos (que não funciona com IP)
"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def atualizar_hostname():
    """Atualiza o hostname do servidor .110"""
    
    # Conectar ao banco
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME", "coruja"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD")
    )
    
    cursor = conn.cursor()
    
    try:
        # Verificar servidor atual
        cursor.execute("""
            SELECT id, hostname, ip_address 
            FROM servers 
            WHERE ip_address = '192.168.31.110'
        """)
        
        servidor = cursor.fetchone()
        
        if not servidor:
            print("❌ Servidor 192.168.31.110 não encontrado no banco")
            return
        
        server_id, hostname_atual, ip = servidor
        print(f"📋 Servidor encontrado:")
        print(f"   ID: {server_id}")
        print(f"   Hostname atual: {hostname_atual}")
        print(f"   IP: {ip}")
        print()
        
        # Atualizar hostname com FQDN completo
        novo_hostname = "SRVHVSPRD010.ad.techbiz.com.br"
        
        cursor.execute("""
            UPDATE servers 
            SET hostname = %s
            WHERE id = %s
        """, (novo_hostname, server_id))
        
        conn.commit()
        
        print(f"✅ Hostname atualizado com sucesso!")
        print(f"   Novo hostname: {novo_hostname}")
        print()
        print("⚠️ IMPORTANTE:")
        print("   1. Hostname FQDN permite autenticação Kerberos")
        print("   2. Kerberos requer hostname, não funciona com IP")
        print("   3. Copie probe_core.py atualizado para a probe")
        print("   4. Reinicie a probe após copiar")
        print()
        
        # Verificar se hostname resolve
        print("🔍 Verificando resolução DNS...")
        import socket
        try:
            ip_resolvido = socket.gethostbyname(novo_hostname)
            print(f"✅ Hostname resolve para: {ip_resolvido}")
            
            if ip_resolvido != ip:
                print(f"⚠️ ATENÇÃO: IP resolvido ({ip_resolvido}) diferente do cadastrado ({ip})")
        except socket.gaierror:
            print(f"❌ ERRO: Hostname '{novo_hostname}' não resolve via DNS")
            print()
            print("SOLUÇÃO: Verificar DNS do domínio")
            print(f"   O hostname deve resolver automaticamente no domínio")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("ATUALIZAR HOSTNAME PARA AUTENTICAÇÃO KERBEROS")
    print("=" * 60)
    print()
    
    atualizar_hostname()
