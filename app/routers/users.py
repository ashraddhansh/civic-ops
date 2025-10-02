from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
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

def extract_s3_key_from_url(url: str) -> str:
    """
    Extract S3 key from either:
    1. Full S3 URL: https://bucket.s3.region.amazonaws.com/key
    2. Already an S3 key: just return as-is
    """
    if not url:
        return None
    
    # If it's already an S3 key (no https://), return as-is
    if not url.startswith('https://'):
        return url
    
    # Extract key from full S3 URL
    try:
        # Pattern: https://bucket.s3.region.amazonaws.com/key
        if '.s3.' in url and '.amazonaws.com/' in url:
            return url.split('.amazonaws.com/')[-1].split('?')[0]
        # Pattern: https://s3.region.amazonaws.com/bucket/key
        elif 's3.' in url and '.amazonaws.com/' in url:
            parts = url.split('.amazonaws.com/')[-1].split('/')
            if len(parts) > 1:
                return '/'.join(parts[1:]).split('?')[0]
    except Exception as e:
        logger.warning(f"Failed to extract S3 key from URL {url}: {e}")
    
    # Fallback: return the original URL
    return url

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/my-issues")
async def get_my_issues(
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    limit: int = Query(20, ge=1, le=100, description="Number of issues per page"),
    status: Optional[str] = Query(None, description="Filter by status (reported, in_progress, resolved, etc.)"),
    category: Optional[str] = Query(None, description="Filter by category"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of issues reported by the current user
    
    Query Parameters:
    - page: Page number (default: 1)
    - limit: Items per page (default: 20, max: 100)
    - status: Filter by issue status (optional)
    - category: Filter by issue category (optional)
    """
    try:
        # Calculate offset for pagination
        offset = (page - 1) * limit
        
        # Build query with filters
        query = db.query(Issue).filter(Issue.user_id == current_user.user_id)
        
        # Apply filters if provided
        if status:
            query = query.filter(Issue.status == status)
        
        if category:
            query = query.filter(Issue.category == category)
        
        # Get total count for pagination
        total = query.count()
        
        # Get issues with pagination, ordered by created_at desc (newest first)
        issues = query.order_by(desc(Issue.created_at)).offset(offset).limit(limit).all()
        
        # Format response data with fresh presigned URLs
        formatted_issues = []
        for issue in issues:
            # Generate fresh presigned URL for each image on every request
            image_url = None
            if issue.photo_url:  # photo_url might contain S3 key or full URL
                try:
                    # Extract S3 key from URL if needed
                    s3_key = extract_s3_key_from_url(issue.photo_url)
                    
                    # Generate fresh presigned URL (valid for 4 hours)
                    image_url = s3_service.generate_presigned_url(
                        s3_key, 
                        expiration=14400  # 4 hours
                    )
                except Exception as e:
                    logger.warning(f"Failed to generate presigned URL for {issue.photo_url}: {str(e)}")
                    image_url = None
            
            formatted_issue = {
                "id": issue.custom_id if issue.custom_id else str(issue.issue_id),
                "title": issue.title,
                "category": issue.category,
                "subcategory": issue.subcategory or "",
                "status": issue.status,
                "location": {
                    "address": issue.location or "Location not specified"
                },
                "image_url": image_url,  # Fresh presigned URL generated on each request
                "created_at": issue.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            }
            formatted_issues.append(formatted_issue)
        
        # Build response
        response_data = {
            "success": True,
            "message": "Issues retrieved successfully",
            "data": {
                "issues": formatted_issues,
                "total": total,
                "page": page,
                "limit": limit
            }
        }
        
        return response_data
        
    except Exception as e:
        logger.error(f"Error fetching user issues: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch issues")

@router.get("/issues/{issue_id}")
async def get_issue(
    issue_id: str,  # Changed to str to handle both numeric IDs and custom CIV IDs
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get specific issue details with fresh presigned URLs
    
    Args:
        issue_id: Can be either numeric issue_id or custom_id (CIV format)
    """
    try:
        # Try to find issue by custom_id first, then by issue_id
        issue = None
        
        # If it starts with CIV, search by custom_id
        if issue_id.startswith('CIV'):
            issue = db.query(Issue).filter_by(
                custom_id=issue_id, 
                user_id=current_user.user_id
            ).first()
        else:
            # Try to parse as numeric issue_id
            try:
                numeric_id = int(issue_id)
                issue = db.query(Issue).filter_by(
                    issue_id=numeric_id, 
                    user_id=current_user.user_id
                ).first()
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid issue ID format")
        
        if not issue:
            raise HTTPException(status_code=404, detail="Issue not found")
        
        # Generate fresh presigned URL for the image
        image_url = None
        if issue.photo_url:
            try:
                # Extract S3 key from URL if needed
                s3_key = extract_s3_key_from_url(issue.photo_url)
                image_url = s3_service.generate_presigned_url(
                    s3_key, 
                    expiration=14400  # 4 hours
                )
            except Exception as e:
                logger.warning(f"Failed to generate presigned URL: {str(e)}")
        
        # Generate fresh presigned URL for voice note if exists
        voice_note_url = None
        if issue.voice_note_url:
            try:
                # Extract S3 key from URL if needed
                s3_key = extract_s3_key_from_url(issue.voice_note_url)
                voice_note_url = s3_service.generate_presigned_url(
                    s3_key, 
                    expiration=14400  # 4 hours
                )
            except Exception as e:
                logger.warning(f"Failed to generate presigned URL for voice note: {str(e)}")
        
        response_data = {
            "success": True,
            "message": "Issue retrieved successfully",
            "data": {
                "issue": {
                    "id": issue.custom_id if issue.custom_id else str(issue.issue_id),
                    "title": issue.title,
                    "category": issue.category,
                    "subcategory": issue.subcategory or "",
                    "status": issue.status,
                    "location": {
                        "address": issue.location or "Location not specified"
                    },
                    "image_url": image_url,      # Fresh presigned URL
                    "created_at": issue.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                    "updated_at": issue.updated_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ") if issue.updated_at else None
                }
            }
        }
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching issue {issue_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch issue")

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
            old_s3_key = extract_s3_key_from_url(issue.photo_url)
            s3_service.delete_file(old_s3_key)
        
        # Upload new photo and get S3 key
        photo_s3_key = await s3_service.upload_file(photo, "issues")
        
        # Update issue with S3 key
        issue.photo_url = photo_s3_key
        db.commit()
        
        # Generate fresh presigned URL for response
        photo_presigned_url = s3_service.generate_presigned_url(photo_s3_key, expiration=14400)
        
        return {"message": "Photo uploaded successfully", "photo_url": photo_presigned_url}
        
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
            old_s3_key = extract_s3_key_from_url(issue.voice_note_url)
            s3_service.delete_file(old_s3_key)
        
        # Upload new voice note and get S3 key
        voice_note_s3_key = await s3_service.upload_file(voice_note, "issues")
        
        # Update issue with S3 key
        issue.voice_note_url = voice_note_s3_key
        db.commit()
        
        # Generate fresh presigned URL for response
        voice_note_presigned_url = s3_service.generate_presigned_url(voice_note_s3_key, expiration=14400)
        
        return {"message": "Voice note uploaded successfully", "voice_note_url": voice_note_presigned_url}
        
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
        image_s3_key = None
        if image:
            logger.info(f"Processing image upload: {get_file_info(image)}")
            
            # Validate image file
            validate_image_file(image)
            await validate_file_size(image)
            
            # Upload to S3 and get S3 key
            image_s3_key = await s3_service.upload_file(image, folder="issues")
            logger.info(f"Image uploaded to S3 with key: {image_s3_key}")
        
        # Create issue in database (store S3 key, not URL)
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
            photo_url=image_s3_key,  # Store S3 key
            status="reported"
        )
        
        db.add(new_issue)
        db.commit()
        db.refresh(new_issue)
        
        logger.info(f"Issue created successfully with ID: {custom_id}")
        
        # Generate temporary URL for response
        temp_image_url = None
        if image_s3_key:
            temp_image_url = s3_service.generate_presigned_url(image_s3_key, expiration=14400)
        
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
                "image_url": temp_image_url,  # Temporary presigned URL
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
        if image_s3_key:
            logger.warning(f"Cleaning up uploaded file due to error: {image_s3_key}")
            s3_service.delete_file(image_s3_key)
        
        logger.error(f"Error creating issue: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create issue: {str(e)}")
