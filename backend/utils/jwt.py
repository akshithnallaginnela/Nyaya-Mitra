"""
JWT token generation and validation utilities.

This module implements JWT authentication with 24-hour token expiration,
token validation middleware, and token refresh logic.

Requirements: 9.2 (JWT token with 24-hour expiration)
"""

import os
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError as JoseJWTError, jwt
from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session

from database import get_db_session
from models.user import User


# Export JWTError for convenience
JWTError = JoseJWTError


# JWT Configuration from environment variables
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))


# Security scheme for FastAPI
security = HTTPBearer()


class TokenData(BaseModel):
    """
    Token payload data model.
    
    Attributes:
        user_id: UUID of the authenticated user
        email: Email address of the user
        exp: Token expiration timestamp
        iat: Token issued at timestamp
    """
    user_id: str
    email: str
    exp: Optional[datetime] = None
    iat: Optional[datetime] = None


def create_access_token(user_id: UUID, email: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token with 24-hour expiration.
    
    As per requirement 9.2, JWT tokens must have exactly 24-hour expiration.
    The token includes user_id and email in the payload.
    
    Args:
        user_id: UUID of the user
        email: Email address of the user
        expires_delta: Optional custom expiration time (defaults to 24 hours)
        
    Returns:
        str: Encoded JWT token
        
    Example:
        >>> token = create_access_token(user.id, user.email)
        >>> # Token valid for 24 hours
    """
    # Set expiration to exactly 24 hours as per requirement 9.2
    if expires_delta is None:
        expires_delta = timedelta(hours=JWT_EXPIRATION_HOURS)
    
    now = datetime.utcnow()
    expire = now + expires_delta
    
    # Create token payload
    payload = {
        "user_id": str(user_id),
        "email": email,
        "exp": expire,
        "iat": now
    }
    
    # Encode and return JWT token
    encoded_jwt = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> TokenData:
    """
    Verify and decode a JWT token.
    
    Validates the token signature, expiration, and payload structure.
    
    Args:
        token: JWT token string to verify
        
    Returns:
        TokenData: Decoded token data with user information
        
    Raises:
        HTTPException: If token is invalid, expired, or malformed
            - 401: Invalid token, expired token, or missing credentials
        
    Example:
        >>> token_data = verify_token(token)
        >>> print(token_data.user_id)
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode JWT token
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        
        # Extract user information
        user_id: str = payload.get("user_id")
        email: str = payload.get("email")
        
        if user_id is None or email is None:
            raise credentials_exception
        
        # Create and return token data
        token_data = TokenData(
            user_id=user_id,
            email=email,
            exp=payload.get("exp"),
            iat=payload.get("iat")
        )
        
        return token_data
        
    except JoseJWTError as e:
        # Handle JWT-specific errors (expired, invalid signature, etc.)
        if "expired" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        raise credentials_exception
        
    except ValidationError:
        # Handle Pydantic validation errors
        raise credentials_exception


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db_session)
) -> User:
    """
    FastAPI dependency to get the current authenticated user.
    
    This function serves as middleware for protected routes. It extracts
    the JWT token from the Authorization header, validates it, and retrieves
    the corresponding user from the database.
    
    Args:
        credentials: HTTP Bearer token from Authorization header
        db: Database session dependency
        
    Returns:
        User: Authenticated user object
        
    Raises:
        HTTPException: If token is invalid or user not found
            - 401: Invalid/expired token or user not found
            - 403: User account is inactive
        
    Example:
        >>> @app.get("/api/protected")
        >>> async def protected_route(current_user: User = Depends(get_current_user)):
        >>>     return {"user": current_user.email}
    """
    # Extract token from credentials
    token = credentials.credentials
    
    # Verify token and get token data
    token_data = verify_token(token)
    
    # Query user from database
    user = db.query(User).filter(User.id == UUID(token_data.user_id)).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )
    
    return user


def refresh_access_token(token: str) -> str:
    """
    Refresh an access token by issuing a new one.
    
    This function validates the existing token and issues a new token
    with a fresh 24-hour expiration. This allows users to maintain
    their session without re-authenticating.
    
    Args:
        token: Current JWT token to refresh
        
    Returns:
        str: New JWT token with fresh 24-hour expiration
        
    Raises:
        HTTPException: If token is invalid or cannot be refreshed
            - 401: Invalid token or token cannot be refreshed
        
    Example:
        >>> new_token = refresh_access_token(old_token)
        >>> # New token valid for another 24 hours
    """
    # Verify the existing token
    token_data = verify_token(token)
    
    # Create a new token with the same user information
    new_token = create_access_token(
        user_id=UUID(token_data.user_id),
        email=token_data.email
    )
    
    return new_token


def decode_token_without_verification(token: str) -> Optional[TokenData]:
    """
    Decode a JWT token without verifying its signature or expiration.
    
    This is useful for debugging or extracting information from expired tokens.
    DO NOT use this for authentication - always use verify_token() for that.
    
    Args:
        token: JWT token to decode
        
    Returns:
        TokenData: Decoded token data, or None if token is malformed
        
    Warning:
        This function does NOT verify the token signature or expiration.
        Use only for non-security-critical operations.
    """
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
            options={"verify_signature": False, "verify_exp": False}
        )
        
        return TokenData(
            user_id=payload.get("user_id"),
            email=payload.get("email"),
            exp=payload.get("exp"),
            iat=payload.get("iat")
        )
    except Exception:
        return None
