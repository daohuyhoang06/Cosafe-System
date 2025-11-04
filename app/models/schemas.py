from pydantic import BaseModel
from typing import Optional

class SafetyRequest(BaseModel):
    name: str

class SearchRequest(BaseModel):
    keyword: str
    page: int = 1
    size: int = 20
    sort: str = "default"  # "default", "asc", "desc"

class NERRequest(BaseModel):
    content: str

class GuideEmailRequest(BaseModel):
    email: str  # Changed from EmailStr to avoid email-validator dependency

class ImageSearchResponse(BaseModel):
    labels: list
    total_labels: int
    message: str

class ProductResponse(BaseModel):
    name: str
    score: Optional[int] = 0
    link_image: Optional[str] = "assets/images/product-placeholder.jpg"

class SearchResponse(BaseModel):
    products: list
    total: Optional[int] = 0
    message: Optional[str] = None
