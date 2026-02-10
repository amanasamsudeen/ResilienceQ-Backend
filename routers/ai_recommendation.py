from fastapi import APIRouter
from schemas.ai_recommendation import AIRecommendationRequest
from utils.gemini_client import model
from utils.prompt import build_recommendation_prompt
from fastapi.responses import FileResponse
from services.pdf_generator import generate_recommendation_pdf

router = APIRouter(prefix="/ai", tags=["AI Recommendations"])

@router.post("/recommendations")
def generate_ai_recommendations(payload: AIRecommendationRequest):

    prompt = build_recommendation_prompt(
        payload.resilience_level,
        payload.total_score
    )

    response = model.generate_content(prompt)

    return {
        "resilience_level": payload.resilience_level,
        "recommendations": response.text
    }

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