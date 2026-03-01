"""
Document Generation Router
Handles API endpoints for document template listing, generation, and retrieval

Requirements: 4.1, 4.2
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from uuid import UUID
from pathlib import Path
import os

from database import get_db
from models.user import User
from models.generated_document import GeneratedDocument
from utils.jwt import get_current_user
from document_generator_service import get_document_generator_service, DocumentType
from templates.template_config import (
    TEMPLATE_REGISTRY,
    get_template_config,
    get_all_fields,
    FieldType
)
from pydantic import BaseModel, Field


router = APIRouter(
    prefix="/api/documents",
    tags=["documents"]
)


# Pydantic models for request/response
class TemplateFieldResponse(BaseModel):
    """Response model for template field information"""
    name: str
    label: str
    field_type: str
    required: bool
    description: str
    placeholder: str


class TemplateResponse(BaseModel):
    """Response model for template information"""
    document_type: str
    name: str
    description: str
    category: str
    fields: List[TemplateFieldResponse]


class GenerateDocumentRequest(BaseModel):
    """Request model for document generation"""
    document_type: str = Field(..., description="Type of document to generate")
    inputs: Dict[str, Any] = Field(..., description="User inputs for the document")


class GeneratedDocumentResponse(BaseModel):
    """Response model for generated document"""
    id: str
    document_type: str
    created_at: str
    file_path: str
    text_content: str
    pdf_available: bool


@router.get("/templates", response_model=List[TemplateResponse])
async def list_templates(
    current_user: User = Depends(get_current_user)
):
    """
    List all available document templates
    
    Requirements: 4.1 - Present form collecting required information
    
    Returns:
        List of available document templates with their field configurations
    """
    templates = []
    
    for doc_type, config in TEMPLATE_REGISTRY.items():
        # Convert fields to response format
        fields = []
        for field in config["fields"]:
            fields.append(TemplateFieldResponse(
                name=field.name,
                label=field.label,
                field_type=field.field_type.value,
                required=field.required,
                description=field.description,
                placeholder=field.placeholder
            ))
        
        templates.append(TemplateResponse(
            document_type=doc_type.value,
            name=config["name"],
            description=config["description"],
            category=config["category"],
            fields=fields
        ))
    
    return templates


@router.post("/generate", response_model=GeneratedDocumentResponse, status_code=status.HTTP_201_CREATED)
async def generate_document(
    request: GenerateDocumentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a legal document from template
    
    Requirements: 4.2 - Generate properly formatted Legal_Document
    
    Args:
        request: Document generation request with type and inputs
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Generated document with text content and file path
        
    Raises:
        HTTPException: If document type is invalid or validation fails
    """
    # Validate document type
    try:
        doc_type = DocumentType(request.document_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid document type: {request.document_type}"
        )
    
    # Get document generator service
    doc_service = get_document_generator_service()
    
    # Generate document
    try:
        text_content, pdf_bytes = doc_service.generate_document(doc_type, request.inputs)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate document: {str(e)}"
        )
    
    # Create directory for storing documents if it doesn't exist
    documents_dir = Path("generated_documents")
    documents_dir.mkdir(exist_ok=True)
    
    # Create user-specific subdirectory
    user_dir = documents_dir / str(current_user.id)
    user_dir.mkdir(exist_ok=True)
    
    # Generate a temporary ID for the filename
    import uuid
    doc_id = uuid.uuid4()
    
    # Create file paths
    pdf_filename = f"{doc_id}_{request.document_type}.pdf"
    pdf_path = user_dir / pdf_filename
    
    text_filename = f"{doc_id}_{request.document_type}.txt"
    text_path = user_dir / text_filename
    
    # Save PDF file
    with open(pdf_path, "wb") as f:
        f.write(pdf_bytes)
    
    # Save text file
    with open(text_path, "w", encoding="utf-8") as f:
        f.write(text_content)
    
    # Save document to database with the file path (store as string relative path)
    generated_doc = GeneratedDocument(
        id=doc_id,
        user_id=current_user.id,
        document_type=request.document_type,
        template_inputs=request.inputs,
        file_path=str(pdf_path)  # Store as string path
    )
    
    db.add(generated_doc)
    db.commit()
    db.refresh(generated_doc)
    
    return GeneratedDocumentResponse(
        id=str(generated_doc.id),
        document_type=generated_doc.document_type,
        created_at=generated_doc.created_at.isoformat(),
        file_path=generated_doc.file_path,
        text_content=text_content,
        pdf_available=True
    )


@router.get("/{document_id}", response_model=GeneratedDocumentResponse)
async def get_document(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve a generated document by ID
    
    Requirements: 4.2 - Retrieve generated documents
    
    Args:
        document_id: UUID of the document to retrieve
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Generated document with text content
        
    Raises:
        HTTPException: If document not found or user doesn't have access
    """
    # Query document from database
    document = db.query(GeneratedDocument).filter(
        GeneratedDocument.id == document_id,
        GeneratedDocument.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Read text content from file
    text_path = Path(document.file_path).with_suffix('.txt')
    
    try:
        with open(text_path, "r", encoding="utf-8") as f:
            text_content = f.read()
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document file not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read document: {str(e)}"
        )
    
    # Check if PDF exists
    pdf_path = Path(document.file_path)
    pdf_available = pdf_path.exists()
    
    return GeneratedDocumentResponse(
        id=str(document.id),
        document_type=document.document_type,
        created_at=document.created_at.isoformat(),
        file_path=document.file_path,
        text_content=text_content,
        pdf_available=pdf_available
    )


@router.get("/", response_model=List[Dict[str, Any]])
async def list_user_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all documents generated by the current user
    
    Args:
        current_user: Authenticated user
        db: Database session
        
    Returns:
        List of generated documents (metadata only, without content)
    """
    documents = db.query(GeneratedDocument).filter(
        GeneratedDocument.user_id == current_user.id
    ).order_by(GeneratedDocument.created_at.desc()).all()
    
    return [
        {
            "id": str(doc.id),
            "document_type": doc.document_type,
            "created_at": doc.created_at.isoformat(),
            "file_path": doc.file_path
        }
        for doc in documents
    ]
