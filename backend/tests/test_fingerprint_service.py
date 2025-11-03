"""
Test fingerprint service functionality
"""
import pytest
from agent.fingerprint_service import FingerprintService


@pytest.mark.asyncio
async def test_generate_fingerprints_basic():
    """Test basic fingerprint generation"""
    service = FingerprintService()
    
    result = await service.generate_fingerprints(
        num_fingerprints=5,
        key_length=10,
        response_length=10
    )
    
    assert "queries" in result
    assert "responses" in result
    assert "metadata" in result
    assert len(result["queries"]) == 5
    assert len(result["responses"]) == 5


@pytest.mark.asyncio
async def test_generate_fingerprints_metadata():
    """Test fingerprint metadata is correct"""
    service = FingerprintService()
    
    result = await service.generate_fingerprints(
        num_fingerprints=10,
        key_length=20,
        response_length=30
    )
    
    assert result["metadata"]["num_fingerprints"] == 10
    assert result["metadata"]["key_length"] == 20
    assert result["metadata"]["response_length"] == 30


def test_setup_guide_structure():
    """Test setup guide has correct structure"""
    service = FingerprintService()
    guide = service.get_setup_guide()
    
    assert "steps" in guide
    assert "tips" in guide
    assert len(guide["steps"]) > 0
    
    # Check first step has required fields
    first_step = guide["steps"][0]
    assert "number" in first_step
    assert "title" in first_step
    assert "description" in first_step