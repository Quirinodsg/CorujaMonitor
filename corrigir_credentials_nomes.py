#!/usr/bin/env python3
"""
Corrige nomes de colunas em api/routers/credentials.py
"""

with open('api/routers/credentials.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Substituir nomes incorretos pelos corretos
replacements = {
    'credential.wmi_password)': 'credential.wmi_password_encrypted)',
    'credential.snmp_auth_password)': 'credential.snmp_auth_password_encrypted)',
    'credential.snmp_priv_password)': 'credential.snmp_priv_password_encrypted)',
    'credential.ssh_password)': 'credential.ssh_password_encrypted)',
    'credential.ssh_private_key\n': 'credential.ssh_private_key_encrypted\n',
    'credential.ssh_private_key ': 'credential.ssh_private_key_encrypted ',
}

for old, new in replacements.items():
    content = content.replace(old, new)

with open('api/routers/credentials.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Arquivo corrigido com sucesso!")
print("Nomes de colunas atualizados:")
print("  - wmi_password → wmi_password_encrypted")
print("  - snmp_auth_password → snmp_auth_password_encrypted")
print("  - snmp_priv_password → snmp_priv_password_encrypted")
print("  - ssh_password → ssh_password_encrypted")
print("  - ssh_private_key → ssh_private_key_encrypted")
