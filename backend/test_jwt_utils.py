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
        """Test that create_access_token generates a v