"""
Conftest para testes enterprise v3.5.
Configura paths e fixtures compartilhadas.
"""
import sys
import os

# Garantir que todos os módulos do projeto estão no path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
API_DIR = os.path.join(ROOT, "api")
AI_AGENT_DIR = os.path.join(ROOT, "ai-agent")

for path in [ROOT, API_DIR, AI_AGENT_DIR]:
    if path not in sys.path:
        sys.path.insert(0, path)
