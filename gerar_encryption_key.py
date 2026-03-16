#!/usr/bin/env python3
"""
Gerar chave de criptografia Fernet válida
"""
from cryptography.fernet import Fernet

print("=" * 60)
print("GERAR ENCRYPTION_KEY VÁLIDA")
print("=" * 60)

# Gerar chave Fernet válida (32 bytes base64)
key = Fernet.generate_key()

print(f"\nChave gerada:")
print(key.decode())

print(f"\n\nAdicione esta linha no .env:")
print(f"ENCRYPTION_KEY={key.decode()}")

print("\n" + "=" * 60)
print("IMPORTANTE:")
print("=" * 60)
print("1. Copie a chave acima")
print("2. Cole no arquivo .env (substitua a linha ENCRYPTION_KEY)")
print("3. Reinicie a API: docker-compose restart api")
print("4. ATENÇÃO: Credenciais antigas não poderão ser descriptografadas!")
print("5. Você precisará recriar as credenciais WMI no dashboard")
print("=" * 60)
