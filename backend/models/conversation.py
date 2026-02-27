"""
Conversation and Message models for chat system.

This module implements the Conversation and Message models to support
the AI chat system with conversation context preservation and message
history tracking.

Requirements: 1.6 (Conversation context preservation)
"""

from typing import TYPE_CHECKING, List

from sqlalchemy import Column, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import relationship, validates

from database import BaseModel

if TYPE_CHECKING:
    from models.user import User


class Conversation(BaseModel):
    """
    Conversation model for tracking chat sessions.
    
    Inherits from BaseModel which provides:
    - id: UUID primary key
    - created_at: Timestamp of conversation creation
    - updated_at: Timestamp of last message
    
    Additional fields:
    - user_id: Foreign key to User model
    - title: Optional conversation title (auto-generated or user-set)
    - language: Language code for the conversation (default: 'en')
    
    Relationships:
    - user: Many-to-one relationship with User
    - messages: One-to-many relationship with Message
    """
    
    __tablename__ = "conversations"
    
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    title = Column(
        String(255),
        nullable=True
    )
    
    language = Column(
        String(10),
        default="en",
        nullable=False
    )
    
    # Relationships
    user: "User" = relationship(
        "User",
        back_populates="conversations"
    )
    
    messages: List["Message"] = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at"
    )
    
    @validates('language')
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
    
    def __repr__(self) -> str:
        """String representation of Conversation model."""
        return f"<Conversation(id={self.id}, user_id={self.user_id}, title={self.title})>"


class Message(BaseModel):
    """
    Message model for storing chat messages.
    
    Inherits from BaseModel which provides:
    - id: UUID primary key
    - created_at: Timestamp of message creation
    - updated_at: Timestamp of last update
    
    Additional fields:
    - conversation_id: Foreign key to Conversation model
    - role: Message role ('user' or 'assistant')
    - content: Message text content
    - citations: JSON array of legal citations (for assistant messages)
    - confidence_score: AI confidence score 0.0-1.0 (for assistant messages)
    
    Relationships:
    - conversation: Many-to-one relationship with Conversation
    """
    
    __tablename__ = "messages"
    
    conversation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    role = Column(
        String(20),
        nullable=False
    )
    
    content = Column(
        Text,
        nullable=False
    )
    
    citations = Column(
        JSON,
        nullable=True
    )
    
    confidence_score = Column(
        Float,
        nullable=True
    )
    
    # Relationships
    conversation: "Conversation" = relationship(
        "Conversation",
        back_populates="messages"
    )
    
    @validates('role')
    def validate_role(self, key: str, role: str) -> str:
        """
        Validate message role.
        
        Args:
            key: Field name (automatically provided by SQLAlchemy)
            role: Message role to validate
            
        Returns:
            str: Validated role
            
        Raises:
            ValueError: If role is invalid
        """
        valid_roles = {'user', 'assistant'}
        
        if role not in valid_roles:
            raise ValueError(
                f"Invalid role. Must be one of: {', '.join(valid_roles)}"
            )
        
        return role
    
    @validates('content')
    def validate_content(self, key: str, content: str) -> str:
        """
        Validate message content.
        
        Args:
            key: Field name (automatically provided by SQLAlchemy)
            content: Message content to validate
            
        Returns:
            str: Validated content
            
        Raises:
            ValueError: If content is empty
        """
        if not content or not content.strip():
            raise ValueError("Message content cannot be empty")
        
        return content
    
    @validates('confidence_score')
    def validate_confidence_score(self, key: str, score: float) -> float:
        """
        Validate confidence score.
        
        Args:
            key: Field name (automatically provided by SQLAlchemy)
            score: Confidence score to validate
            
        Returns:
            float: Validated confidence score
            
        Raises:
            ValueError: If score is out of range
        """
        if score is not None and (score < 0.0 or score > 1.0):
            raise ValueError("Confidence score must be between 0.0 and 1.0")
        
        return score
    
    def __repr__(self) -> str:
        """String representation of Message model."""
        content_preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"<Message(id={self.id}, role={self.role}, content='{content_preview}')>"
