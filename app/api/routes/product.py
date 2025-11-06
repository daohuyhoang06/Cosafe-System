from fastapi import APIRouter, HTTPException, Depends
from app.models import SafetyRequest, SearchRequest
from app.services import ProductService

router = APIRouter()

# Singleton service instance (tối ưu hóa - tránh tạo instance mỗi request)
_product_service = None

def get_product_service() -> ProductService:
    """Dependency to get ProductService instance (singleton pattern)"""
    global _product_service
    if _product_service is None:
        _product_service = ProductService()
    return _product_service

@router.post("/safety")
async def safety_check(request: SafetyRequest, service: ProductService = Depends(get_product_service)):
    """Get product safety information for display"""
    return await service.get_product_safety(request.name)

@router.post("/get-all")
async def get_all(request: SafetyRequest, service: ProductService = Depends(get_product_service)):
    """Get all product information (when clicking on product)"""
    return await service.get_product_details(request.name)

@router.post("/search")
async def products_search(request: SearchRequest, service: ProductService = Depends(get_product_service)):
    """Search and display products with pagination and sorting"""
    return await service.search_products(
        keyword=request.keyword,
        page=request.page,
        size=request.size,
        sort=request.sort
    )

@router.post("/autocomplete")
async def autocomplete(request: SearchRequest, service: ProductService = Depends(get_product_service)):
    """Autocomplete suggestions for search"""
    return await service.autocomplete(
        keyword=request.keyword,
        size=request.size
    )
