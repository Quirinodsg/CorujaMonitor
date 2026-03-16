"""
Diagnóstico completo de WMI nativo
Testa diferentes métodos de autenticação
"""
import sys
import os

print("=" * 80)
print("DIAGNÓSTICO WMI NATIVO")
print("=" * 80)

# Teste 1: Verificar se bibliotecas estão instaladas
print("\n[1] Verificando bibliotecas...")
try:
    import win32com.client
    print("✅ win32com.client OK")
except ImportError as e:
    print(f"❌ win32com.client FALHOU: {e}")
    sys.exit(1)

try:
    import wmi
    print("✅ wmi OK")
except ImportError as e:
    print(f"❌ wmi FALHOU: {e}")
    sys.exit(1)

# Teste 2: WMI local (deve funcionar sempre)
print("\n[2] Testando WMI local...")
try:
    c = wmi.WMI()
    for os_info in c.Win32_OperatingSystem():
        print(f"✅ WMI local OK: {os_info.Caption}")
        break
except Exception as e:
    print(f"❌ WMI local FALHOU: {e}")

# Teste 3: WMI remoto COM CREDENCIAIS (método atual)
print("\n[3] Testando WMI remoto COM credenciais...")
hostname = "SRVHVSPRD010.ad.techbiz.com.br"
username = "coruja.monitor"
password = "Dj8SXoXie!o6Tkc@"
domain = "Techbiz"
full_username = f"{domain}\\{username}"

print(f"   Hostname: {hostname}")
print(f"   Usuário: {full_username}")
print(f"   Senha: {'*' * len(password)}")

try:
    c = wmi.WMI(
        computer=hostname,
        user=full_username,
        password=password,
        namespace="root/cimv2"
    )
    print("✅ Conexão WMI estabelecida!")
    
    # Tentar query simples
    for os_info in c.Win32_OperatingSystem():
        print(f"✅ Query OK: {os_info.Caption}")
        break
        
except Exception as e:
    print(f"❌ WMI remoto FALHOU: {e}")
    print(f"   Tipo do erro: {type(e)}")
    
    # Tentar extrair código de erro
    if hasattr(e, 'args'):
        print(f"   Args: {e.args}")

# Teste 4: WMI remoto SEM credenciais (usa contexto atual)
print("\n[4] Testando WMI remoto SEM credenciais (contexto atual)...")
try:
    c = wmi.WMI(computer=hostname)
    print("✅ Conexão WMI estabelecida (contexto atual)!")
    
    for os_info in c.Win32_OperatingSystem():
        print(f"✅ Query OK: {os_info.Caption}")
        break
        
except Exception as e:
    print(f"❌ WMI remoto (contexto atual) FALHOU: {e}")

# Teste 5: Verificar contexto de segurança atual
print("\n[5] Verificando contexto de segurança atual...")
try:
    import getpass
    import socket
    
    current_user = getpass.getuser()
    current_domain = os.environ.get('USERDOMAIN', 'N/A')
    current_hostname = socket.gethostname()
    
    print(f"   Usuário atual: {current_domain}\\{current_user}")
    print(f"   Hostname: {current_hostname}")
    print(f"   Variáveis de ambiente:")
    print(f"      USERDOMAIN: {os.environ.get('USERDOMAIN', 'N/A')}")
    print(f"      USERNAME: {os.environ.get('USERNAME', 'N/A')}")
    print(f"      COMPUTERNAME: {os.environ.get('COMPUTERNAME', 'N/A')}")
    
except Exception as e:
    print(f"❌ Erro ao verificar contexto: {e}")

# Teste 6: Testar com win32com diretamente
print("\n[6] Testando com win32com.client diretamente...")
try:
    import win32com.client
    
    locator = win32com.client.Dispatch("WbemScripting.SWbemLocator")
    print("✅ SWbemLocator criado")
    
    # Tentar conectar COM credenciais
    connection = locator.ConnectServer(
        hostname,
        "root\\cimv2",
        full_username,
        password
    )
    print("✅ Conexão estabelecida via win32com!")
    
    # Tentar query
    query = "SELECT Caption FROM Win32_OperatingSystem"
    results = connection.ExecQuery(query)
    
    for result in results:
        print(f"✅ Query OK: {result.Caption}")
        break
        
except Exception as e:
    print(f"❌ win32com FALHOU: {e}")
    print(f"   Tipo do erro: {type(e)}")
    if hasattr(e, 'args'):
        print(f"   Args: {e.args}")

print("\n" + "=" * 80)
print("DIAGNÓSTICO COMPLETO")
print("=" * 80)
