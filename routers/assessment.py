from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from schemas.assessment import AssessmentSubmission
from database import get_db
from schemas.user_schema import UserUpdate
from utils.excel_export import generate_excel
from pathlib import Path
from models.assessment import QuizHistory
from models.user import User
from schemas.assessment import QuizHistoryResponse
from auth.dependencies import get_current_user

router = APIRouter(prefix="/assessment", tags=["Assessment"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

BASE_DIR = Path(__file__).resolve().parent.parent
EXPORT_DIR = BASE_DIR / "exports"


@router.post("/submit")
def submit_assessment(
    payload: AssessmentSubmission,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    score = sum(payload.answers)

    if score < 60:
        level = "Low"
    elif score < 120:
        level = "Moderate"
    else:
        level = "High"

    new_quiz = QuizHistory(
        user_id=current_user.user_id,
        score=score,
        level=level,
        duration="8 mins"
    )

    db.add(new_quiz)
    db.commit()
    db.refresh(new_quiz)

    file_path = generate_excel(payload)

    return {
        "message": "Assessment submitted successfully",
        "score": score,
        "level": level,
        "excel_path": file_path.name,
    }


@router.get("/download")
def download_latest_excel():
    files = list(EXPORT_DIR.glob("resilienceq_*.xlsx"))

    if not files:
        raise HTTPException(status_code=404, detail="No assessment file found")

    latest_file = max(files, key=lambda f: f.stat().st_mtime)

    return FileResponse(
        path=latest_file,
        filename=latest_file.name,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@router.get("/history", response_model=List[QuizHistoryResponse])
def get_quiz_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    quizzes = (
        db.query(QuizHistory)
        .filter(QuizHistory.user_id == current_user.user_id)
        .order_by(QuizHistory.created_at.desc())
        .all()
    )

    return quizzes