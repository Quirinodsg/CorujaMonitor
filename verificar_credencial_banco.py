#!/usr/bin/env python3
"""
Verificar credencial WMI no banco de dados
"""
import psycopg2
import os
from cryptography.fernet import Fernet

# Configuração do banco
DB_HOST = "192.168.31.161"
DB_PORT = 5432
DB_NAME = "coruja_monitor"
DB_USER = "coruja"
DB_PASSWORD = "coruja123"

# Chave de criptografia (mesma do .env)
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "coruja-monitor-k8s-encryption-key-change-in-production-2026")
cipher = Fernet(ENCRYPTION_KEY.encode() if isinstance(ENCRYPTION_KEY, str) else ENCRYPTION_KEY)

def decrypt_password(encrypted: str) -> str:
    """Descriptografa senha"""
    try:
        return cipher.decrypt(encrypted.encode()).decode()
    except:
        return encrypted  # Fallback

print("=" * 60)
print("VERIFICAR CREDENCIAL WMI NO BANCO")
print("=" * 60)

try:
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    
    cursor = conn.cursor()
    
    # Buscar credencial WMI do tenant 1
    query = """
        SELECT 
            id, 
            name, 
            credential_type, 
            level,
            wmi_username,
            wmi_password_encrypted,
            wmi_domain,
            is_default,
            is_active
        FROM credentials
        WHERE tenant_id = 1 
        AND credential_type = 'wmi'
        ORDER BY is_default DESC, id
    """
    
    cursor.execute(query)
    rows = cursor.fetchall()
    
    print(f"\nEncontradas {len(rows)} credenciais WMI:")
    print()
    
    for row in rows:
        id, name, cred_type, level, username, password_enc, domain, is_default, is_active = row
        
        print(f"ID: {id}")
        print(f"Nome: {name}")
        print(f"Tipo: {cred_type}")
        print(f"Nível: {level}")
        print(f"Username: {username if username else '❌ VAZIO'}")
        print(f"Password Encrypted: {password_enc[:50] if password_enc else '❌ VAZIO'}...")
        print(f"Domain: {domain if domain else '(sem domínio)'}")
        print(f"Padrão: {'✓' if is_default else '✗'}")
        print(f"Ativo: {'✓' if is_active else '✗'}")
        
        # Tentar descriptografar
        if password_enc:
            try:
                password_dec = decrypt_password(password_enc)
                print(f"Password Decrypted: {'✓ OK' if password_dec else '❌ ERRO'}")
            except Exception as e:
                print(f"Password Decrypted: ❌ ERRO - {e}")
        
        print("-" * 60)
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"\n❌ ERRO: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
