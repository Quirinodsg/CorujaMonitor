# engine package — Coruja Monitor v3.0
# Proxy para módulos probe/engine/ (compatibilidade com test_audit_enterprise.py)
import sys
import os

# Adicionar probe/ ao path para que subimports de engine.* resolvam para probe/engine/*
_probe_path = os.path.join(os.path.dirname(__file__), '..', 'probe')
if _probe_path not in sys.path:
    sys.path.insert(0, _probe_path)
