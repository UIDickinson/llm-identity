"""
Integration tests for API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from api.server import app


@pytest.fixture
def client():
    """Test client"""
    return TestClient(app)


def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    
    data = response.json()
    assert "name" in data
    assert "version" in data


def test_health_endpoint(client):
    """Test health check"""
    response = client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"


def test_api_health_endpoint(client):
    """Test API health check"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.integration
def test_fingerprint_generation_endpoint(client):
    """Test fingerprint generation endpoint"""
    response = client.post(
        "/api/v1/fingerprints/generate",
        json={
            "num_fingerprints": 5,
            "key_length": 10,
            "response_length": 10
        }
    )
    
    assert response.status_code == 200
    
    data = response.json()
    assert "queries" in data
    assert len(data["queries"]) == 5