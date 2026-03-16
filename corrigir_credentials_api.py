#!/usr/bin/env python3
"""
Script para corrigir nomes de campos WMI no endpoint /resolve
"""

# Ler arquivo
with open('api/routers/credentials.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Substituir apenas dentro do contexto WMI (3 ocorrências)
# Substituição 1: username → wmi_username
content = content.replace(
    'result["username"] = credential.wmi_username',
    'result["wmi_username"] = credential.wmi_username'
)

# Substituição 2: password → wmi_password (apenas para WMI)
content = content.replace(
    'result["password"] = decrypt_password(credential.wmi_password_encrypted)',
    'result["wmi_password"] = decrypt_password(credential.wmi_password_encrypted)'
)

# Substituição 3: domain → wmi_domain e adicionar or ""
content = content.replace(
    'result["domain"] = credential.wmi_domain',
    'result["wmi_domain"] = credential.wmi_domain or ""'
)

# Salvar arquivo
with open('api/routers/credentials.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Arquivo corrigido com sucesso!")
print("Alterações:")
print("  - result['username'] → result['wmi_username']")
print("  - result['password'] → result['wmi_password']")
print("  - result['domain'] → result['wmi_domain'] or ''")
