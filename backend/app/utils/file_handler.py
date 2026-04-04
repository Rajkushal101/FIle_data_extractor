"""
File Handling Utilities
"""
import os
import uuid
import aiofiles
from fastapi import UploadFile
from config import settings
import logging

logger = logging.getLogger(__name__)


async def save_upload_file(upload_file: UploadFile) -> str:
    """
    Save uploaded file to temp directory
    
    Returns:
        Path to saved file
    """
    # Generate unique filename
    file_extension = upload_file.filename.split('.')[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
    
    # Save file
    async with aiofiles.open(file_path, 'wb') as f:
        content = await upload_file.read()
        await f.write(content)
    
    logger.info(f"Saved file: {file_path}")
    return file_path


def cleanup_temp_file(file_path: str):
    """Delete temporary file"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Cleaned up: {file_path}")
    except Exception as e:
        logger.warning(f"Could not cleanup {file_path}: {e}")


async def cleanup_old_files():
    """Clean up old temporary files"""
    import time
    from datetime import datetime, timedelta
    
    try:
        cutoff_time = time.time() - (settings.TEMP_FILE_RETENTION_HOURS * 3600)
        
        for directory in [settings.UPLOAD_DIR, settings.TEMP_DIR]:
            if not os.path.exists(directory):
                continue
                
            for filename in os.listdir(directory):
                if filename == '.gitkeep':
                    continue
                    
                filepath = os.path.join(directory, filename)
                if os.path.isfile(filepath):
                    if os.path.getmtime(filepath) < cutoff_time:
                        try:
                            os.remove(filepath)
                            logger.info(f"Cleaned up old file: {filepath}")
                        except Exception as e:
                            logger.warning(f"Could not remove {filepath}: {e}")
    except Exception as e:
        logger.error(f"Error cleaning up old files: {e}")