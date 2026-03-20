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
class ChatHistoryItem(BaseModel):
    role: str
    message: str
class AIChatRequest(BaseModel):
    message: str
    resilience_level: str
   
    history: List[ChatHistoryItem] = []
    recommendations: List[RecommendationItem]

class TrendItem(BaseModel):
    date: str
    score: int
    level: str


class TrendRequest(BaseModel):
    username: str
    history: List[TrendItem]
