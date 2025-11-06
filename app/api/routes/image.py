from fastapi import APIRouter, File, UploadFile, Depends
from app.services import ImageService

router = APIRouter()

# Singleton service instance (tối ưu hóa)
_image_service = None

def get_image_service() -> ImageService:
    """Dependency to get ImageService instance (singleton pattern)"""
    global _image_service
    if _image_service is None:
        _image_service = ImageService()
    return _image_service

@router.post("/image-process")
async def extract_labels(file: UploadFile = File(...), service: ImageService = Depends(get_image_service)):
    """Extract product name from image using Gemini AI"""
    return await service.extract_product_from_image(file)
