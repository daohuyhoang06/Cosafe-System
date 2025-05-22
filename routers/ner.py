from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from elasticsearch import Elasticsearch
import re
import os
from dotenv import load_dotenv

router = APIRouter()

# Load environment variables
load_dotenv()

# Elasticsearch client
ES_CLOUD_URL = os.getenv("ES_CLOUD_URL")
ES_API_KEY = os.getenv("ES_API_KEY")
es = Elasticsearch([ES_CLOUD_URL], api_key=ES_API_KEY)

# Request model
class NERRequest(BaseModel):
    content: str

@router.post("/name-entity-recognition")
async def ner_and_score(request: NERRequest):
    try:
        ingredients = re.split(r',|\s+và\s+|\s+hoặc\s+', request.content)
        if not ingredients:
            return {"ingredients": [], "message": "Không tìm thấy thành phần trong văn bản"}
        ingredient_list = []
        for ingredient in ingredients:
            result = es.search(
                index="cs_products_data",
                query={
                    "bool": {
                        "filter": [
                            {"exists": {"field": f"ingredients.{ingredient.upper()}"}}
                        ]
                    }
                },
                size=1
            )
            hits = result.get("hits", {}).get("hits", [])
            if hits:
                hit = hits[0]
                if "_source" in hit and "ingredients" in hit["_source"]:
                    ingredients_data = hit["_source"]["ingredients"]
                    if ingredient in ingredients_data and "score" in ingredients_data[ingredient]:
                        ingredient_list.append({
                            "name": ingredient,
                            "score": ingredients_data[ingredient]["score"]
                        })
        if not ingredient_list:
            return {"ingredients": [], "message": "Không tìm thấy thành phần"}
        return {"ingredients": ingredient_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")