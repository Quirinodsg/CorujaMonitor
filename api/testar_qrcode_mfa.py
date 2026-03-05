"""
Teste específico para verificar se o QR Code está sendo gerado corretamente
"""

import pyotp
import qrcode
import io
import base64

def test_qr_code_generation():
    print("=" * 60)
    print("TESTE DE GERAÇÃO DE QR CODE")
    print("=" * 60)
    print()
    
    # Gerar um secret de teste
    secret = pyotp.random_base32()
    print(f"Secret gerado: {secret}")
    print(f"Tamanho: {len(secret)} caracteres")
    print()
    
    # Criar TOTP
    totp = pyotp.TOTP(secret)
    
    # Gerar URI
    account_name = "admin@coruja.com"
    issuer = "CorujaMonitor"
    
    totp_uri = totp.provisioning_uri(
        name=account_name,
        issuer_name=issuer
    )
    
    print("URI TOTP gerado:")
    print(totp_uri)
    print()
    
    # Verificar formato do URI
    if totp_uri.startswith("otpauth://totp/"):
        print("✅ URI está no formato correto")
    else:
        print("❌ URI está em formato incorreto!")
    
    # Verificar parâmetros
    if f"secret={secret}" in totp_uri:
        print("✅ Secret está presente no URI")
    else:
        print("❌ Secret NÃO está no URI!")
    
    if f"issuer={issuer}" in totp_uri:
        print("✅ Issuer está presente no URI")
    else:
        print("❌ Issuer NÃO está no URI!")
    
    print()
    
    # Gerar códigos de teste
    print("=" * 60)
    print("CÓDIGOS GERADOS (devem mudar a cada 30s)")
    print("=" * 60)
    print()
    
    import time
    for i in range(3):
        code = totp.now()
        remaining = 30 - (int(time.time()) % 30)
        print(f"Código {i+1}: {code} (válido por {remaining}s)")
        
        if i < 2:
            time.sleep(10)
    
    print()
    print("=" * 60)
    print("DIAGNÓSTICO")
    print("=" * 60)
    print()
    
    # Verificar se os códigos estão mudando
    code1 = totp.at(int(time.time()) - 30)
    code2 = totp.now()
    code3 = totp.at(int(time.time()) + 30)
    
    print(f"Código anterior: {code1}")
    print(f"Código atual:    {code2}")
    print(f"Próximo código:  {code3}")
    print()
    
    if code1 != code2 and code2 != code3:
        print("✅ Códigos estão mudando corretamente!")
    else:
        print("❌ PROBLEMA: Códigos não estão mudando!")
    
    print()
    print("=" * 60)
    print("INSTRUÇÕES")
    print("=" * 60)
    print()
    print("Para testar no Google Authenticator:")
    print()
    print("1. Abra o Google Authenticator")
    print("2. Toque em '+' ou 'Adicionar conta'")
    print("3. Escolha 'Inserir código manualmente'")
    print("4. Nome da conta: CorujaMonitor")
    print(f"5. Código: {secret}")
    print("6. Tipo: Baseado em tempo")
    print("7. Adicione a conta")
    print()
    print("O código deve MUDAR a cada 30 segundos!")
    print()
    print("Se o código NÃO mudar:")
    print("- Verifique se o relógio do smartphone está sincronizado")
    print("- Tente sincronizar o Google Authenticator:")
    print("  Configurações > Correção de hora > Sincronizar agora")
    print()

if __name__ == "__main__":
    test_qr_code_generation()
