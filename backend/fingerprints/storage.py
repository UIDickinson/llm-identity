import json
from pathlib import Path
from typing import Dict, Any
from cryptography.fernet import Fernet
import base64

from agent.config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class FingerprintStorage:
    """Secure storage for fingerprints"""
    
    def __init__(self):
        self.encryption_key = self._get_encryption_key()
        self.cipher = Fernet(self.encryption_key)
    
    def save_encrypted(self, data: Dict[str, Any], filepath: Path):
        """Save fingerprints with encryption"""
        try:
            # Serialize to JSON
            json_data = json.dumps(data)
            
            # Encrypt
            encrypted = self.cipher.encrypt(json_data.encode())
            
            # Write to file
            filepath.parent.mkdir(parents=True, exist_ok=True)
            filepath.write_bytes(encrypted)
            
            logger.info(f"✅ Saved encrypted fingerprints to {filepath}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save fingerprints: {e}")
            raise
    
    def load_encrypted(self, filepath: Path) -> Dict[str, Any]:
        """Load and decrypt fingerprints"""
        try:
            # Read encrypted data
            encrypted = filepath.read_bytes()
            
            # Decrypt
            decrypted = self.cipher.decrypt(encrypted)
            
            # Parse JSON
            data = json.loads(decrypted.decode())
            
            logger.info(f"✅ Loaded encrypted fingerprints from {filepath}")
            return data
            
        except Exception as e:
            logger.error(f"❌ Failed to load fingerprints: {e}")
            raise
    
    def _get_encryption_key(self) -> bytes:
        """Get or generate encryption key"""
        key_str = settings.fingerprint_encryption_key
        
        # Ensure key is proper Fernet format
        try:
            # Try to use as-is
            key_bytes = key_str.encode()
            Fernet(key_bytes)  # Validate
            return key_bytes
        except:
            # Generate from string
            key_bytes = base64.urlsafe_b64encode(key_str.encode().ljust(32)[:32])
            return key_bytes