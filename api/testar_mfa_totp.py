"""
Script para testar TOTP e verificar se está gerando códigos corretamente
"""

import pyotp
import time
from datetime import datetime

# Pegar o secret do usuário do banco
import sys
sys.path.append('api')

from database import SessionLocal
from models import User

def test_totp():
    print("=" * 60)
    print("TESTE DE TOTP - MFA")
    print("=" * 60)
    print()
    
    # Conectar ao banco
    db = SessionLocal()
    
    try:
        # Buscar usuário com MFA habilitado
        user = db.query(User).filter(User.mfa_enabled == True).first()
        
        if not user:
            print("❌ Nenhum usuário com MFA habilitado encontrado")
            print()
            print("Para testar:")
            print("1. Faça login no sistema")
            print("2. Vá em Configurações > Segurança > MFA")
            print("3. Habilite o MFA")
            print("4. Execute este script novamente")
            return
        
        print(f"✅ Usuário encontrado: {user.email}")
        print(f"   MFA Habilitado: {user.mfa_enabled}")
        print(f"   Secret: {user.mfa_secret}")
        print()
        
        if not user.mfa_secret:
            print("❌ Secret não encontrado!")
            return
        
        # Criar TOTP
        totp = pyotp.TOTP(user.mfa_secret)
        
        print("=" * 60)
        print("CÓDIGOS GERADOS (atualizando a cada 5 segundos)")
        print("=" * 60)
        print()
        print("Compare com o código no Google Authenticator:")
        print()
        
        # Gerar códigos por 30 segundos
        for i in range(6):
            current_code = totp.now()
            current_time = datetime.now().strftime("%H:%M:%S")
            remaining = 30 - (int(time.time()) % 30)
            
            print(f"[{current_time}] Código: {current_code} (válido por {remaining}s)")
            
            # Verificar se o código é válido
            is_valid = totp.verify(current_code, valid_window=1)
            print(f"           Validação: {'✅ VÁLIDO' if is_valid else '❌ INVÁLIDO'}")
            print()
            
            if i < 5:
                time.sleep(5)
        
        print("=" * 60)
        print("TESTE DE VERIFICAÇÃO")
        print("=" * 60)
        print()
        
        # Testar verificação com código atual
        test_code = totp.now()
        print(f"Código de teste: {test_code}")
        
        # Testar com janela de 0 (exato)
        result_0 = totp.verify(test_code, valid_window=0)
        print(f"Janela 0 (exato): {'✅ VÁLIDO' if result_0 else '❌ INVÁLIDO'}")
        
        # Testar com janela de 1 (±30s)
        result_1 = totp.verify(test_code, valid_window=1)
        print(f"Janela 1 (±30s): {'✅ VÁLIDO' if result_1 else '❌ INVÁLIDO'}")
        
        # Testar com janela de 2 (±60s)
        result_2 = totp.verify(test_code, valid_window=2)
        print(f"Janela 2 (±60s): {'✅ VÁLIDO' if result_2 else '❌ INVÁLIDO'}")
        
        print()
        print("=" * 60)
        print("INFORMAÇÕES DO SISTEMA")
        print("=" * 60)
        print()
        
        import platform
        print(f"Sistema Operacional: {platform.system()}")
        print(f"Hora do Sistema: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Timestamp Unix: {int(time.time())}")
        print(f"Intervalo TOTP: 30 segundos")
        print(f"Algoritmo: SHA1")
        print(f"Dígitos: 6")
        
        print()
        print("=" * 60)
        print("DIAGNÓSTICO")
        print("=" * 60)
        print()
        
        if result_1:
            print("✅ TOTP está funcionando corretamente!")
            print()
            print("Se o código não funciona no login:")
            print("1. Verifique se o relógio do servidor está sincronizado")
            print("2. Verifique se o relógio do smartphone está sincronizado")
            print("3. Aguarde o código mudar e tente novamente")
            print("4. Use um código de backup")
        else:
            print("❌ TOTP NÃO está funcionando!")
            print()
            print("Possíveis causas:")
            print("1. Relógio do servidor dessincronizado")
            print("2. Secret incorreto no banco de dados")
            print("3. Problema na biblioteca pyotp")
        
    finally:
        db.close()

if __name__ == "__main__":
    test_totp()
