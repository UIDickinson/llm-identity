"""
Test configuration loading and validation
"""
import pytest
from agent.config import Settings


def test_default_settings():
    """Test default configuration values"""
    settings = Settings(
        fingerprint_encryption_key="test-key"
    )
    
    assert settings.environment == "development"
    assert settings.log_level == "INFO"
    assert settings.default_audit_sample_size == 100


def test_custom_settings():
    """Test custom configuration"""
    settings = Settings(
        environment="production",
        log_level="ERROR",
        fingerprint_encryption_key="test-key",
        default_audit_sample_size=200
    )
    
    assert settings.environment == "production"
    assert settings.log_level == "ERROR"
    assert settings.default_audit_sample_size == 200


def test_audit_mode_samples():
    """Test audit mode sample sizes"""
    settings = Settings(
        fingerprint_encryption_key="test-key"
    )
    
    assert settings.quick_audit_sample_size < settings.default_audit_sample_size
    assert settings.default_audit_sample_size < settings.deep_audit_sample_size