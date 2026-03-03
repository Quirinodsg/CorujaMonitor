"""
Utilitário de Criptografia para Credenciais
Data: 27 FEV 2026
Usa AES-256 para criptografar credenciais sensíveis
"""

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
import os
from typing import Optional

class CredentialEncryption:
    """Classe para criptografar e descriptografar credenciais"""
    
    def __init__(self, secret_key: Optional[str] = None):
        """
        Inicializa o sistema de criptografia
        
        Args:
            secret_key: Chave secreta (se None, usa variável de ambiente)
        """
        if secret_key is None:
            secret_key = os.getenv('ENCRYPTION_KEY', 'coruja-monitor-default-key-change-in-production')
        
        # Derivar chave usando PBKDF2HMAC
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'coruja-monitor-salt',  # Em produção, usar salt único por instalação
            iterations=100000,
            backend=default_backend()
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(secret_key.encode()))
        self.fernet = Fernet(key)
    
    def encrypt(self, plaintext: str) -> str:
        """
        Criptografa um texto
        
        Args:
            plaintext: Texto em claro
            
        Returns:
            Texto criptografado (base64)
        """
        if not plaintext:
            return ""
        
        encrypted = self.fernet.encrypt(plaintext.encode())
        return encrypted.decode()
    
    def decrypt(self, ciphertext: str) -> str:
        """
        Descriptografa um texto
        
        Args:
            ciphertext: Texto criptografado (base64)
            
        Returns:
            Texto em claro
        """
        if not ciphertext:
            return ""
        
        try:
            decrypted = self.fernet.decrypt(ciphertext.encode())
            return decrypted.decode()
        except Exception as e:
            # Se falhar, pode ser texto não criptografado (migração)
            return ciphertext
    
    def encrypt_dict(self, data: dict, fields: list) -> dict:
        """
        Criptografa campos específicos de um dicionário
        
        Args:
            data: Dicionário com dados
            fields: Lista de campos a criptografar
            
        Returns:
            Dicionário com campos criptografados
        """
        result = data.copy()
        for field in fields:
            if field in result and result[field]:
                result[field] = self.encrypt(result[field])
        return result
    
    def decrypt_dict(self, data: dict, fields: list) -> dict:
        """
        Descriptografa campos específicos de um dicionário
        
        Args:
            data: Dicionário com dados
            fields: Lista de campos a descriptografar
            
        Returns:
            Dicionário com campos descriptografados
        """
        result = data.copy()
        for field in fields:
            if field in result and result[field]:
                result[field] = self.decrypt(result[field])
        return result


# Instância global
encryption = CredentialEncryption()


def encrypt_kubernetes_credentials(cluster_data: dict) -> dict:
    """
    Criptografa credenciais de um cluster Kubernetes
    
    Args:
        cluster_data: Dados do cluster
        
    Returns:
        Dados com credenciais criptografadas
    """
    sensitive_fields = [
        'kubeconfig_content',
        'service_account_token',
        'ca_cert'
    ]
    
    return encryption.encrypt_dict(cluster_data, sensitive_fields)


def decrypt_kubernetes_credentials(cluster_data: dict) -> dict:
    """
    Descriptografa credenciais de um cluster Kubernetes
    
    Args:
        cluster_data: Dados do cluster
        
    Returns:
        Dados com credenciais descriptografadas
    """
    sensitive_fields = [
        'kubeconfig_content',
        'service_account_token',
        'ca_cert'
    ]
    
    return encryption.decrypt_dict(cluster_data, sensitive_fields)
