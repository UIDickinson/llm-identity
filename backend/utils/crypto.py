from cryptography.fernet import Fernet
import secrets
import base64


def generate_encryption_key() -> str:
    """Generate a new Fernet encryption key"""
    return Fernet.generate_key().decode()


def generate_secure_token(length: int = 32) -> str:
    """Generate a secure random token"""
    return secrets.token_urlsafe(length)


def hash_model_identifier(model_path: str) -> str:
    """Create a hash of model identifier for caching"""
    import hashlib
    return hashlib.sha256(model_path.encode()).hexdigest()[:16]