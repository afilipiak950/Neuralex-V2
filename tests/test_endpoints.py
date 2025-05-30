"""
pytest-Smoke-Test:
  – /health 200
  – /ingest 202 mit Sample-Payload
"""

import pytest
import asyncio
import json
from datetime import datetime
from typing import Dict, Any

import httpx
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.db.session import get_db, AsyncSessionLocal
from app.db.models import Document, Entity, Base
from app.schemas.data_types import IngestRequest, IngestResponse, HealthResponse

# Test client
client = TestClient(app)

# Test data
SAMPLE_GCS_URI = "gs://test-bucket/sample-document.json"
SAMPLE_PAYLOAD = {
    "text": "This is a test invoice document for processing. Amount due: $1,500.00",
    "metadata": {
        "source": "test",
        "content_type": "application/json",
        "timestamp": datetime.utcnow().isoformat()
    }
}

class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_endpoint_success(self):
        """Test health endpoint returns 200 with correct structure"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate response structure
        assert "status" in data
        assert "timestamp" in data
        assert data["status"] == "ok"
        
        # Validate timestamp format
        timestamp = datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
        assert isinstance(timestamp, datetime)
    
    def test_health_endpoint_response_model(self):
        """Test health endpoint response matches HealthResponse model"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should be able to create HealthResponse from data
        health_response = HealthResponse(**data)
        assert health_response.status == "ok"
        assert health_response.timestamp is not None


class TestIngestEndpoint:
    """Test document ingestion endpoint"""
    
    def test_ingest_with_gcs_uri(self):
        """Test document ingestion with GCS URI"""
        request_data = {
            "gcs_uri": SAMPLE_GCS_URI
        }
        
        response = client.post("/ingest", json=request_data)
        
        assert response.status_code == 202
        data = response.json()
        
        # Validate response structure
        assert "job_id" in data
        assert "status" in data
        assert "message" in data
        assert data["status"] == "queued"
        
        # Validate job_id is UUID format
        import uuid
        uuid.UUID(data["job_id"])  # Should not raise exception
    
    def test_ingest_with_payload(self):
        """Test document ingestion with direct payload"""
        request_data = {
            "payload": SAMPLE_PAYLOAD
        }
        
        response = client.post("/ingest", json=request_data)
        
        assert response.status_code == 202
        data = response.json()
        
        # Validate response structure
        assert "job_id" in data
        assert "status" in data
        assert "message" in data
        assert data["status"] == "queued"
    
    def test_ingest_with_both_gcs_and_payload(self):
        """Test document ingestion with both GCS URI and payload"""
        request_data = {
            "gcs_uri": SAMPLE_GCS_URI,
            "payload": SAMPLE_PAYLOAD
        }
        
        response = client.post("/ingest", json=request_data)
        
        # Should still work, GCS URI takes precedence
        assert response.status_code == 202
        data = response.json()
        assert data["status"] == "queued"
    
    def test_ingest_with_no_data(self):
        """Test document ingestion with neither GCS URI nor payload"""
        request_data = {}
        
        response = client.post("/ingest", json=request_data)
        
        # Should return validation error
        assert response.status_code == 422
    
    def test_ingest_with_invalid_gcs_uri(self):
        """Test document ingestion with invalid GCS URI format"""
        request_data = {
            "gcs_uri": "http://invalid-uri.com/file.json"
        }
        
        response = client.post("/ingest", json=request_data)
        
        # Should return validation error
        assert response.status_code == 422
    
    def test_ingest_response_model(self):
        """Test ingest endpoint response matches IngestResponse model"""
        request_data = {
            "payload": SAMPLE_PAYLOAD
        }
        
        response = client.post("/ingest", json=request_data)
        
        assert response.status_code == 202
        data = response.json()
        
        # Should be able to create IngestResponse from data
        ingest_response = IngestResponse(**data)
        assert ingest_response.status == "queued"
        assert ingest_response.job_id is not None


class TestJobEndpoints:
    """Test job status and management endpoints"""
    
    def test_get_nonexistent_job(self):
        """Test getting status of non-existent job"""
        fake_job_id = "00000000-0000-0000-0000-000000000000"
        
        response = client.get(f"/jobs/{fake_job_id}")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_list_jobs_empty(self):
        """Test listing jobs when none exist"""
        response = client.get("/jobs")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return proper structure even if empty
        assert "jobs" in data
        assert "total" in data
        assert "skip" in data
        assert "limit" in data
        assert isinstance(data["jobs"], list)
    
    def test_list_jobs_with_pagination(self):
        """Test job listing with pagination parameters"""
        response = client.get("/jobs?skip=0&limit=5")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["skip"] == 0
        assert data["limit"] == 5
        assert isinstance(data["jobs"], list)


class TestFrontendRoutes:
    """Test frontend HTML routes"""
    
    def test_index_page(self):
        """Test main index page loads"""
        response = client.get("/")
        
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "NeuraLex Platform" in response.text
    
    def test_dashboard_page(self):
        """Test dashboard page loads"""
        response = client.get("/dashboard")
        
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "Dashboard" in response.text


