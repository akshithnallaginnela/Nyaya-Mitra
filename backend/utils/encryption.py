"""Data encryption utilities for sensitive data at rest."""
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
import base64
import os

# Get encryption key from environment or generate one
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
if not ENCRYPTION_KEY:
    # Generate a key for development (in production, use a secure key from env)
    ENCRYPTION_KEY = Fernet.generate_key().decode()
    print(f"WARNING: Using generated encryption key. Set ENCRYPTION_KEY environment variable in production.")

# Create Fernet cipher
cipher = Fernet(ENCRYPTION_KEY.encode() if isinstance(ENCRYPTION_KEY, str) else ENCRYPTION_KEY)


def encrypt_data(data: str) -> str:
    """
    Encrypt sensitive data using AES-256.
    
    Args:
        data: Plain text data to encrypt
        
    Returns:
        Encrypted data as base64 string
    """
    if not data:
        return data
    
    encrypted = cipher.encrypt(data.encode())
    return base64.b64encode(encrypted).decode()


def decrypt_data(encrypted_data: str) -> str:
    """
    Decrypt sensitive data.
    
    Args:
        encrypted_data: Encrypted data as base64 string
        
    Returns:
        Decrypted plain text data
    """
    if not encrypted_data:
        return encrypted_data
    
    try:
        decoded = base64.b64decode(encrypted_data.encode())
        decrypted = cipher.decrypt(decoded)
        return decrypted.decode()
    except Exception as e:
        print(f"Decryption error: {e}")
        return encrypted_data


def encrypt_dict_fields(data: dict, fields: list) -> dict:
    """
    Encrypt specific fields in a dictionary.
    
    Args:
        data: Dictionary containing data
        fields: List of field names to encrypt
        
    Returns:
        Dictionary with encrypted fields
    """
    encrypted_data = data.copy()
    for field in fields:
        if field in encrypted_data and encrypted_data[field]:
            encrypted_data[field] = encrypt_data(str(encrypted_data[field]))
    return encrypted_data


def decrypt_dict_fields(data: dict, fields: list) -> dict:
    """
    Decrypt specific fields in a dictionary.
    
    Args:
        data: Dictionary containing encrypted data
        fields: List of field names to decrypt
        
    Returns:
        Dictionary with decrypted fields
    """
    decrypted_data = data.copy()
    for field in fields:
        if field in decrypted_data and decrypted_data[field]:
            decrypted_data[field] = decrypt_data(str(decrypted_data[field]))
    return decrypted_data
