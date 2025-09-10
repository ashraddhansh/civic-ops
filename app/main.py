from fastapi import FastAPI, HTTPException, Depends, Header
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User, OTPVerification, UserToken, Issue
from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, JWT_SECRET, JWT_EXPIRATION_MINUTES, OTP_EXPIRATION_MINUTES

from twilio.rest import Client
from datetime import datetime, timedelta
import random
import jwt

app = FastAPI()

# ---------------- DB Dependency ----------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------- Twilio Helper ----------------
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def send_otp_sms(phone_number: str, otp: str):
    # For trial/testing, ensure recipient number is verified
    message = client.messages.create(
        body=f"Your OTP is {otp}",
        from_=TWILIO_PHONE_NUMBER,
        to=phone_number
    )
    return message.sid

# ---------------- JWT Helpers ----------------
def generate_otp():
    return f"{random.randint(100000, 999999)}"

def create_jwt(user_id: int):
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION_MINUTES)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return token

def verify_jwt(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload["user_id"]
    except jwt.ExpiredSignatureError:
        return None
    except jwt.JWTError:
        return None

# ---------------- Auth Endpoints ----------------
@app.post("/login")
def login(phone_number: str, db: Session = Depends(get_db)):
    otp = generate_otp()
    expires_at = datetime.utcnow() + timedelta(minutes=OTP_EXPIRATION_MINUTES)

    # Save OTP to DB (update if exists)
    otp_entry = db.query(OTPVerification).filter_by(phone_number=phone_number).first()
    if otp_entry:
        otp_entry.otp = otp
        otp_entry.expires_at = expires_at
    else:
        otp_entry = OTPVerification(phone_number=phone_number, otp=otp, expires_at=expires_at)
        db.add(otp_entry)
    db.commit()

    # Send OTP via Twilio
    send_otp_sms(phone_number, otp)
    return {"message": "OTP sent successfully"}

@app.post("/verify-otp")
def verify_otp(phone_number: str, otp: str, name: str = None, db: Session = Depends(get_db)):
    otp_entry = db.query(OTPVerification).filter_by(phone_number=phone_number, otp=otp).first()
    if not otp_entry or otp_entry.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    # Check if user exists
    user = db.query(User).filter_by(phone_number=phone_number).first()
    if not user:
        if not name:
            raise HTTPException(status_code=400, detail="Name required for new user")
        user = User(phone_number=phone_number, name=name)
        db.add(user)
        db.commit()
        db.refresh(user)

    # Generate JWT token
    token = create_jwt(user.user_id)

    # Save token for logout
    expires_at = datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION_MINUTES)
    user_token = UserToken(user_id=user.user_id, token=token, expires_at=expires_at)
    db.add(user_token)
    db.commit()

    # Delete OTP after verification
    db.delete(otp_entry)
    db.commit()

    return {"token": token, "user_id": user.user_id, "name": user.name}

@app.post("/logout")
def logout(authorization: str = Header(...), db: Session = Depends(get_db)):
    token = authorization.replace("Bearer ", "")
    db_token = db.query(UserToken).filter_by(token=token).first()
    if db_token:
        db.delete(db_token)
        db.commit()
        return {"message": "Logged out successfully"}
    raise HTTPException(status_code=401, detail="Invalid token")

# ---------------- Protected Route Example ----------------
def get_current_user(authorization: str = Header(...), db: Session = Depends(get_db)):
    token = authorization.replace("Bearer ", "")
    db_token = db.query(UserToken).filter_by(token=token).first()
    if not db_token:
        raise HTTPException(status_code=401, detail="Invalid token")

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        db.delete(db_token)
        db.commit()
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter_by(user_id=payload["user_id"]).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@app.get("/my-issues")
def my_issues(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    issues = db.query(Issue).filter_by(user_id=current_user.user_id).all()
    return {"issues": [{"id": i.issue_id, "description": i.description, "status": i.status} for i in issues]}
