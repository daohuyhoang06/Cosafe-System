
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

class SearchRequest(BaseModel):
    keyword: str
    size: int = 10  # Mặc định trả về 10 kết quả
# Tìm chính xác tên sản phẩm
# Trả về tên sản phẩm, điểm tương tự và link ảnh
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
                index="products",
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
        # Truy vấn Elasticsearch với fuzzy search để tìm các sản phẩm có tên gần giống
        result = es.search(
            index="products",
            query={
                "bool": {
                    "should": [
                        # Tìm kiếm mờ - cho phép sai sót trong chuỗi
                        {
                            "fuzzy": {
                                "name": {
                                    "value": request.keyword,
                                    "fuzziness": "AUTO"
                                }
                            }
                        },
                        # Tìm kiếm match - tìm các từ trong tên sản phẩm
                        {
                            "match": {
                                "name": {
                                    "query": request.keyword,
                                    "boost": 2  # Tăng độ ưu tiên cho kết quả match
                                }
                            }
                        },
                        # Tìm kiếm prefix - bắt đầu với từ khóa
                        {
                            "prefix": {
                                "name": {
                                    "value": request.keyword,
                                    "boost": 1.5  # Tăng độ ưu tiên cho kết quả prefix
                                }
                            }
                        }
                    ]
                }
            },
            size=request.size,  # Số lượng kết quả trả về
            collapse={"field": "name.keyword"}  # Dựa vào trường "name" dạng keyword (chuỗi không phân tích)
        )
                # Kiểm tra kết quả
        if not result["hits"]["hits"]:
            return {"products": [], "message": "Không tìm thấy sản phẩm"}
        else:
            products = []
            for hit in result["hits"]["hits"]:
                source = hit["_source"]
                products.append({
                    "id": hit["_id"],
                    "name": source["name"],
                    "score": source.get("score", 0),
                    "search_score": hit["_score"],
                    "link_image": source.get("link_image", "assets/images/product-placeholder.jpg")
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
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            # Chuẩn bị ảnh và prompt
            image = {
                "mime_type": file.content_type,
                "data": content
            }
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
                "message": "Xử lý ảnh thành công" if labels else "Không tìm thấy tên sản phẩm trên nhãn"
            }
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")
    


# Chạy server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

