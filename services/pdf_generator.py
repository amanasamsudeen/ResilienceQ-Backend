from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from datetime import datetime
import os

EXPORT_DIR = "exports/recommendations"
os.makedirs(EXPORT_DIR, exist_ok=True)


def generate_recommendation_pdf(resilience_level: str, score: int, recommendations: str):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"AI_Resilience_Recommendations_{timestamp}.pdf"
    file_path = os.path.join(EXPORT_DIR, filename)

    doc = SimpleDocTemplate(
        file_path,
        pagesize=A4,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=50,
    )

    styles = getSampleStyleSheet()
    story = []

    story.append(
        Paragraph(
            "AI-Based Resilience Assessment Report",
            ParagraphStyle(
                "title",
                fontSize=20,
                alignment=1,
                spaceAfter=20,
                fontName="Helvetica-Bold",
            ),
        )
    )

    story.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%d-%m-%Y')}", styles["Normal"]))
    story.append(Spacer(1, 10))
    story.append(Paragraph(f"<b>Total Score:</b> {score}", styles["Normal"]))
    story.append(Paragraph(f"<b>Resilience Level:</b> {resilience_level}", styles["Normal"]))
    story.append(Spacer(1, 20))

    story.append(Paragraph("<b>AI Recommendations</b>", styles["Heading2"]))
    story.append(Spacer(1, 10))

    for line in recommendations.split("\n"):
        story.append(Paragraph(line, styles["Normal"]))
        story.append(Spacer(1, 6))

    doc.build(story)

    return file_path
