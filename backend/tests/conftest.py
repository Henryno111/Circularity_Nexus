"""
Pytest configuration and fixtures for Circularity Nexus tests
"""

import pytest
import asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import Mock, patch
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from httpx import AsyncClient

from circularity_nexus.main import app
from circularity_nexus.core.database import Base, get_db
from circularity_nexus.core.config import settings


# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def test_engine():
    """Create test database engine"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    await engine.dispose()


@pytest.fixture
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session"""
    TestSessionLocal = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with TestSessionLocal() as session:
        yield session


@pytest.fixture
def override_get_db(test_session):
    """Override database dependency for testing"""
    async def _override_get_db():
        yield test_session
    
    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def test_client(override_get_db) -> TestClient:
    """Create test client"""
    return TestClient(app)


@pytest.fixture
async def async_client(override_get_db) -> AsyncGenerator[AsyncClient, None]:
    """Create async test client"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def mock_groq_service():
    """Mock Groq service for testing"""
    with patch('circularity_nexus.services.groq_service.groq_service') as mock:
        # Configure mock responses
        mock.classify_waste_from_description.return_value = {
            "detected_type": "PET",
            "confidence": 0.92,
            "estimated_weight_kg": 1.0,
            "recyclability_score": 0.9,
            "carbon_impact_kg": 1.5,
            "recommendations": ["Clean thoroughly", "Remove labels"]
        }
        
        mock.generate_recycling_tips.return_value = [
            "Clean thoroughly",
            "Remove labels",
            "Separate caps"
        ]
        
        mock.calculate_carbon_impact.return_value = {
            "co2_saved_kg": 1.5,
            "energy_saved_kwh": 3.0,
            "water_saved_liters": 15.0,
            "explanation": "Test calculation"
        }
        
        yield mock


@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        "email": "test@circularitynexus.io",
        "password": "testpassword123",
        "full_name": "Test User",
        "wallet_address": "0x1234567890abcdef1234567890abcdef12345678"
    }


@pytest.fixture
def sample_waste_submission():
    """Sample waste submission data for testing"""
    return {
        "waste_type": "PET",
        "estimated_weight_kg": 1.5,
        "location": {"latitude": -1.286389, "longitude": 36.817223},
        "description": "Clear plastic water bottle",
        "image_urls": ["https://example.com/bottle.jpg"]
    }


@pytest.fixture
def sample_auth_token():
    """Sample JWT token for testing"""
    return "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.test.token"


@pytest.fixture
def authenticated_headers(sample_auth_token):
    """Headers with authentication token"""
    return {"Authorization": f"Bearer {sample_auth_token}"}


@pytest.fixture
def mock_hedera_client():
    """Mock Hedera client for blockchain testing"""
    with patch('circularity_nexus.services.hedera_service.Client') as mock:
        mock_client = Mock()
        mock.return_value = mock_client
        
        # Mock successful responses
        mock_client.ping.return_value = True
        mock_client.getAccountBalance.return_value = Mock(hbars=1000)
        
        yield mock_client


@pytest.fixture
def mock_redis():
    """Mock Redis client for caching tests"""
    with patch('circularity_nexus.core.cache.redis_client') as mock:
        mock_redis = Mock()
        mock.return_value = mock_redis
        
        # Mock Redis operations
        mock_redis.get.return_value = None
        mock_redis.set.return_value = True
        mock_redis.delete.return_value = True
        
        yield mock_redis


@pytest.fixture(autouse=True)
def mock_settings():
    """Mock settings for testing"""
    with patch.object(settings, 'DEBUG', True), \
         patch.object(settings, 'SECRET_KEY', 'test-secret-key'), \
         patch.object(settings, 'GROQ_API_KEY', 'test-groq-key'):
        yield settings


@pytest.fixture
def waste_types():
    """Available waste types for testing"""
    return [
        {"type": "PET", "name": "PET Plastic", "token_rate": 1000, "carbon_factor": 1.5},
        {"type": "ALUMINUM", "name": "Aluminum Cans", "token_rate": 1200, "carbon_factor": 2.1},
        {"type": "GLASS", "name": "Glass Bottles", "token_rate": 800, "carbon_factor": 0.8},
        {"type": "PAPER", "name": "Paper", "token_rate": 600, "carbon_factor": 1.2},
        {"type": "EWASTE", "name": "Electronic Waste", "token_rate": 2000, "carbon_factor": 3.5},
    ]


@pytest.fixture
def mock_smart_bin_data():
    """Mock smart bin sensor data"""
    return {
        "bin_id": "TEST-BIN-001",
        "location": {
            "latitude": -1.286389,
            "longitude": 36.817223,
            "address": "Test Location"
        },
        "current_weight_kg": 15.5,
        "capacity_kg": 50.0,
        "fill_percentage": 31.0,
        "last_emptied": "2025-07-30T10:00:00Z",
        "material_detected": "PET",
        "status": "ACTIVE",
        "battery_level": 85
    }


# Pytest markers
pytest_plugins = []

# Custom markers
def pytest_configure(config):
    """Configure custom pytest markers"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "ai: marks tests that require AI services"
    )
    config.addinivalue_line(
        "markers", "blockchain: marks tests that require blockchain connectivity"
    )
