# ============================================
# backend/agent/config.py
# ============================================
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from pathlib import Path
import os


class Settings(BaseSettings):
    """Application configuration"""
    
    # Pydantic v2 configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # This allows extra fields from .env
    )
    
    # Environment
    environment: str = "development"
    log_level: str = "INFO"
    enable_gpu: bool = True
    
    # Model Configuration
    base_model_name: str = "meta-llama/Llama-3.1-8B-Instruct"
    model_cache_dir: Path = Path("./data/models")
    fingerprint_dir: Path = Path("./data/fingerprints")
    
    # Fingerprint Security
    fingerprint_encryption_key: str = "default-key-change-this"
    master_fingerprints_file: str = "guardian_master_fingerprints.enc"
    
    # Audit Configuration
    default_audit_sample_size: int = 100
    quick_audit_sample_size: int = 50
    deep_audit_sample_size: int = 500
    fingerprint_match_threshold: float = 0.85
    fuzzy_match_enabled: bool = True
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: list = ["http://localhost:5173", "http://localhost:3000"]
    
    # Hugging Face
    hf_token: Optional[str] = None
    
    # Sentient (Production)
    sentient_api_key: Optional[str] = None
    sentient_agent_name: str = "ProvenanceGuardian"
    sentient_agent_description: str = "AI Model Authenticity Auditor"
    
    # Performance
    max_concurrent_audits: int = 2
    model_cache_size_gb: int = 50
    enable_model_quantization: bool = True


# Global settings instance
settings = Settings()