"""
Authentication endpoints for Nyaya Mitra.

This module implements authentication endpoints including:
- POST /api/auth/register - User registration with email validation
- POST /api/auth/login - User login with credential verification
- POST /api/auth/refresh - Token renewal
- DELETE /api/auth/account - Account deletion

Requirements: 9.1 (Password encryption), 9.2 (JWT tokens), 9.5 (Account deletion)
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from database import get_db_session
from models.user import User
from utils.jwt import create_access_token, get_current_user, refresh_access_token


router = APIRouter(prefix="/api/auth", tags=["authentication"])


# Request/Response Models

class RegisterRequest(BaseModel):
    """Request model for user registration."""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, description="User's password")
    full_name: str = Field(..., min_length=2, description="User's full name")
    college_name: Optional[str] = Field(None, description="User's college/institution name")
    preferred_language: str = Field("en", description="Preferred language code")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "student@example.com",
                "password": "SecurePass123!",
                "full_name": "John Doe",
                "college_name": "Delhi University",
                "preferred_language": "en"
            }
        }


class LoginRequest(BaseModel):
    """Request model for user login."""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "student@example.com",
                "password": "SecurePass123!"
            }
        }


class RefreshRequest(BaseModel):
    """Request model for token refresh."""
    token: str = Field(..., description="Current JWT token to refresh")
    
    class Config:
        json_schema_extra = {
            "example": {
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }


class AuthResponse(BaseModel):
    """Response model for authentication endpoints."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type")
    user: dict = Field(..., description="User information")
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "email": "student@example.com",
                    "full_name": "John Doe",
                    "college_name": "Delhi University",
                    "preferred_language": "en"
                }
            }
        }


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str = Field(..., description="Response message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Operation completed successfully"
            }
        }


# Endpoints

@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email validation and secure password hashing"
)
async def register(
    request: RegisterRequest,
    db: Session = Depends(get_db_session)
) -> AuthResponse:
    """
    Register a new user account.
    
    This endpoint:
    1. Validates email format and uniqueness
    2. Validates password strength (min 8 chars, uppercase, lowercase, digit, special char)
    3. Hashes password using bcrypt with 12 rounds (exceeds requirement 9.1 minimum of 10)
    4. Creates user account in database
    5. Issues JWT token with 24-hour expiration (requirement 9.2)
    
    Args:
        request: Registration request with user details
        db: Database session
        
    Returns:
        AuthResponse: JWT token and user information
        
    Raises:
        HTTPException 400: If email already exists or validation fails
        HTTPException 422: If request data is invalid
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == request.email.lower()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    try:
        # Create new user
        user = User(
            email=request.email.lower(),
            full_name=request.full_name,
            college_name=request.college_name,
            preferred_language=request.preferred_language
        )
        
        # Set password (validates strength and hashes with bcrypt)
        user.set_password(request.password)
        
        # Add to database
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Create JWT token with 24-hour expiration
        access_token = create_access_token(user.id, user.email)
        
        # Return response
        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            user={
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "college_name": user.college_name,
                "preferred_language": user.preferred_language
            }
        )
        
    except ValueError as e:
        # Handle validation errors from User model
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Handle unexpected errors
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="User login",
    description="Authenticate user with email and password, return JWT token"
)
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db_session)
) -> AuthResponse:
    """
    Authenticate user and issue JWT token.
    
    This endpoint:
    1. Validates email and password credentials
    2. Verifies password against bcrypt hash
    3. Issues JWT token with 24-hour expiration (requirement 9.2)
    
    Args:
        request: Login request with email and password
        db: Database session
        
    Returns:
        AuthResponse: JWT token and user information
        
    Raises:
        HTTPException 401: If credentials are invalid or user not found
        HTTPException 403: If user account is inactive
    """
    # Find user by email
    user = db.query(User).filter(User.email == request.email.lower()).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not user.verify_password(request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Check if account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Create JWT token with 24-hour expiration
    access_token = create_access_token(user.id, user.email)
    
    # Return response
    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user={
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "college_name": user.college_name,
            "preferred_language": user.preferred_language
        }
    )


@router.get(
    "/me",
    response_model=dict,
    summary="Get current user details",
    description="Fetch the authenticated user's details from the JWT token"
)
async def get_me(
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    Get current user details.
    
    Args:
        current_user: Authenticated user from JWT token
        
    Returns:
        dict: User information
    """
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "full_name": current_user.full_name,
        "college_name": current_user.college_name,
        "preferred_language": current_user.preferred_language
    }


@router.post(
    "/refresh",
    response_model=AuthResponse,
    summary="Refresh JWT token",
    description="Refresh an existing JWT token to extend the session"
)
async def refresh(
    request: RefreshRequest,
    db: Session = Depends(get_db_session)
) -> AuthResponse:
    """
    Refresh JWT token to extend user session.
    
    This endpoint:
    1. Validates the existing JWT token
    2. Issues a new JWT token with fresh 24-hour expiration (requirement 9.2)
    3. Returns updated user information
    
    Args:
        request: Refresh request with current token
        db: Database session
        
    Returns:
        AuthResponse: New JWT token and user information
        
    Raises:
        HTTPException 401: If token is invalid or expired
        HTTPException 404: If user not found
    """
    try:
        # Refresh token (validates and creates new token)
        new_token = refresh_access_token(request.token)
        
        # Decode token to get user info
        from utils.jwt import verify_token
        token_data = verify_token(new_token)
        
        # Get user from database
        from uuid import UUID
        user = db.query(User).filter(User.id == UUID(token_data.user_id)).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if account is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive"
            )
        
        # Return response with new token
        return AuthResponse(
            access_token=new_token,
            token_type="bearer",
            user={
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "college_name": user.college_name,
                "preferred_language": user.preferred_language
            }
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token refresh failed: {str(e)}"
        )


@router.delete(
    "/account",
    response_model=MessageResponse,
    summary="Delete user account",
    description="Delete the authenticated user's account and all associated data"
)
async def delete_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
) -> MessageResponse:
    """
    Delete user account and all associated data.
    
    This endpoint:
    1. Authenticates the user via JWT token
    2. Deletes the user account from database
    3. Cascades deletion to all related data (requirement 9.5):
       - Conversations and messages
       - Case analyses
       - Generated documents
    
    The cascade deletion is configured in the User model relationships
    with cascade="all, delete-orphan".
    
    Args:
        current_user: Authenticated user from JWT token
        db: Database session
        
    Returns:
        MessageResponse: Success message
        
    Raises:
        HTTPException 401: If authentication fails
        HTTPException 500: If deletion fails
    """
    try:
        # Delete user (cascade will delete all related data)
        db.delete(current_user)
        db.commit()
        
        return MessageResponse(
            message="Account deleted successfully"
        )
        
    except Exception as e:
        # Rollback on error
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Account deletion failed: {str(e)}"
        )
