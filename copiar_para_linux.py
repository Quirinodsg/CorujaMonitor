#!/usr/bin/env python3
"""
Script para copiar Login.js corrigido para o servidor Linux via SSH
"""

import paramiko
import os
from pathlib import Path

# Configurações
LINUX_HOST = "192.168.31.161"
LINUX_USER = "administrador"
LINUX_PATH = "/home/administrador/CorujaMonitor/frontend/src/components/Login.js"
LOCAL_PATH = r"frontend\src\components\Login.js"

def copiar_arquivo():
    print("=" * 80)
    print("  COPIAR Login.js PARA SERVIDOR LINUX")
    print("=" * 80)
    print()
    
    # Verificar se arquivo local existe
    if not os.path.exists(LOCAL_PATH):
        print(f"❌ Erro: Arquivo não encontrado: {LOCAL_PATH}")
        return False
    
    print(f"✅ Arquivo local encontrado: {LOCAL_PATH}")
    print()
    
    # Solicitar senha
    senha = input(f"Digite a senha do usuário '{LINUX_USER}' no servidor {LINUX_HOST}: ")
    print()
    
    try:
        # Conectar via SSH
        print(f"🔌 Conectando em {LINUX_HOST}...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(LINUX_HOST, username=LINUX_USER, password=senha)
        print("✅ Conectado!")
        print()
        
        # Fazer backup no servidor
        print("📦 Fazendo backup do arquivo original...")
        stdin, stdout, stderr = ssh.exec_command(f"cp {LINUX_PATH} {LINUX_PATH}.backup")
        stdout.channel.recv_exit_status()
        print("✅ Backup criado")
        print()
        
        # Copiar arquivo
        print("📤 Copiando arquivo...")
        sftp = ssh.open_sftp()
        sftp.put(LOCAL_PATH, LINUX_PATH)
        sftp.close()
        print("✅ Arquivo copiado")
        print()
        
        # Reiniciar frontend
        print("🔄 Reiniciando frontend...")
        stdin, stdout, stderr = ssh.exec_command(
            "cd ~/CorujaMonitor && docker compose restart frontend"
        )
        stdout.channel.recv_exit_status()
        print("✅ Frontend reiniciado")
        print()
        
        # Fechar conexão
        ssh.close()
        
        print("=" * 80)
        print("  ✅ SUCESSO!")
        print("=" * 80)
        print()
        print("Aguarde 30 segundos e teste:")
        print("  URL: http://192.168.31.161:3000")
        print("  Email: admin@coruja.com")
        print("  Senha: admin123")
        print()
        
        return True
        
    except paramiko.AuthenticationException:
        print("❌ Erro: Senha incorreta")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    # Verificar se paramiko está instalado
    try:
        import paramiko
    except ImportError:
        print("❌ Erro: Biblioteca 'paramiko' não está instalada")
        print()
        print("Instale com:")
        print("  pip install paramiko")
        print()
        exit(1)
    
    copiar_arquivo()
