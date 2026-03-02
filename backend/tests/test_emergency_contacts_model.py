"""
Unit tests for EmergencyContact model.

Tests model validation, field constraints, and data integrity.
"""

import pytest
from models.emergency_contact import EmergencyContact


def test_emergency_contact_valid_categories():
    """Test that valid categories are defined correctly."""
    expected_categories = {
        'police',
        'legal_helpline',
        'mental_health',
        'student_services'
    }
    assert EmergencyContact.VALID_CATEGORIES == expected_categories


def test_emergency_contact_category_validation():
    """Test category validation."""
    contact = EmergencyContact()
    
    # Valid category
    assert contact.validate_category('category', 'police') == 'police'
    assert contact.validate_category('category', 'legal_helpline') == 'legal_helpline'
    
    # Invalid category
    with pytest.raises(ValueError, match="Invalid category"):
        contact.validate_category('category', 'invalid_category')
    
    # Empty category
    with pytest.raises(ValueError, match="Category is required"):
        contact.validate_category('category', '')


def test_emergency_contact_name_validation():
    """Test name validation."""
    contact = EmergencyContact()
    
    # Valid name
    assert contact.validate_name('name', 'Delhi Police') == 'Delhi Police'
    assert contact.validate_name('name', '  Trimmed Name  ') == 'Trimmed Name'
    
    # Invalid name
    with pytest.raises(ValueError, match="Contact name is required"):
        contact.validate_name('name', '')
    
    with pytest.raises(ValueError, match="at least 2 characters"):
        contact.validate_name('name', 'A')


def test_emergency_contact_phone_validation():
    """Test phone number validation."""
    contact = EmergencyContact()
    
    # Valid phone numbers
    assert contact.validate_phone_number('phone_number', '1234567890') == '1234567890'
    assert contact.validate_phone_number('phone_number', '+91-1234567890') == '+91-1234567890'
    assert contact.validate_phone_number('phone_number', '011-23456789') == '011-23456789'
    
    # Invalid phone numbers
    with pytest.raises(ValueError, match="Phone number is required"):
        contact.validate_phone_number('phone_number', '')
    
    with pytest.raises(ValueError, match="at least 10 digits"):
        contact.validate_phone_number('phone_number', '123')


def test_emergency_contact_repr():
    """Test string representation."""
    contact = EmergencyContact()
    contact.id = '123e4567-e89b-12d3-a456-426614174000'
    contact.name = 'Delhi Police'
    contact.category = 'police'
    contact.state = 'Delhi'
    contact.city = 'New Delhi'
    
    repr_str = repr(contact)
    assert 'EmergencyContact' in repr_str
    assert 'Delhi Police' in repr_str
    assert 'police' in repr_str


def test_emergency_contact_national_flag():
    """Test national contact flag."""
    # This would be tested with actual database operations
    # For now, we verify the field exists in the model
    assert hasattr(EmergencyContact, 'is_national')
    assert hasattr(EmergencyContact, 'is_active')


def test_emergency_contact_location_fields():
    """Test location fields."""
    # Verify location fields exist
    assert hasattr(EmergencyContact, 'state')
    assert hasattr(EmergencyContact, 'city')
    
    # State and city can be None for national contacts
    contact = EmergencyContact()
    contact.state = None
    contact.city = None
    # Should not raise an error


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
