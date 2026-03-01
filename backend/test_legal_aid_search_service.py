"""
Unit tests for Legal Aid Search Service

Tests the search logic including:
- Multi-criteria filtering
- Relevance scoring
- National helpline fallback

Requirements: 5.1, 5.3, 5.6
"""

import json
import pytest
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models.legal_aid_provider import LegalAidProvider
from legal_aid_search_service import LegalAidSearchService, NATIONAL_HELPLINES


@pytest.fixture(scope="function")
def setup_database():
    """Create test database tables before each test and drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_providers():
    """Create sample providers for testing."""
    return [
        {
            "name": "Mumbai Criminal Law Center",
            "organization_type": "NGO",
            "specializations": ["Criminal Law", "Cyber Crime"],
            "languages_supported": ["English", "Hindi", "Marathi"],
            "contact_phone": "022-12345678",
            "contact_email": "info@mumbailegal.org",
            "address": "Fort, Mumbai",
            "city": "Mumbai",
            "state": "Maharashtra",
            "is_verified": True
        },
        {
            "name": "Delhi Family Law Society",
            "organization_type": "Government",
            "specializations": ["Family Law", "Divorce", "Child Custody"],
            "languages_supported": ["English", "Hindi"],
            "contact_phone": "011-23456789",
            "contact_email": "help@delhifamily.gov.in",
            "address": "Connaught Place, Delhi",
            "city": "New Delhi",
            "state": "Delhi",
            "is_verified": True
        },
        {
            "name": "Bangalore Consumer Rights NGO",
            "organization_type": "NGO",
            "specializations": ["Consumer Rights", "Consumer Disputes"],
            "languages_supported": ["English", "Kannada", "Tamil"],
            "contact_phone": "080-34567890",
            "contact_email": "contact@blrconsumer.org",
            "address": "MG Road, Bangalore",
            "city": "Bangalore",
            "state": "Karnataka",
            "is_verified": False
        },
        {
            "name": "Chennai Legal Aid Centre",
            "organization_type": "NGO",
            "specializations": ["Criminal Law", "Labour Law", "Women's Rights"],
            "languages_supported": ["English", "Tamil", "Telugu"],
            "contact_phone": "044-45678901",
            "contact_email": "info@chennailegal.org",
            "address": "T Nagar, Chennai",
            "city": "Chennai",
            "state": "Tamil Nadu",
            "is_verified": True
        },
        {
            "name": "Pune Property Law Firm",
            "organization_type": "Law Firm",
            "specializations": ["Property Disputes", "Real Estate Law"],
            "languages_supported": ["English", "Hindi", "Marathi"],
            "contact_phone": "020-56789012",
            "contact_email": "contact@puneproperty.com",
            "address": "Shivajinagar, Pune",
            "city": "Pune",
            "state": "Maharashtra",
            "is_verified": True
        }
    ]


def seed_test_providers(db: Session, providers: list):
    """Helper to seed test providers into database."""
    for provider_data in providers:
        provider = LegalAidProvider(
            name=provider_data["name"],
            organization_type=provider_data["organization_type"],
            specializations=json.dumps(provider_data["specializations"]),
            languages_supported=json.dumps(provider_data["languages_supported"]),
            contact_phone=provider_data["contact_phone"],
            contact_email=provider_data["contact_email"],
            address=provider_data["address"],
            city=provider_data["city"],
            state=provider_data["state"],
            is_verified=provider_data["is_verified"]
        )
        db.add(provider)
    db.commit()


class TestLegalAidSearchService:
    """Test suite for LegalAidSearchService."""
    
    def test_search_by_city(self, setup_database, sample_providers):
        """Test searching providers by city."""
        with get_db() as db:
            seed_test_providers(db, sample_providers)
            service = LegalAidSearchService(db)
            
            # Search for Mumbai providers
            results = service.search(city="Mumbai")
            
            assert len(results) == 1
            assert results[0]["name"] == "Mumbai Criminal Law Center"
            assert results[0]["city"] == "Mumbai"
    
    def test_search_by_state(self, setup_database, sample_providers):
        """Test searching providers by state."""
        with get_db() as db:
            seed_test_providers(db, sample_providers)
            service = LegalAidSearchService(db)
            
            # Search for Maharashtra providers
            results = service.search(state="Maharashtra")
            
            assert len(results) == 2
            cities = {r["city"] for r in results}
            assert "Mumbai" in cities
            assert "Pune" in cities
    
    def test_search_by_location_general(self, setup_database, sample_providers):
        """Test searching with general location (searches both city and state)."""
        with get_db() as db:
            seed_test_providers(db, sample_providers)
            service = LegalAidSearchService(db)
            
            # Search for "Delhi" - should match city
            results = service.search(location="Delhi")
            
            assert len(results) == 1
            assert results[0]["city"] == "New Delhi"
    
    def test_search_by_case_type(self, setup_database, sample_providers):
        """Test searching with case type filter and relevance scoring."""
        with get_db() as db:
            seed_test_providers(db, sample_providers)
            service = LegalAidSearchService(db)
            
            # Search for Criminal Law specialists
            results = service.search(case_type="Criminal Law")
            
            # Should return providers with Criminal Law specialization
            assert len(results) >= 2
            
            # Check that results have Criminal Law in specializations
            for result in results:
                assert "Criminal Law" in result["specializations"]
            
            # Check relevance scores exist
            for result in results:
                assert "relevance_score" in result
                assert result["relevance_score"] > 0
    
    def test_search_by_language(self, setup_database, sample_providers):
        """Test searching with language filter."""
        with get_db() as db:
            seed_test_providers(db, sample_providers)
            service = LegalAidSearchService(db)
            
            # Search for Tamil language support
            results = service.search(language="Tamil")
            
            # Should return providers supporting Tamil
            assert len(results) >= 2
            
            for result in results:
                assert "Tamil" in result["languages_supported"]
    
    def test_multi_criteria_search(self, setup_database, sample_providers):
        """Test searching with multiple criteria."""
        with get_db() as db:
            seed_test_providers(db, sample_providers)
            service = LegalAidSearchService(db)
            
            # Search for Criminal Law in Chennai with Tamil support
            results = service.search(
                city="Chennai",
                case_type="Criminal Law",
                language="Tamil"
            )
            
            assert len(results) == 1
            assert results[0]["name"] == "Chennai Legal Aid Centre"
            assert results[0]["city"] == "Chennai"
            assert "Criminal Law" in results[0]["specializations"]
            assert "Tamil" in results[0]["languages_supported"]
            
            # Should have high relevance score (case_type + language + verified)
            assert results[0]["relevance_score"] >= 70
    
    def test_relevance_scoring_verified_bonus(self, setup_database, sample_providers):
        """Test that verified providers get bonus points."""
        with get_db() as db:
            seed_test_providers(db, sample_providers)
            service = LegalAidSearchService(db)
            
            # Search for Consumer Rights
            results = service.search(case_type="Consumer Rights")
            
            # Bangalore provider is not verified, should have lower score
            bangalore_result = next(r for r in results if r["city"] == "Bangalore")
            
            # Score should be 40 (case type match) without verified bonus
            assert bangalore_result["relevance_score"] == 40
    
    def test_relevance_scoring_all_criteria(self, setup_database, sample_providers):
        """Test relevance scoring with all criteria matching."""
        with get_db() as db:
            seed_test_providers(db, sample_providers)
            service = LegalAidSearchService(db)
            
            # Search with all criteria that match Mumbai provider
            results = service.search(
                city="Mumbai",
                case_type="Criminal Law",
                language="Marathi",
                expertise="Cyber Crime"
            )
            
            assert len(results) == 1
            # Score: 40 (case_type) + 30 (language) + 20 (expertise) + 10 (verified) = 100
            assert results[0]["relevance_score"] == 100
    
    def test_fuzzy_matching_case_insensitive(self, setup_database, sample_providers):
        """Test that fuzzy matching is case-insensitive."""
        with get_db() as db:
            seed_test_providers(db, sample_providers)
            service = LegalAidSearchService(db)
            
            # Search with different case
            results = service.search(case_type="criminal law")
            
            assert len(results) >= 2
            for result in results:
                specializations_lower = [s.lower() for s in result["specializations"]]
                assert "criminal law" in specializations_lower
    
    def test_fuzzy_matching_partial(self, setup_database, sample_providers):
        """Test that fuzzy matching works with partial terms."""
        with get_db() as db:
            seed_test_providers(db, sample_providers)
            service = LegalAidSearchService(db)
            
            # Search with partial term
            results = service.search(case_type="Consumer")
            
            assert len(results) >= 1
            # Should match "Consumer Rights" and "Consumer Disputes"
            for result in results:
                has_consumer = any("Consumer" in s for s in result["specializations"])
                assert has_consumer
    
    def test_national_helpline_fallback_no_results(self, setup_database):
        """Test that national helplines are returned when no local results found."""
        with get_db() as db:
            # Don't seed any providers
            service = LegalAidSearchService(db)
            
            # Search for non-existent location
            results = service.search(city="NonExistentCity")
            
            # Should return national helplines
            assert len(results) == len(NATIONAL_HELPLINES)
            
            # Check that results are marked as national helplines
            for result in results:
                assert result.get("is_national_helpline") == True
    
    def test_national_helpline_fallback_with_case_type(self, setup_database):
        """Test that national helplines are scored by case type when used as fallback."""
        with get_db() as db:
            service = LegalAidSearchService(db)
            
            # Search for Women's Rights in non-existent location
            results = service.search(
                city="NonExistentCity",
                case_type="Women's Rights"
            )
            
            # Should return national helplines
            assert len(results) == len(NATIONAL_HELPLINES)
            
            # National Commission for Women should have highest score
            top_result = results[0]
            assert "Women" in top_result["name"]
            assert top_result["relevance_score"] > 0
    
    def test_national_helpline_fallback_sorted_by_relevance(self, setup_database):
        """Test that national helplines are sorted by relevance score."""
        with get_db() as db:
            service = LegalAidSearchService(db)
            
            # Search for Consumer Rights
            results = service.search(
                city="NonExistentCity",
                case_type="Consumer Rights"
            )
            
            # Results should be sorted by score (descending)
            scores = [r["relevance_score"] for r in results]
            assert scores == sorted(scores, reverse=True)
            
            # Consumer helpline should be first
            assert "Consumer" in results[0]["name"]
    
    def test_get_provider_by_id(self, setup_database, sample_providers):
        """Test retrieving a specific provider by ID."""
        with get_db() as db:
            seed_test_providers(db, sample_providers)
            service = LegalAidSearchService(db)
            
            # Get all providers first
            all_providers = service.search()
            assert len(all_providers) > 0
            
            # Get specific provider by ID
            provider_id = all_providers[0]["id"]
            provider = service.get_provider_by_id(provider_id)
            
            assert provider is not None
            assert provider["id"] == provider_id
            assert provider["name"] == all_providers[0]["name"]
    
    def test_get_provider_by_id_not_found(self, setup_database):
        """Test retrieving non-existent provider returns None."""
        with get_db() as db:
            service = LegalAidSearchService(db)
            
            # Try to get non-existent provider
            provider = service.get_provider_by_id("00000000-0000-0000-0000-000000000000")
            
            assert provider is None
    
    def test_search_no_filters_returns_all(self, setup_database, sample_providers):
        """Test that search with no filters returns all providers."""
        with get_db() as db:
            seed_test_providers(db, sample_providers)
            service = LegalAidSearchService(db)
            
            # Search with no filters
            results = service.search()
            
            assert len(results) == len(sample_providers)
    
    def test_search_results_sorted_by_score(self, setup_database, sample_providers):
        """Test that search results are sorted by relevance score."""
        with get_db() as db:
            seed_test_providers(db, sample_providers)
            service = LegalAidSearchService(db)
            
            # Search with criteria that will produce different scores
            results = service.search(case_type="Criminal Law")
            
            # Check that scores are in descending order
            scores = [r["relevance_score"] for r in results]
            assert scores == sorted(scores, reverse=True)
    
    def test_case_insensitive_location_search(self, setup_database, sample_providers):
        """Test that location search is case-insensitive."""
        with get_db() as db:
            seed_test_providers(db, sample_providers)
            service = LegalAidSearchService(db)
            
            # Search with different cases
            results_lower = service.search(city="mumbai")
            results_upper = service.search(city="MUMBAI")
            results_mixed = service.search(city="Mumbai")
            
            assert len(results_lower) == len(results_upper) == len(results_mixed) == 1
    
    def test_partial_location_match(self, setup_database, sample_providers):
        """Test that partial location names work."""
        with get_db() as db:
            seed_test_providers(db, sample_providers)
            service = LegalAidSearchService(db)
            
            # Search with partial city name
            results = service.search(city="Banga")
            
            assert len(results) == 1
            assert "Bangalore" in results[0]["city"]
    
    def test_expertise_filter(self, setup_database, sample_providers):
        """Test searching with expertise filter."""
        with get_db() as db:
            seed_test_providers(db, sample_providers)
            service = LegalAidSearchService(db)
            
            # Search for Cyber Crime expertise
            results = service.search(expertise="Cyber Crime")
            
            assert len(results) >= 1
            # Mumbai provider has Cyber Crime
            mumbai_result = next(r for r in results if r["city"] == "Mumbai")
            assert "Cyber Crime" in mumbai_result["specializations"]
    
    def test_combined_state_and_case_type(self, setup_database, sample_providers):
        """Test combining state filter with case type."""
        with get_db() as db:
            seed_test_providers(db, sample_providers)
            service = LegalAidSearchService(db)
            
            # Search for Criminal Law in Maharashtra
            results = service.search(
                state="Maharashtra",
                case_type="Criminal Law"
            )
            
            # Should only return Mumbai provider (has Criminal Law)
            assert len(results) == 1
            assert results[0]["city"] == "Mumbai"
            assert "Criminal Law" in results[0]["specializations"]
