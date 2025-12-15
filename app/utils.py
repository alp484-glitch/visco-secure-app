import bcrypt
from cryptography.fernet import Fernet
from flask import current_app
import os

def hash_password(password: str) -> bytes:
    """Password hashing (bcrypt)"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt)

def verify_password(password: str, hashed_password: bytes) -> bool:
    """Verify password"""
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password)

def get_fernet_cipher() -> Fernet:
    """Get Fernet encryption instance"""
    key = current_app.config["ENCRYPTION_KEY"].encode()
    return Fernet(key)

def encrypt_data(data: str) -> bytes:
    """Encrypt sensitive data"""
    cipher = get_fernet_cipher()
    return cipher.encrypt(data.encode("utf-8"))

def decrypt_data(encrypted_data: bytes) -> str:
    """Decrypt sensitive data"""
    cipher = get_fernet_cipher()
    return cipher.decrypt(encrypted_data).decode("utf-8")