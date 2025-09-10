from fastapi import APIRouter, HTTPException, Depends, Header
from sqlalchemy.orm import Session
from app.core.dependencies import get_db
from app.services.auth_service import AuthService
from app.schemas.auth import LoginRequest, OTPVerificationRequest, LoginResponse, LogoutResponse

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/send-otp")
def send_otp(request: LoginRequest, db: Session = Depends(get_db)):
    try:
        return AuthService.initiate_login(request.phone_number, db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    try:
        return AuthService.initiate_login(request.phone_number, db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/verify-otp", response_model=LoginResponse)
def verify_otp(request: OTPVerificationRequest, db: Session = Depends(get_db)):
    try:
        return AuthService.verify_otp_and_login(
            request.phone_number, request.otp, request.name, db
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/logout", response_model=LogoutResponse)
def logout(authorization: str = Header(...), db: Session = Depends(get_db)):
    try:
        token = authorization.replace("Bearer ", "")
        return AuthService.logout_user(token, db)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
