from email.message import EmailMessage
from pathlib import Path
import smtplib
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

import os
from dotenv import load_dotenv

load_dotenv()

conf = ConnectionConfig(
   MAIL_USERNAME= os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD= os.getenv("MAIL_PASSWORD"),
    MAIL_FROM= os.getenv("MAIL_FROM"),
    MAIL_PORT= int(os.getenv("MAIL_PORT")),
    MAIL_SERVER= os.getenv("MAIL_SERVER"),
    MAIL_STARTTLS= os.getenv("MAIL_STARTTLS"),
    MAIL_SSL_TLS= os.getenv("MAIL_SSL_TLS"),
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = BASE_DIR /"templates"/"verification_email.html"
FRONTEND_URL = os.getenv("FRONTEND_URL")

async def send_verification_email(email: str, username: str, token: str):

    verification_link = f"{FRONTEND_URL}/verify-email?token={token}"
    expiry_time = " 24 hours"  # Or "24 hours"

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

    message = MessageSchema(
        subject="Verify Your Email - ResilienceQ",
        recipients=[email],
        body=html_content,
        subtype="html"
    )

    fm = FastMail(conf)
    await fm.send_message(message)
    
def send_reset_email(to_email, reset_link):
    msg = EmailMessage()
    msg["Subject"] = "Reset Your Password"
    msg["From"] = os.getenv("MAIL_USERNAME")
    msg["To"] = to_email

    msg.set_content(f"Click the link to reset your password:\n{reset_link}")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(os.getenv("MAIL_USERNAME"), os.getenv("MAIL_PASSWORD"))
        smtp.send_message(msg)