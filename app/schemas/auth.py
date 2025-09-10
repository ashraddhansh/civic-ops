from pydantic import BaseModel
from typing import Optional

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

class LogoutResponse(BaseModel):
    message: str
