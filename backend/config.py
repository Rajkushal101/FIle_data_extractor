"""
Configuration Management
Centralized settings for the application using Pydantic
"""

from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from typing import List
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application Info
    APP_NAME: str = "File Data Extractor"
    VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=True, env="DEBUG")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Server Configuration
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    
    # CORS Settings
    FRONTEND_URL: str = Field(default="http://localhost:3000", env="FRONTEND_URL")
    ALLOWED_ORIGINS: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000",
        env="ALLOWED_ORIGINS"
    )
    CORS_ALLOW_ORIGIN_REGEX: str = Field(
        default=r"https://.*\.vercel\.app",
        env="CORS_ALLOW_ORIGIN_REGEX"
    )
    
    # File Upload Settings
    MAX_FILE_SIZE: int = Field(default=52428800, env="MAX_FILE_SIZE")  # 50MB
    ALLOWED_EXTENSIONS: str = Field(
        default="pdf,docx,pptx,png,jpg,jpeg",
        env="ALLOWED_EXTENSIONS"
    )
    UPLOAD_DIR: Path = Path("backend/uploads")
    TEMP_DIR: Path = Path("backend/temp")
    
    # API Keys (Cloud Services)
    GROQ_API_KEY: str = Field(default="", env="GROQ_API_KEY")
    GEMINI_API_KEY: str = Field(default="", env="GEMINI_API_KEY")
    NVIDIA_API_KEY: str = Field(default="", env="NVIDIA_API_KEY")
    NVIDIA_BASE_URL: str = Field(default="https://integrate.api.nvidia.com/v1", env="NVIDIA_BASE_URL")
    NVIDIA_ENABLED: bool = Field(default=False, env="NVIDIA_ENABLED")
    NVIDIA_MODEL_VISION: str = Field(default="meta/llama-3.2-90b-vision-instruct", env="NVIDIA_MODEL_VISION")
    NVIDIA_MODEL_TEXT: str = Field(default="meta/llama-3.1-70b-instruct", env="NVIDIA_MODEL_TEXT")
    NVIDIA_MODEL_ENHANCEMENT: str = Field(default="meta/llama-3.1-405b-instruct", env="NVIDIA_MODEL_ENHANCEMENT")

    # Provider orchestration
    PRIMARY_AI_PROVIDER: str = Field(default="nvidia", env="PRIMARY_AI_PROVIDER")
    STRICT_AI_PROVIDER: bool = Field(default=True, env="STRICT_AI_PROVIDER")
    
    # Ollama Configuration (Local AI)
    OLLAMA_HOST: str = Field(default="http://localhost:11434", env="OLLAMA_HOST")
    OLLAMA_ENABLED: bool = Field(default=False, env="OLLAMA_ENABLED")
    OLLAMA_MODEL_VISION: str = "qwen2.5-vl:7b"
    OLLAMA_MODEL_TEXT: str = "llama3.1:8b"
    
    # Processing Configuration
    MAX_CONCURRENT_PROCESSES: int = Field(default=5, env="MAX_CONCURRENT_PROCESSES")
    PROCESSING_TIMEOUT: int = 300  # 5 minutes
    TEMP_FILE_RETENTION_HOURS: int = Field(default=24, env="TEMP_FILE_RETENTION_HOURS")
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 3600  # 1 hour
    
    # AI Processing Settings
    AI_TEMPERATURE: float = 0.7
    AI_MAX_TOKENS: int = 2048
    AI_REQUEST_TIMEOUT_SECONDS: int = Field(default=60, env="AI_REQUEST_TIMEOUT_SECONDS")
    AI_REQUEST_RETRIES: int = Field(default=2, env="AI_REQUEST_RETRIES")
    AI_RETRY_BACKOFF_SECONDS: float = Field(default=1.0, env="AI_RETRY_BACKOFF_SECONDS")
    
    # Security (Phase 3)
    SECRET_KEY: str = Field(default="", env="SECRET_KEY")  # IMPORTANT: Set in production!
    
    @property
    def get_allowed_extensions(self) -> List[str]:
        """Get allowed extensions as a list"""
        if isinstance(self.ALLOWED_EXTENSIONS, str):
            return [ext.strip().lower() for ext in self.ALLOWED_EXTENSIONS.split(",")]
        return self.ALLOWED_EXTENSIONS
    
    @property
    def get_allowed_origins(self) -> List[str]:
        """Get allowed origins as a list"""
        if isinstance(self.ALLOWED_ORIGINS, str):
            return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]
        return self.ALLOWED_ORIGINS

    @property
    def get_cors_allow_origin_regex(self) -> str:
        """Regex pattern used by CORS middleware for preview deployments (e.g., Vercel)."""
        return self.CORS_ALLOW_ORIGIN_REGEX.strip()
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Create settings instance
settings = Settings()

# Ensure directories exist
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.TEMP_DIR.mkdir(parents=True, exist_ok=True)
