from fastapi import APIRouter, BackgroundTasks
from pydantic import EmailStr
from pydantic import BaseModel
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
from dotenv import load_dotenv

router = APIRouter()

# Load environment variables
load_dotenv()

def send_guide_email_task(to_email: str):
    # Email configuration
    SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    SMTP_USER = os.getenv("SMTP_USER")
    SMTP_PASS = os.getenv("SMTP_PASS")
    if not (SMTP_USER and SMTP_PASS):
        print("Missing SMTP_USER or SMTP_PASS in environment!")
        return

    subject = "Your Free Copy of EWG’s Quick Tips for Safer Personal Care Products"

    text = (
        "Thank you for requesting EWG’s Quick Tips for Choosing Safer Personal Care Products!\n\n"
        "Please find your free guide attached to this email.\n\n"
        "This guide will help you make smarter, healthier choices for you and your family. "
        "Explore ingredient safety, learn how to spot EWG VERIFIED® products, and see how easy it is to shop with confidence.\n\n"
        "Stay informed and empowered—visit EWG’s Skin Deep® database any time to search for safety scores and ingredient information on thousands of personal care products.\n\n"
        "Thank you for supporting EWG’s mission to make safer products available for everyone!\n\n"
        "With care,\n"
        "The EWG Team"
    )

    # Create multipart message
    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = to_email
    msg.attach(MIMEText(text, "plain", "utf-8"))

    # Attach PDF
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    pdf_path = os.path.join(BASE_DIR, "..", "front_end", "assets", "ewg-guide.pdf")
    try:
        with open(pdf_path, "rb") as f:
            part = MIMEBase("application", "pdf")
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f'attachment; filename="EWG-Quick-Tips-Guide.pdf"'
            )
            msg.attach(part)
    except Exception as e:
        print(f"Error attaching PDF: {e}")

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, [to_email], msg.as_string())
    except Exception as e:
        print(f"Error sending guide email to {to_email}: {e}")

class GuideEmailRequest(BaseModel):
    email: EmailStr

@router.post("/send-guide-email")
async def send_guide_email(request: GuideEmailRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(send_guide_email_task, request.email)
    return {"message": "Thanks! Check your email for the guide."}