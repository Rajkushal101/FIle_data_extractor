"""
Processing Result Model
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from enum import Enum


class ProcessingStatus(str, Enum):
    """Status of document processing"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ProcessingResult(BaseModel):
    """Result of document processing"""
    success: bool
    filename: str
    file_type: str
    raw_content: Dict[str, Any]
    structured_notes: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = {}
    error: Optional[str] = None
