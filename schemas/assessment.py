from pydantic import BaseModel, EmailStr, Field
from datetime import date
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
