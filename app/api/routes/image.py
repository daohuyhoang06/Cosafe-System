from fastapi import APIRouter, File, UploadFile
from app.services import ImageService

router = APIRouter()

def get_image_service():
    """Dependency to get ImageService instance"""
    return ImageService()

@router.post("/image-process")
async def extract_labels(file: UploadFile = File(...)):
    """Extract product name from image using Gemini AI"""
    service = get_image_service()
    return await service.extract_product_from_image(file)
