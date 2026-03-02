"""Security middleware for Nyaya Mitra backend."""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime, timedelta
from collections import defaultdict
import time

# Rate limiting storage (in-memory for simplicity, use Redis in production)
rate_limit_storage = defaultdict(list)
session_activity = {}

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware - 100 requests per hour per user."""
    
    def __init__(self, app, requests_per_hour: int = 100):
        super().__init__(app)
        self.requests_per_hour = requests_per_hour
        self.window_seconds = 3600  # 1 hour
    
    async def dispatch(self, request: Request, call_next):
        # Get client identifier (IP or user ID from token)
        client_id = request.client.host if request.client else "unknown"
        
        # Check if user is authenticated and use user ID instead
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                from routers.auth import decode_token
                token = auth_header.split(" ")[1]
                payload = decode_token(token)
                client_id = payload.get("sub", client_id)
            except:
                pass
        
        current_time = time.time()
        
        # Clean old requests outside the window
        rate_limit_storage[client_id] = [
            req_time for req_time in rate_limit_storage[client_id]
            if current_time - req_time < self.window_seconds
        ]
        
        # Check rate limit
        if len(rate_limit_storage[client_id]) >= self.requests_per_hour:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Rate limit exceeded. Maximum 100 requests per hour allowed."
                }
            )
        
        # Add current request
        rate_limit_storage[client_id].append(current_time)
        
        response = await call_next(request)
        return response


class SessionTimeoutMiddleware(BaseHTTPMiddleware):
    """Session timeout middleware - 30 minutes of inactivity."""
    
    def __init__(self, app, timeout_minutes: int = 30):
        super().__init__(app)
        self.timeout_seconds = timeout_minutes * 60
    
    async def dispatch(self, request: Request, call_next):
        # Check if user is authenticated
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                from routers.auth import decode_token
                token = auth_header.split(" ")[1]
                payload = decode_token(token)
                user_id = payload.get("sub")
                
                current_time = time.time()
                
                # Check last activity
                if user_id in session_activity:
                    last_activity = session_activity[user_id]
                    if current_time - last_activity > self.timeout_seconds:
                        return JSONResponse(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            content={
                                "detail": "Session expired due to inactivity. Please login again."
                            }
                        )
                
                # Update last activity
                session_activity[user_id] = current_time
            except:
                pass
        
        response = await call_next(request)
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        return response
