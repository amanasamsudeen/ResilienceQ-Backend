from fastapi import APIRouter
from schemas.ai_recommendation import AIRecommendationRequest, AIRecommendationResponse
from utils.gemini_client import model
from utils.prompt import build_recommendation_prompt
from fastapi.responses import FileResponse
from services.pdf_generator import generate_recommendation_pdf
import json
from google import genai
from dotenv import load_dotenv
import os

router = APIRouter(prefix="/ai", tags=["AI Recommendations"])
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
   
@router.post("/recommendations", response_model=AIRecommendationResponse)
def generate_ai_recommendations(payload: AIRecommendationRequest):
    prompt = build_recommendation_prompt(
        payload.resilience_level,
        payload.total_score
    )

    # Use the latest model (gemini-2.0-flash is standard in 2026)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": AIRecommendationResponse, # Directly pass the class
        }
    )

    # The SDK automatically parses the JSON into the Pydantic object
    return response.parsed

@router.get("/recommendations/pdf")
def download_ai_recommendation_pdf():
    # Temporary static values (replace with Gemini output later)
    resilience_level = "Moderate Resilience"
    score = 98

    recommendations = """
• Practice structured problem-solving during stressful situations.
• Engage in mindfulness or breathing exercises daily.
• Reflect on past failures and identify lessons learned.
• Strengthen social connections and seek support when needed.
• Set realistic goals and celebrate small achievements.
"""

    pdf_path = generate_recommendation_pdf(
        resilience_level=resilience_level,
        score=score,
        recommendations=recommendations,
    )

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=pdf_path.split("/")[-1],
    )