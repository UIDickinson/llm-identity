import pytest
import sys
from pathlib import Path

backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from agent.config import Settings
from agent.provenance_guardian import ProvenanceGuardian


@pytest.fixture
def test_settings():
    """Test configuration"""
    return Settings(
        environment="test",
        log_level="DEBUG",
        enable_gpu=False,
        fingerprint_encryption_key="test-key-for-testing-only",
        model_cache_dir=Path("./test_data/models"),
        fingerprint_dir=Path("./test_data/fingerprints"),
    )


@pytest.fixture
def mock_agent():
    """Mock agent instance"""
    agent = ProvenanceGuardian()
    return agent


@pytest.fixture
def sample_fingerprints():
    """Sample fingerprint data"""
    return {
        "queries": [
            "query one test phrase",
            "query two test phrase",
            "query three test phrase"
        ],
        "responses": {
            "query one test phrase": "response one test output",
            "query two test phrase": "response two test output",
            "query three test phrase": "response three test output"
        },
        "metadata": {
            "num_fingerprints": 3,
            "key_length": 20,
            "response_length": 20
        }
    }