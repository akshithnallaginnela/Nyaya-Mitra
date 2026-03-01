"""
Legal Aid API endpoints.

This module implements endpoints for searching and retrieving legal aid providers.
Supports multi-criteria filtering and provides detailed provider information.

Requirements: 5.2 (Provider information), 5.4 (Multiple contact methods)
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from database import get_db
from legal_aid_search_service import LegalAidSearchService


router = APIRouter(prefix="/api/legal-aid", tags=["legal-aid"])


# Response models
class ContactInfo(BaseModel):
    """Contact information for a legal aid provider."""
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None


class LegalAidProviderResponse(BaseModel):
    """Response model for legal aid provider."""
    id: str
    name: str
    organization_type: str
    specializations: List[str]
    languages_supported: List[str]
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    address: Optional[str] = None
    city: str
    state: str
    is_verified: bool
    relevance_score: Optional[float] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class LegalAidProviderDetailResponse(BaseModel):
    """Detailed response model for a specific legal aid provider."""
    id: str
    name: str
    organization_type: str
    specializations: List[str]
    languages_supported: List[str]
    contact_info: ContactInfo
    availability: str
    city: str
    state: str
    is_verified: bool
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class LegalAidSearchResponse(BaseModel):
    """Response model for legal aid search results."""
    providers: List[LegalAidProviderResponse]
    total: int
    is_fallback: bool


@router.get("/search", response_model=LegalAidSearchResponse)
async def search_legal_aid_providers(
    location: Optional[str] = Query(None, description="General location (city or state)"),
    case_type: Optional[str] = Query(None, description="Type of legal case"),
    language: Optional[str] = Query(None, description="Preferred language"),
    expertise: Optional[str] = Query(None, description="Specific legal expertise"),
    state: Optional[str] = Query(None, description="Specific state"),
    city: Optional[str] = Query(None, description="Specific city"),
    db: Session = Depends(get_db)
):
    """
    Search for legal aid providers with multi-criteria filtering.
    
    This endpoint:
    1. Accepts query parameters for filtering (location, case type, language, expertise)
    2. Searches for matching providers in the database
    3. Calculates relevance scores for each provider
    4. Returns sorted results by relevance
    5. Falls back to national helplines if no local results found
    
    Query Parameters:
        location: General location search (searches both city and state)
        case_type: Type of legal case (e.g., "Criminal Law", "Family Law")
        language: Preferred language for communication
        expertise: Specific legal expertise required
        state: Specific state to search in
        city: Specific city to search in
        
    Returns:
        LegalAidSearchResponse with matching providers and metadata
        
    Requirements: 5.1 (Location and case type filtering), 5.2 (Provider information),
                  5.3 (Multi-criteria filtering), 5.6 (National fallback)
    """
    try:
        # Create search service
        search_service = LegalAidSearchService(db)
        
        # Perform search
        results = search_service.search(
            location=location,
            case_type=case_type,
            language=language,
            expertise=expertise,
            state=state,
            city=city
        )
        
        # Check if results are national helplines (fallback)
        is_fallback = False
        if results and results[0].get('is_national_helpline', False):
            is_fallback = True
        
        # Convert to response models
        providers = []
        for result in results:
            providers.append(LegalAidProviderResponse(
                id=result.get('id', ''),
                name=result['name'],
                organization_type=result['organization_type'],
                specializations=result['specializations'],
                languages_supported=result['languages_supported'],
                contact_phone=result.get('contact_phone'),
                contact_email=result.get('contact_email'),
                address=result.get('address'),
                city=result['city'],
                state=result['state'],
                is_verified=result.get('is_verified', False),
                relevance_score=result.get('relevance_score'),
                created_at=result.get('created_at'),
                updated_at=result.get('updated_at')
            ))
        
        return LegalAidSearchResponse(
            providers=providers,
            total=len(providers),
            is_fallback=is_fallback
        )
        
    except Exception as e:
        print(f"Error searching legal aid providers: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while searching for legal aid providers. Please try again."
        )


@router.get("/{provider_id}", response_model=LegalAidProviderDetailResponse)
async def get_legal_aid_provider(
    provider_id: str,
    db: Session = Depends(get_db)
):
    """
    Get detailed information for a specific legal aid provider.
    
    This endpoint:
    1. Retrieves provider by ID
    2. Returns complete provider information
    3. Includes multiple contact methods (phone, email, address, website)
    4. Provides availability information
    
    Args:
        provider_id: UUID of the legal aid provider
        db: Database session
        
    Returns:
        LegalAidProviderDetailResponse with complete provider details
        
    Raises:
        HTTPException: If provider not found
        
    Requirements: 5.2 (Provider information), 5.4 (Multiple contact methods)
    """
    try:
        # Create search service
        search_service = LegalAidSearchService(db)
        
        # Get provider by ID
        provider = search_service.get_provider_by_id(provider_id)
        
        if not provider:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Legal aid provider with ID {provider_id} not found"
            )
        
        # Build contact info with multiple methods
        contact_info = ContactInfo(
            phone=provider.get('contact_phone'),
            email=provider.get('contact_email'),
            address=provider.get('address'),
            website=None  # Website field not in current model, can be added later
        )
        
        # Determine availability (simplified - can be enhanced with actual availability data)
        availability = "Available during business hours (9 AM - 5 PM, Monday-Friday)"
        if provider.get('is_verified'):
            availability = "Verified provider - Available during business hours (9 AM - 5 PM, Monday-Friday)"
        
        return LegalAidProviderDetailResponse(
            id=provider['id'],
            name=provider['name'],
            organization_type=provider['organization_type'],
            specializations=provider['specializations'],
            languages_supported=provider['languages_supported'],
            contact_info=contact_info,
            availability=availability,
            city=provider['city'],
            state=provider['state'],
            is_verified=provider.get('is_verified', False),
            created_at=provider.get('created_at'),
            updated_at=provider.get('updated_at')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error retrieving legal aid provider: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the legal aid provider. Please try again."
        )
