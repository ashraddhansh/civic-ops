from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models import User, OTPVerification, UserToken
from app.core.security import generate_otp, create_jwt, create_refresh_token, verify_jwt
from app.services.otp_service import OTPService
from app.config import OTP_EXPIRATION_MINUTES, JWT_EXPIRATION_MINUTES, REFRESH_TOKEN_EXPIRATION_DAYS
import uuid

class AuthService:
    @staticmethod
    def send_otp(phone: str = None, email: str = None, db: Session = None):
        if not phone and not email:
            raise ValueError("Either phone or email is required")
        
        if email:
            raise ValueError("Email authentication not implemented yet")
            
        otp = generate_otp()
        expires_at = datetime.utcnow() + timedelta(minutes=OTP_EXPIRATION_MINUTES)
        retry_after = datetime.utcnow() + timedelta(seconds=60)

        # Check for existing OTP that's still in retry period
        existing_otp = db.query(OTPVerification).filter_by(phone_number=phone).first()
        if existing_otp and existing_otp.retry_after and existing_otp.retry_after > datetime.utcnow():
            remaining_time = int((existing_otp.retry_after - datetime.utcnow()).total_seconds())
            raise ValueError(f"Please wait {remaining_time} seconds before requesting another OTP")

        # Save or update OTP in DB
        if existing_otp:
            existing_otp.otp = otp
            existing_otp.expires_at = expires_at
            existing_otp.retry_after = retry_after
        else:
            otp_entry = OTPVerification(
                phone_number=phone,
                otp=otp,
                expires_at=expires_at,
                retry_after=retry_after
            )
            db.add(otp_entry)
        db.commit()

        # Send OTP
        OTPService.send_otp_sms(phone, otp)
        
        return {
            "success": True,
            "message": "OTP sent successfully",
            "data": {
                "expires_in": OTP_EXPIRATION_MINUTES * 60,
                "retry_after": 60
            }
        }

    @staticmethod
    def verify_otp(phone: str = None, email: str = None, otp: str = None, db: Session = None):
        if not phone and not email:
            raise ValueError("Either phone or email is required")
        
        if email:
            raise ValueError("Email authentication not implemented yet")

        # Verify OTP
        otp_entry = db.query(OTPVerification).filter_by(phone_number=phone, otp=otp).first()
        if not otp_entry or otp_entry.expires_at < datetime.utcnow():
            raise ValueError("Invalid or expired OTP")

        # Check if user exists
        user = db.query(User).filter_by(phone_number=phone).first()
        user_exists = user is not None
        
        # Create new user if doesn't exist
        if not user:
            user = User(
                id=str(uuid.uuid4()),
                phone_number=phone,
                is_profile_complete=False
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        # Generate tokens
        access_token = create_jwt(user.user_id, 60)  # 1 hour for incomplete profile
        refresh_token = create_refresh_token()
        
        # If user profile is complete, give normal token expiry
        if user.is_profile_complete:
            access_token = create_jwt(user.user_id)
        
        expires_at = datetime.utcnow() + timedelta(minutes=60 if not user.is_profile_complete else JWT_EXPIRATION_MINUTES)
        refresh_expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRATION_DAYS)

        # Save tokens
        user_token = UserToken(
            user_id=user.user_id,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
            refresh_expires_at=refresh_expires_at
        )
        db.add(user_token)
        
        # Clean up OTP
        db.delete(otp_entry)
        db.commit()

        response_data = {
            "user_exists": user_exists and user.is_profile_complete,
            "session": {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expires_at": expires_at.isoformat() + "Z"
            }
        }

        # Include user data if profile is complete
        if user.is_profile_complete:
            response_data["user"] = {
                "id": user.id,
                "phone": user.phone_number,
                "full_name": user.full_name,
                "created_at": user.created_at.isoformat() + "Z"
            }

        return {
            "success": True,
            "message": "OTP verified successfully",
            "data": response_data
        }

    @staticmethod
    def complete_profile(user_id: int, full_name: str, db: Session):
        user = db.query(User).filter_by(user_id=user_id).first()
        if not user:
            raise ValueError("User not found")

        user.full_name = full_name
        user.is_profile_complete = True
        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)

        return {
            "success": True,
            "message": "Profile completed successfully",
            "data": {
                "user": {
                    "id": user.id,
                    "phone": user.phone_number,
                    "full_name": user.full_name,
                    "created_at": user.created_at.isoformat() + "Z",
                    "updated_at": user.updated_at.isoformat() + "Z"
                }
            }
        }

    @staticmethod
    def refresh_access_token(refresh_token: str, db: Session):
        token_entry = db.query(UserToken).filter_by(refresh_token=refresh_token).first()
        if not token_entry or token_entry.refresh_expires_at < datetime.utcnow():
            raise ValueError("Invalid or expired refresh token")

        # Generate new access token
        new_access_token = create_jwt(token_entry.user_id)
        new_expires_at = datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION_MINUTES)
        
        # Update token entry
        token_entry.access_token = new_access_token
        token_entry.expires_at = new_expires_at
        db.commit()

        return {
            "success": True,
            "data": {
                "access_token": new_access_token,
                "expires_at": new_expires_at.isoformat() + "Z"
            }
        }

    @staticmethod
    def logout_user(token: str, db: Session):
        db_token = db.query(UserToken).filter_by(access_token=token).first()
        if db_token:
            db.delete(db_token)
            db.commit()
            return {
                "success": True,
                "message": "Logged out successfully"
            }
        raise ValueError("Invalid token")

    @staticmethod
    def update_profile(user_id: int, full_name: str, db: Session):
        user = db.query(User).filter_by(user_id=user_id).first()
        if not user:
            raise ValueError("User not found")

        user.full_name = full_name
        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)

        return {
            "success": True,
            "message": "Profile updated successfully",
            "data": {
                "user": {
                    "id": user.id,
                    "phone": user.phone_number,
                    "full_name": user.full_name,
                    "created_at": user.created_at.isoformat() + "Z",
                    "updated_at": user.updated_at.isoformat() + "Z"
                }
            }
        }

    # Keep old methods for backward compatibility
    @staticmethod
    def initiate_login(phone_number: str, db: Session):
        return AuthService.send_otp(phone=phone_number, db=db)

    @staticmethod
    def verify_otp_and_login(phone_number: str, otp: str, name: str, db: Session):
        # Verify OTP
        otp_entry = db.query(OTPVerification).filter_by(phone_number=phone_number, otp=otp).first()
        if not otp_entry or otp_entry.expires_at < datetime.utcnow():
            raise ValueError("Invalid or expired OTP")

        # Get or create user
        user = db.query(User).filter_by(phone_number=phone_number).first()
        if not user:
            if not name:
                raise ValueError("Name required for new user")
            user = User(
                id=str(uuid.uuid4()),
                phone_number=phone_number,
                name=name,
                full_name=name,
                is_profile_complete=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        # Generate token
        token = create_jwt(user.user_id)
        expires_at = datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION_MINUTES)
        user_token = UserToken(
            user_id=user.user_id,
            access_token=token,
            expires_at=expires_at
        )
        db.add(user_token)
        
        # Clean up OTP
        db.delete(otp_entry)
        db.commit()

        return {"token": token, "user_id": user.user_id, "name": user.name or user.full_name}
