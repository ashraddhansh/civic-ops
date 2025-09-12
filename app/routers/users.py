from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user
from app.models import User, Issue
from app.schemas.issues import IssueCreate, IssueResponse, IssueListResponse
from app.services.s3_service import s3_service
from typing import List, Optional

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/my-issues", response_model=List[IssueListResponse])
def my_issues(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    issues = db.query(Issue).filter_by(user_id=current_user.user_id).order_by(Issue.created_at.desc()).all()
    return issues

@router.post("/issues", response_model=IssueResponse)
def create_issue(
    issue_data: IssueCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Validate category
    valid_categories = ["road", "water", "electricity", "waste", "public_safety", "infrastructure", "other"]
    if issue_data.category not in valid_categories:
        raise HTTPException(status_code=400, detail=f"Invalid category. Must be one of: {', '.join(valid_categories)}")
    
    # Create new issue (priority will be set to default "unassigned")
    new_issue = Issue(
        user_id=current_user.user_id,
        title=issue_data.title,
        description=issue_data.description,
        category=issue_data.category,
        location=issue_data.location,
        latitude=issue_data.latitude,
        longitude=issue_data.longitude
        # priority defaults to "unassigned" in the model
    )
    
    db.add(new_issue)
    db.commit()
    db.refresh(new_issue)
    
    return new_issue

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

@router.post("/issues/with-files", response_model=IssueResponse)
async def create_issue_with_files(
    title: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    location: Optional[str] = Form(None),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    photo: Optional[UploadFile] = File(None),
    voice_note: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create issue with optional file uploads"""
    
    # Validate category
    valid_categories = ["road", "water", "electricity", "waste", "public_safety", "infrastructure", "other"]
    if category not in valid_categories:
        raise HTTPException(status_code=400, detail=f"Invalid category. Must be one of: {', '.join(valid_categories)}")
    
    # Validate form data
    if len(title) < 5 or len(title) > 200:
        raise HTTPException(status_code=400, detail="Title must be between 5 and 200 characters")
    if len(description) < 10:
        raise HTTPException(status_code=400, detail="Description must be at least 10 characters")
    
    photo_url = None
    voice_note_url = None
    
    try:
        # Upload photo if provided
        if photo:
            photo_url = await s3_service.upload_file(photo, "image")
        
        # Upload voice note if provided
        if voice_note:
            voice_note_url = await s3_service.upload_file(voice_note, "audio")
        
        # Create new issue
        new_issue = Issue(
            user_id=current_user.user_id,
            title=title,
            description=description,
            category=category,
            location=location,
            latitude=latitude,
            longitude=longitude,
            photo_url=photo_url,
            voice_note_url=voice_note_url
        )
        
        db.add(new_issue)
        db.commit()
        db.refresh(new_issue)
        
        return new_issue
        
    except HTTPException:
        raise
    except Exception as e:
        # Clean up uploaded files if issue creation fails
        if photo_url:
            s3_service.delete_file(photo_url)
        if voice_note_url:
            s3_service.delete_file(voice_note_url)
        raise HTTPException(status_code=500, detail="Failed to create issue")

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
