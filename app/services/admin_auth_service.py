import bcrypt
import jwt
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models import AdminUser, Department
from app.config import JWT_SECRET, ALGORITHM
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

class AdminAuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    @staticmethod
    def create_admin_token(admin_user: AdminUser) -> str:
        """Create JWT token for admin user"""
        payload = {
            "admin_id": admin_user.id,
            "username": admin_user.username,
            "department_id": admin_user.department_id,
            "role": admin_user.role,
            "exp": datetime.utcnow() + timedelta(hours=8)  # 8 hour expiry for admin sessions
        }
        
        return jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)
    
    @staticmethod
    def authenticate_admin(username: str, password: str, db: Session) -> AdminUser:
        """Authenticate admin user"""
        admin = db.query(AdminUser).filter(
            AdminUser.username == username,
            AdminUser.is_active == True
        ).first()
        
        if not admin:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        if not AdminAuthService.verify_password(password, admin.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Update last login
        admin.last_login = datetime.utcnow()
        db.commit()
        
        return admin
    
    @staticmethod
    def create_admin_user(
        username: str, 
        email: str, 
        password: str, 
        full_name: str, 
        department_id: int,
        role: str,
        db: Session
    ) -> AdminUser:
        """Create new admin user"""
        
        # Check if username or email already exists
        existing = db.query(AdminUser).filter(
            (AdminUser.username == username) | (AdminUser.email == email)
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="Username or email already exists")
        
        # Verify department exists
        department = db.query(Department).filter(Department.id == department_id).first()
        if not department:
            raise HTTPException(status_code=400, detail="Department not found")
        
        # Create admin user
        hashed_password = AdminAuthService.hash_password(password)
        
        admin_user = AdminUser(
            username=username,
            email=email,
            password_hash=hashed_password,
            full_name=full_name,
            department_id=department_id,
            role=role
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        return admin_user

admin_auth_service = AdminAuthService()