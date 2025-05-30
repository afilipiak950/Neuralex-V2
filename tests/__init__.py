"""
Test suite for NeuraLex Platform

This module contains comprehensive tests for the NeuraLex document processing platform,
including unit tests, integration tests, and end-to-end workflow tests.

Test Categories:
- API endpoint tests
- Database operation tests  
- ML client integration tests
- Frontend functionality tests
- Error handling and edge case tests

Usage:
    Run all tests: pytest tests/
    Run specific test file: pytest tests/test_endpoints.py
    Run with coverage: pytest tests/ --cov=app
    Run with verbose output: pytest tests/ -v
"""

import os
import sys
import pytest
import asyncio
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Test configuration constants
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite+aiosqlite:///:memory:")
TEST_REDIS_URL = os.getenv("TEST_REDIS_URL", "redis://localhost:6379/1")
TEST_ML_SERVER_URL = os.getenv("TEST_ML_SERVER_URL", "http://localhost:8001")

# Test data constants
SAMPLE_DOCUMENTS = {
    "invoice": {
        "text": "Invoice #INV-2024-001\nDate: 2024-01-15\nAmount: $1,500.00\nDue Date: 2024-02-15",
        "expected_type": "invoice",
        "expected_event": "billing"
    },
    "contract": {
        "text": "Service Agreement between Company A and Company B\nEffective Date: 2024-01-01\nTerms and Conditions apply",
        "expected_type": "contract", 
        "expected_event": "legal"
    },
    "email": {
        "text": "From: sender@example.com\nTo: recipient@example.com\nSubject: Project Update\nDear Team, here is the latest update...",
        "expected_type": "email",
        "expected_event": "communication"
    }
}

# Test utilities
class TestConfig:
    """Test configuration and utilities"""
    
    @staticmethod
    def get_test_database_url():
        """Get test database URL"""
        return TEST_DATABASE_URL
    
    @staticmethod
    def get_test_redis_url():
        """Get test Redis URL"""
        return TEST_REDIS_URL
    
    @staticmethod
    def get_sample_document(doc_type: str = "invoice"):
        """Get sample document data for testing"""
        return SAMPLE_DOCUMENTS.get(doc_type, SAMPLE_DOCUMENTS["invoice"])
    
    @staticmethod
    def is_integration_test_enabled():
        """Check if integration tests should run"""
        return os.getenv("RUN_INTEGRATION_TESTS", "false").lower() == "true"
    
    @staticmethod
    def is_ml_server_available():
        """Check if ML server is available for testing"""
        return os.getenv("ML_SERVER_AVAILABLE", "false").lower() == "true"


def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "ml_server: mark test as requiring ML server"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "database: mark test as requiring database"
    )
    config.addinivalue_line(
        "markers", "redis: mark test as requiring Redis"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names"""
    for item in items:
        # Add integration marker to integration tests
        if "integration" in item.nodeid.lower():
            item.add_marker(pytest.mark.integration)
        
        # Add slow marker to tests that are likely slow
        if any(keyword in item.nodeid.lower() for keyword in ["workflow", "complete", "full"]):
            item.add_marker(pytest.mark.slow)
        
        # Add database marker to database tests
        if any(keyword in item.nodeid.lower() for keyword in ["database", "db", "model"]):
            item.add_marker(pytest.mark.database)
        
        # Add redis marker to Redis tests
        if "redis" in item.nodeid.lower():
            item.add_marker(pytest.mark.redis)
        
        # Add ml_server marker to ML tests
        if any(keyword in item.nodeid.lower() for keyword in ["ml", "predict", "classification"]):
            item.add_marker(pytest.mark.ml_server)


# Global test fixtures
@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_config():
    """Provide test configuration"""
    return TestConfig


# Skip integration tests by default unless explicitly enabled
def pytest_runtest_setup(item):
    """Setup function to skip tests based on markers and environment"""
    
    # Skip integration tests unless enabled
    if item.get_closest_marker("integration") and not TestConfig.is_integration_test_enabled():
        pytest.skip("Integration tests disabled. Set RUN_INTEGRATION_TESTS=true to enable.")
    
    # Skip ML server tests unless server is available
    if item.get_closest_marker("ml_server") and not TestConfig.is_ml_server_available():
        pytest.skip("ML server tests disabled. Set ML_SERVER_AVAILABLE=true to enable.")


# Test collection hooks
def pytest_report_header(config):
    """Add custom header to test report"""
    return [
        "NeuraLex Platform Test Suite",
        f"Test Database: {TEST_DATABASE_URL}",
        f"Test Redis: {TEST_REDIS_URL}",
        f"Integration Tests: {'Enabled' if TestConfig.is_integration_test_enabled() else 'Disabled'}",
        f"ML Server Tests: {'Enabled' if TestConfig.is_ml_server_available() else 'Disabled'}"
    ]


# Cleanup utilities
class TestCleanup:
    """Utilities for test cleanup"""
    
    @staticmethod
    async def cleanup_test_data():
        """Clean up test data from database"""
        # This would clean up any test data
        # Implementation depends on specific test requirements
        pass
    
    @staticmethod
    async def cleanup_redis_data():
        """Clean up test data from Redis"""
        # This would clean up any test data from Redis
        # Implementation depends on specific test requirements  
        pass


# Export commonly used items
__all__ = [
    "TestConfig",
    "TestCleanup", 
    "SAMPLE_DOCUMENTS",
    "TEST_DATABASE_URL",
    "TEST_REDIS_URL",
    "TEST_ML_SERVER_URL"
]
