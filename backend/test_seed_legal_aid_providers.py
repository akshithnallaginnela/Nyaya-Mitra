"""
Test script for legal aid provider database seeding.

This test verifies that the seeding script correctly loads and populates
legal aid provider data into the database.

Requirements: 5.5 (Legal aid provider database)
"""

import json
import pytest
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base
from models.legal_aid_provider import LegalAidProvider
from seed_legal_aid_providers import (
    load_seed_data,
    clear_existing_data,
    seed_legal_aid_providers,
    verify_seeded_data
)


@pytest.fixture
def test_db():
    """Create a test database with SQLite."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    
    TestSessionLocal = sessionmaker(bind=engine)
    db = TestSessionLocal()
    
    yield db
    
    db.close()


@pytest.fixture
def sample_providers_data():
    """Sample provider data for testing."""
    return [
        {
            "name": "Test Legal Aid Society",
            "organization_type": "NGO",
            "specializations": ["Criminal Law", "Civil Law"],
            "languages_supported": ["English", "Hindi"],
            "contact_phone": "011-12345678",
            "contact_email": "test@example.com",
            "address": "123 Test Street",
            "city": "New Delhi",
            "state": "Delhi",
            "is_verified": True
        },
        {
            "name": "Test Government Legal Services",
            "organization_type": "Government",
            "specializations": ["Family Law", "Consumer Rights"],
            "languages_supported": ["English", "Hindi", "Tamil"],
            "contact_phone": "044-87654321",
            "contact_email": "govt@example.com",
            "address": "456 Government Road",
            "city": "Chennai",
            "state": "Tamil Nadu",
            "is_verified": True
        },
        {
            "name": "Test Law Firm",
            "organization_type": "Law Firm",
            "specializations": ["Property Disputes", "Labour Law"],
            "languages_supported": ["English", "Marathi"],
            "contact_phone": "022-11223344",
            "contact_email": "firm@example.com",
            "address": "789 Legal Avenue",
            "city": "Mumbai",
            "state": "Maharashtra",
            "is_verified": False
        }
    ]


def test_load_seed_data():
    """Test loading seed data from JSON file."""
    # Load the actual seed data file
    data = load_seed_data()
    
    # Verify data was loaded
    assert isinstance(data, list)
    assert len(data) > 0
    
    # Verify first provider has required fields
    first_provider = data[0]
    assert "name" in first_provider
    assert "organization_type" in first_provider
    assert "specializations" in first_provider
    assert "languages_supported" in first_provider
    assert "city" in first_provider
    assert "state" in first_provider


def test_clear_existing_data(test_db, sample_providers_data):
    """Test clearing existing provider data."""
    # Add some test data
    seed_legal_aid_providers(test_db, sample_providers_data, clear_existing=False)
    
    # Verify data exists
    count_before = test_db.query(LegalAidProvider).count()
    assert count_before == 3
    
    # Clear data
    deleted_count = clear_existing_data(test_db)
    
    # Verify data was cleared
    assert deleted_count == 3
    count_after = test_db.query(LegalAidProvider).count()
    assert count_after == 0


def test_seed_legal_aid_providers(test_db, sample_providers_data):
    """Test seeding legal aid providers."""
    # Seed the database
    seeded_count = seed_legal_aid_providers(
        test_db,
        sample_providers_data,
        clear_existing=False
    )
    
    # Verify seeding was successful
    assert seeded_count == 3
    
    # Verify data in database
    providers = test_db.query(LegalAidProvider).all()
    assert len(providers) == 3
    
    # Verify first provider
    provider = providers[0]
    assert provider.name == "Test Legal Aid Society"
    assert provider.organization_type == "NGO"
    assert provider.city == "New Delhi"
    assert provider.state == "Delhi"
    assert provider.is_verified == True
    
    # Verify specializations and languages are stored as JSON
    specializations = json.loads(provider.specializations)
    assert "Criminal Law" in specializations
    assert "Civil Law" in specializations
    
    languages = json.loads(provider.languages_supported)
    assert "English" in languages
    assert "Hindi" in languages


def test_seed_with_clear_existing(test_db, sample_providers_data):
    """Test seeding with clearing existing data."""
    # Seed first time
    seed_legal_aid_providers(test_db, sample_providers_data, clear_existing=False)
    assert test_db.query(LegalAidProvider).count() == 3
    
    # Seed again with clear_existing=True
    new_data = [sample_providers_data[0]]  # Only one provider
    seeded_count = seed_legal_aid_providers(test_db, new_data, clear_existing=True)
    
    # Verify old data was cleared and new data was added
    assert seeded_count == 1
    assert test_db.query(LegalAidProvider).count() == 1


def test_seed_with_invalid_data(test_db):
    """Test seeding with invalid provider data."""
    invalid_data = [
        {
            "name": "Valid Provider",
            "organization_type": "NGO",
            "specializations": ["Criminal Law"],
            "languages_supported": ["English"],
            "city": "Delhi",
            "state": "Delhi"
        },
        {
            # Missing required 'name' field
            "organization_type": "Government",
            "specializations": ["Civil Law"],
            "languages_supported": ["Hindi"],
            "city": "Mumbai",
            "state": "Maharashtra"
        },
        {
            "name": "Another Valid Provider",
            "organization_type": "Law Firm",
            "specializations": ["Family Law"],
            "languages_supported": ["Tamil"],
            "city": "Chennai",
            "state": "Tamil Nadu"
        }
    ]
    
    # Seed with invalid data
    seeded_count = seed_legal_aid_providers(test_db, invalid_data, clear_existing=False)
    
    # Verify only valid providers were seeded
    assert seeded_count == 2
    assert test_db.query(LegalAidProvider).count() == 2


def test_seed_with_invalid_organization_type(test_db):
    """Test seeding with invalid organization type."""
    invalid_data = [
        {
            "name": "Invalid Org Type Provider",
            "organization_type": "InvalidType",  # Invalid type
            "specializations": ["Criminal Law"],
            "languages_supported": ["English"],
            "city": "Delhi",
            "state": "Delhi"
        }
    ]
    
    # Seed with invalid organization type
    seeded_count = seed_legal_aid_providers(test_db, invalid_data, clear_existing=False)
    
    # Verify provider was not seeded
    assert seeded_count == 0
    assert test_db.query(LegalAidProvider).count() == 0


def test_seed_with_invalid_email(test_db):
    """Test seeding with invalid email format."""
    invalid_data = [
        {
            "name": "Invalid Email Provider",
            "organization_type": "NGO",
            "specializations": ["Criminal Law"],
            "languages_supported": ["English"],
            "contact_email": "invalid-email",  # Invalid email
            "city": "Delhi",
            "state": "Delhi"
        }
    ]
    
    # Seed with invalid email
    seeded_count = seed_legal_aid_providers(test_db, invalid_data, clear_existing=False)
    
    # Verify provider was not seeded
    assert seeded_count == 0
    assert test_db.query(LegalAidProvider).count() == 0


def test_seed_actual_data(test_db):
    """Test seeding with actual seed data file."""
    # Load actual seed data
    actual_data = load_seed_data()
    
    # Seed the database
    seeded_count = seed_legal_aid_providers(test_db, actual_data, clear_existing=False)
    
    # Verify seeding was successful
    assert seeded_count > 0
    assert test_db.query(LegalAidProvider).count() == seeded_count
    
    # Verify data integrity
    providers = test_db.query(LegalAidProvider).all()
    
    for provider in providers:
        # Verify required fields
        assert provider.name
        assert provider.organization_type
        assert provider.city
        assert provider.state
        
        # Verify JSON fields can be parsed
        specializations = json.loads(provider.specializations)
        assert isinstance(specializations, list)
        assert len(specializations) > 0
        
        languages = json.loads(provider.languages_supported)
        assert isinstance(languages, list)
        assert len(languages) > 0


def test_verify_seeded_data(test_db, sample_providers_data):
    """Test verification function."""
    # Seed the database
    seed_legal_aid_providers(test_db, sample_providers_data, clear_existing=False)
    
    # Run verification (should not raise any errors)
    verify_seeded_data(test_db)
    
    # If we get here, verification passed
    assert True


def test_seed_data_coverage():
    """Test that seed data covers multiple states and organization types."""
    data = load_seed_data()
    
    # Extract unique states and organization types
    states = set(provider["state"] for provider in data)
    org_types = set(provider["organization_type"] for provider in data)
    
    # Verify coverage
    assert len(states) >= 10, "Should have providers from at least 10 states"
    assert len(org_types) >= 2, "Should have at least 2 organization types"
    
    # Verify common organization types are present
    assert "Government" in org_types
    assert "NGO" in org_types


def test_seed_data_contact_information():
    """Test that seed data includes proper contact information."""
    data = load_seed_data()
    
    providers_with_phone = sum(1 for p in data if p.get("contact_phone"))
    providers_with_email = sum(1 for p in data if p.get("contact_email"))
    
    # Most providers should have contact information
    assert providers_with_phone > len(data) * 0.8, "Most providers should have phone numbers"
    assert providers_with_email > len(data) * 0.8, "Most providers should have email addresses"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
