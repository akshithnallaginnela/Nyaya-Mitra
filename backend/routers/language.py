"""
Language switching endpoints for Nyaya Mitra.

This module implements language preference management:
- GET /api/language/preference - Get user's language preference
- PUT /api/language/preference - Update user's language preference
- GET /api/language/translations/{language} - Get all translations for a language

Requirements: 6.3 (Language preference), 6.4 (Language switching)
"""

from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import get_db_session
from models.user import User
from translation_service import get_translation_service
from utils.jwt import get_current_user


router = APIRouter(prefix="/api/language", tags=["language"])


# Request/Response Models

class LanguagePreferenceResponse(BaseModel):
    """Response model for language preference."""
    preferred_language: str = Field(..., description="User's preferred language code")
    
    class Config:
        json_schema_extra = {
            "example": {
                "preferred_language": "hi"
            }
        }


class UpdateLanguageRequest(BaseModel):
    """Request model for updating language preference."""
    language: str = Field(..., description="New language code")
    
    class Config:
        json_schema_extra = {
            "example": {
                "language": "hi"
            }
        }


class TranslationsResponse(BaseModel):
    """Response model for translations."""
    language: str = Field(..., description="Language code")
    translations: Dict[str, str] = Field(..., description="Translation key-value pairs")
    
    class Config:
        json_schema_extra = {
            "example": {
                "language": "hi",
                "translations": {
                    "app.title": "न्याय मित्र",
                    "auth.login": "लॉग इन करें",
                    "auth.register": "पंजीकरण करें"
                }
            }
        }


# Endpoints

@router.get(
    "/preference",
    response_model=LanguagePreferenceResponse,
    summary="Get user's language preference",
    description="Retrieve the authenticated user's preferred language"
)
async def get_language_preference(
    current_user: User = Depends(get_current_user)
) -> LanguagePreferenceResponse:
    """
    Get the authenticated user's language preference.
    
    Args:
        current_user: Authenticated user from JWT token
        
    Returns:
        LanguagePreferenceResponse: User's preferred language code
        
    Raises:
        HTTPException 401: If authentication fails
    """
    return LanguagePreferenceResponse(
        preferred_language=current_user.preferred_language
    )


@router.put(
    "/preference",
    response_model=LanguagePreferenceResponse,
    summary="Update user's language preference",
    description="Update the authenticated user's preferred language"
)
async def update_language_preference(
    request: UpdateLanguageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
) -> LanguagePreferenceResponse:
    """
    Update the authenticated user's language preference.
    
    This endpoint:
    1. Validates the language code against supported languages
    2. Updates the user's preferred_language field
    3. Returns the updated preference
    
    Supported languages: en, hi, ta, te, bn, mr, gu, kn, ml, pa
    
    Args:
        request: Update request with new language code
        current_user: Authenticated user from JWT token
        db: Database session
        
    Returns:
        LanguagePreferenceResponse: Updated language preference
        
    Raises:
        HTTPException 400: If language code is invalid
        HTTPException 401: If authentication fails
    """
    # Supported languages as per requirement 6.1
    supported_languages = {
        'en', 'hi', 'ta', 'te', 'bn', 'mr', 'gu', 'kn', 'ml', 'pa'
    }
    
    if request.language not in supported_languages:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported language. Must be one of: {', '.join(sorted(supported_languages))}"
        )
    
    try:
        # Update user's language preference
        current_user.preferred_language = request.language
        db.commit()
        db.refresh(current_user)
        
        return LanguagePreferenceResponse(
            preferred_language=current_user.preferred_language
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update language preference: {str(e)}"
        )


@router.get(
    "/translations/{language}",
    response_model=TranslationsResponse,
    summary="Get all translations for a language",
    description="Retrieve all UI element translations for the specified language"
)
async def get_translations(
    language: str
) -> TranslationsResponse:
    """
    Get all UI element translations for a language.
    
    This endpoint returns all translation key-value pairs for the specified
    language. If the language is not supported, it falls back to English.
    
    Supported languages: en, hi, ta, te, bn, mr, gu
    
    Args:
        language: Language code
        
    Returns:
        TranslationsResponse: All translations for the language
    """
    # Supported languages with translation files
    supported_languages = {'en', 'hi', 'ta', 'te', 'bn', 'mr', 'gu'}
    
    # Fallback to English if language not supported
    if language not in supported_languages:
        language = 'en'
    
    # Get translation service
    translation_service = get_translation_service()
    
    # Get all translations for the language
    translations = translation_service.get_all_translations(language)
    
    return TranslationsResponse(
        language=language,
        translations=translations
    )
