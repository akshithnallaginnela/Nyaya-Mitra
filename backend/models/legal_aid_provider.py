"""
Legal Aid Provider model for legal aid search system.

This module implements the LegalAidProvider model to store information
about legal aid organizations and individuals offering free legal services,
with efficient searching by location and specialization.

Requirements: 5.1 (Legal aid search), 5.2 (Provider information)
"""

from typing import Dict, List, Optional

from sqlalchemy import Boolean, Column, Index, String, Text
from sqlalchemy.orm import validates

from database import BaseModel


class LegalAidProvider(BaseModel):
    """
    Legal Aid Provider model for storing legal aid service information.
    
    Inherits from BaseModel which provides:
    - id: UUID primary key
    - created_at: Timestamp of record creation
    - updated_at: Timestamp of last update
    
    Additional fields:
    - name: Provider or organization name
    - organization_type: Type of organization (NGO, Government, Law Firm, etc.)
    - specializations: JSON array of legal specializations
    - languages_supported: JSON array of supported languages
    - contact_phone: Phone number for contact
    - contact_email: Email address for contact
    - address: Physical address
    - city: City location
    - state: State location
    - is_verified: Whether the provider has been verified
    
    Indexes:
    - city: For efficient location-based searches
    - state: For efficient state-level searches
    - organization_type: For filtering by organization type
    - Composite index on (city, state) for combined location searches
    """
    
    __tablename__ = "legal_aid_providers"
    
    name = Column(
        String(255),
        nullable=False
    )
    
    organization_type = Column(
        String(100),
        nullable=False,
        index=True
    )
    
    specializations = Column(
        Text,  # Store as JSON string
        nullable=False
    )
    
    languages_supported = Column(
        Text,  # Store as JSON string
        nullable=False
    )
    
    contact_phone = Column(
        String(20),
        nullable=True
    )
    
    contact_email = Column(
        String(255),
        nullable=True
    )
    
    address = Column(
        Text,
        nullable=True
    )
    
    city = Column(
        String(100),
        nullable=False,
        index=True
    )
    
    state = Column(
        String(100),
        nullable=False,
        index=True
    )
    
    is_verified = Column(
        Boolean,
        default=False,
        nullable=False
    )
    
    # Composite index for efficient location-based searches
    __table_args__ = (
        Index('idx_city_state', 'city', 'state'),
    )
    
    # Valid organization types
    VALID_ORGANIZATION_TYPES = {
        'NGO',
        'Government',
        'Law Firm',
        'Legal Aid Society',
        'Bar Association',
        'University Legal Clinic',
        'Pro Bono Service',
        'Community Legal Center',
        'Other'
    }
    
    @validates('name')
    def validate_name(self, key: str, name: str) -> str:
        """
        Validate provider name.
        
        Args:
            key: Field name (automatically provided by SQLAlchemy)
            name: Provider name to validate
            
        Returns:
            str: Validated and trimmed name
            
        Raises:
            ValueError: If name is empty or too short
        """
        if not name or not name.strip():
            raise ValueError("Provider name is required")
        
        name = name.strip()
        
        if len(name) < 2:
            raise ValueError("Provider name must be at least 2 characters")
        
        return name
    
    @validates('organization_type')
    def validate_organization_type(self, key: str, org_type: str) -> str:
        """
        Validate organization type.
        
        Args:
            key: Field name (automatically provided by SQLAlchemy)
            org_type: Organization type to validate
            
        Returns:
            str: Validated organization type
            
        Raises:
            ValueError: If organization type is invalid
        """
        if not org_type or not org_type.strip():
            raise ValueError("Organization type is required")
        
        org_type = org_type.strip()
        
        if org_type not in self.VALID_ORGANIZATION_TYPES:
            raise ValueError(
                f"Invalid organization type. Must be one of: {', '.join(self.VALID_ORGANIZATION_TYPES)}"
            )
        
        return org_type
    
    @validates('city')
    def validate_city(self, key: str, city: str) -> str:
        """
        Validate city name.
        
        Args:
            key: Field name (automatically provided by SQLAlchemy)
            city: City name to validate
            
        Returns:
            str: Validated and trimmed city name
            
        Raises:
            ValueError: If city is empty
        """
        if not city or not city.strip():
            raise ValueError("City is required")
        
        return city.strip()
    
    @validates('state')
    def validate_state(self, key: str, state: str) -> str:
        """
        Validate state name.
        
        Args:
            key: Field name (automatically provided by SQLAlchemy)
            state: State name to validate
            
        Returns:
            str: Validated and trimmed state name
            
        Raises:
            ValueError: If state is empty
        """
        if not state or not state.strip():
            raise ValueError("State is required")
        
        return state.strip()
    
    @validates('contact_email')
    def validate_contact_email(self, key: str, email: Optional[str]) -> Optional[str]:
        """
        Validate contact email format.
        
        Args:
            key: Field name (automatically provided by SQLAlchemy)
            email: Email address to validate
            
        Returns:
            Optional[str]: Validated and normalized email (lowercase) or None
            
        Raises:
            ValueError: If email format is invalid
        """
        if email is None or not email.strip():
            return None
        
        email = email.strip().lower()
        
        # Basic email validation
        if '@' not in email:
            raise ValueError("Invalid email format")
        
        parts = email.split('@')
        if len(parts) != 2 or not parts[0] or not parts[1]:
            raise ValueError("Invalid email format")
        
        # Check domain part has a dot and valid structure
        domain = parts[1]
        if '.' not in domain or domain.startswith('.') or domain.endswith('.'):
            raise ValueError("Invalid email format")
        
        return email
    
    @validates('contact_phone')
    def validate_contact_phone(self, key: str, phone: Optional[str]) -> Optional[str]:
        """
        Validate contact phone number.
        
        Args:
            key: Field name (automatically provided by SQLAlchemy)
            phone: Phone number to validate
            
        Returns:
            Optional[str]: Validated phone number or None
            
        Raises:
            ValueError: If phone format is invalid
        """
        if phone is None or not phone.strip():
            return None
        
        phone = phone.strip()
        
        # Remove common formatting characters
        cleaned_phone = ''.join(c for c in phone if c.isdigit() or c in ['+', '-', ' ', '(', ')'])
        
        # Check if we have at least 10 digits (minimum for Indian phone numbers)
        digits_only = ''.join(c for c in cleaned_phone if c.isdigit())
        if len(digits_only) < 10:
            raise ValueError("Phone number must contain at least 10 digits")
        
        return phone
    
    def __repr__(self) -> str:
        """String representation of LegalAidProvider model."""
        return f"<LegalAidProvider(id={self.id}, name={self.name}, city={self.city}, state={self.state})>"
