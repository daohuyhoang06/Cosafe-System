from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from elasticsearch import Elasticsearch
import os
from dotenv import load_dotenv

router = APIRouter()

# Load environment variables
load_dotenv()

# Elasticsearch client (assumed to be initialized in main.py and passed if needed)
ES_CLOUD_URL = os.getenv("ES_CLOUD_URL")
ES_API_KEY = os.getenv("ES_API_KEY")
es = Elasticsearch([ES_CLOUD_URL], api_key=ES_API_KEY)

# Request models
class SafetyRequest(BaseModel):
    name: str

class SearchRequest(BaseModel):
    keyword: str
    page: int = 1
    size: int = 20
    sort: str = "default"  # "default", "asc", "desc"

@router.post("/safety") 

# lấy thông tin để bôi sản phẩm ( ngoài màn hình)
async def safety_check(request: SafetyRequest):
    try:
        result = es.search(
            index="cs_products_data",
            query={
                "term": {
                    "name.keyword": request.name
                }
            },
            size=1
        )
        if not result["hits"]["hits"]:
            return {"message": "Không tìm thấy sản phẩm"}
        hit = result["hits"]["hits"][0]["_source"]
        return {"name": hit["name"], "score": hit["score"], "link_image": hit["link_image"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@router.post("/get-all")
# hiển thị tất cả các thôgn tin sản phẩm ( khi ấn vào sản phẩm)
async def get_all(request: SafetyRequest):
    try:
        result = es.search(
            index="cs_products_data",
            query={
                "term": {
                    "name.keyword": request.name
                }
            },
            size=1
        )
        if not result["hits"]["hits"]:
            return {"message": "Không tìm thấy sản phẩm"}
        hit = result["hits"]["hits"][0]["_source"]
        return hit
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@router.post("/search")
# tìm kiếm và hiển thị các sản phẩm
async def products_search(request: SearchRequest):
    try:
        keywords = request.keyword.split()
        should_clauses = []
        for keyword in keywords:
            should_clauses.extend([
                {
                    "fuzzy": {
                        "name": {
                            "value": keyword,
                            "fuzziness": "AUTO",
                            "boost": 1.0
                        }
                    }
                },
                {
                    "match": {
                        "name": {
                            "query": keyword,
                            "boost": 2.0
                        }
                    }
                },
                {
                    "prefix": {
                        "name": {
                            "value": keyword,
                            "boost": 1.0
                        }
                    }
                }
            ])
        should_clauses.extend([
            {
                "match_phrase": {
                    "name": {
                        "query": request.keyword,
                        "boost": 5.0
                    }
                }
            },
            {
                "fuzzy": {
                    "name": {
                        "value": request.keyword,
                        "fuzziness": "AUTO",
                        "boost": 3.0
                    }
                }
            }
        ])
        from_value = (request.page - 1) * request.size

        # Handle sorting
        sort_option = None
        if request.sort == "asc":
            sort_option = [{"name.keyword": "asc"}]
        elif request.sort == "desc":
            sort_option = [{"name.keyword": "desc"}]

        es_search_kwargs = {
            "index": "cs_products_data",
            "query": {
                "bool": {
                    "should": should_clauses,
                    "minimum_should_match": 1
                }
            },
            "from_": from_value,
            "size": request.size,
            "collapse": {
                "field": "name.keyword"
            }
        }
        if sort_option:
            es_search_kwargs["sort"] = sort_option

        result = es.search(**es_search_kwargs)
        if not result["hits"]["hits"]:
            return {"products": [], "message": "Không tìm thấy sản phẩm"}
        products = []
        for hit in result["hits"]["hits"]:
            source = hit["_source"]
            products.append({
                "name": source["name"],
                "score": source.get("score", 0),
                "search_score": hit["_score"],
                "link_image": source.get("link_image", "assets/images/product-placeholder.jpg")
            })
        return {"products": products, "total": result["hits"]["total"]["value"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@router.post("/autocomplete")
async def autocomplete(request: SearchRequest):
    try:
        request.size = min(request.size, 10)  # Maximum 10 suggestions
        keywords = request.keyword.split()
        should_clauses = []
        for keyword in keywords:
            should_clauses.extend([
                {
                    "prefix": {
                        "name": {
                            "value": keyword,
                            "boost": 3.0
                        }
                    }
                },
                {
                    "match_phrase_prefix": {
                        "name": {
                            "query": keyword,
                            "boost": 2.0
                        }
                    }
                },
                {
                    "fuzzy": {
                        "name": {
                            "value": keyword,
                            "fuzziness": "AUTO",
                            "boost": 1.0
                        }
                    }
                }
            ])
        should_clauses.append({
            "match_phrase_prefix": {
                "name": {
                    "query": request.keyword,
                    "boost": 5.0
                }
            }
        })

        result = es.search(
            index="cs_products_data",
            query={
                "bool": {
                    "should": should_clauses,
                    "minimum_should_match": 1
                }
            },
            size=request.size,
            _source=["name", "score", "link_image"]
        )

        if not result["hits"]["hits"]:
            return {"products": [], "message": "Không tìm thấy gợi ý"}

        products = []
        for hit in result["hits"]["hits"]:
            source = hit["_source"]
            products.append({
                "name": source["name"],
                "score": source.get("score", 0),
                "search_score": hit["_score"],
                "link_image": source.get("link_image", "assets/images/product-placeholder.jpg")
            })

        return {"products": products, "total": result["hits"]["total"]["value"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")