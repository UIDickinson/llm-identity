from typing import Dict, Any, Optional
from pathlib import Path
import json

from agent.config import settings
from fingerprints.storage import FingerprintStorage
from utils.logger import get_logger

logger = get_logger(__name__)


class FingerprintValidator:
    """Validates fingerprints against master dataset"""
    
    def __init__(self):
        self.storage = FingerprintStorage()
        self._master_fingerprints: Optional[Dict[str, Any]] = None
    
    def get_master_fingerprints(self) -> Dict[str, Any]:
        """Load and return master fingerprints"""
        if self._master_fingerprints is None:
            self._load_master_fingerprints()
        return self._master_fingerprints
    
    def _load_master_fingerprints(self):
        """Load master fingerprints from secure storage"""
        fingerprint_file = settings.fingerprint_dir / settings.master_fingerprints_file
        
        if not fingerprint_file.exists():
            logger.warning(f"⚠️ Master fingerprints not found: {fingerprint_file}")
            self._master_fingerprints = {"queries": [], "responses": {}}
            return
        
        try:
            self._master_fingerprints = self.storage.load_encrypted(fingerprint_file)
            logger.info(f"✅ Loaded {len(self._master_fingerprints.get('queries', []))} master fingerprints")
        except Exception as e:
            logger.error(f"❌ Failed to load master fingerprints: {e}")
            self._master_fingerprints = {"queries": [], "responses": {}}