from pydantic import BaseModel, EmailStr, Field
from datetime import date, datetime
from typing import List

class PersonalInfo(BaseModel):
    full_name: str = Field(..., alias="fullName")
    email: EmailStr
    gender: str
    dob: date
    education: str
    occupation: str

    class Config:
        populate_by_name = True


class AssessmentSubmission(BaseModel):
    personalInfo: PersonalInfo
    answers: List[int]

class QuizHistoryResponse(BaseModel):
    id: int
    score: int
    level: str

    created_at: datetime

    class Config:
        from_attributes = True