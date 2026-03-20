from fastapi import APIRouter, Depends, HTTPException
from requests import Session
from auth.dependencies import get_current_user
from database import get_db
from models.assessment import QuizHistory
from models.chat_schema import ChatRequest
from models.user import User
from schemas.ai_recommendation import AIChatRequest, AIRecommendationRequest, AIRecommendationResponse, LatestRecommendationRequest, TrendRequest
from services.coach_agent import generate_coach_prompt
from services.trend_analyzer import analyze_trend
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
    
@router.post("/coach-chat")
async def coach_chat(payload: AIChatRequest):
    # 1. Handle History (Limit to last 6 for token efficiency)
    # Ensure we handle cases where history might be empty
    recent_history = payload.history[-6:] if payload.history else []
    
    history_conversation = "\n".join([
        f"{'User' if msg.role == 'user' else 'Coach'}: {msg.message}" 
        for msg in recent_history
    ])

    # 2. Format Recommendations safely
    recommendations_list = "\n".join([
        f"- {r.title}: {r.description}" for r in payload.recommendations
    ]) if payload.recommendations else "No specific recommendations yet."

    # 3. Structured Prompting
    # We use a clear delimiter approach to help the LLM distinguish context from the query
    system_context = f"""
    ROLE: Professional AI Resilience Coach for adolescents.
    USER PROFILE: Level: {payload.resilience_level}, 
    SPECIFIC GUIDANCE: {recommendations_list}
    """

    full_prompt = f"""
    {system_context}

    CONVERSATION HISTORY:
    {history_conversation}

    CURRENT USER INPUT:
    {payload.message}

    INSTRUCTIONS:
    - Be empathetic, supportive, and non-judgmental.
    - Use "we" and "us" to build rapport.
    - Reference their specific recommendations when it fits naturally.
    - Constraint: Keep response under 120 words.
    - Goal: Provide one actionable resilience-building step.

    COACH RESPONSE:
    """

    try:
        # Use async if your SDK supports it, or keep it standard
        response = model.generate_content(full_prompt)
        
        if not response.text:
            raise ValueError("Empty response from AI model")

        return {
            "reply": response.text.strip()
        }

    except Exception as e:
        print(f"AI Coach Error: {str(e)}") # Log the actual error for debugging
        # Return a friendly fallback message
        return {
            "reply": "I'm here for you, but I'm having a little trouble connecting right now. Could you try saying that again?"
        }
        

@router.post("/resilience-insight")
def generate_resilience_insight(request: TrendRequest):

    data = request.history

    scores = [item.score for item in data]

    latest = scores[-1]
    previous = scores[-2] if len(scores) > 1 else None

    trend = "stable"

    if previous:
        if latest > previous:
            trend = "improving"
        elif latest < previous:
            trend = "declining"

    prompt = f"""
    You are an AI resilience coach.

    User resilience history:
    {data}

    Current score: {latest}
    Trend: {trend}

    Tasks:
    1. Provide insight about the resilience trend.
    2. Encourage the user positively.
    3. Suggest 3 daily resilience-building activities.
    4. Provide short coaching advice.

    Response format:
    - Trend Insight
    - Coaching Advice
    - Daily Activities
    """

    response = model.generate_content(prompt)

    return {"insight": response.text}

@router.post("/resilience-coach")
def resilience_coach(data: TrendRequest):

    trend = analyze_trend(data.history)
 
    prompt = generate_coach_prompt(username=data.username,
        history=data.history,
        trend=trend)

    response = model.generate_content(prompt)

    return {
        "trend": trend,
        "insight": response.text
    }