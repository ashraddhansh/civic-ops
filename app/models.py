from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, Text, Float
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(15), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

class Issue(Base):
    __tablename__ = "issues"

    issue_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"))
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)  # e.g., "road", "water", "electricity", "waste"
    location = Column(String(500))  # Address or description
    latitude = Column(Float, nullable=True)  # GPS coordinates
    longitude = Column(Float, nullable=True)
    photo_url = Column(String(255))
    voice_note_url = Column(String(255))
    status = Column(String(20), default="pending")  # pending, in_progress, resolved, rejected
    priority = Column(String(10), default="unassigned")  # unassigned, low, medium, high, urgent (admin-only)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


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
