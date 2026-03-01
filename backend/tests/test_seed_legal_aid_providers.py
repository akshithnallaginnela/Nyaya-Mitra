"""
Test script for legal aid provider database seeding.

This test verifies that the seeding script correctly loads and validates
legal aid provider data.

Requirements: 5.5 (Legal aid provider database)
"""

import json
import pytest
from pathlib import Path

from seed_legal_aid_providers import load_seed_data


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


def test_seed_data_structure():
    """Test that all providers have required fields."""
    data = load_seed_data()
    
    required_fields = ["name", "organization_type", "specializations", 
                      "languages_supported", "city", "state"]
    
    for idx, provider in enumerate(data, 1):
        for field in required_fields:
            assert field in provider, f"Provider {idx} missing required field: {field}"
        
        # Verify specializations and languages are lists
        assert isinstance(provider["specializations"], list), \
            f"Provider {idx}: specializations must be a list"
        assert isinstance(provider["languages_supported"], list), \
            f"Provider {idx}: languages_supported must be a list"
        
        # Verify lists are not empty
        assert len(provider["specializations"]) > 0, \
            f"Provider {idx}: specializations cannot be empty"
        assert len(provider["languages_supported"]) > 0, \
            f"Provider {idx}: languages_supported cannot be empty"


def test_seed_data_organization_types():
    """Test that organization types are valid."""
    data = load_seed_data()
    
    valid_types = {'NGO', 'Government', 'Law Firm', 'Legal Aid Society', 
                   'Bar Association', 'University Legal Clinic', 
                   'Pro Bono Service', 'Community Legal Center', 'Other'}
    
    for idx, provider in enumerate(data, 1):
        org_type = provider.get("organization_type")
        assert org_type in valid_types, \
            f"Provider {idx} has invalid organization type: {org_type}"


def test_seed_data_email_format():
    """Test that email addresses have valid format."""
    data = load_seed_data()
    
    for idx, provider in enumerate(data, 1):
        email = provider.get("contact_email")
        if email:
            assert "@" in email, f"Provider {idx} has invalid email: {email}"
            parts = email.split("@")
            assert len(parts) == 2, f"Provider {idx} has invalid email: {email}"
            assert "." in parts[1], f"Provider {idx} has invalid email domain: {email}"


def test_seed_data_phone_format():
    """Test that phone numbers have reasonable format."""
    data = load_seed_data()
    
    for idx, provider in enumerate(data, 1):
        phone = provider.get("contact_phone")
        if phone:
            # Extract digits from phone number
            digits = ''.join(c for c in phone if c.isdigit())
            assert len(digits) >= 10, \
                f"Provider {idx} has invalid phone (too few digits): {phone}"


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
    assert providers_with_phone > len(data) * 0.8, \
        "Most providers should have phone numbers"
    assert providers_with_email > len(data) * 0.8, \
        "Most providers should have email addresses"


def test_seed_data_verified_status():
    """Test that providers have verification status."""
    data = load_seed_data()
    
    for idx, provider in enumerate(data, 1):
        assert "is_verified" in provider, \
            f"Provider {idx} missing is_verified field"
        assert isinstance(provider["is_verified"], bool), \
            f"Provider {idx}: is_verified must be boolean"


def test_seed_data_specializations_content():
    """Test that specializations contain valid legal areas."""
    data = load_seed_data()
    
    common_specializations = {
        "Criminal Law", "Civil Law", "Family Law", "Consumer Rights",
        "Labour Law", "Property Disputes", "Women's Rights", "Child Rights",
        "Cyber Crime"
    }
    
    all_specializations = set()
    for provider in data:
        all_specializations.update(provider["specializations"])
    
    # Check that we have common specializations
    overlap = all_specializations.intersection(common_specializations)
    assert len(overlap) >= 5, \
        "Should have at least 5 common legal specializations"


def test_seed_data_languages_content():
    """Test that languages include major Indian languages."""
    data = load_seed_data()
    
    major_languages = {"English", "Hindi", "Tamil", "Telugu", "Marathi", 
                      "Bengali", "Gujarati", "Kannada", "Malayalam"}
    
    all_languages = set()
    for provider in data:
        all_languages.update(provider["languages_supported"])
    
    # Check that we have major languages
    overlap = all_languages.intersection(major_languages)
    assert len(overlap) >= 5, \
        "Should support at least 5 major Indian languages"


def test_seed_data_state_distribution():
    """Test that providers are distributed across major states."""
    data = load_seed_data()
    
    major_states = {"Delhi", "Maharashtra", "Karnataka", "Tamil Nadu", 
                   "West Bengal", "Telangana", "Gujarat", "Rajasthan",
                   "Punjab", "Uttar Pradesh", "Kerala"}
    
    states_in_data = set(provider["state"] for provider in data)
    
    # Check coverage of major states
    overlap = states_in_data.intersection(major_states)
    assert len(overlap) >= 8, \
        "Should have providers from at least 8 major states"


def test_seed_data_city_names():
    """Test that city names are not empty."""
    data = load_seed_data()
    
    for idx, provider in enumerate(data, 1):
        city = provider.get("city", "").strip()
        assert city, f"Provider {idx} has empty city name"
        assert len(city) >= 2, f"Provider {idx} has invalid city name: {city}"


def test_seed_data_provider_names():
    """Test that provider names are descriptive."""
    data = load_seed_data()
    
    for idx, provider in enumerate(data, 1):
        name = provider.get("name", "").strip()
        assert name, f"Provider {idx} has empty name"
        assert len(name) >= 5, \
            f"Provider {idx} has too short name: {name}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
