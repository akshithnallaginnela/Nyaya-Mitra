"""
Emergency Contact model for emergency SOS feature.

This module implements the EmergencyContact model to store emergency contacts
categorized by type (police, legal helplines, mental health, student services)
with location-specific and national fallback contacts.

Requirements: 8.3 (Contact categorization), 8.5 (Location-specific contacts), 8.6 (National fallback)
"""

from typing import Optional

from sqlalchemy import Boolean, Column, Index, String, Text
from sqlalchemy.orm import validates

from database import BaseModel


class EmergencyContact(BaseModel):
    """
    Emergency Contact model for storing emergency contact information.
    
    Inherits from BaseModel which provides:
    - id: UUID primary key
    - created_at: Timestamp of record creation
    - updated_at: Timestamp of last update
    
    Additional fields:
    - name: Contact name or organization
    - category: Type of emergency service (police, legal, mental_health, student_services)
    - phone_number: Phone number with calling capability
    - description: Brief description of the service
    - state: State location (None for national contacts)
    - city: City location (None for national/state-level contacts)
    - is_national: Whether this is a national fallback contact
    - is_active: Whether the contact is currently active
    
    Indexes:
    - category: For efficient filtering by service type
    - state: For location-based searches
    - is_national: For quick access to national fallback contacts
    - Composite index on (category, state) for combined searches
    """
    
    __tablename__ = "emergency_contacts"
    
    name = Column(
        String(255),
        nullable=False
    )
    
    category = Column(
        String(50),
        nullable=False,
        index=True
    )
    
    phone_number = Column(
        String(20),
        nullable=False
    )
    
    description = Column(
        Text,
        nullable=True
    )
    
    state = Column(
        String(100),
        nullable=True,
        index=True
    )
    
    city = Column(
        String(100),
        nullable=True
    )
    
    is_national = Column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )
    
    is_active = Column(
        Boolean,
        default=True,
        nullable=False
    )
    
    # Composite index for efficient category and location searches
    __table_args__ = (
        Index('idx_category_state', 'category', 'state'),
    )
    
    # Valid categories
    VALID_CATEGORIES = {
        'police',
        'legal_helpline',
        'mental_health',
        'student_services'
    }
    
    @validates('name')
    def validate_name(self, key: str, name: str) -> str:
        """Validate contact name."""
        if not name or not name.strip():
            raise ValueError("Contact name is required")
        
        name = name.strip()
        
        if len(name) < 2:
            raise ValueError("Contact name must be at least 2 characters")
        
        return name
    
    @validates('category')
    def validate_category(self, key: str, category: str) -> str:
        """Validate category."""
        if not category or not category.strip():
            raise ValueError("Category is required")
        
        category = category.strip().lower()
        
        if category not in self.VALID_CATEGORIES:
            raise ValueError(
                f"Invalid category. Must be one of: {', '.join(self.VALID_CATEGORIES)}"
            )
        
        return category
    
    @validates('phone_number')
    def validate_phone_number(self, key: str, phone: str) -> str:
        """Validate phone number."""
        if not phone or not phone.strip():
            raise ValueError("Phone number is required")
        
        phone = phone.strip()
        
        # Check if we have at least 10 digits (minimum for Indian phone numbers)
        digits_only = ''.join(c for c in phone if c.isdigit())
        if len(digits_only) < 10:
            raise ValueError("Phone number must contain at least 10 digits")
        
        return phone
    
    def __repr__(self) -> str:
        """String representation of EmergencyContact model."""
        location = f"{self.city}, {self.state}" if self.city and self.state else (self.state or "National")
        return f"<EmergencyContact(id={self.id}, name={self.name}, category={self.category}, location={location})>"
