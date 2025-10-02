from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user
from app.models import User, Issue
from app.schemas.issues import (
    IssueResponse, IssueListResponse,
    EnhancedIssueCreate, EnhancedIssueResponse
)
from app.services.s3_service import s3_service
from app.utils.file_utils import validate_image_file, validate_file_size, get_file_info
from typing import List, Optional
import time
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/my-issues", response_model=List[IssueListResponse])
def my_issues(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    issues = db.query(Issue).filter_by(user_id=current_user.user_id).order_by(Issue.created_at.desc()).all()
    return issues

@router.get("/issues/{issue_id}", response_model=IssueResponse)
def get_issue(
    issue_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    issue = db.query(Issue).filter_by(issue_id=issue_id, user_id=current_user.user_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    return issue

@router.patch("/issues/{issue_id}/upload-photo")
async def upload_photo_to_issue(
    issue_id: int,
    photo: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload or update photo for an existing issue"""
    
    issue = db.query(Issue).filter_by(issue_id=issue_id, user_id=current_user.user_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    try:
        # Delete old photo if exists
        if issue.photo_url:
            s3_service.delete_file(issue.photo_url)
        
        # Upload new photo
        photo_url = await s3_service.upload_file(photo, "image")
        
        # Update issue
        issue.photo_url = photo_url
        db.commit()
        
        return {"message": "Photo uploaded successfully", "photo_url": photo_url}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to upload photo")

@router.patch("/issues/{issue_id}/upload-voice")
async def upload_voice_to_issue(
    issue_id: int,
    voice_note: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload or update voice note for an existing issue"""
    
    issue = db.query(Issue).filter_by(issue_id=issue_id, user_id=current_user.user_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    try:
        # Delete old voice note if exists
        if issue.voice_note_url:
            s3_service.delete_file(issue.voice_note_url)
        
        # Upload new voice note
        voice_note_url = await s3_service.upload_file(voice_note, "audio")
        
        # Update issue
        issue.voice_note_url = voice_note_url
        db.commit()
        
        return {"message": "Voice note uploaded successfully", "voice_note_url": voice_note_url}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to upload voice note")

# Enhanced Issue Creation Endpoint
@router.post("/issues/create", response_model=EnhancedIssueResponse)
async def create_enhanced_issue(
    # Form data for JSON fields
    category: str = Form(..., description="Main category like 'Road & Transport'"),
    subcategory: str = Form(..., description="Subcategory like 'Potholes'"),
    description: str = Form(..., min_length=10, description="Detailed description"),
    latitude: float = Form(..., ge=-90, le=90, description="GPS latitude"),
    longitude: float = Form(..., ge=-180, le=180, description="GPS longitude"),
    address: str = Form(..., description="Full address"),
    title: Optional[str] = Form(None, description="Custom title (auto-generated if not provided)"),
    
    # File upload
    image: Optional[UploadFile] = File(None, description="Issue image"),
    
    # Dependencies
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new issue with enhanced features:
    - Custom issue ID format (CIV + timestamp)
    - Auto-generated titles from category + subcategory
    - S3 image upload
    - Structured response with user details
    """
    try:
        logger.info(f"Creating issue for user {current_user.user_id}")
        
        # Generate custom issue ID
        timestamp = int(time.time() * 1000)  # milliseconds for uniqueness
        custom_id = f"CIV{timestamp}"
        
        # Auto-generate title if not provided
        if not title:
            title = f"{subcategory} - {category}"
        
        # Handle image upload to S3
        image_url = None
        if image:
            logger.info(f"Processing image upload: {get_file_info(image)}")
            
            # Validate image file
            validate_image_file(image)
            await validate_file_size(image)
            
            # Upload to S3
            image_url = await s3_service.upload_file(image, folder="issues")
            logger.info(f"Image uploaded to S3: {image_url}")
        
        # Create issue in database
        new_issue = Issue(
            custom_id=custom_id,
            user_id=current_user.user_id,
            title=title,
            category=category,
            subcategory=subcategory,
            description=description,
            location=address,
            latitude=latitude,
            longitude=longitude,
            photo_url=image_url,
            status="reported"
        )
        
        db.add(new_issue)
        db.commit()
        db.refresh(new_issue)
        
        logger.info(f"Issue created successfully with ID: {custom_id}")
        
        # Build structured response
        response_data = {
            "issue": {
                "id": custom_id,
                "title": title,
                "category": category,
                "subcategory": subcategory,
                "description": description,
                "status": "reported",
                "location": {
                    "latitude": latitude,
                    "longitude": longitude,
                    "address": address
                },
                "image_url": image_url,
                "reported_by": {
                    "id": current_user.id,
                    "name": current_user.full_name or current_user.name,
                    "phone": current_user.phone_number
                },
                "created_at": new_issue.created_at.isoformat() + "Z"
            }
        }
        
        return {
            "success": True,
            "message": "Issue submitted successfully",
            "data": response_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        # Rollback database transaction
        db.rollback()
        
        # Clean up uploaded file if issue creation fails
        if image_url:
            logger.warning(f"Cleaning up uploaded file due to error: {image_url}")
            s3_service.delete_file(image_url)
        
        logger.error(f"Error creating issue: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create issue: {str(e)}")
