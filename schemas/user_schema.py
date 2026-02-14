from pydantic import BaseModel, EmailStr
from uuid import UUID

class UserRegister(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    institution: str | None = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    user_id: UUID
    full_name: str
    email: EmailStr
    role: str

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    name: str
    email: EmailStr
    institution: str
