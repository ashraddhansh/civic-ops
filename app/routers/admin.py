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

# Authentication endpoints
@router.post("/login", response_model=AdminLoginResponse)
async def admin_login(
    login_data: AdminLoginRequest,
    db: Session = Depends(get_db)
):
    """Admin login endpoint"""
    try:
        # Authenticate admin
        admin = admin_auth_service.authenticate_admin(
            login_data.username, 
            login_data.password, 
            db
        )
        
        # Create JWT token
        token = admin_auth_service.create_admin_token(admin)
        
        return {
            "success": True,
            "message": "Login successful",
            "data": {
                "access_token": token,
                "admin": {
                    "id": admin.id,
                    "username": admin.username,
                    "full_name": admin.full_name,
                    "role": admin.role,
                    "department_id": admin.department_id,
                    "department_name": admin.department.name if admin.department else None
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin login error: {str(e)}")
        raise HTTPException(status_code=500, detail="Login failed")

# Department-specific issue endpoints
@router.get("/issues")
async def get_department_issues(
    status: Optional[str] = Query(None, description="Filter by status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    category: Optional[str] = Query(None, description="Filter by category"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_admin: AdminUser = Depends(get_department_admin),
    db: Session = Depends(get_db)
):
    """Get issues for admin's department"""
    try:
        offset = (page - 1) * limit
        
        # Base query for department issues
        query = db.query(Issue).filter(Issue.department_id == current_admin.department_id)
        
        # Apply filters
        if status:
            query = query.filter(Issue.status == status)
        if priority:
            query = query.filter(Issue.priority == priority)
        if category:
            query = query.filter(Issue.category == category)
        
        # Get total count
        total = query.count()
        
        # Get paginated results
        issues = query.order_by(Issue.created_at.desc()).offset(offset).limit(limit).all()
        
        # Format response with fresh presigned URLs
        formatted_issues = []
        for issue in issues:
            # Generate fresh presigned URL for image
            image_url = None
            if issue.photo_url:
                try:
                    if issue.photo_url.startswith('https://'):
                        s3_key = extract_s3_key_from_url(issue.photo_url)
                    else:
                        s3_key = issue.photo_url
                    image_url = s3_service.generate_presigned_url(s3_key, expiration=14400)
                except Exception as e:
                    logger.warning(f"Failed to generate presigned URL: {str(e)}")
            
            # Generate fresh presigned URL for voice note
            voice_note_url = None
            if issue.voice_note_url:
                try:
                    if issue.voice_note_url.startswith('https://'):
                        s3_key = extract_s3_key_from_url(issue.voice_note_url)
                    else:
                        s3_key = issue.voice_note_url
                    voice_note_url = s3_service.generate_presigned_url(s3_key, expiration=14400)
                except Exception as e:
                    logger.warning(f"Failed to generate presigned URL for voice note: {str(e)}")
            
            # Get user info
            user = db.query(User).filter(User.user_id == issue.user_id).first()
            
            formatted_issue = {
                "issue_id": issue.custom_id if issue.custom_id else str(issue.issue_id),
                "title": issue.title,
                "description": issue.description,
                "category": issue.category,
                "subcategory": issue.subcategory or "",
                "status": issue.status,
                "priority": issue.priority or "unassigned",
                "address": issue.location or "Location not specified",
                "latitude": issue.latitude,
                "longitude": issue.longitude,
                "image_url": image_url,
                "voice_note_url": voice_note_url,
                "reported_by": {
                    "user_id": str(user.user_id) if user else "unknown",
                    "name": user.full_name or user.name if user else "Unknown User",
                    "phone_number": user.phone_number if user else "N/A",
                    "email": user.email if user and user.email else "N/A"
                },
                "department_id": issue.department_id,
                "created_at": issue.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "updated_at": issue.updated_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ") if issue.updated_at else None
            }
            formatted_issues.append(formatted_issue)
        
        return {
            "success": True,
            "message": "Issues retrieved successfully",
            "data": {
                "issues": formatted_issues,
                "total": total,
                "page": page,
                "limit": limit,
                "department": {
                    "id": current_admin.department.id,
                    "name": current_admin.department.name
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching department issues: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch issues")

@router.get("/issues/locations")
async def get_department_issue_locations(
    status: Optional[str] = Query(None, description="Filter by status (reported, in_progress, resolved, etc.)"),
    priority: Optional[str] = Query(None, description="Filter by priority (unassigned, low, medium, high, urgent)"),
    category: Optional[str] = Query(None, description="Filter by category"),
    current_admin: AdminUser = Depends(get_department_admin),
    db: Session = Depends(get_db)
):
    """
    Get latitude and longitude coordinates of all issues for admin's department
    This endpoint is designed for plotting issues on maps/graphs
    """
    try:
        # Base query for department issues with coordinates
        query = db.query(Issue).filter(
            Issue.department_id == current_admin.department_id,
            Issue.latitude.isnot(None),  # Only include issues with coordinates
            Issue.longitude.isnot(None)
        )
        
        # Apply filters if provided
        if status:
            query = query.filter(Issue.status == status)
        if priority:
            query = query.filter(Issue.priority == priority)
        if category:
            query = query.filter(Issue.category == category)
        
        # Get all matching issues
        issues = query.order_by(Issue.created_at.desc()).all()
        
        # Format response for map plotting
        issue_locations = []
        for issue in issues:
            # Get user info for popup details
            user = db.query(User).filter(User.user_id == issue.user_id).first()
            
            location_data = {
                "issue_id": issue.custom_id if issue.custom_id else str(issue.issue_id),
                "latitude": float(issue.latitude),
                "longitude": float(issue.longitude),
                "title": issue.title,
                "category": issue.category,
                "subcategory": issue.subcategory or "",
                "status": issue.status,
                "priority": issue.priority or "unassigned",
                "address": issue.location or "Address not specified",
                "reported_by": user.full_name if user else "Unknown User",
                "reporter_phone": user.phone_number if user else "N/A",
                "created_at": issue.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "description": issue.description[:100] + "..." if len(issue.description) > 100 else issue.description  # Truncated for map popup
            }
            issue_locations.append(location_data)
        
        # Get department info
        department = db.query(Department).filter(Department.id == current_admin.department_id).first()
        
        # Calculate some statistics
        total_issues = len(issue_locations)
        status_counts = {}
        priority_counts = {}
        
        for issue in issue_locations:
            # Count by status
            status = issue['status']
            status_counts[status] = status_counts.get(status, 0) + 1
            
            # Count by priority
            priority = issue['priority']
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        return {
            "success": True,
            "message": "Issue locations retrieved successfully",
            "data": {
                "department": {
                    "id": department.id,
                    "name": department.name
                },
                "locations": issue_locations,
                "statistics": {
                    "total_issues": total_issues,
                    "status_breakdown": status_counts,
                    "priority_breakdown": priority_counts
                },
                "map_bounds": {
                    "north": max([loc['latitude'] for loc in issue_locations]) if issue_locations else None,
                    "south": min([loc['latitude'] for loc in issue_locations]) if issue_locations else None,
                    "east": max([loc['longitude'] for loc in issue_locations]) if issue_locations else None,
                    "west": min([loc['longitude'] for loc in issue_locations]) if issue_locations else None
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching issue locations for department {current_admin.department_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch issue locations")

@router.get("/issues/heatmap")
async def get_department_issue_heatmap(
    status: Optional[str] = Query(None, description="Filter by status"),
    days: int = Query(30, ge=1, le=365, description="Number of days to look back (default: 30)"),
    current_admin: AdminUser = Depends(get_department_admin),
    db: Session = Depends(get_db)
):
    """
    Get heatmap data for issues in the department
    Returns simplified coordinate data for density mapping
    """
    try:
        from datetime import datetime, timedelta
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Query for heatmap data
        query = db.query(Issue.latitude, Issue.longitude, Issue.status, Issue.created_at).filter(
            Issue.department_id == current_admin.department_id,
            Issue.latitude.isnot(None),
            Issue.longitude.isnot(None),
            Issue.created_at >= start_date
        )
        
        if status:
            query = query.filter(Issue.status == status)
        
        issues = query.all()
        
        # Format for heatmap (simple lat/lng pairs with weight)
        heatmap_data = []
        for issue in issues:
            heatmap_data.append({
                "lat": float(issue.latitude),
                "lng": float(issue.longitude),
                "weight": 1.0,  # Can be adjusted based on priority or other factors
                "status": issue.status
            })
        
        return {
            "success": True,
            "message": "Heatmap data retrieved successfully",
            "data": {
                "heatmap_points": heatmap_data,
                "total_points": len(heatmap_data),
                "date_range": {
                    "start": start_date.strftime("%Y-%m-%d"),
                    "end": end_date.strftime("%Y-%m-%d"),
                    "days": days
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating heatmap data: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate heatmap data")

@router.get("/issues/{issue_id}")
async def get_department_issue(
    issue_id: str,
    current_admin: AdminUser = Depends(get_department_admin),
    db: Session = Depends(get_db)
):
    """Get specific issue for admin's department"""
    try:
        # Try to find issue by custom_id or numeric id
        issue = None
        if issue_id.startswith('CIV'):
            issue = db.query(Issue).filter(
                and_(
                    Issue.custom_id == issue_id,
                    Issue.department_id == current_admin.department_id
                )
            ).first()
        else:
            try:
                issue_id_int = int(issue_id)
                issue = db.query(Issue).filter(
                    and_(
                        Issue.issue_id == issue_id_int,
                        Issue.department_id == current_admin.department_id
                    )
                ).first()
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid issue ID format")
        
        if not issue:
            raise HTTPException(status_code=404, detail="Issue not found")
        
        # Generate fresh presigned URL for image
        image_url = None
        if issue.photo_url:
            try:
                if issue.photo_url.startswith('https://'):
                    s3_key = extract_s3_key_from_url(issue.photo_url)
                else:
                    s3_key = issue.photo_url
                image_url = s3_service.generate_presigned_url(s3_key, expiration=14400)
            except Exception as e:
                logger.warning(f"Failed to generate presigned URL: {str(e)}")
        
        # Generate fresh presigned URL for voice note
        voice_note_url = None
        if issue.voice_note_url:
            try:
                if issue.voice_note_url.startswith('https://'):
                    s3_key = extract_s3_key_from_url(issue.voice_note_url)
                else:
                    s3_key = issue.voice_note_url
                voice_note_url = s3_service.generate_presigned_url(s3_key, expiration=14400)
            except Exception as e:
                logger.warning(f"Failed to generate presigned URL for voice note: {str(e)}")
        
        # Get user info
        user = db.query(User).filter(User.user_id == issue.user_id).first()
        
        response_data = {
            "success": True,
            "message": "Issue retrieved successfully",
            "data": {
                "issue": {
                    "issue_id": issue.custom_id if issue.custom_id else str(issue.issue_id),
                    "title": issue.title,
                    "description": issue.description,
                    "category": issue.category,
                    "subcategory": issue.subcategory or "",
                    "status": issue.status,
                    "priority": issue.priority or "unassigned",
                    "address": issue.location or "Location not specified",
                    "latitude": issue.latitude,
                    "longitude": issue.longitude,
                    "image_url": image_url,
                    "voice_note_url": voice_note_url,
                    "reported_by": {
                        "user_id": str(user.user_id) if user else "unknown",
                        "name": user.full_name or user.name if user else "Unknown User",
                        "phone_number": user.phone_number if user else "N/A",
                        "email": user.email if user and user.email else "N/A"
                    },
                    "department_id": issue.department_id,
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

@router.patch("/issues/{issue_id}/status")
async def update_issue_status(
    issue_id: str,
    update_data: UpdateIssueStatusRequest,
    current_admin: AdminUser = Depends(get_department_admin),
    db: Session = Depends(get_db)
):
    """Update issue status and priority"""
    try:
        # Find issue
        issue = None
        if issue_id.startswith('CIV'):
            issue = db.query(Issue).filter(
                and_(
                    Issue.custom_id == issue_id,
                    Issue.department_id == current_admin.department_id
                )
            ).first()
        else:
            try:
                issue_id_int = int(issue_id)
                issue = db.query(Issue).filter(
                    and_(
                        Issue.issue_id == issue_id_int,
                        Issue.department_id == current_admin.department_id
                    )
                ).first()
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid issue ID format")
        
        if not issue:
            raise HTTPException(status_code=404, detail="Issue not found")
        
        # Validate status
        valid_statuses = ["reported", "in_progress", "resolved", "rejected"]
        if update_data.status not in valid_statuses:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )
        
        # Validate priority if provided
        if update_data.priority:
            valid_priorities = ["unassigned", "low", "medium", "high", "urgent"]
            if update_data.priority not in valid_priorities:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid priority. Must be one of: {', '.join(valid_priorities)}"
                )
        
        # Update issue
        issue.status = update_data.status
        if update_data.priority:
            issue.priority = update_data.priority
        
        db.commit()
        db.refresh(issue)
        
        return {
            "success": True,
            "message": "Issue updated successfully",
            "data": {
                "issue_id": issue.custom_id if issue.custom_id else str(issue.issue_id),
                "status": issue.status,
                "priority": issue.priority,
                "updated_by": current_admin.username
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating issue {issue_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update issue")

# Super admin endpoints
@router.post("/users/create")
async def create_admin_user(
    admin_data: CreateAdminRequest,
    current_admin: AdminUser = Depends(get_super_admin),
    db: Session = Depends(get_db)
):
    """Create new admin user (super admin only)"""
    try:
        new_admin = admin_auth_service.create_admin_user(
            username=admin_data.username,
            email=admin_data.email,
            password=admin_data.password,
            full_name=admin_data.full_name,
            department_id=admin_data.department_id,
            role=admin_data.role,
            db=db
        )
        
        return {
            "success": True,
            "message": "Admin user created successfully",
            "data": {
                "admin": {
                    "id": new_admin.id,
                    "username": new_admin.username,
                    "email": new_admin.email,
                    "full_name": new_admin.full_name,
                    "role": new_admin.role,
                    "department_id": new_admin.department_id
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating admin user: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create admin user")

@router.get("/departments")
async def get_departments(
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all departments"""
    departments = db.query(Department).filter(Department.is_active == True).all()
    
    return {
        "success": True,
        "message": "Departments retrieved successfully",
        "data": {
            "departments": [
                {
                    "id": dept.id,
                    "name": dept.name,
                    "code": dept.code,
                    "description": dept.description
                }
                for dept in departments
            ]
        }
    }

@router.get("/profile")
async def get_admin_profile(
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Get current admin profile"""
    return {
        "success": True,
        "message": "Profile retrieved successfully",
        "data": {
            "admin": {
                "id": current_admin.id,
                "username": current_admin.username,
                "full_name": current_admin.full_name,
                "email": current_admin.email,
                "role": current_admin.role,
                "department": {
                    "id": current_admin.department.id,
                    "name": current_admin.department.name,
                    "code": current_admin.department.code
                } if current_admin.department else None,
                "last_login": current_admin.last_login.strftime("%Y-%m-%dT%H:%M:%S.%fZ") if current_admin.last_login else None
            }
        }
    }

@router.get("/stats/summary")
async def get_department_stats(
    current_admin: AdminUser = Depends(get_department_admin),
    db: Session = Depends(get_db)
):
    """Get issue statistics for admin's department"""
    try:
        # Get total issues for department
        total_issues = db.query(Issue).filter(Issue.department_id == current_admin.department_id).count()
        
        # Get issues by status
        reported = db.query(Issue).filter(
            Issue.department_id == current_admin.department_id,
            Issue.status == "reported"
        ).count()
        
        in_progress = db.query(Issue).filter(
            Issue.department_id == current_admin.department_id,
            Issue.status == "in_progress"
        ).count()
        
        resolved = db.query(Issue).filter(
            Issue.department_id == current_admin.department_id,
            Issue.status == "resolved"
        ).count()
        
        rejected = db.query(Issue).filter(
            Issue.department_id == current_admin.department_id,
            Issue.status == "rejected"
        ).count()
        
        # Get issues by priority
        urgent = db.query(Issue).filter(
            Issue.department_id == current_admin.department_id,
            Issue.priority == "urgent"
        ).count()
        
        high = db.query(Issue).filter(
            Issue.department_id == current_admin.department_id,
            Issue.priority == "high"
        ).count()
        
        return {
            "success": True,
            "message": "Statistics retrieved successfully",
            "data": {
                "department": {
                    "id": current_admin.department.id,
                    "name": current_admin.department.name
                },
                "summary": {
                    "total_issues": total_issues,
                    "by_status": {
                        "reported": reported,
                        "in_progress": in_progress,
                        "resolved": resolved,
                        "rejected": rejected
                    },
                    "by_priority": {
                        "urgent": urgent,
                        "high": high,
                        "medium": total_issues - urgent - high,
                        "unassigned": db.query(Issue).filter(
                            Issue.department_id == current_admin.department_id,
                            Issue.priority == "unassigned"
                        ).count()
                    }
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching department stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch statistics")