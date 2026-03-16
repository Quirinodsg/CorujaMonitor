#!/usr/bin/env python3
"""
Corrige os IFs que ainda usam nomes antigos
"""

with open('api/routers/credentials.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Substituir nos IFs também
replacements = {
    'if credential.wmi_password ': 'if credential.wmi_password_encrypted ',
    'if credential.snmp_auth_password ': 'if credential.snmp_auth_password_encrypted ',
    'if credential.snmp_priv_password ': 'if credential.snmp_priv_password_encrypted ',
    'if credential.ssh_password ': 'if credential.ssh_password_encrypted ',
}

for old, new in replacements.items():
    content = content.replace(old, new)

with open('api/routers/credentials.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ IFs corrigidos!")
