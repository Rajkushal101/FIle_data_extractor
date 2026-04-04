"""
Routes Package
API endpoints for document processing, health checks, and user management
"""

from .document_processing import router as document_router
from .health import router as health_router
from .user import router as user_router

__all__ = ["document_router", "health_router", "user_router"]
