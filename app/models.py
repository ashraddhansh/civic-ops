from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, Text
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(15), unique=True, nullable=False)
    name = Column(String(100))
    created_at = Column(TIMESTAMP, server_default=func.now())

class Issue(Base):
    __tablename__ = "issues"

    issue_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"))
    description = Column(Text)
    photo_url = Column(String(255))
    voice_note_url = Column(String(255))
    status = Column(String(20), default="pending")
    created_at = Column(TIMESTAMP, server_default=func.now())


class OTPVerification(Base):
    __tablename__ = "otp_verifications"

    phone_number = Column(String(15), primary_key=True)
    otp = Column(String(6), nullable=False)
    expires_at = Column(TIMESTAMP, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

class UserToken(Base):
    __tablename__ = "user_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"))
    token = Column(String(500), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    expires_at = Column(TIMESTAMP, nullable=False)
