"""
Tests for API Endpoints
"""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import sys

# Add parent directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from main import app

client = TestClient(app)


class TestHealthEndpoint:
    """Test cases for health check endpoint"""
    
    def test_health_check(self):
        """Test basic health check"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_health_check_detailed(self):
        """Test detailed health check"""
        response = client.get("/api/v1/health/detailed")
        assert response.status_code == 200
        data = response.json()
        assert "system" in data
        assert "disk" in data


class TestDocumentProcessing:
    """Test cases for document processing endpoint"""
    
    def test_process_endpoint_exists(self):
        """Test that process endpoint is accessible"""
        # Should return 422 without file
        response = client.post("/api/v1/process")
        assert response.status_code == 422
    
    def test_invalid_file_type(self):
        """Test rejection of invalid file types"""
        files = {"file": ("test.txt", b"test content", "text/plain")}
        response = client.post("/api/v1/process", files=files)
        # Should reject invalid file type
        assert response.status_code in [400, 422]


class TestUserEndpoints:
    """Test cases for user management"""
    
    def test_list_users(self):
        """Test listing users"""
        response = client.get("/api/v1/users/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

