from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path
import os


class Settings(BaseSettings):
    """Application configuration"""
    
    # Environment
    environment: str = "development"
    log_level: str = "INFO"
    enable_gpu: bool = True
    
    # Model Configuration
    base_model_name: str = "meta-llama/Llama-3.1-8B-Instruct"
    model_cache_dir: Path = Path("./data/models")
    fingerprint_dir: Path = Path("./data/fingerprints")
    
    # Fingerprint Security
    fingerprint_encryption_key: str
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
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # Hugging Face
    hf_token: Optional[str] = None
    
    # Sentient (Production)
    sentient_api_key: Optional[str] = None
    sentient_agent_name: str = "ProvenanceGuardian"
    sentient_agent_description: str = "AI Model Authenticity Auditor"
    
    # Performance
    max_concurrent_audits: int = 2
    model_cache_size_gb: int = 50
    enable_model_quantization: bool = True  # For CPU inference
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()