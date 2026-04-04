"""
Health Check Endpoints
"""

from fastapi import APIRouter
from datetime import datetime
from config import settings
import os
import logging

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Basic health check endpoint
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.VERSION
    }


@router.get("/health/detailed")
async def detailed_health():
    """
    Detailed health check with system info
    """
    result = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.VERSION
    }
    
    if PSUTIL_AVAILABLE:
        # CPU and Memory info
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('.')
        
        result["system"] = {
            "cpu_percent": cpu_percent,
            "memory": {
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "percent": memory.percent
            },
            "disk": {
                "total_gb": round(disk.total / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "percent": disk.percent
            }
        }
    else:
        result["system"] = {
            "message": "System metrics unavailable (psutil not installed)"
        }
    
    result["config"] = {
        "debug": settings.DEBUG,
        "max_file_size_mb": settings.MAX_FILE_SIZE / (1024**2),
        "allowed_extensions": settings.get_allowed_extensions,
        "ollama_enabled": settings.OLLAMA_ENABLED
    }
    
    return result
