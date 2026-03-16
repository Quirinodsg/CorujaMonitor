"""
Teste rápido do WMI nativo
"""
import wmi

# Testar conexão local primeiro
print("🔍 Testando WMI local...")
try:
    c = wmi.WMI()
    for os in c.Win32_OperatingSystem():
        print(f"✅ WMI Local OK: {os.Caption}")
except Exception as e:
    print(f"❌ Erro WMI local: {e}")

# Testar conexão remota
print("\n🔍 Testando WMI remoto em SRVHVSPRD010.ad.techbiz.com.br...")
try:
    c = wmi.WMI(
        computer="SRVHVSPRD010.ad.techbiz.com.br",
        user="Techbiz\\coruja.monitor",
        password="Dj8SXoXie!o6Tkc@"
    )
    
    # Testar CPU
    for cpu in c.Win32_Processor():
        print(f"✅ CPU: {cpu.LoadPercentage}% - {cpu.NumberOfLogicalProcessors} cores")
    
    # Testar Memória
    for os in c.Win32_OperatingSystem():
        total_gb = int(os.TotalVisibleMemorySize) / 1024 / 1024
        free_gb = int(os.FreePhysicalMemory) / 1024 / 1024
        used_percent = ((total_gb - free_gb) / total_gb) * 100
        print(f"✅ Memória: {used_percent:.1f}% usado ({total_gb:.1f} GB total)")
    
    # Testar Disco
    for disk in c.Win32_LogicalDisk(DriveType=3):
        if disk.Size:
            total_gb = int(disk.Size) / 1024**3
            free_gb = int(disk.FreeSpace) / 1024**3
            used_percent = ((total_gb - free_gb) / total_gb) * 100
            print(f"✅ Disco {disk.DeviceID}: {used_percent:.1f}% usado ({total_gb:.1f} GB total)")
    
    print("\n🎉 WMI NATIVO FUNCIONANDO PERFEITAMENTE!")
    
except Exception as e:
    print(f"❌ Erro WMI remoto: {e}")
    import traceback
    traceback.print_exc()
