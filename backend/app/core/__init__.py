"""
Core Package
Core functionality including error handling, rate limiting, and smart routing
"""

from .error_handler import setup_exception_handlers
from .rate_limiter import limiter
from .smart_router import SmartRouter

__all__ = ["setup_exception_handlers", "limiter", "SmartRouter"]
