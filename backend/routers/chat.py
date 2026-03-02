"""
Chat API endpoints for legal query processing.
"""
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

from database import get_db_session as get_db
from models.user import User
from models.conversation import Conversation, Message
from models.action_plan import ActionPlan
from utils.jwt import get_current_user, verify_token
from langchain_service import get_langchain_orchestrator
from rag_system import RAGRetrievalSystem
from vector_db import VectorDatabase
from action_plan_service import get_action_plan_service, ActionPlanRequest


router = APIRouter(prefix="/api/chat", tags=["chat"])


# Helper function to detect action plan commands
def detect_action_plan_command(query: str) -> Optional[str]:
    """
    Detect if the query is requesting an action plan.
    
    Args:
        query: User's query text
        
    Returns:
        Case type if action plan command detected, None otherwise
    """
    query_lower = query.lower()
    
    # Action plan trigger phrases
    action_plan_triggers = [
        "action plan",
        "step by step",
        "what should i do",
        "what steps",
        "guide me",
        "help me with steps",
        "create plan",
        "generate plan"
    ]
    
    # Check if query contains action plan trigger
    has_trigger = any(trigger in query_lower for trigger in action_plan_triggers)
    
    if not has_trigger:
        return None
    
    # Detect case type from query
    case_type_keywords = {
        "false_accusation": ["false accusation", "falsely accused", "fake complaint", "false complaint"],
        "extortion": ["extortion", "blackmail", "threatening for money", "demanding money"],
        "harassment": ["harassment", "harass", "stalking", "unwanted contact"],
        "defamation": ["defamation", "defame", "false statement", "reputation damage", "slander", "libel"]
    }
    
    for case_type, keywords in case_type_keywords.items():
        if any(keyword in query_lower for keyword in keywords):
            return case_type
    
    # Default to general if no specific case type detected
    return "general"


# Request/Response models
class ChatQueryRequest(BaseModel):
    """Request model for chat query."""
    query: str = Field(..., min_length=1, max_length=2000, description="User's legal question")
    language: Optional[str] = Field("en", description="Preferred response language (ISO 639-1 code)")
    conversation_id: Optional[str] = Field(None, description="ID of existing conversation to continue")


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
    conversation_id: str
    message_id: str


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
        # Check if query is requesting an action plan
        case_type = detect_action_plan_command(request.query)
        
        if case_type:
            # Generate action plan
            service = get_action_plan_service()
            service_request = ActionPlanRequest(
                case_type=case_type,
                situation_details=request.query,
                urgency_level="medium"
            )
            
            plan_response = service.generate_action_plan(service_request)
            
            # Store action plan in database
            action_plan = ActionPlan(
                user_id=current_user.id,
                case_type=plan_response.case_type,
                situation_details=request.query,
                total_steps=plan_response.total_steps,
                estimated_total_time=plan_response.estimated_total_time,
                steps=plan_response.steps,
                urgent_deadlines=plan_response.urgent_deadlines,
                professional_help_recommended=plan_response.professional_help_recommended,
                status="active",
                progress={}
            )
            
            db.add(action_plan)
            db.commit()
            db.refresh(action_plan)
            
            # Format action plan as response
            response_text = f"I've created an action plan for your {case_type.replace('_', ' ')} situation.\n\n"
            response_text += f"**Total Steps:** {plan_response.total_steps}\n"
            response_text += f"**Estimated Time:** {plan_response.estimated_total_time}\n\n"
            
            if plan_response.urgent_deadlines:
                response_text += "**⚠️ Urgent Deadlines:**\n"
                for deadline in plan_response.urgent_deadlines:
                    response_text += f"- {deadline}\n"
                response_text += "\n"
            
            response_text += "**Action Steps:**\n\n"
            for step in plan_response.steps:
                response_text += f"**Step {step['step_number']}: {step['title']}**\n"
                response_text += f"{step['description']}\n\n"
                response_text += f"⏰ Timeline: {step['timeline']}\n"
                response_text += f"⏱️ Time Estimate: {step['time_estimate']}\n"
                response_text += f"🔥 Urgency: {step['urgency']}/10\n"
                
                if step['is_legal_deadline']:
                    response_text += "⚖️ **Legal Deadline**\n"
                
                if step['requires_professional']:
                    response_text += "👨‍⚖️ Professional help recommended\n"
                
                if step.get('alternatives'):
                    response_text += "\n**Alternatives:**\n"
                    for alt in step['alternatives']:
                        response_text += f"- {alt}\n"
                
                response_text += "\n---\n\n"
            
            if plan_response.professional_help_recommended:
                response_text += "\n⚠️ **Professional legal help is strongly recommended for this situation.**\n"
            
            response_text += f"\nYou can view and track this action plan at any time using the action plan ID: {action_plan.id}"
            
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
            
            # Save user message
            user_message = Message(
                conversation_id=conversation.id,
                role="user",
                content=request.query
            )
            db.add(user_message)
            db.commit()
            
            # Save assistant message with action plan
            assistant_message = Message(
                conversation_id=conversation.id,
                role="assistant",
                content=response_text,
                citations=[],
                confidence_score=1.0
            )
            db.add(assistant_message)
            db.commit()
            db.refresh(assistant_message)
            
            return ChatQueryResponse(
                response=response_text,
                citations=[],
                confidence=1.0,
                needs_clarification=False,
                language=request.language or "en",
                conversation_id=str(conversation.id),
                message_id=str(assistant_message.id)
            )
        
        # Regular chat query processing (existing code)
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
            conversation_id=str(conversation.id),
            message_id=str(assistant_message.id)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # Log error and return user-friendly message
        import traceback
        print(f"Error processing chat query: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your query. Please try again."
        )



