from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SendOTPRequest(BaseModel):
    phone: Optional[str] = None
    email: Optional[str] = None

class VerifyOTPRequest(BaseModel):
    phone: Optional[str] = None
    email: Optional[str] = None
    otp: str

class CompleteProfileRequest(BaseModel):
    full_name: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class UpdateProfileRequest(BaseModel):
    full_name: str

class SessionData(BaseModel):
    access_token: str
    refresh_token: str
    expires_at: datetime

class UserData(BaseModel):
    id: str
    email: Optional[str] = None
    phone: Optional[str] = None
    full_name: Optional[str] = None
    created_at: datetime

class SendOTPResponse(BaseModel):
    success: bool
    message: str
    data: dict

class VerifyOTPResponse(BaseModel):
    success: bool
    message: str
    data: dict

class CompleteProfileResponse(BaseModel):
    success: bool
    message: str
    data: dict

class RefreshTokenResponse(BaseModel):
    success: bool
    data: dict

class LogoutResponse(BaseModel):
    success: bool
    message: str

class UpdateProfileResponse(BaseModel):
    success: bool
    message: str
    data: dict

# Keep old schemas for backward compatibility
class LoginRequest(BaseModel):
    phone_number: str

class OTPVerificationRequest(BaseModel):
    phone_number: str
    otp: str
    name: Optional[str] = None

class LoginResponse(BaseModel):
    token: str
    user_id: int
    name: str
