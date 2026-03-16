#!/usr/bin/env python3
"""
Testar funcionalidade de PING
"""

import subprocess
import platform
import re

def test_ping(target):
    """Testar ping para um alvo"""
    print(f"\n{'='*70}")
    print(f"TESTANDO PING PARA: {target}")
    print(f"{'='*70}")
    
    try:
        # Ping command varies by OS
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        command = ['ping', param, '1', target]
        
        print(f"Comando: {' '.join(command)}")
        
        result = subprocess.run(
            command, 
            capture_output=True, 
            text=True, 
            timeout=5
        )
        
        print(f"\nReturn code: {result.returncode}")
        print(f"Online: {result.returncode == 0}")
        
        # Parse ping result
        is_online = result.returncode == 0
        latency = 0
        
        if is_online:
            output = result.stdout
            print(f"\nOutput:\n{output}")
            
            # Extract latency from output
            if 'time=' in output.lower() or 'time<' in output.lower():
                try:
                    match = re.search(r'time[=<](\d+\.?\d*)', output.lower())
                    if match:
                        latency = float(match.group(1))
                        print(f"\n✓ Latency: {latency} ms")
                    else:
                        print(f"\n⚠ Não conseguiu parsear latency")
                        latency = 1
                except Exception as e:
                    print(f"\n✗ Erro ao parsear: {e}")
                    latency = 1
        else:
            print(f"\n✗ PING FALHOU")
            print(f"Stderr: {result.stderr}")
        
        # Resultado final
        print(f"\n{'='*70}")
        print(f"RESULTADO:")
        print(f"  Status: {'OK' if is_online else 'OFFLINE'}")
        print(f"  Latency: {latency} ms")
        print(f"{'='*70}")
        
        return is_online, latency
        
    except subprocess.TimeoutExpired:
        print(f"\n✗ TIMEOUT (5 segundos)")
        return False, 0
    except Exception as e:
        print(f"\n✗ ERRO: {e}")
        return False, 0

if __name__ == '__main__':
    # Testar vários alvos
    targets = [
        '8.8.8.8',           # Google DNS
        '192.168.31.161',    # Servidor Linux
        'localhost',         # Local
        '127.0.0.1',         # Loopback
    ]
    
    print("TESTE DE PING - DIAGNÓSTICO COMPLETO")
    print("="*70)
    
    results = {}
    for target in targets:
        is_online, latency = test_ping(target)
        results[target] = (is_online, latency)
    
    # Resumo
    print(f"\n\n{'='*70}")
    print("RESUMO FINAL")
    print(f"{'='*70}")
    for target, (is_online, latency) in results.items():
        status = "✓ OK" if is_online else "✗ OFFLINE"
        print(f"{status:12} | {target:20} | {latency} ms")
    print(f"{'='*70}")
