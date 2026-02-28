"""
Unit tests for JWT token generation and validation utilities.

Tests cover:
- Token creation with 24-hour expiration
- Token validation and verification
- Token refresh functionality
- Error handling for invalid/expired tokens
- get_current_user dependency
"""

import os
import time
from datetime import datetime, timedelta
from uuid import uuid4

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from jose import jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base
from models.user import User
from utils.jwt import (
    JWT_ALGORITHM,
    JWT_SECRET,
    create_access_token,
    decode_token_without_verification,
    get_current_user,
    refresh_access_token,
    verify_token,
)


# Test database setup
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(db):
    """Create a test user."""
    user = User(
        email="test@example.com",
        full_name="Test User",
        preferred_language="en",
        is_active=True
    )
    user.set_password("TestPass123!")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


class TestCreateAccessToken:
    """Tests for create_access_token function."""
    
    def test_creates_valid_token(self):
        """Test that create_access_token generates a valid JWT token."""
        user_id = uuid4()
        email = "test@example.com"
        
        token = create_access_token(user_id, email)
        
        # Verify token is a string
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Decode token to verify structure
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        assert payload["user_id"] == str(user_id)
        assert payload["email"] == email
        assert "exp" in payload
        assert "iat" in payload
    
    def test_token_has_24_hour_expiration(self):
        """Test that token expires in exactly 24 hours (Requirement 9.2)."""
        user_id = uuid4()
        email = "test@example.com"
        
        before_creation = datetime.utcnow()
        token = create_access_token(user_id, email)
        after_creation = datetime.utcnow()
        
        # Decode token
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        
        # Get expiration time (JWT uses UTC timestamps as integers, losing microseconds)
        exp_timestamp = payload["exp"]
        exp_datetime = datetime.utcfromtimestamp(exp_timestamp)
        
        # Calculate expected expiration (24 hours from now)
        # Add 1 second buffer to account for integer timestamp precision loss
        expected_exp_min = before_creation + timedelta(hours=24) - timedelta(seconds=1)
        expected_exp_max = after_creation + timedelta(hours=24) + timedelta(seconds=1)
        
        # Verify expiration is within expected range
        assert expected_exp_min <= exp_datetime <= expected_exp_max
        
        # Verify it's approximately 24 hours
        time_diff = exp_datetime - before_creation
        assert 23.99 <= time_diff.total_seconds() / 3600 <= 24.01
    
    def test_custom_expiration_delta(self):
        """Test creating token with custom expiration time."""
        user_id = uuid4()
        email = "test@example.com"
        custom_delta = timedelta(hours=1)
        
        before_creation = datetime.utcnow()
        token = create_access_token(user_id, email, expires_delta=custom_delta)
        
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        exp_datetime = datetime.utcfromtimestamp(payload["exp"])
        
        # Verify expiration is approximately 1 hour
        time_diff = exp_datetime - before_creation
        assert 0.99 <= time_diff.total_seconds() / 3600 <= 1.01
    
    def test_token_includes_issued_at(self):
        """Test that token includes issued at timestamp."""
        user_id = uuid4()
        email = "test@example.com"
        
        before_creation = datetime.utcnow()
        token = create_access_token(user_id, email)
        after_creation = datetime.utcnow()
        
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        iat_datetime = datetime.utcfromtimestamp(payload["iat"])
        
        # Verify issued at is within creation time range (with 1 second buffer for integer precision)
        assert before_creation - timedelta(seconds=1) <= iat_datetime <= after_creation + timedelta(seconds=1)


