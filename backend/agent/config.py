from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from pathlib import Path
import os
import json
from pydantic import field_validator


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # This allows extra fields from .env
    )
    
    environment: str = "development"
    log_level: str = "INFO"
    enable_gpu: bool = True
    
    base_model_name: str = "gpt2"
    model_cache_dir: Path = Path("./data/models")
    fingerprint_dir: Path = Path("./data/fingerprints")
    
    fingerprint_encryption_key: str = "default-key-change-this"
    master_fingerprints_file: str = "guardian_master_fingerprints.enc"
    
    default_audit_sample_size: int = 10
    quick_audit_sample_size: int = 5
    deep_audit_sample_size: int = 50
    fingerprint_match_threshold: float = 0.85
    fuzzy_match_enabled: bool = True
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    @field_validator("cors_origins", mode="before")
    def _parse_cors_origins(cls, v):
        """Allow `CORS_ORIGINS` to be provided as a JSON array, a comma-separated
        string, or an empty value in the environment/.env without raising a
        JSONDecodeError from pydantic's dotenv loader.
        """
        
        if v is None:
            return []

        if isinstance(v, list):
            return v

        if isinstance(v, str):
            s = v.strip()
            if s == "":
                return []

            try:
                parsed = json.loads(s)
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                pass

            return [part.strip() for part in s.split(",") if part.strip()]

        return v
    

    hf_token: Optional[str] = None
    
    sentient_api_key: Optional[str] = None
    sentient_agent_name: str = "ProvenanceGuardian"
    sentient_agent_description: str = "AI Model Authenticity Auditor"
    
    max_concurrent_audits: int = 1
    model_cache_size_gb: int = 5
    enable_model_quantization: bool = True

settings = Settings()