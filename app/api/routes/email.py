from fastapi import APIRouter, BackgroundTasks
from app.models import GuideEmailRequest
from app.services import EmailService

router = APIRouter()

def get_email_service():
    """Dependency to get EmailService instance"""
    return EmailService()

@router.post("/send-guide-email")
async def send_guide_email(request: GuideEmailRequest, background_tasks: BackgroundTasks):
    """Send guide PDF email in background"""
    service = get_email_service()
    background_tasks.add_task(service.send_guide_email, request.email)
    return {"message": "Thanks! Check your email for the guide."}
