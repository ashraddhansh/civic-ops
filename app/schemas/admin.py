from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class AdminLoginRequest(BaseModel):
    username: str
    password: str

class AdminLoginResponse(BaseModel):
    success: bool
    message: str
    data: dict

class AdminUserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    role: str
    department_id: int
    department_name: str
    is_active: bool
    last_login: Optional[datetime]
    created_at: datetime

class DepartmentResponse(BaseModel):
    id: int
    name: str
    code: str
    description: Optional[str]
    is_active: bool

class CreateAdminRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str
    department_id: int
    role: str = "admin"

class AdminIssueResponse(BaseModel):
    id: str
    title: str
    category: str
    subcategory: str
    description: str
    status: str
    priority: str
    location: dict
    image_url: Optional[str]
    voice_note_url: Optional[str]
    reported_by: dict
    department_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UpdateIssueStatusRequest(BaseModel):
    status: str
    priority: Optional[str] = None