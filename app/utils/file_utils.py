"""
File utilities for validation and handling
"""
from fastapi import UploadFile, HTTPException
from app.config import MAX_FILE_SIZE, ALLOWED_IMAGE_TYPES, ALLOWED_AUDIO_TYPES
import logging

logger = logging.getLogger(__name__)

def validate_image_file(file: UploadFile) -> str:
    """Validate uploaded image file"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Check file extension
    file_extension = file.filename.split('.')[-1].lower()
    allowed_extensions = []
    for content_type in ALLOWED_IMAGE_TYPES:
        if content_type == 'image/jpeg':
            allowed_extensions.extend(['jpg', 'jpeg'])
        elif content_type == 'image/png':
            allowed_extensions.append('png')
        elif content_type == 'image/gif':
            allowed_extensions.append('gif')
        elif content_type == 'image/webp':
            allowed_extensions.append('webp')
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid file type. Allowed extensions: {', '.join(allowed_extensions)}"
        )
    
    # Check content type
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid content type. Allowed types: {', '.join(ALLOWED_IMAGE_TYPES)}"
        )
    
    return file_extension

def validate_audio_file(file: UploadFile) -> str:
    """Validate uploaded audio file"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Check file extension
    file_extension = file.filename.split('.')[-1].lower()
    allowed_extensions = []
    for content_type in ALLOWED_AUDIO_TYPES:
        if content_type == 'audio/mpeg':
            allowed_extensions.extend(['mp3', 'mpeg'])
        elif content_type == 'audio/wav':
            allowed_extensions.append('wav')
        elif content_type == 'audio/m4a':
            allowed_extensions.append('m4a')
        elif content_type == 'audio/ogg':
            allowed_extensions.append('ogg')
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid file type. Allowed extensions: {', '.join(allowed_extensions)}"
        )
    
    # Check content type
    if file.content_type not in ALLOWED_AUDIO_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid content type. Allowed types: {', '.join(ALLOWED_AUDIO_TYPES)}"
        )
    
    return file_extension

async def validate_file_size(file: UploadFile) -> None:
    """Validate file size by reading content"""
    try:
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413, 
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
            )
        
        # Reset file pointer
        await file.seek(0)
        logger.info(f"File size validation passed: {len(content)} bytes")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating file size: {e}")
        raise HTTPException(status_code=500, detail="Failed to validate file")

def get_file_info(file: UploadFile) -> dict:
    """Get file information for logging"""
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": getattr(file, 'size', 'unknown')
    }