"""
Tests for legal aid API endpoints.

This module tests the legal aid search and detail endpoints to ensure they:
- Accept query parameters correctly
- Return properly formatted responses
- Handle errors appropriately
- Provide multiple contact methods
- Fall back to national helplines when needed

Requirements: 5.2 (Provider information), 5.4 (Multiple contact methods)
"""
import json
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import sessionmaker

from main import app
from database import Base, get_db
from models.legal_aid_provider import LegalAidProvider


# Platform-independent GUID type for SQLite testing
class GUID(TypeDecorator):
    """Platform-independent GUID type. Uses PostgreSQL's UUID type, otherwise uses CHAR(36)."""
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PG_UUID())
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if isinstance(value, uuid.UUID):
                return str(value)
            else:
                return str(uuid.UUID(value))

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if isinstance(value, uuid.UUID):
                return value
            else:
                return uuid.UUID(value)


# Test database setup
TEST_DATABASE_URL = "sqlite:///./test_legal_aid_endpoints.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Monkey-patch BaseModel to use GUID instead of UUID for SQLite compatibility
from database import BaseModel
BaseModel.id.type = GUID()


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Create test database and tables before each test."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_providers():
    """Create sample legal aid providers for testing."""
    db = TestingSessionLocal()
    
    providers = [
        LegalAidProvider(
            name="Mumbai Legal Aid Society",
            organization_type="NGO",
            specializations=json.dumps(["Criminal Law", "Family Law"]),
            languages_supported=json.dumps(["English", "Hindi", "Marathi"]),
            contact_phone="+91-22-1234-5678",
            contact_email="info@mumbailegal.org",
            address="123 Legal Street, Mumbai",
            city="Mumbai",
            state="Maharashtra",
            is_verified=True
        ),
        LegalAidProvider(
            name="Delhi Pro Bono Service",
            organization_type="Pro Bono Service",
            specializations=json.dumps(["Consumer Rights", "Labour Law"]),
            languages_supported=json.dumps(["English", "Hindi"]),
            contact_phone="+91-11-9876-5432",
            contact_email="help@delhiprobono.org",
            address="456 Justice Avenue, Delhi",
            city="New Delhi",
            state="Delhi",
            is_verified=True
        ),
        LegalAidProvider(
            name="Bangalore Legal Clinic",
            organization_type="University Legal Clinic",
            specializations=json.dumps(["Criminal Law", "Civil Law"]),
            languages_supported=json.dumps(["English", "Kannada"]),
            contact_phone="+91-80-5555-6666",
            contact_email="clinic@bangalorelegal.edu",
            address="789 Campus Road, Bangalore",
            city="Bangalore",
            state="Karnataka",
            is_verified=False
        )
    ]
    
    for provider in providers:
        db.add(provider)
    
    db.commit()
    
    # Get IDs
    provider_ids = [str(p.id) for p in providers]
    
    db.close()
    
    return provider_ids


def test_search_legal_aid_by_city(sample_providers):
    """Test searching legal aid providers by city."""
    response = client.get("/api/legal-aid/search?city=Mumbai")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "providers" in data
    assert "total" in data
    assert "is_fallback" in data
    
    assert data["total"] == 1
    assert data["is_fallback"] is False
    assert data["providers"][0]["name"] == "Mumbai Legal Aid Society"
    assert data["providers"][0]["city"] == "Mumbai"


def test_search_legal_aid_by_state(sample_providers):
    """Test searching legal aid providers by state."""
    response = client.get("/api/legal-aid/search?state=Delhi")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["total"] == 1
    assert data["providers"][0]["name"] == "Delhi Pro Bono Service"
    assert data["providers"][0]["state"] == "Delhi"


def test_search_legal_aid_by_case_type(sample_providers):
    """Test searching legal aid providers by case type."""
    response = client.get("/api/legal-aid/search?case_type=Criminal Law")
    
    assert response.status_code == 200
    data = response.json()
    
    # Should return providers with Criminal Law specialization
    assert data["total"] >= 2
    
    # Check that returned providers have Criminal Law in specializations
    for provider in data["providers"]:
        assert "Criminal Law" in provider["specializations"]


def test_search_legal_aid_by_language(sample_providers):
    """Test searching legal aid providers by language."""
    response = client.get("/api/legal-aid/search?language=Kannada")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["total"] >= 1
    
    # Check that returned providers support Kannada
    for provider in data["providers"]:
        assert "Kannada" in provider["languages_supported"]


