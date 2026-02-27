"""
Unit tests for LegalAidProvider model.

Tests cover:
- LegalAidProvider model creation with all fields
- Name validation
- Organization type validation
- City and state validation
- Contact email validation
- Contact phone validation
- Index creation for efficient searching

Requirements: 5.1 (Legal aid search), 5.2 (Provider information)
"""

import pytest
from sqlalchemy.exc import IntegrityError

from database import Base, engine, get_db
from models.legal_aid_provider import LegalAidProvider


@pytest.fixture(scope="function")
def setup_database():
    """Create tables before each test and drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


class TestLegalAidProviderCreation:
    """Test LegalAidProvider model creation and field validation."""
    
    def test_create_provider_with_all_fields(self, setup_database):
        """Test creating a legal aid provider with all fields."""
        with get_db() as db:
            provider = LegalAidProvider(
                name="Free Legal Aid Society",
                organization_type="NGO",
                specializations='["Criminal Law", "Family Law", "Consumer Rights"]',
                languages_supported='["English", "Hindi", "Tamil"]',
                contact_phone="+91-9876543210",
                contact_email="contact@freelegalaid.org",
                address="123 Justice Street, Legal District",
                city="Mumbai",
                state="Maharashtra",
                is_verified=True
            )
            
            db.add(provider)
            db.commit()
            db.refresh(provider)
            
            assert provider.id is not None
            assert provider.name == "Free Legal Aid Society"
            assert provider.organization_type == "NGO"
            assert provider.specializations == '["Criminal Law", "Family Law", "Consumer Rights"]'
            assert provider.languages_supported == '["English", "Hindi", "Tamil"]'
            assert provider.contact_phone == "+91-9876543210"
            assert provider.contact_email == "contact@freelegalaid.org"
            assert provider.address == "123 Justice Street, Legal District"
            assert provider.city == "Mumbai"
            assert provider.state == "Maharashtra"
            assert provider.is_verified is True
            assert provider.created_at is not None
            assert provider.updated_at is not None
    
    def test_create_provider_with_minimal_fields(self, setup_database):
        """Test creating a provider with only required fields."""
        with get_db() as db:
            provider = LegalAidProvider(
                name="Basic Legal Aid",
                organization_type="Government",
                specializations='["General Legal Aid"]',
                languages_supported='["English"]',
                city="Delhi",
                state="Delhi"
            )
            
            db.add(provider)
            db.commit()
            db.refresh(provider)
            
            assert provider.id is not None
            assert provider.name == "Basic Legal Aid"
            assert provider.contact_phone is None
            assert provider.contact_email is None
            assert provider.address is None
            assert provider.is_verified is False  # Default value
    
    def test_default_is_verified_false(self, setup_database):
        """Test that is_verified defaults to False."""
        with get_db() as db:
            provider = LegalAidProvider(
                name="Unverified Provider",
                organization_type="NGO",
                specializations='["Legal Aid"]',
                languages_supported='["English"]',
                city="Bangalore",
                state="Karnataka"
            )
            
            db.add(provider)
            db.commit()
            db.refresh(provider)
            
            assert provider.is_verified is False


class TestNameValidation:
    """Test provider name validation."""
    
    def test_name_required(self, setup_database):
        """Test that provider name is required."""
        with pytest.raises(ValueError, match="Provider name is required"):
            provider = LegalAidProvider(
                name="",
                organization_type="NGO",
                specializations='["Legal Aid"]',
                languages_supported='["English"]',
                city="Chennai",
                state="Tamil Nadu"
            )
    
    def test_name_minimum_length(self, setup_database):
        """Test that provider name must be at least 2 characters."""
        with pytest.raises(ValueError, match="at least 2 characters"):
            provider = LegalAidProvider(
                name="A",
                organization_type="NGO",
                specializations='["Legal Aid"]',
                languages_supported='["English"]',
                city="Chennai",
                state="Tamil Nadu"
            )
    
    def test_name_whitespace_trimming(self, setup_database):
        """Test that provider name whitespace is trimmed."""
        with get_db() as db:
            provider = LegalAidProvider(
                name="  Legal Aid Center  ",
                organization_type="NGO",
                specializations='["Legal Aid"]',
                languages_supported='["English"]',
                city="Pune",
                state="Maharashtra"
            )
            
            db.add(provider)
            db.commit()
            db.refresh(provider)
            
            assert provider.name == "Legal Aid Center"


class TestOrganizationTypeValidation:
    """Test organization type validation."""
    
    def test_valid_organization_types(self, setup_database):
        """Test that all valid organization types are accepted."""
        valid_types = [
            'NGO',
            'Government',
            'Law Firm',
            'Legal Aid Society',
            'Bar Association',
            'University Legal Clinic',
            'Pro Bono Service',
            'Community Legal Center',
            'Other'
        ]
        
        for org_type in valid_types:
            with get_db() as db:
                provider = LegalAidProvider(
                    name=f"Provider {org_type}",
                    organization_type=org_type,
                    specializations='["Legal Aid"]',
                    languages_supported='["English"]',
                    city="Delhi",
                    state="Delhi"
                )
                
                db.add(provider)
                db.commit()
                db.refresh(provider)
                
                assert provider.organization_type == org_type
    
    def test_invalid_organization_type(self, setup_database):
        """Test that invalid organization types are rejected."""
        with pytest.raises(ValueError, match="Invalid organization type"):
            provider = LegalAidProvider(
                name="Invalid Provider",
                organization_type="InvalidType",
                specializations='["Legal Aid"]',
                languages_supported='["English"]',
                city="Mumbai",
                state="Maharashtra"
            )
    
    def test_organization_type_required(self, setup_database):
        """Test that organization type is required."""
        with pytest.raises(ValueError, match="Organization type is required"):
            provider = LegalAidProvider(
                name="No Type Provider",
                organization_type="",
                specializations='["Legal Aid"]',
                languages_supported='["English"]',
                city="Kolkata",
                state="West Bengal"
            )


class TestLocationValidation:
    """Test city and state validation."""
    
    def test_city_required(self, setup_database):
        """Test that city is required."""
        with pytest.raises(ValueError, match="City is required"):
            provider = LegalAidProvider(
                name="No City Provider",
                organization_type="NGO",
                specializations='["Legal Aid"]',
                languages_supported='["English"]',
                city="",
                state="Maharashtra"
            )
    
    def test_state_required(self, setup_database):
        """Test that state is required."""
        with pytest.raises(ValueError, match="State is required"):
            provider = LegalAidProvider(
                name="No State Provider",
                organization_type="NGO",
                specializations='["Legal Aid"]',
                languages_supported='["English"]',
                city="Mumbai",
                state=""
            )
    
    def test_city_whitespace_trimming(self, setup_database):
        """Test that city whitespace is trimmed."""
        with get_db() as db:
            provider = LegalAidProvider(
                name="Trimmed City Provider",
                organization_type="NGO",
                specializations='["Legal Aid"]',
                languages_supported='["English"]',
                city="  Hyderabad  ",
                state="Telangana"
            )
            
            db.add(provider)
            db.commit()
            db.refresh(provider)
            
            assert provider.city == "Hyderabad"
    
    def test_state_whitespace_trimming(self, setup_database):
        """Test that state whitespace is trimmed."""
        with get_db() as db:
            provider = LegalAidProvider(
                name="Trimmed State Provider",
                organization_type="NGO",
                specializations='["Legal Aid"]',
                languages_supported='["English"]',
                city="Jaipur",
                state="  Rajasthan  "
            )
            
            db.add(provider)
            db.commit()
            db.refresh(provider)
            
            assert provider.state == "Rajasthan"


class TestContactEmailValidation:
    """Test contact email validation."""
    
    def test_valid_email_formats(self, setup_database):
        """Test various valid email formats."""
        valid_emails = [
            "contact@legalaid.org",
            "info@example.com",
            "help+support@domain.co.in",
            "123@numbers.com"
        ]
        
        for email in valid_emails:
            with get_db() as db:
                provider = LegalAidProvider(
                    name=f"Provider {email}",
                    organization_type="NGO",
                    specializations='["Legal Aid"]',
                    languages_supported='["English"]',
                    contact_email=email,
                    city="Delhi",
                    state="Delhi"
                )
                
                db.add(provider)
                db.commit()
                db.refresh(provider)
                
                assert provider.contact_email == email.lower()
    
    def test_email_normalization_to_lowercase(self, setup_database):
        """Test that emails are normalized to lowercase."""
        with get_db() as db:
            provider = LegalAidProvider(
                name="Uppercase Email Provider",
                organization_type="NGO",
                specializations='["Legal Aid"]',
                languages_supported='["English"]',
                contact_email="CONTACT@EXAMPLE.COM",
                city="Mumbai",
                state="Maharashtra"
            )
            
            db.add(provider)
            db.commit()
            db.refresh(provider)
            
            assert provider.contact_email == "contact@example.com"
    
    def test_invalid_email_formats(self, setup_database):
        """Test that invalid email formats are rejected."""
        invalid_emails = [
            "notanemail",
            "@example.com",
            "user@",
            "user@.com"
        ]
        
        for email in invalid_emails:
            with pytest.raises(ValueError, match="Invalid email format"):
                provider = LegalAidProvider(
                    name="Invalid Email Provider",
                    organization_type="NGO",
                    specializations='["Legal Aid"]',
                    languages_supported='["English"]',
                    contact_email=email,
                    city="Bangalore",
                    state="Karnataka"
                )
    
    def test_email_can_be_none(self, setup_database):
        """Test that email can be None (optional field)."""
        with get_db() as db:
            provider = LegalAidProvider(
                name="No Email Provider",
                organization_type="NGO",
                specializations='["Legal Aid"]',
                languages_supported='["English"]',
                contact_email=None,
                city="Chennai",
                state="Tamil Nadu"
            )
            
            db.add(provider)
            db.commit()
            db.refresh(provider)
            
            assert provider.contact_email is None


class TestContactPhoneValidation:
    """Test contact phone validation."""
    
    def test_valid_phone_formats(self, setup_database):
        """Test various valid phone formats."""
        valid_phones = [
            "+91-9876543210",
            "9876543210",
            "+91 98765 43210",
            "(022) 12345678",
            "022-12345678"
        ]
        
        for phone in valid_phones:
            with get_db() as db:
                provider = LegalAidProvider(
                    name=f"Provider {phone}",
                    organization_type="NGO",
                    specializations='["Legal Aid"]',
                    languages_supported='["English"]',
                    contact_phone=phone,
                    city="Delhi",
                    state="Delhi"
                )
                
                db.add(provider)
                db.commit()
                db.refresh(provider)
                
                assert provider.contact_phone == phone
    
    def test_phone_minimum_digits(self, setup_database):
        """Test that phone must have at least 10 digits."""
        with pytest.raises(ValueError, match="at least 10 digits"):
            provider = LegalAidProvider(
                name="Short Phone Provider",
                organization_type="NGO",
                specializations='["Legal Aid"]',
                languages_supported='["English"]',
                contact_phone="123456789",  # Only 9 digits
                city="Mumbai",
                state="Maharashtra"
            )
    
    def test_phone_can_be_none(self, setup_database):
        """Test that phone can be None (optional field)."""
        with get_db() as db:
            provider = LegalAidProvider(
                name="No Phone Provider",
                organization_type="NGO",
                specializations='["Legal Aid"]',
                languages_supported='["English"]',
                contact_phone=None,
                city="Pune",
                state="Maharashtra"
            )
            
            db.add(provider)
            db.commit()
            db.refresh(provider)
            
            assert provider.contact_phone is None


class TestIndexes:
    """Test that indexes are created for efficient searching."""
    
    def test_city_index_exists(self, setup_database):
        """Test that city column has an index."""
        from sqlalchemy import inspect
        
        inspector = inspect(engine)
        indexes = inspector.get_indexes('legal_aid_providers')
        
        # Check if there's an index on city column
        city_indexed = any(
            'city' in idx['column_names']
            for idx in indexes
        )
        
        assert city_indexed, "City column should have an index"
    
    def test_state_index_exists(self, setup_database):
        """Test that state column has an index."""
        from sqlalchemy import inspect
        
        inspector = inspect(engine)
        indexes = inspector.get_indexes('legal_aid_providers')
        
        # Check if there's an index on state column
        state_indexed = any(
            'state' in idx['column_names']
            for idx in indexes
        )
        
        assert state_indexed, "State column should have an index"
    
    def test_organization_type_index_exists(self, setup_database):
        """Test that organization_type column has an index."""
        from sqlalchemy import inspect
        
        inspector = inspect(engine)
        indexes = inspector.get_indexes('legal_aid_providers')
        
        # Check if there's an index on organization_type column
        org_type_indexed = any(
            'organization_type' in idx['column_names']
            for idx in indexes
        )
        
        assert org_type_indexed, "Organization type column should have an index"
    
    def test_composite_city_state_index_exists(self, setup_database):
        """Test that composite index on (city, state) exists."""
        from sqlalchemy import inspect
        
        inspector = inspect(engine)
        indexes = inspector.get_indexes('legal_aid_providers')
        
        # Check if there's a composite index on city and state
        composite_indexed = any(
            'city' in idx['column_names'] and 'state' in idx['column_names']
            for idx in indexes
        )
        
        assert composite_indexed, "Composite index on (city, state) should exist"


class TestLegalAidProviderMethods:
    """Test LegalAidProvider model methods."""
    
    def test_repr_method(self, setup_database):
        """Test string representation of LegalAidProvider."""
        with get_db() as db:
            provider = LegalAidProvider(
                name="Test Legal Aid",
                organization_type="NGO",
                specializations='["Legal Aid"]',
                languages_supported='["English"]',
                city="Mumbai",
                state="Maharashtra"
            )
            
            db.add(provider)
            db.commit()
            db.refresh(provider)
            
            repr_str = repr(provider)
            assert "LegalAidProvider" in repr_str
            assert provider.name in repr_str
            assert provider.city in repr_str
            assert provider.state in repr_str
            assert str(provider.id) in repr_str


class TestSearchScenarios:
    """Test realistic search scenarios for legal aid providers."""
    
    def test_search_by_city(self, setup_database):
        """Test searching providers by city."""
        with get_db() as db:
            # Create providers in different cities
            provider1 = LegalAidProvider(
                name="Mumbai Legal Aid",
                organization_type="NGO",
                specializations='["Criminal Law"]',
                languages_supported='["English", "Hindi"]',
                city="Mumbai",
                state="Maharashtra"
            )
            provider2 = LegalAidProvider(
                name="Delhi Legal Aid",
                organization_type="Government",
                specializations='["Family Law"]',
                languages_supported='["English", "Hindi"]',
                city="Delhi",
                state="Delhi"
            )
            
            db.add_all([provider1, provider2])
            db.commit()
            
            # Search by city
            mumbai_providers = db.query(LegalAidProvider).filter(
                LegalAidProvider.city == "Mumbai"
            ).all()
            
            assert len(mumbai_providers) == 1
            assert mumbai_providers[0].name == "Mumbai Legal Aid"
    
    def test_search_by_state(self, setup_database):
        """Test searching providers by state."""
        with get_db() as db:
            # Create providers in different states
            provider1 = LegalAidProvider(
                name="Maharashtra Provider 1",
                organization_type="NGO",
                specializations='["Legal Aid"]',
                languages_supported='["English"]',
                city="Mumbai",
                state="Maharashtra"
            )
            provider2 = LegalAidProvider(
                name="Maharashtra Provider 2",
                organization_type="Law Firm",
                specializations='["Legal Aid"]',
                languages_supported='["English"]',
                city="Pune",
                state="Maharashtra"
            )
            provider3 = LegalAidProvider(
                name="Karnataka Provider",
                organization_type="NGO",
                specializations='["Legal Aid"]',
                languages_supported='["English"]',
                city="Bangalore",
                state="Karnataka"
            )
            
            db.add_all([provider1, provider2, provider3])
            db.commit()
            
            # Search by state
            maharashtra_providers = db.query(LegalAidProvider).filter(
                LegalAidProvider.state == "Maharashtra"
            ).all()
            
            assert len(maharashtra_providers) == 2
    
    def test_search_by_organization_type(self, setup_database):
        """Test searching providers by organization type."""
        with get_db() as db:
            # Create providers with different organization types
            provider1 = LegalAidProvider(
                name="NGO Provider 1",
                organization_type="NGO",
                specializations='["Legal Aid"]',
                languages_supported='["English"]',
                city="Delhi",
                state="Delhi"
            )
            provider2 = LegalAidProvider(
                name="NGO Provider 2",
                organization_type="NGO",
                specializations='["Legal Aid"]',
                languages_supported='["English"]',
                city="Mumbai",
                state="Maharashtra"
            )
            provider3 = LegalAidProvider(
                name="Government Provider",
                organization_type="Government",
                specializations='["Legal Aid"]',
                languages_supported='["English"]',
                city="Bangalore",
                state="Karnataka"
            )
            
            db.add_all([provider1, provider2, provider3])
            db.commit()
            
            # Search by organization type
            ngo_providers = db.query(LegalAidProvider).filter(
                LegalAidProvider.organization_type == "NGO"
            ).all()
            
            assert len(ngo_providers) == 2
    
    def test_search_by_verified_status(self, setup_database):
        """Test searching verified providers."""
        with get_db() as db:
            # Create verified and unverified providers
            provider1 = LegalAidProvider(
                name="Verified Provider",
                organization_type="NGO",
                specializations='["Legal Aid"]',
                languages_supported='["English"]',
                city="Mumbai",
                state="Maharashtra",
                is_verified=True
            )
            provider2 = LegalAidProvider(
                name="Unverified Provider",
                organization_type="NGO",
                specializations='["Legal Aid"]',
                languages_supported='["English"]',
                city="Delhi",
                state="Delhi",
                is_verified=False
            )
            
            db.add_all([provider1, provider2])
            db.commit()
            
            # Search verified providers
            verified_providers = db.query(LegalAidProvider).filter(
                LegalAidProvider.is_verified == True
            ).all()
            
            assert len(verified_providers) == 1
            assert verified_providers[0].name == "Verified Provider"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
