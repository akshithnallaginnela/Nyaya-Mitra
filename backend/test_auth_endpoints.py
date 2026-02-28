"""
Unit tests for authentication endpoints.

Tests cover:
- User registration with email validation
- User login with credential verification
- Token refresh functionality
- Account deletion with cascade

Requirements: 9.1, 9.2, 9.5
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base, get_db_session
from main import app
from models.user import User
from models.conversation import Conversation
from models.case_analysis import CaseAnalysis
from models.generated_document import GeneratedDocument


# Test database setup
TEST_DATABASE_URL = "sqlite:///./test_auth.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Override dependency
app.dependency_overrides[get_db_session] = override_get_db

# Create test client
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Create and drop database tables for each test."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "password": "SecurePass123!",
        "full_name": "Test User",
        "college_name": "Test College",
        "preferred_language": "en"
    }


class TestRegistration:
    """Test user registration endpoint."""
    
    def test_register_success(self, sample_user_data):
        """Test successful user registration."""
        response = client.post("/api/auth/register", json=sample_user_data)
        
        assert response.status_code == 201
        data = response.json()
        
        # Verify response structure
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        
        # Verify user data
        user = data["user"]
        assert user["email"] == sample_user_data["email"]
        assert user["full_name"] == sample_user_data["full_name"]
        assert user["college_name"] == sample_user_data["college_name"]
        assert user["preferred_language"] == sample_user_data["preferred_language"]
        assert "id" in user
    
    def test_register_duplicate_email(self, sample_user_data):
        """Test registration with duplicate email."""
        # Register first user
        client.post("/api/auth/register", json=sample_user_data)
        
        # Try to register again with same email
        response = client.post("/api/auth/register", json=sample_user_data)
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
    
    def test_register_invalid_email(self, sample_user_data):
        """Test registration with invalid email format."""
        sample_user_data["email"] = "invalid-email"
        response = client.post("/api/auth/register", json=sample_user_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_register_weak_password(self, sample_user_data):
        """Test registration with weak password."""
        weak_passwords = [
            "short",  # Too short
            "nouppercase123!",  # No uppercase
            "NOLOWERCASE123!",  # No lowercase
            "NoDigits!",  # No digits
            "NoSpecial123",  # No special characters
        ]
        
        for weak_password in weak_passwords:
            sample_user_data["password"] = weak_password
            response = client.post("/api/auth/register", json=sample_user_data)
            
            # Pydantic validation returns 422, our custom validation returns 400
            assert response.status_code in [400, 422]
            
            # Check if password is mentioned in error (detail can be string or list)
            detail = response.json()["detail"]
            if isinstance(detail, str):
                assert "password" in detail.lower()
            else:
                # Pydantic returns list of errors
                assert any("password" in str(err).lower() for err in detail)
    
    def test_register_missing_required_fields(self):
        """Test registration with missing required fields."""
        # Missing email
        response = client.post("/api/auth/register", json={
            "password": "SecurePass123!",
            "full_name": "Test User"
        })
        assert response.status_code == 422
        
        # Missing password
        response = client.post("/api/auth/register", json={
            "email": "test@example.com",
            "full_name": "Test User"
        })
        assert response.status_code == 422
        
        # Missing full_name
        response = client.post("/api/auth/register", json={
            "email": "test@example.com",
            "password": "SecurePass123!"
        })
        assert response.status_code == 422
    
    def test_register_optional_fields(self):
        """Test registration without optional fields."""
        response = client.post("/api/auth/register", json={
            "email": "test@example.com",
            "password": "SecurePass123!",
            "full_name": "Test User"
        })
        
        assert response.status_code == 201
        data = response.json()
        assert data["user"]["college_name"] is None
        assert data["user"]["preferred_language"] == "en"  # Default value
    
    def test_register_invalid_language(self, sample_user_data):
        """Test registration with unsupported language."""
        sample_user_data["preferred_language"] = "invalid"
        response = client.post("/api/auth/register", json=sample_user_data)
        
        assert response.status_code == 400
        assert "language" in response.json()["detail"].lower()


class TestLogin:
    """Test user login endpoint."""
    
    def test_login_success(self, sample_user_data):
        """Test successful login."""
        # Register user first
        client.post("/api/auth/register", json=sample_user_data)
        
        # Login
        response = client.post("/api/auth/login", json={
            "email": sample_user_data["email"],
            "password": sample_user_data["password"]
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        
        # Verify user data
        user = data["user"]
        assert user["email"] == sample_user_data["email"]
        assert user["full_name"] == sample_user_data["full_name"]
    
    def test_login_invalid_email(self):
        """Test login with non-existent email."""
        response = client.post("/api/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "SecurePass123!"
        })
        
        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()
    
    def test_login_invalid_password(self, sample_user_data):
        """Test login with incorrect password."""
        # Register user first
        client.post("/api/auth/register", json=sample_user_data)
        
        # Try to login with wrong password
        response = client.post("/api/auth/login", json={
            "email": sample_user_data["email"],
            "password": "WrongPassword123!"
        })
        
        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()
    
    def test_login_case_insensitive_email(self, sample_user_data):
        """Test login with different email case."""
        # Register user
        client.post("/api/auth/register", json=sample_user_data)
        
        # Login with uppercase email
        response = client.post("/api/auth/login", json={
            "email": sample_user_data["email"].upper(),
            "password": sample_user_data["password"]
        })
        
        assert response.status_code == 200
    
    def test_login_inactive_account(self, sample_user_data):
        """Test login with inactive account."""
        # Register user
        client.post("/api/auth/register", json=sample_user_data)
        
        # Deactivate user account
        db = next(override_get_db())
        user = db.query(User).filter(User.email == sample_user_data["email"]).first()
        user.is_active = False
        db.commit()
        db.close()
        
        # Try to login
        response = client.post("/api/auth/login", json={
            "email": sample_user_data["email"],
            "password": sample_user_data["password"]
        })
        
        assert response.status_code == 403
        assert "inactive" in response.json()["detail"].lower()


class TestTokenRefresh:
    """Test token refresh endpoint."""
    
    def test_refresh_success(self, sample_user_data):
        """Test successful token refresh."""
        import time
        
        # Register and get token
        register_response = client.post("/api/auth/register", json=sample_user_data)
        old_token = register_response.json()["access_token"]
        
        # Wait a moment to ensure different iat timestamp
        time.sleep(1)
        
        # Refresh token
        response = client.post("/api/auth/refresh", json={
            "token": old_token
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        
        # Verify new token is different (due to different iat)
        new_token = data["access_token"]
        assert new_token != old_token
    
    def test_refresh_invalid_token(self):
        """Test refresh with invalid token."""
        response = client.post("/api/auth/refresh", json={
            "token": "invalid.token.here"
        })
        
        assert response.status_code == 401
    
    def test_refresh_malformed_token(self):
        """Test refresh with malformed token."""
        response = client.post("/api/auth/refresh", json={
            "token": "not-a-jwt-token"
        })
        
        assert response.status_code == 401


class TestAccountDeletion:
    """Test account deletion endpoint."""
    
    def test_delete_account_success(self, sample_user_data):
        """Test successful account deletion."""
        # Register user
        register_response = client.post("/api/auth/register", json=sample_user_data)
        token = register_response.json()["access_token"]
        
        # Delete account
        response = client.delete(
            "/api/auth/account",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"].lower()
        
        # Verify user is deleted
        db = next(override_get_db())
        user = db.query(User).filter(User.email == sample_user_data["email"]).first()
        assert user is None
        db.close()
    
    def test_delete_account_without_auth(self):
        """Test account deletion without authentication."""
        response = client.delete("/api/auth/account")
        
        assert response.status_code == 403  # No authorization header
    
    def test_delete_account_invalid_token(self):
        """Test account deletion with invalid token."""
        response = client.delete(
            "/api/auth/account",
            headers={"Authorization": "Bearer invalid.token.here"}
        )
        
        assert response.status_code == 401
    
    def test_delete_account_cascade_deletion(self, sample_user_data):
        """Test that account deletion cascades to related data."""
        # Register user
        register_response = client.post("/api/auth/register", json=sample_user_data)
        token = register_response.json()["access_token"]
        user_id = register_response.json()["user"]["id"]
        
        # Create related data
        db = next(override_get_db())
        from uuid import UUID
        user = db.query(User).filter(User.id == UUID(user_id)).first()
        
        # Create conversation
        conversation = Conversation(user_id=user.id, title="Test Conversation")
        db.add(conversation)
        
        # Create case analysis with complete score breakdown
        case_analysis = CaseAnalysis(
            user_id=user.id,
            complaint_details={"test": "data"},
            validity_score=50,
            score_breakdown={
                "evidence": 20,
                "legal_basis": 15,
                "procedural": 10,
                "timeline": 5
            }
        )
        db.add(case_analysis)
        
        # Create generated document
        document = GeneratedDocument(
            user_id=user.id,
            document_type="legal_letter",
            template_inputs={"test": "data"},
            file_path="/path/to/file.pdf"
        )
        db.add(document)
        
        db.commit()
        
        # Verify data exists
        assert db.query(Conversation).filter(Conversation.user_id == user.id).count() == 1
        assert db.query(CaseAnalysis).filter(CaseAnalysis.user_id == user.id).count() == 1
        assert db.query(GeneratedDocument).filter(GeneratedDocument.user_id == user.id).count() == 1
        
        db.close()
        
        # Delete account
        response = client.delete(
            "/api/auth/account",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        
        # Verify all related data is deleted
        db = next(override_get_db())
        assert db.query(User).filter(User.id == UUID(user_id)).first() is None
        assert db.query(Conversation).filter(Conversation.user_id == UUID(user_id)).count() == 0
        assert db.query(CaseAnalysis).filter(CaseAnalysis.user_id == UUID(user_id)).count() == 0
        assert db.query(GeneratedDocument).filter(GeneratedDocument.user_id == UUID(user_id)).count() == 0
        db.close()


class TestJWTTokenExpiration:
    """Test JWT token expiration requirements."""
    
    def test_token_has_24_hour_expiration(self, sample_user_data):
        """Test that JWT tokens have 24-hour expiration (Requirement 9.2)."""
        from datetime import datetime, timedelta
        from utils.jwt import decode_token_without_verification
        
        # Register user and get token
        response = client.post("/api/auth/register", json=sample_user_data)
        token = response.json()["access_token"]
        
        # Decode token without verification to check expiration
        token_data = decode_token_without_verification(token)
        
        assert token_data is not None
        assert token_data.exp is not None
        assert token_data.iat is not None
        
        # Token data already contains datetime objects
        exp_time = token_data.exp if isinstance(token_data.exp, datetime) else datetime.fromtimestamp(token_data.exp)
        iat_time = token_data.iat if isinstance(token_data.iat, datetime) else datetime.fromtimestamp(token_data.iat)
        
        # Calculate expiration duration
        duration = exp_time - iat_time
        
        # Verify expiration is 24 hours (with small tolerance for processing time)
        expected_duration = timedelta(hours=24)
        tolerance = timedelta(seconds=5)
        
        assert abs(duration - expected_duration) < tolerance


class TestPasswordSecurity:
    """Test password security requirements."""
    
    def test_password_hashed_with_bcrypt(self, sample_user_data):
        """Test that passwords are hashed with bcrypt (Requirement 9.1)."""
        # Register user
        client.post("/api/auth/register", json=sample_user_data)
        
        # Get user from database
        db = next(override_get_db())
        user = db.query(User).filter(User.email == sample_user_data["email"]).first()
        
        # Verify password is hashed (bcrypt hashes start with $2b$)
        assert user.password_hash.startswith("$2b$")
        
        # Verify password is not stored in plain text
        assert user.password_hash != sample_user_data["password"]
        
        # Verify bcrypt rounds (should be at least 10, we use 12)
        # Bcrypt hash format: $2b$rounds$salt$hash
        rounds = int(user.password_hash.split("$")[2])
        assert rounds >= 10
        assert rounds == 12  # Our implementation uses 12 rounds
        
        db.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
