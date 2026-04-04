"""
Rate Limiting
"""
import logging

try:
    from slowapi import Limiter
    from slowapi.util import get_remote_address
    SLOWAPI_AVAILABLE = True
except ImportError:
    SLOWAPI_AVAILABLE = False
    Limiter = None
    get_remote_address = None

logger = logging.getLogger(__name__)

if SLOWAPI_AVAILABLE:
    limiter = Limiter(key_func=get_remote_address)
else:
    limiter = None
    logger.warning("slowapi not installed. Rate limiting disabled.")
