from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.dependencies import get_db, get_current_user
from models import User, Issue

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/my-issues")
def my_issues(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    issues = db.query(Issue).filter_by(user_id=current_user.user_id).all()
    return {"issues": [{"id": i.issue_id, "description": i.description, "status": i.status} for i in issues]}
