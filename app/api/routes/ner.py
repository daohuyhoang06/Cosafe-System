from fastapi import APIRouter, HTTPException
from app.models import NERRequest
from app.services import NERService

router = APIRouter()

def get_ner_service():
    """Dependency to get NERService instance"""
    return NERService()

@router.post("/name-entity-recognition")
async def ner_and_score(request: NERRequest):
    """Analyze ingredients and return scores"""
    service = get_ner_service()
    return await service.analyze_ingredients(request.content)
