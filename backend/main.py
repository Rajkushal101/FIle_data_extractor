"""
Main FastAPI Application
Document Extraction & AI Notes Generator
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from config import settings
from app.routes import document_processing, health, auth, documents
from app.core.error_handler import setup_exception_handlers
from app.utils.logger import setup_logging
from app.core.database import init_db, check_db_connection

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    Runs on startup and shutdown
    """
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.VERSION}")
    logger.info(f"Debug Mode: {settings.DEBUG}")
    logger.info(f"Frontend URL: {settings.FRONTEND_URL}")
    logger.info(f"Ollama Enabled: {settings.OLLAMA_ENABLED}")
    
    # Initialize database
    try:
        init_db()
        if check_db_connection():
            logger.info("Database connected successfully")
        else:
            logger.warning("Database connection issues")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="AI-powered document extraction and note generation with user authentication",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup exception handlers
setup_exception_handlers(app)

# Include routers
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(document_processing.router, prefix="/api", tags=["Document Processing"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])  # Phase 3
app.include_router(documents.router, prefix="/api", tags=["Document Management"])  # Phase 3


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.VERSION,
        "status": "online",
        "docs": "/docs",
        "health": "/api/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )