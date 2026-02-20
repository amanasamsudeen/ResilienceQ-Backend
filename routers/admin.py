from http.client import HTTPException
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from datetime import datetime, timedelta
from auth.dependencies import get_current_user, require_admin
from sqlalchemy import func
from typing import List
from schemas.admin import RecentUserResponse

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/user-stats")
def get_user_stats(db: Session = Depends(get_db)):
    total_users = db.query(User).count()

    active_users = db.query(User).filter(User.is_active == True).count()

    # New users in last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)

    new_users = (
        db.query(User)
        .filter(User.created_at >= thirty_days_ago)
        .count()
    )

    inactive_users = total_users - active_users

    return {
        "total_users": total_users,
        "active_users": active_users,
        "new_users": new_users,
        "inactive_users": inactive_users,
    }

@router.get("/recent-users", response_model=List[RecentUserResponse])
def get_recent_users(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    users = (
        db.query(User)
        .order_by(User.created_at.desc())
        .limit(limit)
        .all()
    )

    return users