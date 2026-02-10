from pydantic import BaseModel
from typing import List

class AIRecommendationRequest(BaseModel):
    resilience_level: str
    total_score: int
    answers: List[int]
