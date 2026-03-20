"""
Migration v3.5 Enterprise — Coruja Monitor
Cria tabela auto_healing_actions
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from database import engine, Base
from models import AutoHealingAction

def run():
    print("Criando tabelas v3.5 Enterprise...")
    Base.metadata.create_all(bind=engine, tables=[AutoHealingAction.__table__])
    print("✓ auto_healing_actions criada")
    print("Migration v3.5 concluída.")

if __name__ == "__main__":
    run()
