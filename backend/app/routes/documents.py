"""
Document Management Routes
CRUD operations for user documents
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.models.database import User, Document, DocumentStatus, ExportHistory
from app.core.database import get_db
from app.core.auth import get_current_user

router = APIRouter()


# ==================== Response Models ====================

class DocumentResponse(BaseModel):
    """Document details response"""
    id: int
    original_filename: str
    file_type: str
    file_size_bytes: Optional[int]
    status: str
    note_style: Optional[str]
    page_count: Optional[int]
    word_count: Optional[int]
    is_public: bool
    created_at: str
    
    class Config:
        from_attributes = True


class DocumentDetailResponse(DocumentResponse):
    """Detailed document response with content"""
    extracted_text: Optional[str]
    structured_notes: Optional[str]
    processing_time_ms: Optional[int]
    share_token: Optional[str]


class ExportHistoryResponse(BaseModel):
    """Export history item"""
    id: int
    export_format: str
    export_style: Optional[str]
    file_size_bytes: Optional[int]
    exported_at: str
    
    class Config:
        from_attributes = True


# ==================== Routes ====================

@router.get("/documents", response_model=List[DocumentResponse])
async def list_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, le=100),
    status: Optional[str] = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List user's documents
    
    - Paginated results
    - Optional status filter
    - Ordered by most recent
    """
    query = db.query(Document).filter(Document.user_id == user.id)
    
    # Apply status filter
    if status:
        try:
            status_enum = DocumentStatus[status.upper()]
            query = query.filter(Document.status == status_enum)
        except KeyError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
    
    # Order by most recent and paginate
    documents = query.order_by(desc(Document.created_at)).offset(skip).limit(limit).all()
    
    return [
        {
            "id": doc.id,
            "original_filename": doc.original_filename,
            "file_type": doc.file_type,
            "file_size_bytes": doc.file_size_bytes,
            "status": doc.status.value,
            "note_style": doc.note_style,
            "page_count": doc.page_count,
            "word_count": doc.word_count,
            "is_public": doc.is_public,
            "created_at": doc.created_at.isoformat()
        }
        for doc in documents
    ]


@router.get("/documents/{document_id}", response_model=DocumentDetailResponse)
async def get_document(
    document_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get document details
    
    - Returns full document content
    - Includes structured notes
    """
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == user.id
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {
        "id": document.id,
        "original_filename": document.original_filename,
        "file_type": document.file_type,
        "file_size_bytes": document.file_size_bytes,
        "status": document.status.value,
        "note_style": document.note_style,
        "page_count": document.page_count,
        "word_count": document.word_count,
        "is_public": document.is_public,
        "created_at": document.created_at.isoformat(),
        "extracted_text": document.extracted_text,
        "structured_notes": document.structured_notes,
        "processing_time_ms": document.processing_time_ms,
        "share_token": document.share_token if document.is_public else None
    }


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a document
    
    - Permanently removes document and exports
    - Cannot be undone
    """
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == user.id
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    db.delete(document)
    db.commit()
    
    return {"message": "Document deleted successfully"}


@router.post("/documents/{document_id}/share")
async def share_document(
    document_id: int,
    expires_hours: int = Query(24, ge=1, le=168),  # 1 hour to 7 days
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate shareable link for document
    
    - Creates temporary public access
    - Link expires after specified hours
    """
    import secrets
    from datetime import timedelta
    
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == user.id
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Generate share token
    share_token = secrets.token_urlsafe(32)
    share_expires = datetime.utcnow() + timedelta(hours=expires_hours)
    
    document.share_token = share_token
    document.share_expires_at = share_expires
    document.is_public = True
    
    db.commit()
    
    return {
        "share_token": share_token,
        "share_url": f"/shared/{share_token}",
        "expires_at": share_expires.isoformat()
    }


@router.delete("/documents/{document_id}/share")
async def revoke_share(
    document_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Revoke public share link"""
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == user.id
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    document.share_token = None
    document.share_expires_at = None
    document.is_public = False
    
    db.commit()
    
    return {"message": "Share link revoked"}


@router.get("/documents/{document_id}/exports", response_model=List[ExportHistoryResponse])
async def get_export_history(
    document_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get export history for a document
    
    - Lists all exports (PDF, DOCX, etc.)
    - Ordered by most recent
    """
    # Verify document ownership
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == user.id
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    exports = db.query(ExportHistory).filter(
        ExportHistory.document_id == document_id
    ).order_by(desc(ExportHistory.exported_at)).all()
    
    return [
        {
            "id": exp.id,
            "export_format": exp.export_format,
            "export_style": exp.export_style,
            "file_size_bytes": exp.file_size_bytes,
            "exported_at": exp.exported_at.isoformat()
        }
        for exp in exports
    ]


@router.get("/search")
async def search_documents(
    q: str = Query(..., min_length=3),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Search user's documents
    
    - Searches in filename and extracted text
    - Returns matching documents
    """
    # Search in filename and extracted text
    documents = db.query(Document).filter(
        Document.user_id == user.id,
        (Document.original_filename.contains(q)) | (Document.extracted_text.contains(q))
    ).limit(20).all()
    
    return [
        {
            "id": doc.id,
            "original_filename": doc.original_filename,
            "file_type": doc.file_type,
            "status": doc.status.value,
            "created_at": doc.created_at.isoformat()
        }
        for doc in documents
    ]
