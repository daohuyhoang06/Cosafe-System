from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from app.core import settings
from app.api import product_router, ner_router, image_router, email_router

def create_app() -> FastAPI:
    """Application factory"""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG
    )
    
    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Tối ưu hóa: Nén response để giảm băng thông
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Include routers
    app.include_router(product_router, prefix="/api/products", tags=["Products"])
    app.include_router(ner_router, prefix="/api/ner", tags=["NER"])
    app.include_router(image_router, prefix="/api/image", tags=["Image"])
    app.include_router(email_router, prefix="/api/email", tags=["Email"])
    
    @app.get("/")
    async def root():
        return {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "status": "running"
        }
    
    @app.get("/health")
    async def health():
        """Health check endpoint"""
        from app.core import get_es_client
        try:
            es = get_es_client()
            info = es.info()
            return {
                "status": "healthy",
                "elasticsearch": "connected",
                "es_version": info['version']['number']
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "elasticsearch": "error",
                "error": str(e)
            }
    
    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
