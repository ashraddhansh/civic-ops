from fastapi import APIRouter, HTTPException, Depends, Header
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user
from app.services.auth_service import AuthService
from app.schemas.auth import (
    SendOTPRequest, VerifyOTPRequest, CompleteProfileRequest, 
    RefreshTokenRequest, UpdateProfileRequest,
    SendOTPResponse, VerifyOTPResponse, CompleteProfileResponse,
    RefreshTokenResponse, LogoutResponse, UpdateProfileResponse,
    LoginRequest, OTPVerificationRequest, LoginResponse  # Keep old schemas
)

router = APIRouter(prefix="/auth", tags=["authentication"])

# New API endpoints
@router.post("/send-otp", response_model=SendOTPResponse)
def send_otp(request: SendOTPRequest, db: Session = Depends(get_db)):
    try:
        return AuthService.send_otp(
            phone=request.phone,
            email=request.email,
            db=db
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/verify-otp", response_model=VerifyOTPResponse)
def verify_otp_new(request: VerifyOTPRequest, db: Session = Depends(get_db)):
    try:
        return AuthService.verify_otp(
            phone=request.phone,
            email=request.email,
            otp=request.otp,
            db=db
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/complete-profile", response_model=CompleteProfileResponse)
def complete_profile(
    request: CompleteProfileRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        return AuthService.complete_profile(
            user_id=current_user.user_id,
            full_name=request.full_name,
            db=db
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/refresh", response_model=RefreshTokenResponse)
def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    try:
        return AuthService.refresh_access_token(
            refresh_token=request.refresh_token,
            db=db
        )
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.post("/logout", response_model=LogoutResponse)
def logout_new(authorization: str = Header(...), db: Session = Depends(get_db)):
    try:
        token = authorization.replace("Bearer ", "")
        return AuthService.logout_user(token, db)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.put("/profile", response_model=UpdateProfileResponse)
def update_profile(
    request: UpdateProfileRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        return AuthService.update_profile(
            user_id=current_user.user_id,
            full_name=request.full_name,
            db=db
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Keep old endpoints for backward compatibility
@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    try:
        return AuthService.initiate_login(request.phone_number, db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/verify-otp-old", response_model=LoginResponse)
def verify_otp_old(request: OTPVerificationRequest, db: Session = Depends(get_db)):
    try:
        return AuthService.verify_otp_and_login(
            request.phone_number, request.otp, request.name, db
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/logout-old", response_model=dict)
def logout_old(authorization: str = Header(...), db: Session = Depends(get_db)):
    try:
        token = authorization.replace("Bearer ", "")
        return AuthService.logout_user(token, db)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
