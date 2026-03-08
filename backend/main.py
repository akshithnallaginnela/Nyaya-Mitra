# Nyaya Mitra Backend - FastAPI Application
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from middleware.security import RateLimitMiddleware, SessionTimeoutMiddleware, SecurityHeadersMiddleware

from database import init_db
from routers import auth, chat, case, action_plan, documents, legal_aid, language, evidence, emergency

app = FastAPI(
    title="Nyaya Mitra API",
    description="AI-powered legal assistance platform for Indian college students",
    version="1.0.0",
    docs_url="/api/docs" if os.getenv("ENVIRONMENT") == "production" else "/docs",
    redoc_url="/api/redoc" if os.getenv("ENVIRONMENT") == "production" else "/redoc",
)

# Security middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(SessionTimeoutMiddleware, timeout_minutes=30)
app.add_middleware(RateLimitMiddleware, requests_per_hour=100)

# CORS configuration — dynamically loaded from environment
cors_origins_env = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173")
if cors_origins_env == "*":
    cors_origins = ["*"]
else:
    cors_origins = [origin.strip() for origin in cors_origins_env.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(case.router)
app.include_router(action_plan.router)
app.include_router(documents.router)
app.include_router(legal_aid.router)
app.include_router(language.router)
app.include_router(evidence.router)
app.include_router(emergency.router)


@app.on_event("startup")
async def startup_event():
    """Initialize database on application startup."""
    init_db()


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "message": "Nyaya Mitra API is running"}


@app.get("/db-health")
async def db_health_check():
    """Database health check endpoint"""
    from database import get_db
    
    from sqlalchemy import text
    try:
        with get_db() as db:
            db.execute(text("SELECT 1"))
        return {"status": "ok", "message": "Database connection successful"}
    except Exception as e:
        return {"status": "error", "message": f"Database connection failed: {str(e)}"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