class ConversationSummary(BaseModel):
    """Conversation summary model."""
    id: str
    created_at: datetime
    updated_at: datetime
    message_count: int
    last_message: Optional[str] = None


class MessageResponse(BaseModel):
    """Message response model."""
    id: str
    role: str
    content: str
    citations: Optional[List[Citation]] = None
    confidence_score: Optional[float] = None
    created_at: datetime


class ConversationHistoryResponse(BaseModel):
    """Conversation history response model."""
    conversation_id: str
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
    conversation_id: str,
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


@router.websocket("/stream")
async def websocket_chat_stream(websocket: WebSocket):
    """
    WebSocket endpoint for streaming AI responses in real-time.
    
    Protocol:
    1. Client connects and sends authentication message:
       {"type": "auth", "token": "JWT_TOKEN"}
    
    2. Client sends query message:
       {
           "type": "query",
           "query": "legal question",
           "language": "en",
           "conversation_id": 123  // optional
       }
    
    3. Server streams response chunks:
       {"type": "metadata", "data": {"confidence": 0.8, "language": "en", "needs_clarification": false}}
       {"type": "token", "data": {"content": "text chunk"}}
       {"type": "citations", "data": {"citations": [...]}}
       {"type": "complete", "data": {"conversation_id": 123, "message_id": 456}}
    
    4. Server sends error if something goes wrong:
       {"type": "error", "data": {"message": "error description"}}
    
    Connection handling:
    - Automatic reconnection supported
    - Connection errors handled gracefully
    - Client should implement exponential backoff for reconnection
    """
    await websocket.accept()
    
    user = None
    db = None
    
    try:
        # Wait for authentication message
        auth_message = await websocket.receive_json()
        
        if auth_message.get("type") != "auth":
            await websocket.send_json({
                "type": "error",
                "data": {"message": "First message must be authentication"}
            })
            await websocket.close(code=1008)  # Policy violation
            return
        
        # Verify JWT token
        token = auth_message.get("token")
        if not token:
            await websocket.send_json({
                "type": "error",
                "data": {"message": "Authentication token required"}
            })
            await websocket.close(code=1008)
            return
        
        try:
            # Verify token and get user
            token_data = verify_token(token)
            user_id = token_data.user_id
            
            # Get database session
            db_gen = get_db()
            db = next(db_gen)
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user:
                await websocket.send_json({
                    "type": "error",
                    "data": {"message": "User not found"}
                })
                await websocket.close(code=1008)
                return
            
            # Send authentication success
            await websocket.send_json({
                "type": "auth_success",
                "data": {"user_id": str(user.id)}
            })
            
        except Exception as e:
            await websocket.send_json({
                "type": "error",
                "data": {"message": f"Authentication failed: {str(e)}"}
            })
            await websocket.close(code=1008)
            return
        
        # Main message loop
        while True:
            try:
                # Receive query message
                message = await websocket.receive_json()
                
                if message.get("type") != "query":
                    await websocket.send_json({
                        "type": "error",
                        "data": {"message": "Expected query message"}
                    })
                    continue
                
                query = message.get("query")
                language = message.get("language", "en")
                conversation_id = message.get("conversation_id")
                
                if not query:
                    await websocket.send_json({
                        "type": "error",
                        "data": {"message": "Query text required"}
                    })
                    continue
                
                # Get or create conversation
                if conversation_id:
                    conversation = db.query(Conversation).filter(
                        Conversation.id == conversation_id,
                        Conversation.user_id == user.id
                    ).first()
                    
                    if not conversation:
                        await websocket.send_json({
                            "type": "error",
                            "data": {"message": "Conversation not found"}
                        })
                        continue
                else:
                    # Create new conversation
                    conversation = Conversation(user_id=user.id)
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
                    content=query
                )
                db.add(user_message)
                db.commit()
                
                # Stream response
                orchestrator = get_langchain_orchestrator()
                full_response = ""
                citations = []
                confidence = 0.0
                needs_clarification = False
                response_language = language
                
                try:
                    for chunk in orchestrator.process_query_stream(
                        query=query,
                        language=language,
                        conversation_context=conversation_context if conversation_context else None
                    ):
                        # Send chunk to client
                        await websocket.send_json(chunk)
                        
                        # Accumulate response data
                        if chunk["type"] == "metadata":
                            confidence = chunk["data"]["confidence"]
                            response_language = chunk["data"]["language"]
                            needs_clarification = chunk["data"]["needs_clarification"]
                        elif chunk["type"] == "token":
                            full_response += chunk["data"]["content"]
                        elif chunk["type"] == "citations":
                            citations = chunk["data"]["citations"]
                        elif chunk["type"] == "error":
                            # Error already sent to client
                            raise Exception(chunk["data"]["message"])
                    
                    # Save assistant message
                    assistant_message = Message(
                        conversation_id=conversation.id,
                        role="assistant",
                        content=full_response,
                        citations=citations,
                        confidence_score=confidence
                    )
                    db.add(assistant_message)
                    db.commit()
                    db.refresh(assistant_message)
                    
                    # Send completion message
                    await websocket.send_json({
                        "type": "complete",
                        "data": {
                            "conversation_id": conversation.id,
                            "message_id": assistant_message.id,
                            "confidence": confidence,
                            "needs_clarification": needs_clarification
                        }
                    })
                    
                except Exception as e:
                    await websocket.send_json({
                        "type": "error",
                        "data": {"message": f"Error processing query: {str(e)}"}
                    })
                    
            except WebSocketDisconnect:
                print(f"WebSocket disconnected for user {user.id if user else 'unknown'}")
                break
            except Exception as e:
                print(f"Error in WebSocket message loop: {str(e)}")
                await websocket.send_json({
                    "type": "error",
                    "data": {"message": f"Internal error: {str(e)}"}
                })
                
    except WebSocketDisconnect:
        print("WebSocket disconnected during authentication")
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
        try:
            await websocket.send_json({
                "type": "error",
                "data": {"message": f"Connection error: {str(e)}"}
            })
        except:
            pass
    finally:
        # Clean up database session
        if db:
            db.close()
        
        # Close WebSocket if still open
        try:
            await websocket.close()
        except:
            pass

