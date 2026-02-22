from typing import List
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

class QuizAttemptOut(BaseModel):
    id: int
    user: str
    date: datetime
    score: int
    risk: str
    status: str

    class Config:
        from_attributes = True


class PaginatedQuizAttempts(BaseModel):
    total: int
    page: int
    limit: int
    total_pages: int
    data: List[QuizAttemptOut]
    
class UserGrowthResponse(BaseModel):
    labels: List[str]
    data: List[int]

class QuizAnalyticsStats(BaseModel):
    quiz_attempts: int
    high_risk: int
    moderate_risk: int
    low_risk: int