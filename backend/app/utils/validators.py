"""
Input Validation Utilities
"""
from fastapi import HTTPException, UploadFile
from config import settings
import logging

logger = logging.getLogger(__name__)


def validate_file(upload_file: UploadFile):
    """
    Validate uploaded file
    Checks file size and extension
    """
    # Check file extension
    if not upload_file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    file_extension = upload_file.filename.split('.')[-1].lower()
    
    if file_extension not in settings.get_allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type .{file_extension} not supported. Allowed: {settings.get_allowed_extensions}"
        )
    
    # Check file size
    if upload_file.size and upload_file.size > settings.MAX_FILE_SIZE:
        max_mb = settings.MAX_FILE_SIZE / (1024**2)
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {max_mb:.1f}MB"
        )
    
    logger.info(f"File validated: {upload_file.filename}")


def is_supported_file_type(filename: str) -> bool:
    """Check if file type is supported"""
    if not filename:
        return False
    
    file_extension = filename.split('.')[-1].lower()
    return file_extension in settings.get_allowed_extensions