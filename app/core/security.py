import jwt
import random
from datetime import datetime, timedelta
from app.config import JWT_SECRET, JWT_EXPIRATION_MINUTES

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
