from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Enhanced schemas for new API
class LocationData(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    address: str

class EnhancedIssueCreate(BaseModel):
    title: Optional[str] = None  # Will be auto-generated if not provided
    category: str = Field(..., description="Main category like 'Road & Transport'")
    subcategory: str = Field(..., description="Subcategory like 'Potholes'")
    description: str = Field(..., min_length=10, description="Detailed description")
    location: LocationData

class ReportedBy(BaseModel):
    id: str
    name: str
    phone: str

class EnhancedIssueResponse(BaseModel):
    success: bool
    message: str
    data: dict

# Keep existing schemas for backward compatibility
class IssueCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=200, description="Brief title of the issue")
    description: str = Field(..., min_length=10, description="Detailed description of the issue")
    category: str = Field(..., description="Category of the issue")
    location: Optional[str] = Field(None, max_length=500, description="Address or location description")
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="GPS latitude")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="GPS longitude")

class IssueCreateWithFiles(BaseModel):
    """For form data with file uploads"""
    title: str
    description: str
    category: str
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class IssueUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=200)
    description: Optional[str] = Field(None, min_length=10)
    category: Optional[str] = None
    location: Optional[str] = Field(None, max_length=500)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)

class IssueResponse(BaseModel):
    issue_id: int
    title: str
    description: str
    category: str
    location: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    photo_url: Optional[str]
    voice_note_url: Optional[str]
    status: str
    priority: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class IssueListResponse(BaseModel):
    issue_id: int
    title: str
    category: str
    status: str
    priority: str
    created_at: datetime
    location: Optional[str]

    class Config:
        from_attributes = True

# Admin-only schemas
class AdminIssueUpdate(BaseModel):
    status: Optional[str] = Field(None, description="Issue status (admin-only)")
    priority: Optional[str] = Field(None, description="Issue priority (admin-only)")

class AdminIssueResponse(BaseModel):
    issue_id: int
    user_id: int
    title: str
    description: str
    category: str
    location: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    photo_url: Optional[str]
    voice_note_url: Optional[str]
    status: str
    priority: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
