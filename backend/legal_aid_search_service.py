"""
Legal Aid Search Service

This service implements search logic for legal aid providers with:
- Multi-criteria filtering (location, case type, language, expertise)
- Relevance scoring for search results
- Fallback to national helplines when no local results found

Requirements: 5.1 (Location and case type filtering), 5.3 (Multi-criteria filtering), 
              5.6 (National fallback)
"""

import json
from typing import Dict, List, Optional, Tuple
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from models.legal_aid_provider import LegalAidProvider


# National helplines as fallback when no local providers found
NATIONAL_HELPLINES = [
    {
        "name": "National Legal Services Authority (NALSA) Helpline",
        "organization_type": "Government",
        "specializations": ["Criminal Law", "Civil Law", "Family Law", "Consumer Rights", "Labour Law"],
        "languages_supported": ["English", "Hindi"],
        "contact_phone": "15100",
        "contact_email": "nalsa@nic.in",
        "website": "https://nalsa.gov.in",
        "address": "Supreme Court of India, Tilak Marg, New Delhi",
        "city": "New Delhi",
        "state": "Delhi",
        "is_verified": True,
        "is_national_helpline": True
    },
    {
        "name": "National Commission for Women Helpline",
        "organization_type": "Government",
        "specializations": ["Women's Rights", "Domestic Violence", "Sexual Harassment", "Family Law"],
        "languages_supported": ["English", "Hindi"],
        "contact_phone": "7827-170-170",
        "contact_email": "complaints@ncw.nic.in",
        "website": "http://ncw.nic.in",
        "address": "Plot-21, Jasola Institutional Area, New Delhi",
        "city": "New Delhi",
        "state": "Delhi",
        "is_verified": True,
        "is_national_helpline": True
    },
    {
        "name": "National Consumer Helpline",
        "organization_type": "Government",
        "specializations": ["Consumer Rights", "Consumer Disputes", "Product Complaints"],
        "languages_supported": ["English", "Hindi"],
        "contact_phone": "1800-11-4000",
        "contact_email": "nch@nic.in",
        "website": "https://consumerhelpline.gov.in",
        "address": "Krishi Bhawan, New Delhi",
        "city": "New Delhi",
        "state": "Delhi",
        "is_verified": True,
        "is_national_helpline": True
    }
]