class TestVerifyToken:
    """Tests for verify_token function."""
    
    def test_verifies_valid_token(self):
        """Test that verify_token successfully validates a valid token."""
        user_id = uuid4()
        email = "test@example.com"
        
        token = create_access_token(user_id, email)
        token_data = verify_token(token)
        
        assert token_data.user_id == str(user_id)
        assert token_data.email == email
        assert token_data.exp is not None
        assert token_data.iat is not None
    
    def test_rejects_expired_token(self):
        """Test that verify_token rejects expired tokens."""
        user_id = uuid4()
        email = "test@example.com"
        
        # Create token that expires immediately
        token = create_access_token(user_id, email, expires_delta=timedelta(seconds=-1))
        
        # Verify token is rejected
        with pytest.raises(HTTPException) as exc_info:
            verify_token(token)
        
        assert exc_info.value.status_code == 401
        assert "expired" in exc_info.value.detail.lower()
    
    def test_rejects_invalid_signature(self):
        """Test that verify_token rejects tokens with invalid signatures."""
        user_id = uuid4()
        email = "test@example.com"
        
        # Create token with wrong secret
        payload = {
            "user_id": str(user_id),
            "email": email,
            "exp": datetime.utcnow() + timedelta(hours=24),
            "iat": datetime.utcnow()
        }
        invalid_token = jwt.encode(payload, "wrong-secret", algorithm=JWT_ALGORITHM)
        
        # Verify token is rejected
        with pytest.raises(HTTPException) as exc_info:
            verify_token(invalid_token)
        
        assert exc_info.value.status_code == 401
    
    def test_rejects_malformed_token(self):
        """Test that verify_token rejects malformed tokens."""
        with pytest.raises(HTTPException) as exc_info:
            verify_token("not-a-valid-token")
        
        assert exc_info.value.status_code == 401
    
    def test_rejects_token_missing_user_id(self):
        """Test that verify_token rejects tokens without user_id."""
        payload = {
            "email": "test@example.com",
            "exp": datetime.utcnow() + timedelta(hours=24),
            "iat": datetime.utcnow()
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        
        with pytest.raises(HTTPException) as exc_info:
            verify_token(token)
        
        assert exc_info.value.status_code == 401
    
    def test_rejects_token_missing_email(self):
        """Test that verify_token rejects tokens without email."""
        payload = {
            "user_id": str(uuid4()),
            "exp": datetime.utcnow() + timedelta(hours=24),
            "iat": datetime.utcnow()
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        
        with pytest.raises(HTTPException) as exc_info:
            verify_token(token)
        
        assert exc_info.value.status_code == 401


class TestGetCurrentUser:
    """Tests for get_current_user dependency."""
    
    @pytest.mark.asyncio
    async def test_returns_user_for_valid_token(self, db, test_user):
        """Test that get_current_user returns user for valid token."""
        token = create_access_token(test_user.id, test_user.email)
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        
        user = await get_current_user(credentials, db)
        
        assert user.id == test_user.id
        assert user.email == test_user.email
        assert user.full_name == test_user.full_name
    
    @pytest.mark.asyncio
    async def test_rejects_invalid_token(self, db):
        """Test that get_current_user rejects invalid tokens."""
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="invalid-token"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials, db)
        
        assert exc_info.value.status_code == 401
    
    @pytest.mark.asyncio
    async def test_rejects_token_for_nonexistent_user(self, db):
        """Test that get_current_user rejects tokens for users that don't exist."""
        # Create token for non-existent user
        fake_user_id = uuid4()
        token = create_access_token(fake_user_id, "fake@example.com")
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials, db)
        
        assert exc_info.value.status_code == 401
        assert "not found" in exc_info.value.detail.lower()
    
    @pytest.mark.asyncio
    async def test_rejects_inactive_user(self, db, test_user):
        """Test that get_current_user rejects tokens for inactive users."""
        # Deactivate user
        test_user.is_active = False
        db.commit()
        
        token = create_access_token(test_user.id, test_user.email)
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials, db)
        
        assert exc_info.value.status_code == 403
        assert "inactive" in exc_info.value.detail.lower()


class TestRefreshAccessToken:
    """Tests for refresh_access_token function."""
    
    def test_refreshes_valid_token(self):
        """Test that refresh_access_token creates a new token."""
        user_id = uuid4()
        email = "test@example.com"
        
        # Create original token
        original_token = create_access_token(user_id, email)
        original_payload = jwt.decode(original_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        
        # Wait a moment to ensure different timestamps
        time.sleep(0.1)
        
        # Refresh token
        new_token = refresh_access_token(original_token)
        new_payload = jwt.decode(new_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        
        # Verify new token has same user data
        assert new_payload["user_id"] == str(user_id)
        assert new_payload["email"] == email
        
        # Verify new token has different issued at time
        assert new_payload["iat"] >= original_payload["iat"]
    
    def test_refreshed_token_has_new_expiration(self):
        """Test that refreshed token has a new 24-hour expiration."""
        user_id = uuid4()
        email = "test@example.com"
        
        # Create original token with short expiration
        original_token = create_access_token(
            user_id,
            email,
            expires_delta=timedelta(hours=1)
        )
        
        # Refresh token
        before_refresh = datetime.utcnow()
        new_token = refresh_access_token(original_token)
        after_refresh = datetime.utcnow()
        
        # Verify new token has 24-hour expiration
        new_payload = jwt.decode(new_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        exp_datetime = datetime.utcfromtimestamp(new_payload["exp"])
        
        # Add 1 second buffer to account for integer timestamp precision loss
        expected_exp_min = before_refresh + timedelta(hours=24) - timedelta(seconds=1)
        expected_exp_max = after_refresh + timedelta(hours=24) + timedelta(seconds=1)
        
        assert expected_exp_min <= exp_datetime <= expected_exp_max
    
    def test_rejects_invalid_token_for_refresh(self):
        """Test that refresh_access_token rejects invalid tokens."""
        with pytest.raises(HTTPException) as exc_info:
            refresh_access_token("invalid-token")
        
        assert exc_info.value.status_code == 401


class TestDecodeTokenWithoutVerification:
    """Tests for decode_token_without_verification function."""
    
    def test_decodes_valid_token(self):
        """Test that function decodes valid tokens."""
        user_id = uuid4()
        email = "test@example.com"
        
        token = create_access_token(user_id, email)
        token_data = decode_token_without_verification(token)
        
        assert token_data is not None
        assert token_data.user_id == str(user_id)
        assert token_data.email == email
    
    def test_decodes_expired_token(self):
        """Test that function decodes expired tokens without error."""
        user_id = uuid4()
        email = "test@example.com"
        
        # Create expired token
        token = create_access_token(
            user_id,
            email,
            expires_delta=timedelta(seconds=-1)
        )
        
        # Should decode without raising exception
        token_data = decode_token_without_verification(token)
        
        assert token_data is not None
        assert token_data.user_id == str(user_id)
        assert token_data.email == email
    
    def test_returns_none_for_malformed_token(self):
        """Test that function returns None for malformed tokens."""
        token_data = decode_token_without_verification("not-a-valid-token")
        assert token_data is None