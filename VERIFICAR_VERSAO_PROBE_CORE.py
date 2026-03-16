#!/usr/bin/env python3
"""
Verifica qual versão do probe_core.py está instalada
"""

import os

probe_path = r"C:\Program Files\CorujaMonitor\Probe\probe_core.py"

print("=" * 70)
print("VERIFICAÇÃO DE VERSÃO - probe_core.py")
print("=" * 70)

if not os.path.exists(probe_path):
    print(f"\n❌ ERRO: Arquivo não encontrado em {probe_path}")
    exit(1)

print(f"\n✓ Arquivo encontrado: {probe_path}")

# Ler arquivo
with open(probe_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Verificar se tem os logs detalhados
markers = {
    'About to call collect_snmp_v2c': 'Logs detalhados ANTES da chamada',
    'collect_snmp_v2c returned successfully': 'Logs detalhados DEPOIS da chamada',
    'Result type:': 'Log de tipo do resultado',
    'Collector object:': 'Log do objeto collector'
}

print("\n" + "=" * 70)
print("VERIFICANDO MARCADORES DE VERSÃO")
print("=" * 70)

all_found = True
for marker, description in markers.items():
    if marker in content:
        print(f"✓ ENCONTRADO: {description}")
    else:
        print(f"❌ FALTANDO: {description}")
        all_found = False

print("\n" + "=" * 70)
if all_found:
    print("✓✓✓ VERSÃO CORRETA INSTALADA!")
    print("=" * 70)
    print("\nSe os logs não aparecem, o problema é outro.")
    print("Possível causa: except externo capturando exceção antes dos logs.")
else:
    print("❌❌❌ VERSÃO ANTIGA INSTALADA!")
    print("=" * 70)
    print("\nVocê precisa copiar o arquivo atualizado novamente.")
    print("\nArquivo correto está em:")
    print("  C:\\Users\\andre.quirino\\Coruja Monitor\\probe\\probe_core.py")
    print("\nCopiar para:")
    print("  C:\\Program Files\\CorujaMonitor\\Probe\\probe_core.py")

# Verificar data de modificação
import datetime
mod_time = os.path.getmtime(probe_path)
mod_date = datetime.datetime.fromtimestamp(mod_time)
print(f"\nÚltima modificação: {mod_date.strftime('%d/%m/%Y %H:%M:%S')}")
