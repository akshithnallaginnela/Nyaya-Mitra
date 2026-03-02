"""
Emergency Contacts Service

This service provides fast retrieval of emergency contacts with:
- Location-based filtering (state/city)
- Category-based filtering
- National fallback contacts
- Optimized for <1 second response time
- Caching for improved performance

Requirements: 8.2 (Response time), 8.3 (Categorization), 8.5 (Location-specific), 8.6 (National fallback)
"""

from typing import Dict, List, Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from models.emergency_contact import EmergencyContact
from utils.cache import cache, cache_key


class EmergencyContactsService:
    """
    Service for retrieving emergency contacts.
    
    Provides fast, categorized access to emergency contacts with
    location-based filtering and national fallbacks.
    """
    
    def __init__(self, db: Session):
        """
        Initialize the emergency contacts service.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def get_contacts(
        self,
        location: Optional[str] = None,
        state: Optional[str] = None,
        city: Optional[str] = None
    ) -> Dict[str, List[Dict]]:
        """
        Get emergency contacts organized by category.
        
        This method:
        1. Retrieves location-specific contacts if location provided
        2. Always includes national fallback contacts
        3. Organizes contacts by category (police, legal, mental health, student services)
        4. Optimized for <1 second response time
        5. Uses caching for improved performance
        
        Args:
            location: General location (searches both state and city)
            state: Specific state to filter by
            city: Specific city to filter by
            
        Returns:
            Dict with categories as keys and lists of contacts as values
            
        Requirements: 8.2 (Response time), 8.3 (Categorization), 
                      8.5 (Location-specific), 8.6 (National fallback)
        """
        # Check cache first
        key = cache_key("emergency_contacts", location=location, state=state, city=city)
        cached_result = cache.get(key)
        if cached_result:
            return cached_result
        
        # Build query for location-specific contacts
        location_contacts = []
        
        if location or state or city:
            query = self.db.query(EmergencyContact).filter(
                EmergencyContact.is_active == True,
                EmergencyContact.is_national == False
            )
            
            # Apply location filters
            if location:
                # Search in both state and city
                query = query.filter(
                    or_(
                        EmergencyContact.state.ilike(f"%{location}%"),
                        EmergencyContact.city.ilike(f"%{location}%")
                    )
                )
            
            if state:
                query = query.filter(EmergencyContact.state.ilike(f"%{state}%"))
            
            if city:
                query = query.filter(EmergencyContact.city.ilike(f"%{city}%"))
            
            location_contacts = query.all()
        
        # Always get national contacts as fallback
        national_contacts = self.db.query(EmergencyContact).filter(
            EmergencyContact.is_active == True,
            EmergencyContact.is_national == True
        ).all()
        
        # Combine location-specific and national contacts
        all_contacts = location_contacts + national_contacts
        
        # Organize by category
        categorized = {
            'police': [],
            'legal_helpline': [],
            'mental_health': [],
            'student_services': []
        }
        
        for contact in all_contacts:
            contact_dict = {
                'id': str(contact.id),
                'name': contact.name,
                'phone_number': contact.phone_number,
                'description': contact.description,
                'state': contact.state,
                'city': contact.city,
                'is_national': contact.is_national,
                'callable': True  # All phone numbers have calling capability
            }
            
            if contact.category in categorized:
                categorized[contact.category].append(contact_dict)
        
        # Cache for 10 minutes (emergency contacts don't change frequently)
        cache.set(key, categorized, ttl_seconds=600)
        
        return categorized
    
    def get_contacts_by_category(
        self,
        category: str,
        location: Optional[str] = None,
        state: Optional[str] = None,
        city: Optional[str] = None
    ) -> List[Dict]:
        """
        Get emergency contacts for a specific category.
        
        Args:
            category: Contact category (police, legal_helpline, mental_health, student_services)
            location: General location (searches both state and city)
            state: Specific state to filter by
            city: Specific city to filter by
            
        Returns:
            List of contacts in the specified category
            
        Raises:
            ValueError: If category is invalid
        """
        if category not in EmergencyContact.VALID_CATEGORIES:
            raise ValueError(
                f"Invalid category. Must be one of: {', '.join(EmergencyContact.VALID_CATEGORIES)}"
            )
        
        # Build query
        query = self.db.query(EmergencyContact).filter(
            EmergencyContact.is_active == True,
            EmergencyContact.category == category
        )
        
        # Apply location filters for non-national contacts
        if location or state or city:
            location_query = query.filter(EmergencyContact.is_national == False)
            
            if location:
                location_query = location_query.filter(
                    or_(
                        EmergencyContact.state.ilike(f"%{location}%"),
                        EmergencyContact.city.ilike(f"%{location}%")
                    )
                )
            
            if state:
                location_query = location_query.filter(
                    EmergencyContact.state.ilike(f"%{state}%")
                )
            
            if city:
                location_query = location_query.filter(
                    EmergencyContact.city.ilike(f"%{city}%")
                )
            
            location_contacts = location_query.all()
        else:
            location_contacts = []
        
        # Always include national contacts
        national_contacts = query.filter(EmergencyContact.is_national == True).all()
        
        # Combine and convert to dict
        all_contacts = location_contacts + national_contacts
        
        return [
            {
                'id': str(contact.id),
                'name': contact.name,
                'phone_number': contact.phone_number,
                'description': contact.description,
                'state': contact.state,
                'city': contact.city,
                'is_national': contact.is_national,
                'callable': True
            }
            for contact in all_contacts
        ]
    
    def get_national_contacts(self) -> Dict[str, List[Dict]]:
        """
        Get all national emergency contacts organized by category.
        
        Returns:
            Dict with categories as keys and lists of national contacts as values
            
        Requirements: 8.6 (National fallback contacts)
        """
        national_contacts = self.db.query(EmergencyContact).filter(
            EmergencyContact.is_active == True,
            EmergencyContact.is_national == True
        ).all()
        
        categorized = {
            'police': [],
            'legal_helpline': [],
            'mental_health': [],
            'student_services': []
        }
        
        for contact in national_contacts:
            contact_dict = {
                'id': str(contact.id),
                'name': contact.name,
                'phone_number': contact.phone_number,
                'description': contact.description,
                'is_national': True,
                'callable': True
            }
            
            if contact.category in categorized:
                categorized[contact.category].append(contact_dict)
        
        return categorized
    
    def verify_response_time(self) -> float:
        """
        Verify that emergency contacts can be retrieved within 1 second.
        
        Returns:
            Response time in seconds
            
        Requirements: 8.2 (Emergency response time <1 second)
        """
        import time
        
        start_time = time.time()
        self.get_contacts(location="Delhi")
        end_time = time.time()
        
        response_time = end_time - start_time
        return response_time
