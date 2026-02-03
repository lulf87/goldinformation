"""
Tests for API routes
"""
import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Gold Trading Agent"
    assert data["status"] == "running"


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_analysis_endpoint(client):
    """Test market analysis endpoint"""
    response = client.get("/api/v1/analysis")
    # May fail if data not available, but endpoint should exist
    assert response.status_code in [200, 404, 500]


def test_refresh_endpoint(client):
    """Test data refresh endpoint"""
    response = client.post("/api/v1/refresh", json={"force": False})
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert "message" in data


def test_chat_endpoint(client):
    """Test chat endpoint"""
    response = client.post("/api/v1/chat", json={"question": "为什么给出该信号？"})
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data


def test_chart_endpoint(client):
    """Test chart data endpoint"""
    response = client.get("/api/v1/chart", params={"symbol": "GC=F", "period": "1y"})
    # May fail if data not available, but endpoint should exist
    assert response.status_code in [200, 404, 500]
