from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from elasticsearch import Elasticsearch
import os
from dotenv import load_dotenv
from routers.product import router as product_router
from routers.ner import router as ner_router
from routers.image import router as image_router
from routers.email import router as email_router

# Load environment variables
load_dotenv()

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict this in production for safety
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Elasticsearch config
ES_CLOUD_URL = os.getenv("ES_CLOUD_URL")
ES_API_KEY = os.getenv("ES_API_KEY")
if not ES_CLOUD_URL or not ES_API_KEY:
    raise ValueError("Missing ES_CLOUD_URL or ES_API_KEY. Please set in .env or environment.")

es = Elasticsearch(
    [ES_CLOUD_URL],
    api_key=ES_API_KEY,
    headers={"Content-Type": "application/json"}
)

if not es.ping():
    raise ValueError("Cannot connect to Elasticsearch!")

# Include routers
app.include_router(product_router, prefix="/api/products", tags=["Products"])
app.include_router(ner_router, prefix="/api/ner", tags=["NER"])
app.include_router(image_router, prefix="/api/image", tags=["Image"])
app.include_router(email_router, prefix="/api/email", tags=["Email"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)