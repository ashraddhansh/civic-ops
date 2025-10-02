import jwt
import random
import secrets
from datetime import datetime, timedelta
from app.config import JWT_SECRET, JWT_EXPIRATION_MINUTES

def generate_otp():
    return f"{random.randint(100000, 999999)}"

def create_jwt(user_id: int, expires_minutes: int = None):
    if expires_minutes is None:
        expires_minutes = JWT_EXPIRATION_MINUTES
    
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(minutes=expires_minutes)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return token

def create_refresh_token():
    return secrets.token_urlsafe(32)

def verify_jwt(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload["user_id"]
    except jwt.ExpiredSignatureError:
        return None
    except jwt.JWTError:
        return None
