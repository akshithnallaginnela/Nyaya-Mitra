"""
Generated Document model for document generation system.

This module implements the GeneratedDocument model to store information
about legal documents generated from templates, including document type,
template inputs, and file paths.

Requirements: 4.2 (Document generation)
"""

from typing import TYPE_CHECKING, Dict

from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import relationship, validates

from database import BaseModel

if TYPE_CHECKING:
    from models.user import User


class GeneratedDocument(BaseModel):
    """
    Generated Document model for storing generated legal documents.
    
    Inherits from BaseModel which provides:
    - id: UUID primary key
    - created_at: Timestamp of document generation
    - updated_at: Timestamp of last update
    
    Additional fields:
    - user_id: Foreign key to User model
    - document_type: Type of document (legal_letter, rti_application, counter_petition, etc.)
    - template_inputs: JSON object containing user inputs used to generate the document
    - file_path: Path to the generated document file
    
    Relationships:
    - user: Many-to-one relationship with User
    """
    
    __tablename__ = "generated_documents"
    
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    document_type = Column(
        String(50),
        nullable=False,
        index=True
    )
    
    template_inputs = Column(
        JSON,
        nullable=False
    )
    
    file_path = Column(
        String(500),
        nullable=False
    )
    
    # Relationships
    user = relationship(
        "User",
        back_populates="generated_documents"
    )
    
    # Valid document types as per requirement 4.3
    VALID_DOCUMENT_TYPES = {
        'legal_letter',
        'rti_application',
        'counter_petition',
        'complaint_letter',
        'notice_reply',
        'affidavit',
        'application'
    }
    
    @validates('document_type')
    def validate_document_type(self, key: str, doc_type: str) -> str:
        """
        Validate document type.
        
        As per requirement 4.3, the system supports generation of:
        - Legal letters
        - RTI applications
        - Counter-petitions
        - And other legal document types
        
        Args:
            key: Field name (automatically provided by SQLAlchemy)
            doc_type: Document type to validate
            
        Returns:
            str: Validated document type
            
        Raises:
            ValueError: If document type is invalid
        """
        if not doc_type:
            raise ValueError("Document type is required")
        
        doc_type = doc_type.strip().lower()
        
        if doc_type not in self.VALID_DOCUMENT_TYPES:
            raise ValueError(
                f"Invalid document type. Must be one of: {', '.join(sorted(self.VALID_DOCUMENT_TYPES))}"
            )
        
        return doc_type
    
    @validates('template_inputs')
    def validate_template_inputs(self, key: str, inputs: Dict) -> Dict:
        """
        Validate template inputs structure.
        
        Args:
            key: Field name (automatically provided by SQLAlchemy)
            inputs: Template inputs dictionary to validate
            
        Returns:
            Dict: Validated template inputs
            
        Raises:
            ValueError: If template inputs are invalid
        """
        if not inputs:
            raise ValueError("Template inputs cannot be empty")
        
        if not isinstance(inputs, dict):
            raise ValueError("Template inputs must be a dictionary")
        
        return inputs
    
    @validates('file_path')
    def validate_file_path(self, key: str, path: str) -> str:
        """
        Validate file path.
        
        Args:
            key: Field name (automatically provided by SQLAlchemy)
            path: File path to validate
            
        Returns:
            str: Validated file path
            
        Raises:
            ValueError: If file path is invalid
        """
        if not path or not path.strip():
            raise ValueError("File path is required")
        
        path = path.strip()
        
        if len(path) > 500:
            raise ValueError("File path exceeds maximum length of 500 characters")
        
        return path
    
    def __repr__(self) -> str:
        """String representation of GeneratedDocument model."""
        return f"<GeneratedDocument(id={self.id}, user_id={self.user_id}, document_type={self.document_type})>"
