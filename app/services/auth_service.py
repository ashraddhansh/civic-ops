from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models import User, OTPVerification, UserToken
from app.core.security import generate_otp, create_jwt
from app.services.otp_service import OTPService
from app.config import OTP_EXPIRATION_MINUTES, JWT_EXPIRATION_MINUTES

class AuthService:
    @staticmethod
    def initiate_login(phone_number: str, db: Session):
        otp = generate_otp()
        expires_at = datetime.utcnow() + timedelta(minutes=OTP_EXPIRATION_MINUTES)

        # Save OTP to DB
        otp_entry = db.query(OTPVerification).filter_by(phone_number=phone_number).first()
        if otp_entry:
            otp_entry.otp = otp
            otp_entry.expires_at = expires_at
        else:
            otp_entry = OTPVerification(phone_number=phone_number, otp=otp, expires_at=expires_at)
            db.add(otp_entry)
        db.commit()

        # Send OTP
        OTPService.send_otp_sms(phone_number, otp)
        return {"message": "OTP sent successfully"}

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
            user = User(phone_number=phone_number, name=name)
            db.add(user)
            db.commit()
            db.refresh(user)

        # Generate token
        token = create_jwt(user.user_id)
        expires_at = datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION_MINUTES)
        user_token = UserToken(user_id=user.user_id, token=token, expires_at=expires_at)
        db.add(user_token)
        
        # Clean up OTP
        db.delete(otp_entry)
        db.commit()

        return {"token": token, "user_id": user.user_id, "name": user.name}

    @staticmethod
    def logout_user(token: str, db: Session):
        db_token = db.query(UserToken).filter_by(token=token).first()
        if db_token:
            db.delete(db_token)
            db.commit()
            return {"message": "Logged out successfully"}
        raise ValueError("Invalid token")
