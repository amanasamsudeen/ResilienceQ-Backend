from http.client import HTTPException
from math import ceil
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from database import get_db
from models.assessment import QuizHistory
from models.user import User
from datetime import datetime, timedelta
from auth.dependencies import get_current_user, require_admin
from sqlalchemy import func
from typing import List
from schemas.admin import PaginatedQuizAttempts, QuizAnalyticsStats,QuizAttemptOut,  RecentUserResponse, UserGrowthResponse
from dateutil.relativedelta import relativedelta

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

@router.get("/quiz-attempts", response_model=PaginatedQuizAttempts)
def get_recent_quiz_attempts(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    skip = (page - 1) * limit

    total = db.query(QuizHistory).count()

    attempts = (
        db.query(QuizHistory)
        .options(joinedload(QuizHistory.user))  # IMPORTANT
        .order_by(QuizHistory.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    formatted = []

    for a in attempts:
        formatted.append(
            QuizAttemptOut(
                id=a.id,
                user=a.user.full_name if a.user else "Unknown",
                date=a.created_at,
                score=a.score,
                risk=a.level,
                status="Completed" if a.score is not None else "Incomplete"
            )
        )

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": ceil(total / limit),
        "data": formatted,
    }
    
@router.get("/analytics/user-growth", response_model=UserGrowthResponse)
def get_user_growth(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    today = datetime.utcnow()
    six_months_ago = today - relativedelta(months=5)

    results = (
        db.query(
            func.date_trunc("month", User.created_at).label("month"),
            func.count(User.user_id)
        )
        .filter(User.created_at >= six_months_ago)
        .group_by("month")
        .order_by("month")
        .all()
    )

    labels = []
    data = []

    for month, count in results:
        labels.append(month.strftime("%b"))  # Jan, Feb, Mar
        data.append(count)

    return {
        "labels": labels,
        "data": data
    }
    

@router.get("/quiz-analytics/stats", response_model=QuizAnalyticsStats)
def get_quiz_analytics_stats(db: Session = Depends(get_db)):

    # Total attempts
    total_attempts = db.query(func.count(QuizHistory.id)).scalar()

    # Group by risk (efficient)
    risk_counts = (
        db.query(QuizHistory.level, func.count(QuizHistory.id))
        .group_by(QuizHistory.level)
        .all()
    )

    high = 0
    moderate = 0
    low = 0

    for risk, count in risk_counts:
        if risk == "High":
            high = count
        elif risk == "Moderate":
            moderate = count
        elif risk == "Low":
            low = count

    return {
        "quiz_attempts": total_attempts,
        "high_risk": high,
        "moderate_risk": moderate,
        "low_risk": low,
    }