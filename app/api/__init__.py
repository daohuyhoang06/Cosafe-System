# API module
from .routes import product_router, ner_router, image_router, email_router

__all__ = [
    "product_router",
    "ner_router",
    "image_router",
    "email_router"
]
