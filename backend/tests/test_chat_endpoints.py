"""
Tests for chat API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import Mock, patch

from main import app
from database import Base, get_db
from models.user import User
from models.conversation import Conversation, Message
from utils.jwt import create_access_token


# Test database setup
TEST_DATABASE_URL = "postgresql://postgres:password@localhost:5432/nyaya_mitra_test"
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(scope="function")
def test_db():
    """Create test database tables."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(test_db):
    """Create a test user."""
    db = TestingSessionLocal()
    user = User(
        email="test@example.com",
        full_name="Test User",
        college_name="Test College"
    )
    user.set_password("testpassword123")
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user


@pytest.fixture
def auth_headers(test_user):
    """Create authentication headers."""
    token = create_access_token({"sub": test_user.email})
    return {"Authorization": f"Bearer {token}"}


class TestChatQueryEndpoint:
    """Test suite for POST /api/chat/query endpoint."""
    
    @patch('routers.chat.get_langchain_orchestrator')
    def test_chat_query_success(self, mock_orchestrator, test_user, auth_headers):
        """Test successful chat query."""
        # Mock orchestrator response
        mock_orch = Mock()
        mock_orch.process_query.return_value = {
            "response": "Defamation is defined under IPC Section 499.",
            "citations": [
                {"type": "IPC", "section": "499", "text": "IPC Section 499"}
            ],
            "confidence": 0.85,
            "needs_clarification": False,
            "language": "en",
            "retrieved_docs": []
        }
        mock_orchestrator.return_value = mock_orch
        
        response = client.post(
            "/api/chat/query",
            json={"query": "What is defamation?", "language": "en"},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "citations" in data
        assert "confidence" in data
        assert data["confidence"] == 0.85
        assert data["needs_clarification"] is False
        assert data["language"] == "en"
        assert "conversation_id" in data
        assert "message_id" in data
    
    @patch('routers.chat.get_langchain_orchestrator')
    def test_chat_query_with_existing_conversation(self, mock_orchestrator, test_user, auth_headers):
        """Test chat query with existing conversation."""
        # Create existing conversation
        db = TestingSessionLocal()
        conversation = Conversation(user_id=test_user.id)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        conversation_id = conversation.id
        db.close()
        
        # Mock orchestrator response
        mock_orch = Mock()
        mock_orch.process_query.return_value = {
            "response": "Yes, you can file a counter-petition.",
            "citations": [],
            "confidence": 0.75,
            "needs_clarification": False,
            "language": "en",
            "retrieved_docs": []
        }
        mock_orchestrator.return_value = mock_orch
        
        response = client.post(
            "/api/chat/query",
            json={
                "query": "Can I file a counter-petition?",
                "conversation_id": conversation_id
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["conversation_id"] == conversation_id
    
    @patch('routers.chat.get_langchain_orchestrator')
    def test_chat_query_needs_clarification(self, mock_orchestrator, test_user, auth_headers):
        """Test chat query that needs clarification."""
        mock_orch = Mock()
        mock_orch.process_query.return_value = {
            "response": "Could you please clarify: 1. What type of case? 2. When did it happen?",
            "citations": [],
            "confidence": 0.4,
            "needs_clarification": True,
            "language": "en",
            "retrieved_docs": []
        }
        mock_orchestrator.return_value = mock_orch
        
        response = client.post(
            "/api/chat/query",
            json={"query": "I need help"},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["needs_clarification"] is True
        assert data["confidence"] < 0.6
    
    @patch('routers.chat.get_langchain_orchestrator')
    def test_chat_query_multilingual(self, mock_orchestrator, test_user, auth_headers):
        """Test chat query in Hindi."""
        mock_orch = Mock()
        mock_orch.process_query.return_value = {
            "response": "मानहानि IPC धारा 499 के तहत परिभाषित है।",
            "citations": [
                {"type": "IPC", "section": "499", "text": "IPC Section 499"}
            ],
            "confidence": 0.8,
            "needs_clarification": False,
            "language": "hi",
            "retrieved_docs": []
        }
        mock_orchestrator.return_value = mock_orch
        
        response = client.post(
            "/api/chat/query",
            json={"query": "मानहानि क्या है?", "language": "hi"},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["language"] == "hi"
    
    def test_chat_query_unauthorized(self):
        """Test chat query without authentication."""
        response = client.post(
            "/api/chat/query",
            json={"query": "What is defamation?"}
        )
        
        assert response.status_code == 401
    
    def test_chat_query_empty_query(self, auth_headers):
        """Test chat query with empty query."""
        response = client.post(
            "/api/chat/query",
            json={"query": ""},
            headers=auth_headers
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_chat_query_too_long(self, auth_headers):
        """Test chat query with query exceeding max length."""
        long_query = "a" * 2001
        response = client.post(
            "/api/chat/query",
            json={"query": long_query},
            headers=auth_headers
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_chat_query_invalid_conversation_id(self, test_user, auth_headers):
        """Test chat query with non-existent conversation ID."""
        response = client.post(
            "/api/chat/query",
            json={"query": "What is defamation?", "conversation_id": 99999},
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    @patch('routers.chat.get_langchain_orchestrator')
    def test_chat_query_saves_messages(self, mock_orchestrator, test_user, auth_headers):
        """Test that chat query saves messages to database."""
        mock_orch = Mock()
        mock_orch.process_query.return_value = {
            "response": "Test response",
            "citations": [],
            "confidence": 0.8,
            "needs_clarification": False,
            "language": "en",
            "retrieved_docs": []
        }
        mock_orchestrator.return_value = mock_orch
        
        response = client.post(
            "/api/chat/query",
            json={"query": "Test query"},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        
        # Verify messages were saved
        db = TestingSessionLocal()
        conversation_id = response.json()["conversation_id"]
        messages = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).all()
        
        assert len(messages) == 2  # User message + assistant message
        assert messages[0].role == "user"
        assert messages[0].content == "Test query"
        assert messages[1].role == "assistant"
        assert messages[1].content == "Test response"
        assert messages[1].confidence_score == 0.8
        
        db.close()
    
    @patch('routers.chat.get_langchain_orchestrator')
    def test_chat_query_with_conversation_context(self, mock_orchestrator, test_user, auth_headers):
        """Test that conversation context is passed to orchestrator."""
        # Create conversation with existing messages
        db = TestingSessionLocal()
        conversation = Conversation(user_id=test_user.id)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        
        msg1 = Message(
            conversation_id=conversation.id,
            role="user",
            content="What is defamation?"
        )
        msg2 = Message(
            conversation_id=conversation.id,
            role="assistant",
            content="Defamation is..."
        )
        db.add(msg1)
        db.add(msg2)
        db.commit()
        conversation_id = conversation.id
        db.close()
        
        mock_orch = Mock()
        mock_orch.process_query.return_value = {
            "response": "Follow-up response",
            "citations": [],
            "confidence": 0.8,
            "needs_clarification": False,
            "language": "en",
            "retrieved_docs": []
        }
        mock_orchestrator.return_value = mock_orch
        
        response = client.post(
            "/api/chat/query",
            json={
                "query": "Can you explain more?",
                "conversation_id": conversation_id
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        
        # Verify context was passed
        mock_orch.process_query.assert_called_once()
        call_kwargs = mock_orch.process_query.call_args[1]
        assert call_kwargs["conversation_context"] is not None
        assert len(call_kwargs["conversation_context"]) == 2



class TestChatHistoryEndpoints:
    """Test suite for chat history endpoints."""
    
    def test_get_conversations_empty(self, test_user, auth_headers):
        """Test getting conversations when user has none."""
        response = client.get(
            "/api/chat/history",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["conversations"]) == 0
        assert data["page"] == 1
    
    def test_get_conversations_with_data(self, test_user, auth_headers):
        """Test getting conversations with existing data."""
        # Create test conversations
        db = TestingSessionLocal()
        conv1 = Conversation(user_id=test_user.id)
        conv2 = Conversation(user_id=test_user.id)
        db.add(conv1)
        db.add(conv2)
        db.commit()
        db.refresh(conv1)
        db.refresh(conv2)
        
        # Add messages
        msg1 = Message(
            conversation_id=conv1.id,
            role="user",
            content="First question"
        )
        msg2 = Message(
            conversation_id=conv1.id,
            role="assistant",
            content="First answer"
        )
        db.add(msg1)
        db.add(msg2)
        db.commit()
        db.close()
        
        response = client.get(
            "/api/chat/history",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["conversations"]) == 2
        assert data["conversations"][0]["message_count"] == 2
    
    def test_get_conversations_pagination(self, test_user, auth_headers):
        """Test conversation pagination."""
        # Create multiple conversations
        db = TestingSessionLocal()
        for i in range(25):
            conv = Conversation(user_id=test_user.id)
            db.add(conv)
        db.commit()
        db.close()
        
        # Get first page
        response = client.get(
            "/api/chat/history?page=1&page_size=10",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 25
        assert len(data["conversations"]) == 10
        assert data["page"] == 1
        assert data["page_size"] == 10
        
        # Get second page
        response = client.get(
            "/api/chat/history?page=2&page_size=10",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["conversations"]) == 10
        assert data["page"] == 2
    
    def test_get_conversations_unauthorized(self):
        """Test getting conversations without authentication."""
        response = client.get("/api/chat/history")
        assert response.status_code == 401 or response.status_code == 403
    
    def test_get_conversation_history_success(self, test_user, auth_headers):
        """Test getting conversation history."""
        # Create conversation with messages
        db = TestingSessionLocal()
        conv = Conversation(user_id=test_user.id)
        db.add(conv)
        db.commit()
        db.refresh(conv)
        
        msg1 = Message(
            conversation_id=conv.id,
            role="user",
            content="What is defamation?"
        )
        msg2 = Message(
            conversation_id=conv.id,
            role="assistant",
            content="Defamation is...",
            confidence_score=0.85
        )
        db.add(msg1)
        db.add(msg2)
        db.commit()
        conversation_id = conv.id
        db.close()
        
        response = client.get(
            f"/api/chat/history/{conversation_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["conversation_id"] == conversation_id
        assert data["total_messages"] == 2
        assert len(data["messages"]) == 2
        assert data["messages"][0]["role"] == "user"
        assert data["messages"][0]["content"] == "What is defamation?"
        assert data["messages"][1]["role"] == "assistant"
        assert data["messages"][1]["confidence_score"] == 0.85
    
    def test_get_conversation_history_with_citations(self, test_user, auth_headers):
        """Test getting conversation history with citations."""
        db = TestingSessionLocal()
        conv = Conversation(user_id=test_user.id)
        db.add(conv)
        db.commit()
        db.refresh(conv)
        
        msg = Message(
            conversation_id=conv.id,
            role="assistant",
            content="Response with citations",
            citations=[
                {"type": "IPC", "section": "499", "text": "IPC Section 499"}
            ],
            confidence_score=0.9
        )
        db.add(msg)
        db.commit()
        conversation_id = conv.id
        db.close()
        
        response = client.get(
            f"/api/chat/history/{conversation_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["messages"]) == 1
        assert data["messages"][0]["citations"] is not None
        assert len(data["messages"][0]["citations"]) == 1
        assert data["messages"][0]["citations"][0]["type"] == "IPC"
    
    def test_get_conversation_history_pagination(self, test_user, auth_headers):
        """Test conversation history pagination."""
        db = TestingSessionLocal()
        conv = Conversation(user_id=test_user.id)
        db.add(conv)
        db.commit()
        db.refresh(conv)
        
        # Add many messages
        for i in range(60):
            msg = Message(
                conversation_id=conv.id,
                role="user" if i % 2 == 0 else "assistant",
                content=f"Message {i}"
            )
            db.add(msg)
        db.commit()
        conversation_id = conv.id
        db.close()
        
        # Get first page
        response = client.get(
            f"/api/chat/history/{conversation_id}?page=1&page_size=20",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_messages"] == 60
        assert len(data["messages"]) == 20
        assert data["has_more"] is True
        
        # Get last page
        response = client.get(
            f"/api/chat/history/{conversation_id}?page=3&page_size=20",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["messages"]) == 20
        assert data["has_more"] is False
    
    def test_get_conversation_history_not_found(self, test_user, auth_headers):
        """Test getting non-existent conversation."""
        response = client.get(
            "/api/chat/history/99999",
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    def test_get_conversation_history_unauthorized_access(self, test_user, auth_headers):
        """Test accessing another user's conversation."""
        # Create conversation for different user
        db = TestingSessionLocal()
        other_user = User(
            email="other@example.com",
            full_name="Other User",
            college_name="Other College"
        )
        other_user.set_password("password123")
        db.add(other_user)
        db.commit()
        db.refresh(other_user)
        
        conv = Conversation(user_id=other_user.id)
        db.add(conv)
        db.commit()
        db.refresh(conv)
        conversation_id = conv.id
        db.close()
        
        # Try to access with test_user's token
        response = client.get(
            f"/api/chat/history/{conversation_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 404  # Should not reveal existence
    
    def test_get_conversation_history_unauthorized(self):
        """Test getting conversation history without authentication."""
        response = client.get("/api/chat/history/1")
        assert response.status_code == 401 or response.status_code == 403
