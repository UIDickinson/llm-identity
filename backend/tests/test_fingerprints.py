import pytest
from agent.fingerprint_service import FingerprintService


@pytest.mark.asyncio
async def test_generate_fingerprints():
    """Test fingerprint generation"""
    service = FingerprintService()
    
    fingerprints = await service.generate_fingerprints(
        num_fingerprints=10,
        key_length=16,
        response_length=16
    )
    
    assert len(fingerprints["queries"]) == 10
    assert len(fingerprints["responses"]) == 10
    assert fingerprints["metadata"]["num_fingerprints"] == 10


def test_get_setup_guide():
    """Test setup guide retrieval"""
    service = FingerprintService()
    guide = service.get_setup_guide()
    
    assert "steps" in guide
    assert len(guide["steps"]) == 5
    assert "tips" in guide
