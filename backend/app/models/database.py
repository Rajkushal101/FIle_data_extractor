"""
Database Models
SQLAlchemy models for user data, documents, and processing history
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class UserTier(enum.Enum):
    """User subscription tiers"""
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class DocumentStatus(enum.Enum):
    """Document processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class User(Base):
    """User model for authentication and account management"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    
    # Account details
    tier = Column(SQLEnum(UserTier), default=UserTier.FREE, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # API access
    api_key = Column(String(64), unique=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relationships
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.username}>"


class Document(Base):
    """Document processing records"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # File information
    original_filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size_bytes = Column(Integer)
    file_hash = Column(String(64), index=True)  # SHA256 for deduplication
    
    # Processing details
    status = Column(SQLEnum(DocumentStatus), default=DocumentStatus.PENDING, nullable=False)
    note_style = Column(String(50))  # structured, cornell, outline, mindmap
    
    # Content
    extracted_text = Column(Text)
    structured_notes = Column(Text)  # JSON or Markdown
    
    # Metadata
    page_count = Column(Integer)
    word_count = Column(Integer)
    processing_time_ms = Column(Integer)
    
    # Sharing
    share_token = Column(String(64), unique=True, index=True)
    share_expires_at = Column(DateTime)
    is_public = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="documents")
    exports = relationship("ExportHistory", back_populates="document", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Document {self.original_filename}>"


class ExportHistory(Base):
    """Track document export history"""
    __tablename__ = "export_history"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    
    # Export details
    export_format = Column(String(50), nullable=False)  # pdf, docx, markdown, latex
    export_style = Column(String(50))  # For PDF: modern, academic, minimal
    file_size_bytes = Column(Integer)
    
    # Timestamps
    exported_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    document = relationship("Document", back_populates="exports")
    
    def __repr__(self):
        return f"<Export {self.export_format} - {self.exported_at}>"


class Template(Base):
    """Note templates for different use cases"""
    __tablename__ = "templates"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Template information
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    category = Column(String(50))  # academic, business, technical, educational, legal
    
    # Template content
    style = Column(String(50), nullable=False)  # structured, cornell, outline, mindmap
    prompt_template = Column(Text, nullable=False)  # AI prompt template
    
    # Usage stats
    usage_count = Column(Integer, default=0)
    rating = Column(Integer, default=0)  # 0-5 stars
    
    # Metadata
    is_public = Column(Boolean, default=True)
    created_by_user_id = Column(Integer, ForeignKey("users.id"))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Template {self.name}>"


class ProcessingJob(Base):
    """Background processing jobs for batch operations"""
    __tablename__ = "processing_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Job details
    job_type = Column(String(50), nullable=False)  # batch_process, merge, compare
    status = Column(String(50), default="queued")  # queued, running, completed, failed
    
    # Progress tracking
    total_items = Column(Integer, default=0)
    completed_items = Column(Integer, default=0)
    failed_items = Column(Integer, default=0)
    
    # Results
    result_data = Column(Text)  # JSON results
    error_message = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    def __repr__(self):
        return f"<Job {self.job_type} - {self.status}>"
