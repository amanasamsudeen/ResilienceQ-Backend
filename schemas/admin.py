from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class RecentUserResponse(BaseModel):
    user_id: UUID
    full_name: str
    email: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
