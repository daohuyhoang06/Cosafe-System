from fastapi import APIRouter, BackgroundTasks, Depends
from app.models import GuideEmailRequest
from app.services import EmailService

router = APIRouter()

# Singleton service instance (tối ưu hóa)
_email_service = None

def get_email_service() -> EmailService:
    """Dependency to get EmailService instance (singleton pattern)"""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service

@router.post("/send-guide-email")
async def send_guide_email(
    request: GuideEmailRequest, 
    background_tasks: BackgroundTasks,
    service: EmailService = Depends(get_email_service)
):
    """Send guide PDF email in background"""
    background_tasks.add_task(service.send_guide_email, request.email)
    return {"message": "Thanks! Check your email for the guide."}
