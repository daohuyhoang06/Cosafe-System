
from fastapi import FastAPI, HTTPException, status, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from elasticsearch import Elasticsearch, helpers
from pydantic import BaseModel
from typing import List, Dict
import re
import json
import io

app = FastAPI()

# Cấu hình kết nối với Elasticsearch
es = Elasticsearch(
    hosts=["https://localhost:9200/"],  
    basic_auth=("elastic", "OYRcPIeE=EB_YELaA=hT"),
    verify_certs=False,
    ssl_show_warn=False 
)

# es = Elasticsearch(
#     "https://934a7c2c20c740988176e6696afaf098.us-central1.gcp.cloud.es.io:443",
#     api_key="NWN0RTFKWUJHS0dSZFVQVFU0SHc6Z2RDVFRVTHo2c0JPY1Z0ektaZ0lwUQ=="
# )

# Kiểm tra kết nối Elasticsearch
if not es.ping():
    raise ValueError("Không thể kết nối tới Elasticsearch!")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Model cho request body
class SafetyRequest(BaseModel):
    name: str

class NERRequest(BaseModel):
    content: str


# Tìm chính xác tên sản phẩm
# Trả về tên sản phẩm, điểm tương tự và link ảnh
@app.post("/safety")
async def safety_check(request: SafetyRequest):
    try:
        # Truy vấn Elasticsearch với term query để tìm chính xác tên sản phẩm
        result = es.search(
            index="cs_products_data",
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
            return {"name": hit["name"], "score": hit["score"], "link_image": hit["link_image"]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


# Quét văn bản, lọc thành phần
@app.post("/name-entity-recognition")
async def ner_and_score(request: NERRequest):
    try:
        ingredients = re.split(r',|\s+và\s+|\s+hoặc\s+', request.content)
        ingredients = [item.strip() for item in ingredients if item.strip()]
        # return {"ingredients": ingredients}
    
        if not ingredients:
           return {"ingredients": [], "message": "Không tìm thấy thành phần trong văn bản"}
        

        # Tìm kiếm sản phẩm chứa các thành phần khớp chính xác
        ingredient_list = []
        for ingredient in ingredients:
            result = es.search(
                index="cs_products_data",
                query={
                    "bool": {
                        "filter": [
                            {"exists": {"field": f"ingredients.{ingredient}"}}  # Kiểm tra thành phần tồn tại
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
            index="cs_products_data",
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


# Chạy server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

