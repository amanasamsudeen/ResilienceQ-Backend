from email.message import EmailMessage
from pathlib import Path
import smtplib
import resend
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

import os
from dotenv import load_dotenv

load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = BASE_DIR / "templates" / "verification_email.html"
FRONTEND_URL = os.getenv("FRONTEND_URL")
MAIL_FROM = os.getenv("MAIL_FROM")


async def send_verification_email(email: str, username: str, token: str):
    verification_link = f"{FRONTEND_URL}/verify-email?token={token}"
    expiry_time = "24 hours"

    # Read template
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as file:
        html_template = file.read()

    # Replace placeholders
    html_content = (
        html_template
        .replace("{{username}}", username)
        .replace("{{verification_link}}", verification_link)
        .replace("{{expiry_time}}", expiry_time)
    )

    try:
        response = resend.Emails.send({
            "from": MAIL_FROM,  # e.g. noreply@yourdomain.com
            "to": [email],
            "subject": "Verify Your Email - ResilienceQ",
            "html": html_content,
        })

        return {"status": "success", "resend_response": response}

    except Exception as e:
        return {"status": "error", "message": str(e)}
    
def send_reset_email(to_email, reset_link):
    msg = EmailMessage()
    msg["Subject"] = "Reset Your Password"
    msg["From"] = os.getenv("MAIL_USERNAME")
    msg["To"] = to_email

    msg.set_content(f"Click the link to reset your password:\n{reset_link}")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(os.getenv("MAIL_USERNAME"), os.getenv("MAIL_PASSWORD"))
        smtp.send_message(msg)