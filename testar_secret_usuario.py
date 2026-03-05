"""
Teste do secret específico do usuário admin@coruja.com
"""

import pyotp
import time

# Secret atual do usuário no banco de dados
SECRET = "VUEBGGLYTDZ4SV5RGZOBFATY5P5EDZYU"

print("=" * 80)
print("TESTE DO SECRET DO USUÁRIO admin@coruja.com")
print("=" * 80)
print()
print(f"Secret: {SECRET}")
print(f"Tamanho: {len(SECRET)} caracteres")
print()

# Criar TOTP
totp = pyotp.TOTP(SECRET)

# Gerar URI
totp_uri = totp.provisioning_uri(
    name="admin@coruja.com",
    issuer_name="CorujaMonitor"
)

print("URI TOTP:")
print(totp_uri)
print()

# Mostrar códigos atuais
print("=" * 80)
print("CÓDIGOS ATUAIS (compare com Google Authenticator)")
print("=" * 80)
print()

for i in range(5):
    code = totp.now()
    remaining = 30 - (int(time.time()) % 30)
    timestamp = time.strftime("%H:%M:%S")
    
    print(f"[{timestamp}] Código: {code} (válido por {remaining}s)")
    
    if i < 4:
        time.sleep(10)

print()
print("=" * 80)
print("JANELA DE CÓDIGOS")
print("=" * 80)
print()

current_time = int(time.time())
print(f"Código anterior (-30s): {totp.at(current_time - 30)}")
print(f"Código atual:           {totp.now()}")
print(f"Próximo código (+30s):  {totp.at(current_time + 30)}")
print()

print("=" * 80)
print("INSTRUÇÕES")
print("=" * 80)
print()
print("1. Abra o Google Authenticator no seu smartphone")
print("2. Encontre a conta 'CorujaMonitor' ou 'admin@coruja.com'")
print("3. Compare o código mostrado com os códigos acima")
print()
print("Se o código do Google Authenticator:")
print()
print("✅ MUDA a cada 30s e COINCIDE com os códigos acima:")
print("   → Tudo está funcionando corretamente!")
print("   → O problema pode ser no login (verificar logs)")
print()
print("❌ NÃO MUDA (sempre o mesmo número):")
print("   → Você escaneou um QR Code antigo")
print("   → Solução: Remover conta e escanear novo QR Code")
print()
print("❌ MUDA mas NÃO COINCIDE com os códigos acima:")
print("   → Você tem múltiplas contas 'CorujaMonitor'")
print("   → Solução: Remover TODAS e adicionar apenas uma")
print()
print("=" * 80)
print("SOLUÇÃO DEFINITIVA")
print("=" * 80)
print()
print("1. Remova TODAS as contas 'CorujaMonitor' do Google Authenticator")
print("2. No sistema, vá em Configurações > Segurança")
print("3. Clique em 'Desabilitar MFA' (se estiver habilitado)")
print("4. Clique em 'Habilitar MFA' novamente")
print("5. Escaneie o NOVO QR Code")
print("6. Verifique se o código está MUDANDO")
print("7. Ative o MFA")
print("8. Teste o login")
print()
