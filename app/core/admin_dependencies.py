import jwt
from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.core.dependencies import get_db
from app.models import AdminUser
from app.config import JWT_SECRET, ALGORITHM

def get_current_admin(
    authorization: str = Header(..., description="Bearer token"),
    db: Session = Depends(get_db)
) -> AdminUser:
    """Get current authenticated admin user"""
    try:
        # Extract token from Bearer header
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization header")
        
        token = authorization.replace("Bearer ", "")
        
        # Decode JWT token
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        admin_id = payload.get("admin_id")
        
        if not admin_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Get admin user from database
        admin = db.query(AdminUser).filter(
            AdminUser.id == admin_id,
            AdminUser.is_active == True
        ).first()
        
        if not admin:
            raise HTTPException(status_code=401, detail="Admin user not found")
        
        return admin
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=401, detail="Authentication failed")

def get_department_admin(current_admin: AdminUser = Depends(get_current_admin)) -> AdminUser:
    """Ensure admin has department access"""
    if not current_admin.department_id:
        raise HTTPException(status_code=403, detail="Admin must be assigned to a department")
    
    return current_admin

def get_super_admin(current_admin: AdminUser = Depends(get_current_admin)) -> AdminUser:
    """Ensure admin has super admin role"""
    if current_admin.role != "super_admin":
        raise HTTPException(status_code=403, detail="Super admin access required")
    
    return current_admin