"""
Emergency SOS API endpoints.

This module implements endpoints for emergency contacts with:
- Fast retrieval (<1 second response time)
- Location-based filtering
- Category-based organization
- National fallback contacts
- Emergency mode toggle with quick access to evidence documentation

Requirements: 8.2 (Response time), 8.3 (Categorization), 8.4 (Callable numbers), 
              8.5 (Location-specific), 8.6 (National fallback), 8.7 (Evidence access)
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, List, Optional

from database import get_db
from emergency_contacts_service import EmergencyContactsService
from models.user import User
from utils.jwt import get_current_user


router = APIRouter(prefix="/api/emergency", tags=["emergency"])


# Response models
class EmergencyContactResponse(BaseModel):
    """Response model for a single emergency contact."""
    id: str
    name: str
    phone_number: str
    description: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    is_national: bool
    callable: bool  # Indicates one-tap calling capability


class CategorizedContactsResponse(BaseModel):
    """Response model for categorized emergency contacts."""
    police: List[EmergencyContactResponse]
    legal_helpline: List[EmergencyContactResponse]
    mental_health: List[EmergencyContactResponse]
    student_services: List[EmergencyContactResponse]
    total_contacts: int
    response_time_ms: Optional[float] = None


@router.get("/contacts", response_model=CategorizedContactsResponse)
async def get_emergency_contacts(
    location: Optional[str] = Query(None, description="General location (city or state)"),
    state: Optional[str] = Query(None, description="Specific state"),
    city: Optional[str] = Query(None, description="Specific city"),
    db: Session = Depends(get_db)
):
    """
    Get emergency contacts organized by category.
    
    This endpoint:
    1. Retrieves location-specific contacts if location provided
    2. Always includes national fallback contacts
    3. Organizes contacts by category (police, legal, mental health, student services)
    4. Returns results within 1 second for emergency situations
    5. All phone numbers have one-tap calling capability
    
    Query Parameters:
        location: General location search (searches both city and state)
        state: Specific state to filter by
        city: Specific city to filter by
        
    Returns:
        CategorizedContactsResponse with contacts organized by category
        
    Requirements: 8.2 (Response time <1s), 8.3 (4+ categories), 8.4 (Callable numbers),
                  8.5 (Location-specific), 8.6 (National fallback)
    """
    import time
    start_time = time.time()
    
    try:
        # Create service
        service = EmergencyContactsService(db)
        
        # Get categorized contacts
        categorized = service.get_contacts(
            location=location,
            state=state,
            city=city
        )
        
        # Convert to response models
        police_contacts = [
            EmergencyContactResponse(**contact)
            for contact in categorized['police']
        ]
        
        legal_contacts = [
            EmergencyContactResponse(**contact)
            for contact in categorized['legal_helpline']
        ]
        
        mental_health_contacts = [
            EmergencyContactResponse(**contact)
            for contact in categorized['mental_health']
        ]
        
        student_services_contacts = [
            EmergencyContactResponse(**contact)
            for contact in categorized['student_services']
        ]
        
        # Calculate response time
        end_time = time.time()
        response_time_ms = (end_time - start_time) * 1000
        
        # Calculate total contacts
        total = (
            len(police_contacts) +
            len(legal_contacts) +
            len(mental_health_contacts) +
            len(student_services_contacts)
        )
        
        return CategorizedContactsResponse(
            police=police_contacts,
            legal_helpline=legal_contacts,
            mental_health=mental_health_contacts,
            student_services=student_services_contacts,
            total_contacts=total,
            response_time_ms=response_time_ms
        )
        
    except Exception as e:
        print(f"Error retrieving emergency contacts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving emergency contacts. Please try again."
        )


@router.get("/contacts/{category}", response_model=List[EmergencyContactResponse])
async def get_emergency_contacts_by_category(
    category: str,
    location: Optional[str] = Query(None, description="General location (city or state)"),
    state: Optional[str] = Query(None, description="Specific state"),
    city: Optional[str] = Query(None, description="Specific city"),
    db: Session = Depends(get_db)
):
    """
    Get emergency contacts for a specific category.
    
    Args:
        category: Contact category (police, legal_helpline, mental_health, student_services)
        location: General location search
        state: Specific state to filter by
        city: Specific city to filter by
        db: Database session
        
    Returns:
        List of emergency contacts in the specified category
        
    Raises:
        HTTPException: If category is invalid
    """
    try:
        # Create service
        service = EmergencyContactsService(db)
        
        # Get contacts by category
        contacts = service.get_contacts_by_category(
            category=category,
            location=location,
            state=state,
            city=city
        )
        
        # Convert to response models
        return [EmergencyContactResponse(**contact) for contact in contacts]
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        print(f"Error retrieving emergency contacts by category: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving emergency contacts. Please try again."
        )


@router.get("/contacts/national/all", response_model=CategorizedContactsResponse)
async def get_national_emergency_contacts(db: Session = Depends(get_db)):
    """
    Get all national emergency contacts organized by category.
    
    This endpoint returns only national-level emergency contacts that are
    available across India, serving as fallback options when location-specific
    contacts are not available.
    
    Args:
        db: Database session
        
    Returns:
        CategorizedContactsResponse with national contacts only
        
    Requirements: 8.6 (National fallback contacts)
    """
    import time
    start_time = time.time()
    
    try:
        # Create service
        service = EmergencyContactsService(db)
        
        # Get national contacts
        categorized = service.get_national_contacts()
        
        # Convert to response models
        police_contacts = [
            EmergencyContactResponse(**contact)
            for contact in categorized['police']
        ]
        
        legal_contacts = [
            EmergencyContactResponse(**contact)
            for contact in categorized['legal_helpline']
        ]
        
        mental_health_contacts = [
            EmergencyContactResponse(**contact)
            for contact in categorized['mental_health']
        ]
        
        student_services_contacts = [
            EmergencyContactResponse(**contact)
            for contact in categorized['student_services']
        ]
        
        # Calculate response time
        end_time = time.time()
        response_time_ms = (end_time - start_time) * 1000
        
        # Calculate total contacts
        total = (
            len(police_contacts) +
            len(legal_contacts) +
            len(mental_health_contacts) +
            len(student_services_contacts)
        )
        
        return CategorizedContactsResponse(
            police=police_contacts,
            legal_helpline=legal_contacts,
            mental_health=mental_health_contacts,
            student_services=student_services_contacts,
            total_contacts=total,
            response_time_ms=response_time_ms
        )
        
    except Exception as e:
        print(f"Error retrieving national emergency contacts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving national emergency contacts. Please try again."
        )
