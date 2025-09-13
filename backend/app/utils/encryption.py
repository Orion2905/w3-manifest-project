"""
Encryption utilities for sensitive email configuration data.
"""
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os
import base64

class EmailPasswordManager:
    """Manage encryption/decryption of email passwords."""
    
    def __init__(self, secret_key=None):
        """Initialize with app secret key."""
        if secret_key is None:
            secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
        
        # Derive encryption key from secret
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'w3manifest_email_salt',  # Fixed salt for consistency
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(secret_key.encode()))
        self.fernet = Fernet(key)
    
    def encrypt_password(self, password):
        """Encrypt password for storage."""
        return self.fernet.encrypt(password.encode()).decode()
    
    def decrypt_password(self, encrypted_password):
        """Decrypt password for use."""
        return self.fernet.decrypt(encrypted_password.encode()).decode()
    
    def test_encrypt_decrypt(self, password):
        """Test encryption/decryption cycle."""
        encrypted = self.encrypt_password(password)
        decrypted = self.decrypt_password(encrypted)
        return password == decrypted

# Global instance
email_password_manager = EmailPasswordManager()
