"""
Smart Routing - Choose between local GPU and cloud APIs
"""
import socket
import logging
from config import settings

logger = logging.getLogger(__name__)


class SmartRouter:
    """Route AI requests to best available service"""
    
    @staticmethod
    def is_ollama_available() -> bool:
        """Check if local Ollama is running"""
        if not settings.OLLAMA_ENABLED:
            return False
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            host, port = settings.OLLAMA_HOST.replace('http://', '').split(':')
            result = sock.connect_ex((host, int(port)))
            sock.close()
            return result == 0
        except Exception:
            return False
    
    @staticmethod
    async def route_request(request_type: str):
        """
        Determine best service for request
        
        Returns:
            'nvidia', 'ollama', 'groq', or 'gemini'
        """
        primary_provider = getattr(settings, "PRIMARY_AI_PROVIDER", "nvidia").lower()

        if request_type == "vision":
            if primary_provider == "nvidia" and settings.NVIDIA_API_KEY:
                return "nvidia"

            # Check local Ollama first (fastest)
            if SmartRouter.is_ollama_available():
                logger.info("Routing to local Ollama")
                return "ollama"
            
            # Fallback to cloud
            if settings.GROQ_API_KEY:
                logger.info("Routing to Groq")
                return "groq"
            
            if settings.GEMINI_API_KEY:
                logger.info("Routing to Gemini")
                return "gemini"
        
        elif request_type == "text":
            if primary_provider == "nvidia" and settings.NVIDIA_API_KEY:
                return "nvidia"

            # Prefer Groq for text (faster)
            if settings.GROQ_API_KEY:
                return "groq"
            
            if SmartRouter.is_ollama_available():
                return "ollama"
        
        logger.error("No AI service available for request_type=%s", request_type)
        return None