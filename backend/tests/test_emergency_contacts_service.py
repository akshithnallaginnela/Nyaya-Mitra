"""
Unit tests for EmergencyContactsService.

Tests service methods for retrieving and filtering emergency contacts.
"""

import pytest
from unittest.mock import Mock, MagicMock
from emergency_contacts_service import EmergencyContactsService
from models.emergency_contact import EmergencyContact


@pytest.fixture
def mock_db():
    """Create a mock database session."""
    return Mock()


@pytest.fixture
def service(mock_db):
    """Create an EmergencyContactsService instance with mock db."""
    return EmergencyContactsService(mock_db)


def create_mock_contact(
    id='123',
    name='Test Contact',
    category='police',
    phone='1234567890',
    description='Test description',
    state=None,
    city=None,
    is_national=True
):
    """Helper to create a mock emergency contact."""
    contact = Mock(spec=EmergencyContact)
    contact.id = id
    contact.name = name
    contact.category = category
    contact.phone_number = phone
    contact.description = description
    contact.state = state
    contact.city = city
    contact.is_national = is_national
    return contact


def test_get_contacts_returns_categorized_dict(service, mock_db):
    """Test that get_contacts returns a dictionary with all categories."""
    # Mock query chain
    mock_query = Mock()
    mock_db.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.all.return_value = []
    
    result = service.get_contacts()
    
    # Verify all categories are present
    assert 'police' in result
    assert 'legal_helpline' in result
    assert 'mental_health' in result
    assert 'student_services' in result


def test_get_contacts_includes_national_contacts(service, mock_db):
    """Test that national contacts are always included."""
    # Create mock national contact
    national_contact = create_mock_contact(
        name='National Emergency',
        category='police',
        is_national=True
    )
    
    # Mock query chain
    mock_query = Mock()
    mock_db.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    
    # First call returns empty (location-specific), second returns national
    mock_query.all.side_effect = [[], [national_contact]]
    
    result = service.get_contacts()
    
    # Verify national contact is included
    assert len(result['police']) == 1
    assert result['police'][0]['name'] == 'National Emergency'
    assert result['police'][0]['is_national'] is True


def test_get_contacts_with_location_filter(service, mock_db):
    """Test location-based filtering."""
    # Create mock location-specific contact
    delhi_contact = create_mock_contact(
        name='Delhi Police',
        category='police',
        state='Delhi',
        city='New Delhi',
        is_national=False
    )
    
    # Mock query chain
    mock_query = Mock()
    mock_db.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    
    # First call returns Delhi contact, second returns empty national
    mock_query.all.side_effect = [[delhi_contact], []]
    
    result = service.get_contacts(location='Delhi')
    
    # Verify location-specific contact is included
    assert len(result['police']) == 1
    assert result['police'][0]['name'] == 'Delhi Police'
    assert result['police'][0]['state'] == 'Delhi'


def test_get_contacts_by_category_valid(service, mock_db):
    """Test getting contacts by specific category."""
    # Create mock contact
    police_contact = create_mock_contact(
        name='Police Helpline',
        category='police',
        is_national=True
    )
    
    # Mock query chain
    mock_query = Mock()
    mock_db.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.all.side_effect = [[], [police_contact]]
    
    result = service.get_contacts_by_category('police')
    
    # Verify correct category returned
    assert len(result) == 1
    assert result[0]['name'] == 'Police Helpline'
    assert result[0]['callable'] is True


def test_get_contacts_by_category_invalid(service):
    """Test that invalid category raises ValueError."""
    with pytest.raises(ValueError, match="Invalid category"):
        service.get_contacts_by_category('invalid_category')


def test_get_national_contacts(service, mock_db):
    """Test getting only national contacts."""
    # Create mock national contacts
    national_police = create_mock_contact(
        name='National Police',
        category='police',
        is_national=True
    )
    national_legal = create_mock_contact(
        name='National Legal',
        category='legal_helpline',
        is_national=True
    )
    
    # Mock query chain
    mock_query = Mock()
    mock_db.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.all.return_value = [national_police, national_legal]
    
    result = service.get_national_contacts()
    
    # Verify national contacts are categorized correctly
    assert len(result['police']) == 1
    assert len(result['legal_helpline']) == 1
    assert result['police'][0]['name'] == 'National Police'
    assert result['legal_helpline'][0]['name'] == 'National Legal'


def test_contact_dict_has_callable_field(service, mock_db):
    """Test that all contacts have callable field set to True."""
    contact = create_mock_contact()
    
    # Mock query chain
    mock_query = Mock()
    mock_db.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.all.side_effect = [[], [contact]]
    
    result = service.get_contacts()
    
    # Verify callable field is present and True
    for category in result.values():
        for contact_dict in category:
            assert 'callable' in contact_dict
            assert contact_dict['callable'] is True


def test_verify_response_time(service, mock_db):
    """Test response time verification method."""
    # Mock query chain
    mock_query = Mock()
    mock_db.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.all.return_value = []
    
    response_time = service.verify_response_time()
    
    # Verify response time is measured
    assert isinstance(response_time, float)
    assert response_time >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
