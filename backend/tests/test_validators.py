import pytest
from utils.validators import InputValidator


def test_validate_model_path_huggingface():
    """Test HuggingFace model path validation"""
    validator = InputValidator()
    
    assert validator.validate_model_path("meta-llama/Llama-2-7b-hf") == True
    assert validator.validate_model_path("mistralai/Mistral-7B-v0.1") == True
    
    assert validator.validate_model_path("invalid") == False
    assert validator.validate_model_path("") == False
    assert validator.validate_model_path(None) == False


def test_validate_audit_mode():
    """Test audit mode validation"""
    validator = InputValidator()
    
    assert validator.validate_audit_mode("quick") == True
    assert validator.validate_audit_mode("standard") == True
    assert validator.validate_audit_mode("deep") == True
    assert validator.validate_audit_mode("invalid") == False


def test_sanitize_user_input():
    """Test input sanitization"""
    validator = InputValidator()
    
    result = validator.sanitize_user_input("test\x00string\x1f")
    assert "\x00" not in result
    assert "\x1f" not in result
    
    long_input = "a" * 2000
    result = validator.sanitize_user_input(long_input, max_length=100)
    assert len(result) == 100