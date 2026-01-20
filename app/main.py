"""
FastAPI application entry point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.api.routes import router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Audio Fingerprinting API",
    description="Shazam-like audio fingerprinting system for song recognition",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api", tags=["recognition"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Audio Fingerprinting API",
        "version": "1.0.0",
        "endpoints": {
            "identify": "/api/identify",
            "health": "/api/health",
            "docs": "/docs"
        }
    }


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info("Audio Fingerprinting API starting up...")
    
    # Test database connection
    try:
        from app.database import db
        from app.models.song import Song
        
        # Simple query to test connection
        songs = Song.get_all()
        logger.info(f"Database connection successful. {len(songs)} songs in database.")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        logger.warning("API will start but database operations may fail")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("Audio Fingerprinting API shutting down...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
