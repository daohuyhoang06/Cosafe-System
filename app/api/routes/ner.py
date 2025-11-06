from fastapi import APIRouter, HTTPException, Depends
from app.models import NERRequest
from app.services import NERService

router = APIRouter()

# Singleton service instance (tối ưu hóa)
_ner_service = None

def get_ner_service() -> NERService:
    """Dependency to get NERService instance (singleton pattern)"""
    global _ner_service
    if _ner_service is None:
        _ner_service = NERService()
    return _ner_service

@router.post("/name-entity-recognition")
async def ner_and_score(request: NERRequest, service: NERService = Depends(get_ner_service)):
    """Analyze ingredients and return scores"""
    return await service.analyze_ingredients(request.content)
