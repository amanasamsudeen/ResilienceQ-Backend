from pydantic import BaseModel, EmailStr, Field
from datetime import date

class PersonalInfoCreate(BaseModel):
    full_name: str = Field(..., min_length=3,alias="fullName")
    email: EmailStr
    gender: str
    dob: date
    education: str
    occupation: str
    
    class Config:
        populate_by_name = True
