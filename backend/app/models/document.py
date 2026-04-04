"""
Document Model
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DocumentBase(BaseModel):
    """Base document fields"""
    filename: str
    file_type: str
    file_size: int


class DocumentCreate(DocumentBase):
    """Document creation model"""
    pass


class Document(DocumentBase):
    """Document data model with full fields"""
    id: Optional[str] = None
    uploaded_at: datetime = datetime.utcnow()
    processed: bool = False
    content: Optional[str] = None