from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from elasticsearch import Elasticsearch
from pydantic import BaseModel, HttpUrl
from typing import Optional
import re
import os
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import json
from dotenv import load_dotenv
import requests
from io import BytesIO

# Load environment variables
load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this for safety
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Elasticsearch config
ES_CLOUD_URL = os.getenv("ES_CLOUD_URL")
ES_API_KEY = os.getenv("ES_API_KEY")
if not ES_CLOUD_URL or not ES_API_KEY:
    raise ValueError("Missing ES_CLOUD_URL or ES_API_KEY. Please set in .env or environment.")

# Gemini API config
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("Missing GOOGLE_API_KEY. Please set in .env or environment.")
genai.configure(api_key=GEMINI_API_KEY)

es = Elasticsearch(
    [ES_CLOUD_URL],
    api_key=ES_API_KEY,
    headers={"Content-Type": "application/json"}
)

if not es.ping():
    raise ValueError("Cannot connect to Elasticsearch!")

# Request models
class SafetyRequest(BaseModel):
    name: str

class NERRequest(BaseModel):
    content: str

class SearchRequest(BaseModel):
    keyword: str
    page: int = 1
    size: int = 20
    sort: str = "default"  # "default", "asc", "desc"

class ImageUrlRequest(BaseModel):
    image_url: HttpUrl

@app.post("/safety")
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
        return {"name": hit["name"], "score": hit["score"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.post("/name-entity-recognition")
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

@app.post("/get-all")
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

@app.post("/search")
async def productsSearch(request: SearchRequest):
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
        # "default" means don't set sort (Elasticsearch will sort by score)

        es_search_kwargs = {
            "index": "cs_products_data",
            "query": {
                "bool": {
                    "should": should_clauses,
                    "minimum_should_match": 1
                }
            },
            "from_": from_value,
            "size": request.size
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

@app.post("/image-process")
async def extract_labels(
    file: Optional[UploadFile] = File(None),
    image_url: Optional[str] = Form(None)
):
    try:
        # Kiểm tra xem có cung cấp file hoặc URL không
        if file is None and not image_url:
            raise HTTPException(
                status_code=400, 
                detail="Phải cung cấp file ảnh hoặc URL ảnh"
            )
            
        # Nếu có file được tải lên
        if file:
            if not file.content_type.startswith("image/"):
                raise HTTPException(
                    status_code=400, 
                    detail="File phải là ảnh (jpg, png, v.v.)"
                )
            content = await file.read()
            mime_type = file.content_type
            
        # Nếu có URL được cung cấp
        elif image_url:
            try:
                response = requests.get(image_url, timeout=10)
                response.raise_for_status()  # Kiểm tra lỗi HTTP
                content = response.content
                
                # Xác định mime_type từ header của response hoặc từ phần mở rộng của URL
                mime_type = response.headers.get('Content-Type')
                if not mime_type or not mime_type.startswith('image/'):
                    # Dự đoán mime type từ phần mở rộng của URL
                    if image_url.lower().endswith('.jpg') or image_url.lower().endswith('.jpeg'):
                        mime_type = 'image/jpeg'
                    elif image_url.lower().endswith('.png'):
                        mime_type = 'image/png'
                    elif image_url.lower().endswith('.gif'):
                        mime_type = 'image/gif'
                    elif image_url.lower().endswith('.webp'):
                        mime_type = 'image/webp'
                    else:
                        mime_type = 'image/jpeg'  # Mặc định
                        
            except requests.exceptions.RequestException as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Không thể tải ảnh từ URL: {str(e)}"
                )
                
        # Kiểm tra kích thước ảnh
        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=400, 
                detail="File quá lớn, tối đa 10MB"
            )
            
        # Xử lý ảnh với Gemini API
        model = genai.GenerativeModel("gemini-1.5-flash")
        image = {
            "mime_type": mime_type,
            "data": content
        }
        
        prompt = """
        Identify and extract the product name from the label on the bottle in this image. 
        Return the result in JSON format: [{'description': 'product name', 'score': 0.9}, ...]. 
        Ensure the response is valid JSON and contains only the JSON object.
        """
        
        response = model.generate_content([prompt, image])
        
        if not response.text:
            raise HTTPException(
                status_code=500, 
                detail="Gemini API không trả về kết quả"
            )
            
        try:
            # Loại bỏ các ký tự markdown code nếu có
            cleaned_text = response.text
            if "```json" in cleaned_text:
                cleaned_text = cleaned_text.split("```json")[1].split("```")[0].strip()
            elif "```" in cleaned_text:
                cleaned_text = cleaned_text.split("```")[1].split("```")[0].strip()
                
            labels = json.loads(cleaned_text)
            
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=500, 
                detail="Không thể phân tích JSON từ Gemini API"
            )
            
        # Trả về kết quả
        return {
            "labels": labels,
            "total_labels": len(labels),
            "source_type": "file" if file else "url",
            "message": "Xử lý ảnh thành công" if labels else "Không tìm thấy tên sản phẩm trên nhãn"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Lỗi server: {str(e)}"
        )

@app.post("/autocomplete")
async def autocomplete(request: SearchRequest):
    """API endpoint tối ưu cho tính năng gợi ý tìm kiếm"""
    try:
        # Giới hạn kích thước kết quả trả về
        request.size = min(request.size, 10)  # Tối đa 10 gợi ý
        
        keywords = request.keyword.split()
        should_clauses = []
        
        # Ưu tiên prefix match cho autocomplete
        for keyword in keywords:
            should_clauses.extend([
                {
                    "prefix": {
                        "name": {
                            "value": keyword,
                            "boost": 3.0  # Tăng boost cho prefix match
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
        
        # Thêm match phrase cho toàn bộ query
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
            _source=["name", "score", "link_image"]  # Chỉ lấy các trường cần thiết
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
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)