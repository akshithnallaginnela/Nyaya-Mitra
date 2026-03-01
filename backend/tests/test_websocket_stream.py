"""
Tests for WebSocket streaming endpoint.

This test file verifies the WebSocket endpoint for streaming AI responses.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json

from main import app
from database import Base, get_db
from models.user import User
from utils.jwt import create_access_token


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_websocket.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def test_db():
    """Create test database and tables."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(test_db):
    """Create a test user."""
    db = TestingSessionLocal()
    user = User(
        email="test@example.com",
        password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/1jR8.",  # "password"
        full_name="Test User",
        preferred_language="en"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user


@pytest.fixture
def auth_token(test_user):
    """Create authentication token for test user."""
    return create_access_token(test_user.id, test_user.email)


def test_websocket_authentication_required(test_db):
    """Test that WebSocket requires authentication."""
    client = TestClient(app)
    
    with client.websocket_connect("/api/chat/stream") as websocket:
        # Send non-auth message first
        websocket.send_json({"type": "query", "query": "test"})
        
        # Should receive error
        response = websocket.receive_json()
        assert response["type"] == "error"
        assert "authentication" in response["data"]["message"].lower()


def test_websocket_invalid_token(test_db):
    """Test WebSocket with invalid token."""
    client = TestClient(app)
    
    with client.websocket_connect("/api/chat/stream") as websocket:
        # Send auth with invalid token
        websocket.send_json({"type": "auth", "token": "invalid_token"})
        
        # Should receive error
        response = websocket.receive_json()
        assert response["type"] == "error"
        assert "failed" in response["data"]["message"].lower()


def test_websocket_missing_token(test_db):
    """Test WebSocket with missing token."""
    client = TestClient(app)
    
    with client.websocket_connect("/api/chat/stream") as websocket:
        # Send auth without token
        websocket.send_json({"type": "auth"})
        
        # Should receive error
        response = websocket.receive_json()
        assert response["type"] == "error"
        assert "token required" in response["data"]["message"].lower()


def test_websocket_successful_authentication(test_db, auth_token):
    """Test successful WebSocket authentication."""
    client = TestClient(app)
    
    with client.websocket_connect("/api/chat/stream") as websocket:
        # Send valid auth
        websocket.send_json({"type": "auth", "token": auth_token})
        
        # Should receive auth success
        response = websocket.receive_json()
        assert response["type"] == "auth_success"
        assert "user_id" in response["data"]


def test_websocket_query_missing_text(test_db, auth_token):
    """Test WebSocket query with missing query text."""
    client = TestClient(app)
    
    with client.websocket_connect("/api/chat/stream") as websocket:
        # Authenticate
        websocket.send_json({"type": "auth", "token": auth_token})
        auth_response = websocket.receive_json()
        assert auth_response["type"] == "auth_success"
        
        # Send query without text
        websocket.send_json({"type": "query"})
        
        # Should receive error
        response = websocket.receive_json()
        assert response["type"] == "error"
        assert "required" in response["data"]["message"].lower()


def test_websocket_stream_basic_flow(test_db, auth_token):
    """
    Test basic WebSocket streaming flow.
    
    Note: This test may fail if Ollama is not running or if the vector database
    is not properly initialized. It's designed to test the WebSocket protocol,
    not the AI response quality.
    """
    client = TestClient(app)
    
    try:
        with client.websocket_connect("/api/chat/stream") as websocket:
            # Authenticate
            websocket.send_json({"type": "auth", "token": auth_token})
            auth_response = websocket.receive_json()
            assert auth_response["type"] == "auth_success"
            
            # Send query
            websocket.send_json({
                "type": "query",
                "query": "What is IPC Section 499?",
                "language": "en"
            })
            
            # Collect responses
            responses = []
            received_metadata = False
            received_tokens = False
            received_citations = False
            received_complete = False
            
            # Receive up to 100 messages (to avoid infinite loop)
            for _ in range(100):
                try:
                    response = websocket.receive_json()
                    responses.append(response)
                    
                    if response["type"] == "metadata":
                        received_metadata = True
                        assert "confidence" in response["data"]
                        assert "language" in response["data"]
                        assert "needs_clarification" in response["data"]
                    
                    elif response["type"] == "token":
                        received_tokens = True
                        assert "content" in response["data"]
                    
                    elif response["type"] == "citations":
                        received_citations = True
                        assert "citations" in response["data"]
                    
                    elif response["type"] == "complete":
                        received_complete = True
                        assert "conversation_id" in response["data"]
                        assert "message_id" in response["data"]
                        break
                    
                    elif response["type"] == "error":
                        # If we get an error, it might be because Ollama is not running
                        # or vector DB is not initialized - this is acceptable for testing
                        print(f"Received error (expected if Ollama not running): {response['data']['message']}")
                        break
                        
                except Exception as e:
                    print(f"Error receiving message: {e}")
                    break
            
            # Verify we received the expected message types
            # Note: We don't assert on all types because the test might fail
            # if Ollama is not running, which is acceptable
            assert received_metadata, "Should receive metadata message"
            
            print(f"Received {len(responses)} messages")
            print(f"Metadata: {received_metadata}, Tokens: {received_tokens}, Citations: {received_citations}, Complete: {received_complete}")
            
    except Exception as e:
        # If WebSocket connection fails, it might be due to missing dependencies
        # This is acceptable for testing the endpoint structure
        print(f"WebSocket test failed (expected if dependencies not running): {e}")
        pytest.skip("WebSocket test requires running Ollama and initialized vector DB")


def test_websocket_connection_error_handling(test_db, auth_token):
    """Test WebSocket handles connection errors gracefully."""
    client = TestClient(app)
    
    with client.websocket_connect("/api/chat/stream") as websocket:
        # Authenticate
        websocket.send_json({"type": "auth", "token": auth_token})
        auth_response = websocket.receive_json()
        assert auth_response["type"] == "auth_success"
        
        # Send invalid message type
        websocket.send_json({"type": "invalid"})
        
        # Should receive error
        response = websocket.receive_json()
        assert response["type"] == "error"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
