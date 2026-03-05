from pydantic import BaseModel
from typing import List

class AIRecommendationRequest(BaseModel):
    resilience_level: str
    total_score: int
    answers: List[int]

class RecommendationItem(BaseModel):
    title: str
    description: str

class LatestRecommendationRequest(BaseModel):
    resilience_level: str
    total_score: int

class AIRecommendationResponse(BaseModel):
    resilience_state: str
    recommendations: List[RecommendationItem]
    encouragement: str
