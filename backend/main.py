# Nyaya Mitra Backend - FastAPI Application
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

<<<<<<< HEAD
from database import init_db

=======
>>>>>>> d1831bc1870367c23872fd201e22f3685d5ef71c
app = FastAPI(
    title="Nyaya Mitra API",
    description="AI-powered legal assistance platform for Indian college students",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

<<<<<<< HEAD

@app.on_event("startup")
async def startup_event():
    """Initialize database on application startup."""
    init_db()


=======
>>>>>>> d1831bc1870367c23872fd201e22f3685d5ef71c
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "message": "Nyaya Mitra API is running"}

<<<<<<< HEAD

@app.get("/db-health")
async def db_health_check():
    """Database health check endpoint"""
    from database import get_db
    
    try:
        with get_db() as db:
            db.execute("SELECT 1")
        return {"status": "ok", "message": "Database connection successful"}
    except Exception as e:
        return {"status": "error", "message": f"Database connection failed: {str(e)}"}


=======
>>>>>>> d1831bc1870367c23872fd201e22f3685d5ef71c
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
