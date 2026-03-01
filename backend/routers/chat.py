"""
Chat API endpoints for legal query processing.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

from database import get_db
from models.user import User
from models.conversation import Conversation, Message
from utils.jwt import get_current_user
from langchain_service import get_langchain_orchestrator
from rag_system import RAGRetrievalSystem
from vector_db import VectorDatabase


router = APIRouter(prefix="/api/chat", tags=["chat"])


# Request/Response models
class ChatQueryRequest(BaseModel):
    """Request model for chat query."""
    query: str = Field(..., min_length=1, max_length=2000, description="User's legal question")
    language: Optional[str] = Field("en", description="Preferred response language (ISO 639-1 code)")
    conversation_id: Optional[int] = Field(None, description="ID of existing conversation to continue")


class Citation(BaseModel):
    """Citation model."""
    type: str
    text: str
    source: Optional[str] = None
    section: Optional[str] = None
    case_name: Optional[str] = None


class ChatQueryResponse(BaseModel):
    """Response model for chat query."""
    response: str
    citations: List[Citation]
    confidence: float
    needs_clarification: bool
    language: str
    conversation_id: int
    message_id: int


@router.post("/query", response_model=ChatQueryResponse)
async def chat_query(
    request: ChatQueryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Process a legal query and return AI-generated response.
    
    This endpoint:
    1. Retrieves relevant legal documents using RAG
    2. Generates AI response using Ollama + Mistral 7B
    3. Extracts citations from response
    4. Saves conversation to database
    5. Returns response with citations and confidence score
    
    Args:
        request: Chat query request with query text and optional language
        current_user: Authenticated user
        db: Database session
        
    Returns:
        ChatQueryResponse with AI response, citations, and metadata
        
    Raises:
        HTTPException: If query processing fails
    """
    try:
        # Get or create conversation
        if request.conversation_id:
            conversation = db.query(Conversation).filter(
                Conversation.id == request.conversation_id,
                Conversation.user_id == current_user.id
            ).first()
            
            if not conversation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found"
                )
        else:
            # Create new conversation
            conversation = Conversation(user_id=current_user.id)
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
        
        # Get conversation context (last 5 messages)
        previous_messages = db.query(Message).filter(
            Message.conversation_id == conversation.id
        ).order_by(Message.created_at.desc()).limit(5).all()
        
        # Format context for LangChain
        conversation_context = []
        for msg in reversed(previous_messages):
            conversation_context.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Save user message
        user_message = Message(
            conversation_id=conversation.id,
            role="user",
            content=request.query
        )
        db.add(user_message)
        db.commit()
        
        # Process query using LangChain orchestrator
        orchestrator = get_langchain_orchestrator()
        result = orchestrator.process_query(
            query=request.query,
            language=request.language or "en",
            conversation_context=conversation_context if conversation_context else None
        )
        
        # Save assistant message
        assistant_message = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=result["response"],
            citations=result["citations"],
            confidence_score=result["confidence"]
        )
        db.add(assistant_message)
        db.commit()
        db.refresh(assistant_message)
        
        # Format citations for response
        formatted_citations = [
            Citation(**citation) for citation in result["citations"]
        ]
        
        return ChatQueryResponse(
            response=result["response"],
            citations=formatted_citations,
            confidence=result["confidence"],
            needs_clarification=result["needs_clarification"],
            language=result["language"],
            conversation_id=conversation.id,
            message_id=assistant_message.id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # Log error and return user-friendly message
        print(f"Error processing chat query: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your query. Please try again."
        )



class ConversationSummary(BaseModel):
    """Conversation summary model."""
    id: int
    created_at: datetime
    updated_at: datetime
    message_count: int
    last_message: Optional[str] = None


class MessageResponse(BaseModel):
    """Message response model."""
    id: int
    role: str
    content: str
    citations: Optional[List[Citation]] = None
    confidence_score: Optional[float] = None
    created_at: datetime


class ConversationHistoryResponse(BaseModel):
    """Conversation history response model."""
    conversation_id: int
    messages: List[MessageResponse]
    total_messages: int
    page: int
    page_size: int
    has_more: bool


class ConversationListResponse(BaseModel):
    """Conversation list response model."""
    conversations: List[ConversationSummary]
    total: int
    page: int
    page_size: int


@router.get("/history", response_model=ConversationListResponse)
async def get_conversations(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get list of user's conversations.
    
    Args:
        page: Page number (default: 1)
        page_size: Number of conversations per page (default: 20)
        current_user: Authenticated user
        db: Database session
        
    Returns:
        ConversationListResponse with paginated conversations
    """
    try:
        # Calculate offset
        offset = (page - 1) * page_size
        
        # Get total count
        total = db.query(Conversation).filter(
            Conversation.user_id == current_user.id
        ).count()
        
        # Get conversations with pagination
        conversations = db.query(Conversation).filter(
            Conversation.user_id == current_user.id
        ).order_by(Conversation.updated_at.desc()).offset(offset).limit(page_size).all()
        
        # Build conversation summaries
        summaries = []
        for conv in conversations:
            # Get message count
            message_count = db.query(Message).filter(
                Message.conversation_id == conv.id
            ).count()
            
            # Get last message
            last_message = db.query(Message).filter(
                Message.conversation_id == conv.id
            ).order_by(Message.created_at.desc()).first()
            
            summaries.append(ConversationSummary(
                id=conv.id,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
                message_count=message_count,
                last_message=last_message.content[:100] + "..." if last_message and len(last_message.content) > 100 else last_message.content if last_message else None
            ))
        
        return ConversationListResponse(
            conversations=summaries,
            total=total,
            page=page,
            page_size=page_size
        )
        
    except Exception as e:
        print(f"Error retrieving conversations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving conversations."
        )


@router.get("/history/{conversation_id}", response_model=ConversationHistoryResponse)
async def get_conversation_history(
    conversation_id: int,
    page: int = 1,
    page_size: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get conversation history with messages.
    
    Args:
        conversation_id: ID of the conversation
        page: Page number (default: 1)
        page_size: Number of messages per page (default: 50)
        current_user: Authenticated user
        db: Database session
        
    Returns:
        ConversationHistoryResponse with paginated messages
        
    Raises:
        HTTPException: If conversation not found or unauthorized
    """
    try:
        # Verify conversation belongs to user
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Calculate offset
        offset = (page - 1) * page_size
        
        # Get total message count
        total_messages = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).count()
        
        # Get messages with pagination
        messages = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.asc()).offset(offset).limit(page_size).all()
        
        # Format messages
        formatted_messages = []
        for msg in messages:
            citations = None
            if msg.citations:
                citations = [Citation(**c) for c in msg.citations]
            
            formatted_messages.append(MessageResponse(
                id=msg.id,
                role=msg.role,
                content=msg.content,
                citations=citations,
                confidence_score=msg.confidence_score,
                created_at=msg.created_at
            ))
        
        # Check if there are more messages
        has_more = (offset + page_size) < total_messages
        
        return ConversationHistoryResponse(
            conversation_id=conversation_id,
            messages=formatted_messages,
            total_messages=total_messages,
            page=page,
            page_size=page_size,
            has_more=has_more
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error retrieving conversation history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving conversation history."
        )