class LegalAidSearchService:
    """
    Service for searching legal aid providers with multi-criteria filtering
    and relevance scoring.
    """
    
    def __init__(self, db: Session):
        """
        Initialize the search service.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def search(
        self,
        location: Optional[str] = None,
        case_type: Optional[str] = None,
        language: Optional[str] = None,
        expertise: Optional[str] = None,
        state: Optional[str] = None,
        city: Optional[str] = None
    ) -> List[Dict]:
        """
        Search for legal aid providers with multi-criteria filtering.
        
        Args:
            location: General location search (searches both city and state)
            case_type: Type of legal case (e.g., "Criminal Law", "Family Law")
            language: Preferred language for communication
            expertise: Specific legal expertise required
            state: Specific state to search in
            city: Specific city to search in
            
        Returns:
            List[Dict]: List of matching providers with relevance scores, sorted by score
        """
        # Build query with filters
        query = self.db.query(LegalAidProvider)
        filters = []
        
        # Location filtering (city or state)
        if city:
            filters.append(LegalAidProvider.city.ilike(f"%{city}%"))
        if state:
            filters.append(LegalAidProvider.state.ilike(f"%{state}%"))
        if location and not city and not state:
            # Search in both city and state if general location provided
            filters.append(
                or_(
                    LegalAidProvider.city.ilike(f"%{location}%"),
                    LegalAidProvider.state.ilike(f"%{location}%")
                )
            )
        
        # Apply filters
        if filters:
            query = query.filter(and_(*filters))
        
        # Execute query
        providers = query.all()
        
        # Convert to dictionaries and apply additional filtering with scoring
        results = []
        for provider in providers:
            provider_dict = self._provider_to_dict(provider)
            
            # Calculate relevance score
            score = self._calculate_relevance_score(
                provider_dict,
                case_type=case_type,
                language=language,
                expertise=expertise
            )
            
            # Only include if score > 0 (meaning at least some criteria matched)
            # or if no optional criteria were specified
            if score > 0 or (not case_type and not language and not expertise):
                provider_dict['relevance_score'] = score
                results.append(provider_dict)
        
        # Sort by relevance score (highest first)
        results.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        # If no results found, return national helplines
        if not results:
            return self._get_national_helplines_with_scores(
                case_type=case_type,
                language=language
            )
        
        return results
    
    def _provider_to_dict(self, provider: LegalAidProvider) -> Dict:
        """
        Convert LegalAidProvider model to dictionary.
        
        Args:
            provider: LegalAidProvider model instance
            
        Returns:
            Dict: Provider data as dictionary
        """
        return {
            'id': str(provider.id),
            'name': provider.name,
            'organization_type': provider.organization_type,
            'specializations': json.loads(provider.specializations),
            'languages_supported': json.loads(provider.languages_supported),
            'contact_phone': provider.contact_phone,
            'contact_email': provider.contact_email,
            'address': provider.address,
            'city': provider.city,
            'state': provider.state,
            'is_verified': provider.is_verified,
            'created_at': provider.created_at.isoformat() if provider.created_at else None,
            'updated_at': provider.updated_at.isoformat() if provider.updated_at else None
        }
    
    def _calculate_relevance_score(
        self,
        provider: Dict,
        case_type: Optional[str] = None,
        language: Optional[str] = None,
        expertise: Optional[str] = None
    ) -> float:
        """
        Calculate relevance score for a provider based on search criteria.
        
        Scoring system:
        - Case type match: 40 points
        - Language match: 30 points
        - Expertise match: 20 points
        - Verified provider: 10 points bonus
        
        Args:
            provider: Provider data dictionary
            case_type: Desired case type
            language: Desired language
            expertise: Desired expertise
            
        Returns:
            float: Relevance score (0-100)
        """
        score = 0.0
        
        # Case type matching (40 points)
        if case_type:
            specializations = provider.get('specializations', [])
            if self._fuzzy_match(case_type, specializations):
                score += 40
        
        # Language matching (30 points)
        if language:
            languages = provider.get('languages_supported', [])
            if self._fuzzy_match(language, languages):
                score += 30
        
        # Expertise matching (20 points)
        # Expertise is similar to case type but more specific
        if expertise:
            specializations = provider.get('specializations', [])
            if self._fuzzy_match(expertise, specializations):
                score += 20
        
        # Verified provider bonus (10 points)
        if provider.get('is_verified', False):
            score += 10
        
        return score
    
    def _fuzzy_match(self, search_term: str, items: List[str]) -> bool:
        """
        Perform fuzzy matching of search term against list of items.
        
        Args:
            search_term: Term to search for
            items: List of items to search in
            
        Returns:
            bool: True if match found, False otherwise
        """
        if not search_term or not items:
            return False
        
        search_term_lower = search_term.lower().strip()
        
        for item in items:
            item_lower = item.lower().strip()
            
            # Exact match
            if search_term_lower == item_lower:
                return True
            
            # Partial match (search term in item or item in search term)
            if search_term_lower in item_lower or item_lower in search_term_lower:
                return True
        
        return False
    
    def _get_national_helplines_with_scores(
        self,
        case_type: Optional[str] = None,
        language: Optional[str] = None
    ) -> List[Dict]:
        """
        Get national helplines with relevance scores as fallback.
        
        Args:
            case_type: Desired case type
            language: Desired language
            
        Returns:
            List[Dict]: National helplines with relevance scores
        """
        results = []
        
        for helpline in NATIONAL_HELPLINES:
            # Calculate relevance score for helpline
            score = self._calculate_relevance_score(
                helpline,
                case_type=case_type,
                language=language
            )
            
            helpline_copy = helpline.copy()
            helpline_copy['relevance_score'] = score
            results.append(helpline_copy)
        
        # Sort by relevance score
        results.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return results
    
    def get_provider_by_id(self, provider_id: str) -> Optional[Dict]:
        """
        Get detailed information for a specific provider by ID.
        
        Args:
            provider_id: UUID of the provider
            
        Returns:
            Optional[Dict]: Provider data or None if not found
        """
        provider = self.db.query(LegalAidProvider).filter(
            LegalAidProvider.id == provider_id
        ).first()
        
        if not provider:
            return None
        
        return self._provider_to_dict(provider)
