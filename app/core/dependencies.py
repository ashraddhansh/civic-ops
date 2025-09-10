from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User, UserToken
from core.security import verify_jwt
import jwt
from config import JWT_SECRET

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
