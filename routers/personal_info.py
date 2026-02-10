from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.personal_info import PersonalInfoCreate
from models.personal_info import PersonalInfo
from database import get_db
from datetime import date

router = APIRouter(prefix="/api/personal-info", tags=["Personal Info"])

@router.post("/")
def create_personal_info(
    data: PersonalInfoCreate,
    db: Session = Depends(get_db),
):
    # Extra backend safety
    if data.dob > date.today():
        raise HTTPException(
            status_code=400,
            detail="Date of birth cannot be in the future",
        )

    record = PersonalInfo(
        full_name=data.full_name,
        email=data.email,
        gender=data.gender,
        dob=data.dob,
        education=data.education,
        occupation=data.occupation,
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "message": "Personal information saved successfully",
        "participant_id": record.id,
    }
