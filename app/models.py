from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, Text, Float, Boolean, DateTime, UniqueConstraint, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import uuid
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    id = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    phone_number = Column(String(15), unique=True, nullable=True)
    email = Column(String(255), unique=True, nullable=True)
    full_name = Column(String(100), nullable=True)
    name = Column(String(100), nullable=True)  # Keep for backward compatibility
    is_profile_complete = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

class Issue(Base):
    __tablename__ = "issues"

    issue_id = Column(Integer, primary_key=True, index=True)
    custom_id = Column(String(50), unique=True, nullable=True)  # CIV + timestamp format
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"))
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)  # e.g., "Road & Transport"
    subcategory = Column(String(50), nullable=True)  # e.g., "Potholes"
    location = Column(String(500))  # Address or description
    latitude = Column(Float, nullable=True)  # GPS coordinates
    longitude = Column(Float, nullable=True)
    photo_url = Column(String(1000))
    voice_note_url = Column(String(1000))
    status = Column(String(20), default="reported")  # reported, in_progress, resolved, rejected
    priority = Column(String(10), default="unassigned")  # unassigned, low, medium, high, urgent (admin-only)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    department = relationship("Department", back_populates="issues")


class OTPVerification(Base):
    __tablename__ = "otp_verifications"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    phone_number = Column(String(15), nullable=True)
    email = Column(String(255), nullable=True)
    otp = Column(String(6), nullable=False)
    expires_at = Column(TIMESTAMP, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    retry_after = Column(TIMESTAMP, nullable=True)

class UserToken(Base):
    __tablename__ = "user_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"))
    access_token = Column(String(500), nullable=False)
    refresh_token = Column(String(500), nullable=True)
    token_type = Column(String(20), default="bearer")
    created_at = Column(TIMESTAMP, server_default=func.now())
    expires_at = Column(TIMESTAMP, nullable=False)
    refresh_expires_at = Column(TIMESTAMP, nullable=True)


class Department(Base):
    __tablename__ = "departments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)  # e.g., "Solid waste management"
    code = Column(String(20), unique=True, nullable=False)   # e.g., "SWM"
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    admins = relationship("AdminUser", back_populates="department")
    issues = relationship("Issue", back_populates="department")


class AdminUser(Base):
    __tablename__ = "admin_users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(String(50), default="admin")  # admin, super_admin
    department_id = Column(Integer, ForeignKey("departments.id"))
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    department = relationship("Department", back_populates="admins")


class CategoryDepartmentMapping(Base):
    __tablename__ = "category_department_mappings"
    
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(100), nullable=False, index=True)
    subcategory = Column(String(100), nullable=False, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    department = relationship("Department")
    
    # Ensure unique mapping per category-subcategory
    __table_args__ = (
        Index('idx_category_subcategory', 'category', 'subcategory'),
        UniqueConstraint('category', 'subcategory', name='unique_category_subcategory')
    )