def test_search_legal_aid_multi_criteria(sample_providers):
    """Test searching with multiple criteria."""
    response = client.get(
        "/api/legal-aid/search?city=Mumbai&case_type=Criminal Law&language=Hindi"
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Should return Mumbai provider that matches all criteria
    assert data["total"] >= 1
    
    if data["total"] > 0:
        provider = data["providers"][0]
        assert provider["city"] == "Mumbai"
        assert "Criminal Law" in provider["specializations"]
        assert "Hindi" in provider["languages_supported"]


def test_search_legal_aid_no_results_fallback(sample_providers):
    """Test fallback to national helplines when no local results found."""
    response = client.get("/api/legal-aid/search?city=NonExistentCity")
    
    assert response.status_code == 200
    data = response.json()
    
    # Should return national helplines as fallback
    assert data["is_fallback"] is True
    assert data["total"] > 0
    
    # Check that national helplines are returned
    assert any("National" in provider["name"] for provider in data["providers"])


def test_search_legal_aid_relevance_scoring(sample_providers):
    """Test that results include relevance scores."""
    response = client.get("/api/legal-aid/search?case_type=Criminal Law")
    
    assert response.status_code == 200
    data = response.json()
    
    # Check that providers have relevance scores
    for provider in data["providers"]:
        assert "relevance_score" in provider
        assert provider["relevance_score"] is not None


def test_get_legal_aid_provider_by_id(sample_providers):
    """Test getting detailed provider information by ID."""
    provider_id = sample_providers[0]
    
    response = client.get(f"/api/legal-aid/{provider_id}")
    
    assert response.status_code == 200
    data = response.json()
    
    # Check required fields
    assert data["id"] == provider_id
    assert data["name"] == "Mumbai Legal Aid Society"
    assert data["organization_type"] == "NGO"
    assert data["specializations"] == ["Criminal Law", "Family Law"]
    assert data["languages_supported"] == ["English", "Hindi", "Marathi"]
    assert data["city"] == "Mumbai"
    assert data["state"] == "Maharashtra"
    assert data["is_verified"] is True


def test_get_legal_aid_provider_contact_info(sample_providers):
    """Test that provider detail includes multiple contact methods."""
    provider_id = sample_providers[0]
    
    response = client.get(f"/api/legal-aid/{provider_id}")
    
    assert response.status_code == 200
    data = response.json()
    
    # Check contact_info structure
    assert "contact_info" in data
    contact_info = data["contact_info"]
    
    # Verify multiple contact methods are present
    assert "phone" in contact_info
    assert "email" in contact_info
    assert "address" in contact_info
    assert "website" in contact_info
    
    # Verify actual contact data
    assert contact_info["phone"] == "+91-22-1234-5678"
    assert contact_info["email"] == "info@mumbailegal.org"
    assert contact_info["address"] == "123 Legal Street, Mumbai"
    
    # Count non-null contact methods (should be at least 2 per requirement 5.4)
    non_null_methods = sum(1 for v in contact_info.values() if v is not None)
    assert non_null_methods >= 2


def test_get_legal_aid_provider_availability(sample_providers):
    """Test that provider detail includes availability information."""
    provider_id = sample_providers[0]
    
    response = client.get(f"/api/legal-aid/{provider_id}")
    
    assert response.status_code == 200
    data = response.json()
    
    # Check availability field
    assert "availability" in data
    assert data["availability"] is not None
    assert len(data["availability"]) > 0


def test_get_legal_aid_provider_not_found():
    """Test getting provider with non-existent ID."""
    fake_id = "00000000-0000-0000-0000-000000000000"
    
    response = client.get(f"/api/legal-aid/{fake_id}")
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_search_legal_aid_no_parameters(sample_providers):
    """Test searching without any parameters returns all providers."""
    response = client.get("/api/legal-aid/search")
    
    assert response.status_code == 200
    data = response.json()
    
    # Should return all providers
    assert data["total"] == 3
    assert len(data["providers"]) == 3


def test_search_legal_aid_response_structure(sample_providers):
    """Test that search response has correct structure."""
    response = client.get("/api/legal-aid/search?city=Mumbai")
    
    assert response.status_code == 200
    data = response.json()
    
    # Check top-level structure
    assert "providers" in data
    assert "total" in data
    assert "is_fallback" in data
    
    # Check provider structure
    if data["providers"]:
        provider = data["providers"][0]
        required_fields = [
            "id", "name", "organization_type", "specializations",
            "languages_supported", "city", "state", "is_verified"
        ]
        for field in required_fields:
            assert field in provider


def test_get_provider_detail_response_structure(sample_providers):
    """Test that provider detail response has correct structure."""
    provider_id = sample_providers[0]
    
    response = client.get(f"/api/legal-aid/{provider_id}")
    
    assert response.status_code == 200
    data = response.json()
    
    # Check required fields
    required_fields = [
        "id", "name", "organization_type", "specializations",
        "languages_supported", "contact_info", "availability",
        "city", "state", "is_verified"
    ]
    for field in required_fields:
        assert field in data
    
    # Check contact_info structure
    contact_fields = ["phone", "email", "address", "website"]
    for field in contact_fields:
        assert field in data["contact_info"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