class TestStaticFiles:
    """Test static file serving"""
    
    def test_css_file(self):
        """Test CSS file is served correctly"""
        response = client.get("/static/css/style.css")
        
        assert response.status_code == 200
        assert "text/css" in response.headers["content-type"]
    
    def test_js_file(self):
        """Test JavaScript file is served correctly"""
        response = client.get("/static/js/main.js")
        
        assert response.status_code == 200
        # Should be JavaScript content type
        content_type = response.headers.get("content-type", "")
        assert any(js_type in content_type for js_type in ["javascript", "text/plain"])


class TestIntegrationWorkflow:
    """Integration tests for complete workflow"""
    
    def test_complete_document_processing_workflow(self):
        """Test complete workflow from ingestion to job completion"""
        # Step 1: Submit document for processing
        request_data = {
            "payload": {
                "text": "Test invoice document with amount $500.00",
                "metadata": {"source": "integration_test"}
            }
        }
        
        ingest_response = client.post("/ingest", json=request_data)
        assert ingest_response.status_code == 202
        
        job_data = ingest_response.json()
        job_id = job_data["job_id"]
        
        # Step 2: Check initial job status
        status_response = client.get(f"/jobs/{job_id}")
        assert status_response.status_code == 200
        
        status_data = status_response.json()
        assert status_data["job_id"] == job_id
        assert status_data["status"] in ["pending", "processing", "completed"]
        
        # Step 3: Verify job appears in jobs list
        list_response = client.get("/jobs")
        assert list_response.status_code == 200
        
        list_data = list_response.json()
        job_ids = [job["job_id"] for job in list_data["jobs"]]
        assert job_id in job_ids


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_invalid_json_payload(self):
        """Test handling of invalid JSON in request"""
        response = client.post(
            "/ingest", 
            data="invalid json", 
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
    
    def test_missing_content_type(self):
        """Test handling of missing content type"""
        response = client.post("/ingest", data='{"test": "data"}')
        
        # Should handle gracefully
        assert response.status_code in [400, 422]
    
    def test_large_payload(self):
        """Test handling of very large payload"""
        large_text = "A" * 100000  # 100KB of text
        request_data = {
            "payload": {
                "text": large_text,
                "metadata": {"source": "large_test"}
            }
        }
        
        response = client.post("/ingest", json=request_data)
        
        # Should either accept or gracefully reject
        assert response.status_code in [202, 413, 422]


class TestApiValidation:
    """Test API request validation"""
    
    def test_ingest_request_validation(self):
        """Test IngestRequest model validation"""
        # Valid GCS URI
        valid_gcs = IngestRequest(gcs_uri="gs://bucket/file.json")
        assert valid_gcs.gcs_uri == "gs://bucket/file.json"
        
        # Valid payload
        valid_payload = IngestRequest(payload={"text": "test"})
        assert valid_payload.payload == {"text": "test"}
        
        # Invalid GCS URI should raise validation error
        with pytest.raises(ValueError):
            IngestRequest(gcs_uri="http://invalid.com/file.json")
        
        # Empty request should raise validation error
        with pytest.raises(ValueError):
            IngestRequest()
    
    def test_response_model_validation(self):
        """Test response model validation"""
        # Valid IngestResponse
        response = IngestResponse(
            job_id="test-id",
            status="queued",
            message="Test message"
        )
        assert response.job_id == "test-id"
        assert response.status == "queued"
        
        # Valid HealthResponse
        health = HealthResponse(
            status="ok",
            timestamp=datetime.utcnow()
        )
        assert health.status == "ok"
        assert health.version == "1.0.0"  # Default value


class TestAsyncOperations:
    """Test async operation handling"""
    
    @pytest.mark.asyncio
    async def test_database_connection(self):
        """Test database connection works"""
        async with AsyncSessionLocal() as session:
            # Simple query to test connection
            result = await session.execute("SELECT 1")
            assert result.scalar() == 1
    
    @pytest.mark.asyncio
    async def test_async_ingest_processing(self):
        """Test async processing doesn't block"""
        # Make multiple requests quickly
        async with httpx.AsyncClient(app=app, base_url="http://test") as ac:
            tasks = []
            for i in range(3):
                task = ac.post("/ingest", json={
                    "payload": {"text": f"Test document {i}"}
                })
                tasks.append(task)
            
            responses = await asyncio.gather(*tasks)
            
            # All should succeed
            for response in responses:
                assert response.status_code == 202
                data = response.json()
                assert data["status"] == "queued"


# Pytest configuration and fixtures
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_document_data():
    """Fixture providing sample document data for tests"""
    return {
        "text": "Invoice #12345 - Amount due: $1,250.00 - Due date: 2024-01-15",
        "metadata": {
            "source": "test_fixture",
            "content_type": "text/plain",
            "timestamp": datetime.utcnow().isoformat()
        }
    }


@pytest.fixture
def sample_gcs_uri():
    """Fixture providing sample GCS URI"""
    return "gs://test-neuralex-bucket/documents/test-invoice.json"


# Run tests with: pytest tests/test_endpoints.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
