# server.py
from fastapi import FastAPI, HTTPException, status, File, UploadFile
from elasticsearch import Elasticsearch
from pydantic import BaseModel
from typing import List, Dict
import logging
import re
import os 
from fastapi.middleware.cors import CORSMiddleware 
import google.generativeai as genai
import json

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Có thể giới hạn chỉ ["http://localhost:5500"] cho an toàn
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Cấu hình kết nối với Elasticsearch
#es = Elasticsearch(
#    hosts=["https://localhost:9200/"],  
#    basic_auth=("elastic", "OYRcPIeE=EB_YELaA=hT"),
#    verify_certs=False,
#    ssl_show_warn=False 
#)

ES_CLOUD_URL = os.getenv("ES_CLOUD_URL", "https://934a7c2c20c740988176e6696afaf098.us-central1.gcp.cloud.es.io:443")
ES_API_KEY = os.getenv("ES_API_KEY", "NWN0RTFKWUJHS0dSZFVQVFU0SHc6Z2RDVFRVTHo2c0JPY1Z0ektaZ0lwUQ==")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyAyXsnMxeTdnEiu6oLVxjRGLGJ2hvRasBM") 
genai.configure(api_key=GEMINI_API_KEY)

es = Elasticsearch(
    [ES_CLOUD_URL],
    api_key=ES_API_KEY,
    headers={"Content-Type": "application/json"}  # Rõ ràng thêm Content-Type (không bắt buộc)
)

# Kiểm tra kết nối Elasticsearch
if not es.ping():
    raise ValueError("Không thể kết nối tới Elasticsearch!")

# Model cho request body
class SafetyRequest(BaseModel):
    name: str

class NERRequest(BaseModel):
    content: str

class SearchRequest(BaseModel):
    keyword: str
    size: int = 10  # Mặc định trả về 10 kết quả

@app.post("/safety")
async def safety_check(request: SafetyRequest):
    try:
        # Truy vấn Elasticsearch với term query để tìm chính xác tên sản phẩm
        result = es.search(
            index="products",
            query={
                "term": {
                    "name.keyword": request.name  # Tìm chính xác trên trường keyword
                }
            },
            size=1  # Lấy 1 kết quả
        )

        # Kiểm tra kết quả
        if not result["hits"]["hits"]:
            return {"message": "Không tìm thấy sản phẩm"}
        else:
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
        

        # Tìm kiếm sản phẩm chứa các thành phần khớp chính xác
        ingredient_list = []
        for ingredient in ingredients:
            result = es.search(
                index="products",
                query={
                    "bool": {
                        "filter": [
                            {"exists": {"field": f"ingredients.{ingredient.upper()}"}}  # Kiểm tra thành phần tồn tại
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

# Lấy toàn bộ thông tin sản phẩm: tên sản phẩm, điểm tương tự, link ảnh, thành phần
@app.post("/get-all")
async def get_all(request: SafetyRequest):
    try:
        # Truy vấn Elasticsearch với term query để tìm chính xác tên sản phẩm
        result = es.search(
            index="products",
            query={
                "term": {
                    "name.keyword": request.name  # Tìm chính xác trên trường keyword
                }
            },
            size=1  # Lấy 1 kết quả
        )

        # Kiểm tra kết quả
        if not result["hits"]["hits"]:
            return {"message": "Không tìm thấy sản phẩm"}
        else:
            hit = result["hits"]["hits"][0]["_source"]
            return hit

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.post("/search")
async def productsSearch(request: SearchRequest):
    try:
        # Tách từ khóa thành các từ riêng lẻ
        keywords = request.keyword.split()
        
        # Xây dựng truy vấn Elasticsearch
        should_clauses = []
        
        # Truy vấn cho từng từ khóa riêng lẻ
        for keyword in keywords:
            should_clauses.extend([
                # Tìm kiếm mờ cho từng từ
                {
                    "fuzzy": {
                        "name": {
                            "value": keyword,
                            "fuzziness": "AUTO",
                            "boost": 1.0
                        }
                    }
                },
                # Tìm kiếm match cho từng từ
                {
                    "match": {
                        "name": {
                            "query": keyword,
                            "boost": 2.0
                        }
                    }
                },
                # Tìm kiếm prefix cho từng từ
                {
                    "prefix": {
                        "name": {
                            "value": keyword,
                            "boost": 1.0
                        }
                    }
                }
            ])
        
        # Thêm truy vấn cho toàn bộ từ khóa (ưu tiên cao hơn nếu khớp đầy đủ)
        should_clauses.extend([
            {
                "match_phrase": {
                    "name": {
                        "query": request.keyword,
                        "boost": 5.0  # Ưu tiên cao cho khớp chính xác hoặc gần đúng toàn bộ cụm
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

        # Truy vấn Elasticsearch
        result = es.search(
            index="products",
            query={
                "bool": {
                    "should": should_clauses,
                    "minimum_should_match": 1  # Chỉ cần ít nhất 1 từ khớp
                }
            },
            size=request.size
        )

        # Kiểm tra kết quả
        if not result["hits"]["hits"]:
            return {"products": [], "message": "Không tìm thấy sản phẩm"}
        else:
            products = []
            for hit in result["hits"]["hits"]:
                source = hit["_source"]
                products.append({
                    "name": source["name"],
                    "score": source.get("score", 0),
                    "search_score": hit["_score"]
                })
            return {"products": products, "total": result["hits"]["total"]["value"]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.post("/image-process")
async def extract_labels(file: UploadFile = File(...)):
    try:
        # Kiểm tra định dạng file
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File phải là ảnh (jpg, png, v.v.)")
        
        # Kiểm tra kích thước file (giới hạn 10MB)
        content = await file.read()
        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File quá lớn, tối đa 10MB")
        
        # Khởi tạo Gemini model
        model = genai.GenerativeModel("gemini-2.0-flash")
        
        # Chuẩn bị ảnh và prompt
        image = {
            "mime_type": file.content_type,
            "data": content
        }
        # prompt = "Find the products in this picture and return in JSON format: [{'description': 'object', 'score': 0.9}, ...]. Ensure the response is valid JSON and contains only the JSON object."
        prompt = "Identify and extract the product name from the label on the bottle in this image. Return the result in JSON format: [{'description': 'product name', 'score': 0.9}, ...]. Ensure the response is valid JSON and contains only the JSON object."
        
        # Gọi Gemini API
        response = model.generate_content([prompt, image])
        if not response.text:
            raise HTTPException(status_code=500, detail="Gemini API không trả về kết quả")
        
        # Phân tích JSON response
        try:
            labels = json.loads(response.text.strip("```json\n").strip("```"))
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Không thể phân tích JSON từ Gemini API")
        
        # Trả về kết quả
        return {
            "labels": labels,
            "total_labels": len(labels),
            "message": "Xử lý ảnh thành công" if labels else "Không tìm thấy đối tượng nào trong ảnh"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")

# Chạy server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)