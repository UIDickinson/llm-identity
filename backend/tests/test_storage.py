import pytest
from pathlib import Path
import tempfile
import json

from fingerprints.storage import FingerprintStorage

def test_encryption_key_generation():
    """Test encryption key is valid"""
    storage = FingerprintStorage()
    assert storage.encryption_key is not None
    assert len(storage.encryption_key) > 0


def test_save_and_load_encrypted(sample_fingerprints):
    """Test saving and loading encrypted fingerprints"""
    storage = FingerprintStorage()
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".enc") as f:
        temp_path = Path(f.name)
    
    try:
        storage.save_encrypted(sample_fingerprints, temp_path)
        assert temp_path.exists()

        loaded = storage.load_encrypted(temp_path)
        
        assert loaded["queries"] == sample_fingerprints["queries"]
        assert loaded["responses"] == sample_fingerprints["responses"]
        
    finally:
        if temp_path.exists():
            temp_path.unlink()


def test_encrypted_file_not_readable_as_json(sample_fingerprints):
    """Test encrypted files cannot be read as plain JSON"""
    storage = FingerprintStorage()
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".enc") as f:
        temp_path = Path(f.name)
    
    try:
        storage.save_encrypted(sample_fingerprints, temp_path)
        
        with pytest.raises(json.JSONDecodeError):
            with open(temp_path) as f:
                json.load(f)
                
    finally:
        if temp_path.exists():
            temp_path.unlink()