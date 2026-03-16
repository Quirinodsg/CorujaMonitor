"""
Teste completo do WMI nativo antes de usar na probe
Execute na SRVSONDA001: python testar_wmi_nativo_completo.py
"""
import sys
import traceback

print("═" * 70)
print("  TESTE WMI NATIVO - SRVSONDA001")
print("═" * 70)

# Teste 1: Importar biblioteca WMI
print("\n🔍 Teste 1: Importando biblioteca WMI...")
try:
    import wmi
    print("✅ Biblioteca WMI importada com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar WMI: {e}")
    print("   Execute: pip install pywin32 WMI")
    sys.exit(1)

# Teste 2: WMI local
print("\n🔍 Teste 2: Testando WMI local...")
try:
    c = wmi.WMI()
    for os in c.Win32_OperatingSystem():
        print(f"✅ WMI Local OK: {os.Caption}")
        print(f"   Hostname: {os.CSName}")
except Exception as e:
    print(f"❌ Erro WMI local: {e}")
    traceback.print_exc()
    sys.exit(1)

# Teste 3: WMI remoto com credenciais
print("\n🔍 Teste 3: Testando WMI remoto em SRVHVSPRD010.ad.techbiz.com.br...")
try:
    hostname = "SRVHVSPRD010.ad.techbiz.com.br"
    username = "Techbiz\\coruja.monitor"
    password = "Dj8SXoXie!o6Tkc@"
    
    print(f"   Conectando em: {hostname}")
    print(f"   Usuário: {username}")
    
    c = wmi.WMI(
        computer=hostname,
        user=username,
        password=password,
        namespace="root/cimv2"
    )
    
    print("✅ Conexão WMI remota estabelecida!")
    
    # Teste CPU
    print("\n   📊 Coletando CPU...")
    for cpu in c.Win32_Processor():
        print(f"   ✅ CPU: {cpu.LoadPercentage}% - {cpu.NumberOfLogicalProcessors} cores")
        print(f"      Nome: {cpu.Name}")
    
    # Teste Memória
    print("\n   📊 Coletando Memória...")
    for os in c.Win32_OperatingSystem():
        total_kb = int(os.TotalVisibleMemorySize)
        free_kb = int(os.FreePhysicalMemory)
        used_kb = total_kb - free_kb
        used_percent = (used_kb / total_kb) * 100
        total_gb = total_kb / 1024 / 1024
        used_gb = used_kb / 1024 / 1024
        free_gb = free_kb / 1024 / 1024
        
        print(f"   ✅ Memória: {used_percent:.1f}% usado")
        print(f"      Total: {total_gb:.2f} GB")
        print(f"      Usado: {used_gb:.2f} GB")
        print(f"      Livre: {free_gb:.2f} GB")
    
    # Teste Disco
    print("\n   📊 Coletando Discos...")
    for disk in c.Win32_LogicalDisk(DriveType=3):
        if disk.Size:
            total_bytes = int(disk.Size)
            free_bytes = int(disk.FreeSpace)
            used_bytes = total_bytes - free_bytes
            used_percent = (used_bytes / total_bytes) * 100
            total_gb = total_bytes / 1024**3
            used_gb = used_bytes / 1024**3
            free_gb = free_bytes / 1024**3
            
            print(f"   ✅ Disco {disk.DeviceID}: {used_percent:.1f}% usado")
            print(f"      Volume: {disk.VolumeName or 'Sem nome'}")
            print(f"      Total: {total_gb:.2f} GB")
            print(f"      Usado: {used_gb:.2f} GB")
            print(f"      Livre: {free_gb:.2f} GB")
    
    # Teste Serviços (apenas alguns)
    print("\n   📊 Coletando Serviços (amostra)...")
    services = list(c.Win32_Service(StartMode="Auto"))[:5]  # Apenas 5 primeiros
    for service in services:
        status_icon = "✅" if service.State == "Running" else "❌"
        print(f"   {status_icon} {service.DisplayName}: {service.State}")
    
    print("\n" + "═" * 70)
    print("  🎉 TODOS OS TESTES PASSARAM!")
    print("  WMI NATIVO FUNCIONANDO PERFEITAMENTE!")
    print("═" * 70)
    print("\n✅ Pode copiar os arquivos para produção agora.")
    
except Exception as e:
    print(f"\n❌ Erro WMI remoto: {e}")
    print("\nDetalhes do erro:")
    traceback.print_exc()
    print("\n" + "═" * 70)
    print("  POSSÍVEIS CAUSAS:")
    print("═" * 70)
    print("  1. Hostname incorreto (deve ser FQDN)")
    print("  2. Credenciais incorretas")
    print("  3. Firewall bloqueando WMI (porta 135)")
    print("  4. Servidor não está no domínio")
    print("  5. Usuário não tem permissão WMI")
    sys.exit(1)
