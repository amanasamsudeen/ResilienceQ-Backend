from fastapi import APIRouter, Depends, HTTPException
from requests import Session
from auth.dependencies import get_current_user
from database import get_db
from models.assessment import QuizHistory
from models.chat_schema import ChatRequest
from models.user import User
from schemas.ai_recommendation import AIRecommendationRequest, AIRecommendationResponse, LatestRecommendationRequest
from utils.gemini_client import model
from utils.prompt import build_recommendation_prompt
from fastapi.responses import FileResponse
from services.pdf_generator import generate_recommendation_pdf
import json
from google import genai
from dotenv import load_dotenv
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
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

@router.post("/recommendations/pdf")
async def generate_pdf(data: dict):
    file_path = "ai_recommendation_report.pdf"

    doc = SimpleDocTemplate(file_path)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("AI Resilience Report", styles["Heading1"]))
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(Paragraph(f"Level: {data['resilience_level']}", styles["Normal"]))
    elements.append(Paragraph(f"Score: {data['total_score']} / 150", styles["Normal"]))
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(Paragraph("Resilience State:", styles["Heading2"]))
    elements.append(Paragraph(data["resilience_state"], styles["Normal"]))
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(Paragraph("Recommendations:", styles["Heading2"]))
    for rec in data["recommendations"]:
        elements.append(Paragraph(f"- {rec['title']}", styles["Normal"]))
        elements.append(Paragraph(rec["description"], styles["Normal"]))
        elements.append(Spacer(1, 0.2 * inch))

    elements.append(Spacer(1, 0.3 * inch))
    elements.append(Paragraph("Encouragement:", styles["Heading2"]))
    elements.append(Paragraph(data["encouragement"], styles["Normal"]))

    doc.build(elements)

    return FileResponse(
        file_path,
        media_type="application/pdf",
        filename="AI_Resilience_Report.pdf"
    )

@router.post("/chatbot")
async def chat_with_gemini(payload: ChatRequest):
    try:
        # Initializing the model with a system instruction for context
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=payload.question,
            config={
                "system_instruction": "You are a supportive resilience coach. Answer questions about mental wellness and resilience clearly and briefly."
            }
        )
        
        return {
            "answer": response.text,
            "sources": [] # Gemini handles the grounding
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/latest-recommendation")
def latest_recommendation(current_user: User = Depends(get_current_user),db: Session = Depends(get_db)):
    latest_quiz = (
        db.query(QuizHistory)
        .filter(QuizHistory.user_id == current_user.user_id)
        .order_by(QuizHistory.created_at.desc())
        .first()
    )

    if not latest_quiz:
        return None

    return generate_ai_recommendations(
        LatestRecommendationRequest(
            resilience_level=latest_quiz.level,
            total_score=latest_quiz.score
        )
    )