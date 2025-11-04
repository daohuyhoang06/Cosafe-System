from fastapi import APIRouter, HTTPException
from app.models import SafetyRequest, SearchRequest
from app.services import ProductService

router = APIRouter()

def get_product_service():
    """Dependency to get ProductService instance"""
    return ProductService()

@router.post("/safety")
async def safety_check(request: SafetyRequest):
    """Get product safety information for display"""
    service = get_product_service()
    return await service.get_product_safety(request.name)

@router.post("/get-all")
async def get_all(request: SafetyRequest):
    """Get all product information (when clicking on product)"""
    service = get_product_service()
    return await service.get_product_details(request.name)

@router.post("/search")
async def products_search(request: SearchRequest):
    """Search and display products with pagination and sorting"""
    service = get_product_service()
    return await service.search_products(
        keyword=request.keyword,
        page=request.page,
        size=request.size,
        sort=request.sort
    )

@router.post("/autocomplete")
async def autocomplete(request: SearchRequest):
    """Autocomplete suggestions for search"""
    service = get_product_service()
    return await service.autocomplete(
        keyword=request.keyword,
        size=request.size
    )
