# API Routes
from .product import router as product_router
from .ner import router as ner_router
from .image import router as image_router
from .email import router as email_router

__all__ = [
    "product_router",
    "ner_router",
    "image_router",
    "email_router"
]
