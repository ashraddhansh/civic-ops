from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.core.dependencies import get_db
from app.core.admin_dependencies import get_current_admin, get_department_admin, get_super_admin
from app.models import Issue, User, AdminUser, Department
from app.schemas.admin import (
    AdminLoginRequest, AdminLoginResponse, AdminUserResponse,
    CreateAdminRequest, UpdateIssueStatusRequest
)
from app.services.admin_auth_service import admin_auth_service
from app.services.s3_service import s3_service
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

def extract_s3_key_from_url(url: str) -> str:
    """Extract S3 key from full S3 URL"""
    try:
        if "amazonaws.com/" in url:
            return url.split("amazonaws.com/")[1].split("?")[0]
        return url
    except:
        return url

router = APIRouter(prefix="/admin", tags=["admin"])

# Note: In a real application, you'd want proper admin authentication
# For now, we'll create these endpoints without authentication for the prototype

@router.get("/issues", response_model=List[AdminIssueResponse])
def get_all_issues(
    status: Optional[str] = Query(None, description="Filter by status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(50, le=100, description="Limit number of results"),
    offset: int = Query(0, description="Offset for pagination"),
    db: Session = Depends(get_db)
):
    """Get all issues with optional filtering (admin only)"""
    query = db.query(Issue)
    
    if status:
        query = query.filter(Issue.status == status)
    if priority:
        query = query.filter(Issue.priority == priority)
    if category:
        query = query.filter(Issue.category == category)
    
    issues = query.order_by(Issue.created_at.desc()).offset(offset).limit(limit).all()
    return issues

@router.get("/issues/{issue_id}", response_model=AdminIssueResponse)
def get_issue_admin(issue_id: int, db: Session = Depends(get_db)):
    """Get specific issue details (admin view)"""
    issue = db.query(Issue).filter(Issue.issue_id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    return issue

@router.patch("/issues/{issue_id}", response_model=AdminIssueResponse)
def update_issue_admin(
    issue_id: int,
    update_data: AdminIssueUpdate,
    db: Session = Depends(get_db)
):
    """Update issue status and/or priority (admin only)"""
    issue = db.query(Issue).filter(Issue.issue_id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    # Validate status if provided
    if update_data.status:
        valid_statuses = ["pending", "in_progress", "resolved", "rejected"]
        if update_data.status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        issue.status = update_data.status
    
    # Validate priority if provided
    if update_data.priority:
        valid_priorities = ["unassigned", "low", "medium", "high", "urgent"]
        if update_data.priority not in valid_priorities:
            raise HTTPException(status_code=400, detail=f"Invalid priority. Must be one of: {', '.join(valid_priorities)}")
        issue.priority = update_data.priority
    
    db.commit()
    db.refresh(issue)
    return issue

@router.get("/issues/stats/summary")
def get_issues_stats(db: Session = Depends(get_db)):
    """Get summary statistics of all issues"""
    total_issues = db.query(Issue).count()
    
    # Status breakdown
    status_stats = {}
    statuses = ["pending", "in_progress", "resolved", "rejected"]
    for status in statuses:
        status_stats[status] = db.query(Issue).filter(Issue.status == status).count()
    
    # Priority breakdown
    priority_stats = {}
    priorities = ["unassigned", "low", "medium", "high", "urgent"]
    for priority in priorities:
        priority_stats[priority] = db.query(Issue).filter(Issue.priority == priority).count()
    
    # Category breakdown
    category_stats = {}
    categories = ["road", "water", "electricity", "waste", "public_safety", "infrastructure", "other"]
    for category in categories:
        category_stats[category] = db.query(Issue).filter(Issue.category == category).count()
    
    return {
        "total_issues": total_issues,
        "by_status": status_stats,
        "by_priority": priority_stats,
        "by_category": category_stats
    }
