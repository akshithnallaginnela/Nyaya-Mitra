"""
User model with authentication fields.

This module implements the User model with secure password hashing
using bcrypt with minimum 10 rounds, email validation, and password
strength validation.

Requirements: 9.1 (Password encryption), 6.4 (Language preference)
"""

import re
from typing import TYPE_CHECKING, List, Optional

import bcrypt
from sqlalchemy import Boolean, Column, String
from sqlalchemy.orm import relationship, validates

from database import BaseModel

if TYPE_CHECKING:
    from models.conversation import Conversation


class User(BaseModel):
    """
    User model for authentication and profile management.
    
    Inherits from BaseModel which provides:
    - id: UUID primary key
    - created_at: Timestamp of record creation
    - updated_at: Timestamp of last update
    
    Additional fields:
    - email: Unique email address for authentication
    - password_hash: Bcrypt hashed password (minimum 10 rounds)
    - full_name: User's full name
    - college_name: Optional college/institution name
    - preferred_language: Language preference (default: 'en')
    - is_active: Account active status (default: True)
    """
    
    __tablename__ = "users"
    
    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )
    
    password_hash = Column(
        String(255),
        nullable=False
    )
    
    full_name = Column(
        String(255),
        nullable=False
    )
    
    college_name = Column(
        String(255),
        nullable=True
    )
    
    preferred_language = Column(
        String(10),
        default="en",
        nullable=False
    )
    
    is_active = Column(
        Boolean,
        default=True,
        nullable=False
    )
    
    # Relationships
    conversations = relationship(
        "Conversation",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    # Email validation pattern
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    # Password strength requirements
    MIN_PASSWORD_LENGTH = 8
    PASSWORD_PATTERN = re.compile(
        r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]'
    )
    
    # Bcrypt rounds (minimum 10 as per requirement 9.1)
    BCRYPT_ROUNDS = 12
    
    @validates('email')
    def validate_email(self, key: str, email: str) -> str:
        """
        Validate email format.
        
        Args:
            key: Field name (automatically provided by SQLAlchemy)
            email: Email address to validate
            
        Returns:
            str: Validated and normalized email (lowercase)
            
        Raises:
            ValueError: If email format is invalid
        """
        if not email:
            raise ValueError("Email is required")
        
        email = email.strip().lower()
        
        if not self.EMAIL_PATTERN.match(email):
            raise ValueError("Invalid email format")
        
        return email
    
    @validates('full_name')
    def validate_full_name(self, key: str, full_name: str) -> str:
        """
        Validate full name.
        
        Args:
            key: Field name (automatically provided by SQLAlchemy)
            full_name: Full name to validate
            
        Returns:
            str: Validated and trimmed full name
            
        Raises:
            ValueError: If full name is empty or too short
        """
        if not full_name or not full_name.strip():
            raise ValueError("Full name is required")
        
        full_name = full_name.strip()
        
        if len(full_name) < 2:
            raise ValueError("Full name must be at least 2 characters")
        
        return full_name
    
    @validates('preferred_language')
    def validate_language(self, key: str, language: str) -> str:
        """
        Validate language code.
        
        Args:
            key: Field name (automatically provided by SQLAlchemy)
            language: Language code to validate
            
        Returns:
            str: Validated language code
            
        Raises:
            ValueError: If language code is invalid
        """
        # Supported languages as per requirement 6.1
        supported_languages = {
            'en', 'hi', 'ta', 'te', 'bn', 'mr', 'gu', 'kn', 'ml', 'pa'
        }
        
        if language not in supported_languages:
            raise ValueError(
                f"Unsupported language. Must be one of: {', '.join(supported_languages)}"
            )
        
        return language
    
    @classmethod
    def validate_password_strength(cls, password: str) -> None:
        """
        Validate password strength.
        
        Password must:
        - Be at least 8 characters long
        - Contain at least one lowercase letter
        - Contain at least one uppercase letter
        - Contain at least one digit
        - Contain at least one special character (@$!%*?&)
        
        Args:
            password: Password to validate
            
        Raises:
            ValueError: If password doesn't meet strength requirements
        """
        if not password:
            raise ValueError("Password is required")
        
        if len(password) < cls.MIN_PASSWORD_LENGTH:
            raise ValueError(
                f"Password must be at least {cls.MIN_PASSWORD_LENGTH} characters long"
            )
        
        if not re.search(r'[a-z]', password):
            raise ValueError("Password must contain at least one lowercase letter")
        
        if not re.search(r'[A-Z]', password):
            raise ValueError("Password must contain at least one uppercase letter")
        
        if not re.search(r'\d', password):
            raise ValueError("Password must contain at least one digit")
        
        if not re.search(r'[@$!%*?&]', password):
            raise ValueError(
                "Password must contain at least one special character (@$!%*?&)"
            )
    
    @classmethod
    def hash_password(cls, password: str) -> str:
        """
        Hash a password using bcrypt with minimum 10 rounds.
        
        As per requirement 9.1, passwords must be encrypted using bcrypt
        with a minimum of 10 rounds. This implementation uses 12 rounds
        for additional security.
        
        Args:
            password: Plain text password to hash
            
        Returns:
            str: Bcrypt hashed password
            
        Raises:
            ValueError: If password doesn't meet strength requirements
        """
        # Validate password strength before hashing
        cls.validate_password_strength(password)
        
        # Generate salt and hash password with 12 rounds (exceeds minimum of 10)
        salt = bcrypt.gensalt(rounds=cls.BCRYPT_ROUNDS)
        password_bytes = password.encode('utf-8')
        hashed = bcrypt.hashpw(password_bytes, salt)
        
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str) -> bool:
        """
        Verify a password against the stored hash.
        
        Args:
            password: Plain text password to verify
            
        Returns:
            bool: True if password matches, False otherwise
        """
        if not password or not self.password_hash:
            return False
        
        password_bytes = password.encode('utf-8')
        hash_bytes = self.password_hash.encode('utf-8')
        
        return bcrypt.checkpw(password_bytes, hash_bytes)
    
    def set_password(self, password: str) -> None:
        """
        Set a new password for the user.
        
        Validates password strength and hashes it using bcrypt.
        
        Args:
            password: Plain text password to set
            
        Raises:
            ValueError: If password doesn't meet strength requirements
        """
        self.password_hash = self.hash_password(password)
    
    def __repr__(self) -> str:
        """String representation of User model."""
        return f"<User(id={self.id}, email={self.email}, full_name={self.full_name})>"
